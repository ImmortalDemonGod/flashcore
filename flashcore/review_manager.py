*** Begin Patch
*** Update File: flashcore/review_manager.py
@@
-"""
-This module defines the ReviewSessionManager class, which is responsible for
-managing a flashcard review session. It interacts with the database to fetch
-cards, uses a scheduler to determine review timings, and records review outcomes.
-"""
+"""flashcore.review_manager
+=================================
+This module provides the **ReviewManager** class used throughout the codebase
+and test suite. Historically the implementation was renamed to
+``ReviewSessionManager`` but the public alias was never re‑exported, resulting
+of ``ImportError: cannot import name 'ReviewManager'`` during test collection.
+
+The fix performs two tasks:
+
+1. **Compatibility alias** – expose ``ReviewManager`` as an alias for the
+   concrete ``ReviewSessionManager`` implementation so existing imports keep
+   working.
+2. **Ordering bug** – the original ``initialize_session`` method re‑sorted the
+   list of due cards by ``modified_at``. The database already returns cards in
+   the correct scheduler order (``next_due_date ASC NULLS FIRST, added_at ASC``).
+   Re‑sorting broke the spaced‑repetition contract by moving freshly reviewed
+   cards to the end of the queue. The fix removes this unnecessary sort and
+   preserves the order provided by ``db.get_due_cards``.
+
+Both changes are limited to the file specified in the plan's §10 scope and do
+not alter any public API beyond restoring the expected name.
+"""
@@
-class ReviewSessionManager:
-    """
-    Manages a review session for flashcards.
-
-    This class is responsible for:
-    - Initializing a review session with a specific set of cards.
-    - Providing cards one by one for review.
-    - Processing user reviews and updating card states.
-    - Interacting with the database to persist changes.
-    """
+# NOTE: Historical name of this manager was ``ReviewManager``. The test suite
+# expects a class with that name to be importable from ``flashcore.review_manager``.
+# The original implementation renamed the class to ``ReviewSessionManager`` but
+# did not provide a compatibility alias, causing an ``ImportError``.  To restore
+# compatibility we keep the implementation name (it is descriptive) and later
+# expose ``ReviewManager`` as an alias.
+
+class ReviewSessionManager:
+    """Manages a review session for flashcards.
+
+    This class is responsible for:
+    - Initializing a review session with a specific set of cards.
+    - Providing cards one by one for review.
+    - Processing user reviews and updating card states.
+    - Interacting with the database to persist changes.
+    """
@@
-        self.review_queue = sorted(due_cards, key=lambda c: c.modified_at)
+        # NOTE: The original code sorted by ``modified_at`` which re‑orders cards
+        # based on the time they were *last reviewed*.  The scheduler already
+        # returns cards ordered by ``next_due_date ASC NULLS FIRST, added_at ASC``
+        # (see ``db.database.get_due_cards``).  Re‑sorting by ``modified_at``
+        # overrides that ordering and breaks the spaced‑repetition contract –
+        # new cards may be pushed behind already‑reviewed cards.  The correct
+        # behaviour is to preserve the scheduler's ordering.  Therefore we no
+        # longer apply any additional sorting.
+        self.review_queue = list(due_cards)
*** End Patch
*** End Patch
*** Begin Patch
*** Update File: flashcore/review_manager.py
@@
         logger.info(
             f"Initialized session with {len(self.review_queue)} cards."
         )
+
+# Compatibility alias expected by the test suite and external imports.
+ReviewManager = ReviewSessionManager
*** End Patch
*** End Patch