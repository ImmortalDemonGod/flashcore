"""
Session management and analytics for flashcore.

This module provides comprehensive session tracking, analytics, and insights
for flashcard review sessions. It addresses the gap where session infrastructure
existed but wasn't actively used in review workflows.

The SessionManager class provides:
- Session lifecycle management (start/end/pause/resume)
- Real-time analytics tracking during reviews
- Session insights and performance metrics
- Cross-session comparison and trend analysis
- Integration with all review workflows
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from statistics import mean, median
from dataclasses import dataclass

from .models import Session, Card, Review
from .db.database import FlashcardDatabase

# Initialize logger
logger = logging.getLogger(__name__)


@dataclass
class SessionInsights:
    """
    Comprehensive insights generated from a review session.

    Provides quantitative metrics, trend analysis, and actionable recommendations
    based on session performance and historical comparisons.
    """

    # Performance Metrics
    cards_per_minute: float
    average_response_time_ms: float
    median_response_time_ms: float
    accuracy_percentage: float
    total_review_time_ms: int

    # Efficiency Metrics
    deck_switch_efficiency: float  # Lower is better
    interruption_impact: float  # Percentage impact on performance
    focus_score: float  # 0-100, higher is better

    # Learning Progress
    improvement_rate: float  # Compared to recent sessions
    learning_velocity: float  # Cards mastered per session
    retention_score: float  # Based on review outcomes

    # Attention Patterns
    fatigue_detected: bool
    optimal_session_length: int  # Recommended duration in minutes
    peak_performance_time: Optional[str]  # Time of day for best performance

    # Recommendations
    recommendations: List[str]
    achievements: List[str]
    alerts: List[str]

    # Comparisons
    vs_last_session: Dict[str, float]  # Percentage changes
    vs_average: Dict[str, float]  # Compared to user average
    trend_direction: str  # "improving", "stable", "declining"


class SessionManager:
    """
    Manages flashcard review sessions with comprehensive analytics and insights.

    This class addresses the gap where session infrastructure existed but wasn't
    actively used. It provides:

    - Session lifecycle management
    - Real-time analytics tracking
    - Performance insights generation
    - Cross-session comparisons
    - Integration with review workflows

    The SessionManager can be used standalone or integrated with existing
    review workflows like ReviewSessionManager and review-all logic.
    """

    def __init__(
        self, db_manager: FlashcardDatabase, user_id: Optional[str] = None
    ):
        """
        Initialize the SessionManager.

        Args:
            db_manager: Database manager instance for persistence
            user_id: Optional user identifier for multi-user support
        """
        self.db_manager = db_manager
        self.user_id = user_id
        self.current_session: Optional[Session] = None
        self.session_start_time: Optional[datetime] = None
        self.last_activity_time: Optional[datetime] = None
        self.pause_start_time: Optional[datetime] = None
        self.total_pause_duration_ms: int = 0

        # Real-time tracking
        self.cards_reviewed_this_session: List[UUID] = []
        self.response_times: List[int] = []
        self.ratings_given: List[int] = []
        self.deck_access_order: List[str] = []
        self.interruption_timestamps: List[datetime] = []

    def start_session(
        self,
        device_type: Optional[str] = None,
        platform: Optional[str] = None,
        session_uuid: Optional[UUID] = None,
    ) -> Session:
        """
        Start a new review session with comprehensive tracking.

        Args:
            device_type: Type of device (desktop, mobile, tablet)
            platform: Platform used (cli, web, mobile_app)
            session_uuid: Optional existing session UUID (for integration)

        Returns:
            Created Session object

        Raises:
            ValueError: If a session is already active
        """
        if self.current_session is not None:
            raise ValueError(
                "A session is already active. End the current session first."
            )

        # Create new session
        self.current_session = Session(
            session_uuid=session_uuid or uuid4(),
            user_id=self.user_id,
            device_type=device_type,
            platform=platform or "cli",
        )

        # Initialize tracking
        self.session_start_time = datetime.now(timezone.utc)
        self.last_activity_time = self.session_start_time
        self.total_pause_duration_ms = 0

        # Reset session-specific tracking
        self.cards_reviewed_this_session = []
        self.response_times = []
        self.ratings_given = []
        self.deck_access_order = []
        self.interruption_timestamps = []

        # Persist to database
        try:
            self.current_session = self.db_manager.create_session(
                self.current_session
            )
            logger.info(f"Started session {self.current_session.session_uuid}")
            return self.current_session

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            self.current_session = None
            raise

    def record_card_review(
        self,
        card: Card,
        rating: int,
        response_time_ms: int,
        evaluation_time_ms: int = 0,
    ) -> None:
        """
        Record a card review with real-time analytics tracking.

        Args:
            card: Card that was reviewed
            rating: User's rating (1-4)
            response_time_ms: Time to reveal answer
            evaluation_time_ms: Time to provide rating

        Raises:
            ValueError: If no active session
        """
        if self.current_session is None:
            raise ValueError("No active session. Start a session first.")

        current_time = datetime.now(timezone.utc)

        # Detect interruptions (gaps > 2 minutes since last activity)
        if self.last_activity_time:
            time_since_last = (
                current_time - self.last_activity_time
            ).total_seconds()
            if time_since_last > 120:  # 2 minutes
                self.record_interruption()

        # Track deck access patterns
        previous_deck = (
            self.deck_access_order[-1] if self.deck_access_order else None
        )

        if card.deck_name not in self.deck_access_order:
            self.deck_access_order.append(card.deck_name)

        # Count deck switch only if switching from a different deck
        if previous_deck is not None and previous_deck != card.deck_name:
            self.current_session.deck_switches += 1

        # Update session analytics manually (to avoid double-counting deck switches)
        self.current_session.decks_accessed.add(card.deck_name)
        self.current_session.cards_reviewed += 1

        # Track performance metrics
        self.cards_reviewed_this_session.append(card.uuid)
        self.response_times.append(response_time_ms)
        self.ratings_given.append(rating)

        # Update last activity time
        self.last_activity_time = current_time

        # Update session in database
        try:
            self.current_session = self.db_manager.update_session(
                self.current_session
            )
            logger.debug(
                f"Recorded review for card {card.uuid} in session {self.current_session.session_uuid}"
            )

        except Exception as e:
            logger.error(f"Failed to update session after card review: {e}")

    def record_interruption(self) -> None:
        """
        Record an interruption in the current session.

        Raises:
            ValueError: If no active session
        """
        if self.current_session is None:
            raise ValueError("No active session. Start a session first.")

        self.current_session.record_interruption()
        self.interruption_timestamps.append(datetime.now(timezone.utc))

        try:
            self.current_session = self.db_manager.update_session(
                self.current_session
            )
            logger.debug(
                f"Recorded interruption in session {self.current_session.session_uuid}"
            )

        except Exception as e:
            logger.error(f"Failed to update session after interruption: {e}")

    def pause_session(self) -> None:
        """
        Pause the current session, stopping time tracking.

        Raises:
            ValueError: If no active session or session already paused
        """
        if self.current_session is None:
            raise ValueError("No active session. Start a session first.")

        if self.pause_start_time is not None:
            raise ValueError("Session is already paused.")

        self.pause_start_time = datetime.now(timezone.utc)
        logger.debug(f"Paused session {self.current_session.session_uuid}")

    def resume_session(self) -> None:
        """
        Resume a paused session, continuing time tracking.

        Raises:
            ValueError: If no active session or session not paused
        """
        if self.current_session is None:
            raise ValueError("No active session. Start a session first.")

        if self.pause_start_time is None:
            raise ValueError("Session is not paused.")

        # Calculate pause duration
        pause_duration = datetime.now(timezone.utc) - self.pause_start_time
        self.total_pause_duration_ms += int(
            pause_duration.total_seconds() * 1000
        )

        self.pause_start_time = None
        self.last_activity_time = datetime.now(timezone.utc)

        logger.debug(f"Resumed session {self.current_session.session_uuid}")

    def end_session(self) -> Session:
        """
        End the current session and generate final analytics.

        Returns:
            Completed Session object with final analytics

        Raises:
            ValueError: If no active session
        """
        if self.current_session is None:
            raise ValueError("No active session. Start a session first.")

        # Resume if paused
        if self.pause_start_time is not None:
            self.resume_session()

        # Calculate final duration (excluding pauses)
        end_time = datetime.now(timezone.utc)
        total_duration_ms = int(
            (end_time - self.session_start_time).total_seconds() * 1000  # type: ignore[operator]
        )
        active_duration_ms = total_duration_ms - self.total_pause_duration_ms

        # Update session with final data
        self.current_session.end_session()
        self.current_session.total_duration_ms = active_duration_ms

        # Persist final session state
        try:
            completed_session = self.db_manager.update_session(
                self.current_session
            )
            logger.info(
                f"Ended session {completed_session.session_uuid}. "
                f"Duration: {active_duration_ms/1000:.1f}s, "
                f"Cards: {completed_session.cards_reviewed}, "
                f"Decks: {len(completed_session.decks_accessed)}"
            )

            # Clear current session
            self.current_session = None
            self.session_start_time = None
            self.last_activity_time = None

            return completed_session

        except Exception as e:
            logger.error(f"Failed to finalize session: {e}")
            raise

    def get_current_session_stats(self) -> Dict[str, Any]:
        """
        Get real-time statistics for the current session.

        Returns:
            Dictionary with current session metrics

        Raises:
            ValueError: If no active session
        """
        if self.current_session is None:
            raise ValueError("No active session. Start a session first.")

        current_time = datetime.now(timezone.utc)
        elapsed_ms = int(
            (current_time - self.session_start_time).total_seconds() * 1000  # type: ignore[operator]
        )
        active_ms = elapsed_ms - self.total_pause_duration_ms

        stats = {
            "session_uuid": str(self.current_session.session_uuid),
            "elapsed_time_ms": active_ms,
            "cards_reviewed": self.current_session.cards_reviewed,
            "decks_accessed": list(self.current_session.decks_accessed),
            "deck_switches": self.current_session.deck_switches,
            "interruptions": self.current_session.interruptions,
            "cards_per_minute": (
                (self.current_session.cards_reviewed / (active_ms / 60000))
                if active_ms > 0
                else 0
            ),
            "average_response_time_ms": (
                mean(self.response_times) if self.response_times else 0
            ),
            "is_paused": self.pause_start_time is not None,
        }

        return stats

    def generate_session_insights(self, session_uuid: UUID) -> SessionInsights:
        """
        Generate comprehensive insights for a completed session.

        Args:
            session_uuid: UUID of the session to analyze

        Returns:
            SessionInsights object with comprehensive analytics

        Raises:
            ValueError: If session not found
        """
        # Get session from database
        session = self.db_manager.get_session_by_uuid(session_uuid)
        if not session:
            raise ValueError(f"Session {session_uuid} not found")

        if session.end_ts is None:
            raise ValueError(f"Session {session_uuid} is still active")

        # Get reviews for this session
        reviews = self._get_session_reviews(session_uuid)

        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(
            session, reviews
        )

        # Get historical context
        historical_sessions = self._get_user_sessions(
            session.user_id, limit=10
        )
        comparisons = self._calculate_session_comparisons(
            session, historical_sessions
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            session, reviews, comparisons
        )

        # Detect achievements
        achievements = self._detect_achievements(
            session, reviews, historical_sessions
        )

        # Generate alerts
        alerts = self._generate_alerts(session, reviews, comparisons)

        return SessionInsights(
            **performance_metrics,
            recommendations=recommendations,
            achievements=achievements,
            alerts=alerts,
            vs_last_session=comparisons.get("vs_last_session", {}),
            vs_average=comparisons.get("vs_average", {}),
            trend_direction=comparisons.get("trend_direction", "stable"),
        )

    def _get_session_reviews(self, session_uuid: UUID) -> List[Review]:
        """Get all reviews for a specific session."""
        # Get the session to find its timeframe
        session = self.db_manager.get_session_by_uuid(session_uuid)
        if not session:
            return []

        try:
            conn = self.db_manager.get_connection()

            def _fetch_as_dicts(connection, query, params):
                """Execute query and return list of dicts using cursor.description."""
                result = connection.execute(query, params)
                cols = [desc[0] for desc in result.description]
                return [dict(zip(cols, row)) for row in result.fetchall()]

            # First try to get reviews by session_uuid (if they were linked)
            sql = "SELECT * FROM reviews WHERE session_uuid = $1 ORDER BY ts ASC;"
            rows = _fetch_as_dicts(conn, sql, (session_uuid,))

            # If no reviews found by session_uuid, try to get reviews by timeframe
            if not rows and session.start_ts and session.end_ts:
                sql = "SELECT * FROM reviews WHERE ts >= $1 AND ts <= $2 ORDER BY ts ASC;"
                rows = _fetch_as_dicts(
                    conn, sql, (session.start_ts, session.end_ts)
                )

            if not rows:
                return []

            # Convert to Review objects
            reviews = []
            for row in rows:
                # Handle UUID conversion safely
                card_uuid = (
                    row["card_uuid"]
                    if isinstance(row["card_uuid"], UUID)
                    else UUID(row["card_uuid"])
                )
                sess_uuid = None
                if row["session_uuid"]:
                    sess_uuid = (
                        row["session_uuid"]
                        if isinstance(row["session_uuid"], UUID)
                        else UUID(row["session_uuid"])
                    )

                review = Review(
                    card_uuid=card_uuid,
                    session_uuid=sess_uuid,
                    ts=row["ts"],
                    rating=row["rating"],
                    resp_ms=row["resp_ms"],
                    eval_ms=row["eval_ms"],
                    stab_before=row["stab_before"],
                    stab_after=row["stab_after"],
                    diff=row["diff"],
                    next_due=row["next_due"],
                    elapsed_days_at_review=row["elapsed_days_at_review"],
                    scheduled_days_interval=row["scheduled_days_interval"],
                    review_type=row["review_type"],
                )
                reviews.append(review)

            return reviews

        except Exception as e:
            logger.error(f"Failed to get session reviews: {e}")
            return []

    def _calculate_performance_metrics(
        self, session: Session, reviews: List[Review]
    ) -> Dict[str, Any]:
        """Calculate performance metrics for a session."""
        if not reviews:
            return {
                "cards_per_minute": 0.0,
                "average_response_time_ms": 0.0,
                "median_response_time_ms": 0.0,
                "accuracy_percentage": 0.0,
                "total_review_time_ms": 0,
                "deck_switch_efficiency": 0.0,
                "interruption_impact": 0.0,
                "focus_score": 100.0,
                "improvement_rate": 0.0,
                "learning_velocity": 0.0,
                "retention_score": 0.0,
                "fatigue_detected": False,
                "optimal_session_length": 30,
                "peak_performance_time": None,
            }

        # Basic metrics
        response_times = [r.resp_ms for r in reviews if r.resp_ms and r.resp_ms > 0]  # type: ignore[operator]
        ratings = [r.rating for r in reviews]

        duration_minutes = (session.total_duration_ms or 0) / 60000
        cards_per_minute = (
            session.cards_reviewed / duration_minutes
            if duration_minutes > 0
            else 0
        )

        avg_response_time = mean(response_times) if response_times else 0  # type: ignore[type-var]
        median_response_time = median(response_times) if response_times else 0  # type: ignore[type-var]

        # Accuracy (Good/Easy ratings as "correct")
        good_ratings = len([r for r in ratings if r >= 3])  # Good or Easy
        accuracy = (good_ratings / len(ratings) * 100) if ratings else 0

        # Focus score (inverse of interruptions and deck switches)
        interruption_penalty = min(session.interruptions * 10, 50)
        deck_switch_penalty = min(session.deck_switches * 5, 30)
        focus_score = max(100 - interruption_penalty - deck_switch_penalty, 0)

        # Fatigue detection (increasing response times over session)
        fatigue_detected = False
        if len(response_times) >= 5:
            first_half = response_times[: len(response_times) // 2]
            second_half = response_times[len(response_times) // 2 :]
            if mean(second_half) > mean(first_half) * 1.3:  # type: ignore[operator]
                fatigue_detected = True

        return {
            "cards_per_minute": round(cards_per_minute, 2),
            "average_response_time_ms": round(avg_response_time, 0),  # type: ignore[arg-type]
            "median_response_time_ms": round(median_response_time, 0),  # type: ignore[arg-type]
            "accuracy_percentage": round(accuracy, 1),
            "total_review_time_ms": sum(response_times),
            "deck_switch_efficiency": round(
                100 - (session.deck_switches * 10), 1
            ),
            "interruption_impact": round(session.interruptions * 5, 1),
            "focus_score": round(focus_score, 1),
            "improvement_rate": 0.0,  # Would need historical comparison
            "learning_velocity": round(
                good_ratings / duration_minutes if duration_minutes > 0 else 0,
                2,
            ),
            "retention_score": round(accuracy, 1),
            "fatigue_detected": fatigue_detected,
            "optimal_session_length": 30,  # Default recommendation
            "peak_performance_time": None,
        }

    def _get_user_sessions(
        self, user_id: Optional[str], limit: int = 10
    ) -> List[Session]:
        """Get recent sessions for a user."""
        try:
            return self.db_manager.get_recent_sessions(
                user_id=user_id, limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []

    def _calculate_session_comparisons(
        self, session: Session, historical_sessions: List[Session]
    ) -> Dict[str, Any]:
        """Calculate comparisons with historical sessions."""
        if len(historical_sessions) < 2:
            return {
                "vs_last_session": {},
                "vs_average": {},
                "trend_direction": "stable",
            }

        # Compare with last session
        last_session = (
            historical_sessions[1] if len(historical_sessions) > 1 else None
        )
        vs_last = {}

        if last_session:
            if last_session.cards_reviewed > 0:
                cards_change = (
                    (session.cards_reviewed - last_session.cards_reviewed)
                    / last_session.cards_reviewed
                ) * 100
                vs_last["cards_reviewed"] = round(cards_change, 1)

            if (
                last_session.total_duration_ms
                and last_session.total_duration_ms > 0
            ):
                duration_change = (
                    (
                        session.total_duration_ms  # type: ignore[operator]
                        - last_session.total_duration_ms
                    )
                    / last_session.total_duration_ms
                ) * 100
                vs_last["duration"] = round(duration_change, 1)

        # Compare with average
        avg_cards = mean([s.cards_reviewed for s in historical_sessions[1:]])
        avg_duration = mean(
            [
                s.total_duration_ms
                for s in historical_sessions[1:]
                if s.total_duration_ms
            ]
        )

        vs_average = {}
        if avg_cards > 0:
            cards_vs_avg = (
                (session.cards_reviewed - avg_cards) / avg_cards
            ) * 100
            vs_average["cards_reviewed"] = round(cards_vs_avg, 1)

        if avg_duration > 0:
            duration_vs_avg = (
                (session.total_duration_ms - avg_duration) / avg_duration  # type: ignore[operator]
            ) * 100
            vs_average["duration"] = round(duration_vs_avg, 1)

        # Determine trend
        recent_cards = [s.cards_reviewed for s in historical_sessions[:3]]
        if len(recent_cards) >= 3:
            if recent_cards[0] > recent_cards[1] > recent_cards[2]:
                trend = "improving"
            elif recent_cards[0] < recent_cards[1] < recent_cards[2]:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "vs_last_session": vs_last,
            "vs_average": vs_average,
            "trend_direction": trend,
        }

    def _generate_recommendations(
        self,
        session: Session,
        reviews: List[Review],
        comparisons: Dict[str, Any],
    ) -> List[str]:
        """Generate actionable recommendations based on session analysis."""
        recommendations = []

        # Duration recommendations
        if (
            session.total_duration_ms and session.total_duration_ms > 3600000
        ):  # > 1 hour
            recommendations.append(
                "Consider shorter sessions (30-45 minutes) to maintain focus and retention."
            )
        elif (
            session.total_duration_ms and session.total_duration_ms < 600000
        ):  # < 10 minutes
            recommendations.append(
                "Try longer sessions (15-30 minutes) for better learning consolidation."
            )

        # Interruption recommendations
        if session.interruptions > 2:
            recommendations.append(
                "Find a quieter environment to reduce interruptions and improve focus."
            )

        # Deck switching recommendations
        if session.deck_switches > 3:
            recommendations.append(
                "Focus on one deck at a time to improve learning efficiency."
            )

        # Performance recommendations
        if reviews:
            avg_rating = mean([r.rating for r in reviews])
            if avg_rating < 2.5:
                recommendations.append(
                    "Consider reviewing cards more frequently to improve retention."
                )
            elif avg_rating > 3.5:
                recommendations.append(
                    "You're doing great! Consider adding more challenging cards."
                )

        return recommendations

    def _detect_achievements(
        self,
        session: Session,
        reviews: List[Review],
        historical_sessions: List[Session],
    ) -> List[str]:
        """Detect achievements and positive milestones."""
        achievements = []

        # Cards reviewed milestones
        if session.cards_reviewed >= 50:
            achievements.append("🎯 Reviewed 50+ cards in one session!")
        elif session.cards_reviewed >= 25:
            achievements.append("📚 Reviewed 25+ cards - great dedication!")

        # Focus achievements
        if session.interruptions == 0:
            achievements.append("🎯 Perfect focus - zero interruptions!")

        # Consistency achievements
        if len(historical_sessions) >= 7:
            recent_sessions = historical_sessions[:7]
            if all(s.cards_reviewed > 0 for s in recent_sessions):
                achievements.append("🔥 7-day review streak!")

        # Efficiency achievements
        duration_minutes = (session.total_duration_ms or 0) / 60000
        if duration_minutes > 0:
            cards_per_minute = session.cards_reviewed / duration_minutes
            if cards_per_minute > 1.0:
                achievements.append(
                    "⚡ High efficiency - over 1 card per minute!"
                )

        return achievements

    def _generate_alerts(
        self,
        session: Session,
        reviews: List[Review],
        comparisons: Dict[str, Any],
    ) -> List[str]:
        """Generate alerts for concerning patterns."""
        alerts = []

        # Performance decline alerts
        vs_last = comparisons.get("vs_last_session", {})
        if vs_last.get("cards_reviewed", 0) < -50:
            alerts.append(
                "⚠️ Significant decrease in cards reviewed compared to last session."
            )

        # Fatigue alerts
        if session.interruptions > 5:
            alerts.append(
                "⚠️ High number of interruptions detected - consider taking a break."
            )

        # Trend alerts
        if comparisons.get("trend_direction") == "declining":
            alerts.append(
                "📉 Performance trend is declining - consider adjusting study schedule."
            )

        return alerts
