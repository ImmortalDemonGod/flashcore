# ADR 001: FSRS Library Selection and Roles for Flashcore Scheduler

*   **Status:** Accepted (Revised)
*   **Date:** 2025-06-18 (Original: 2025-06-18)
*   **Deciders:** User (Tom Riddle), Cascade
*   **Context:** Task 19 ([Flashcore] Integrate FSRS Library for Core Scheduling in `flashcore.scheduler`) requires the implementation of the Free Spaced Repetition Scheduling (FSRS) algorithm. This involves both runtime scheduling of cards and offline optimization of FSRS parameters.
*   **Decision:**
    *   For **runtime scheduling** within `FSRS_Scheduler.compute_next_state`, the `py-fsrs` library (PyPI: `fsrs`) will be used.
    *   For **offline optimization** of FSRS parameters (`w`), the `FSRS-Optimizer` library (PyPI: `fsrs-optimizer`) remains the chosen tool.
*   **Rationale:**
    *   **Distinct Roles:** Further investigation (Checkpoint 3, Previous Session Summary) clarified that `fsrs-optimizer` is primarily for generating optimized FSRS parameters (`w`) from review logs, while `py-fsrs` provides the `Scheduler` class necessary for applying these parameters to individual card reviews at runtime.
    *   **`py-fsrs` for Runtime Scheduling:**
        *   Provides the `fsrs.Scheduler` class which can be initialized with custom parameters (`w`).
        *   Its `review_card` method directly supports the calculation of a card's next state (stability, difficulty, due date) based on a review.
        *   Successfully installed (`pip install fsrs`) and imported, making it immediately usable for `FSRS_Scheduler` implementation.
    *   **`FSRS-Optimizer` for Parameter Optimization:**
        *   Aligns with the project's goal of a robust, personalized scheduling mechanism by allowing FSRS parameters to be tuned to the user's learning history.
        *   Defines a clear "Review Logs Schema" for input.
        *   Provides links to FSRS algorithm details.
        *   Simple installation via pip: `python -m pip install fsrs-optimizer`.
        *   Clear usage for optimization: `python -m fsrs_optimizer "revlog.csv"`.
    *   **User Guidance:** The initial selection of `FSRS-Optimizer` was refined through research and understanding its specific role in the FSRS ecosystem.
*   **Consequences:**
    *   The `flashcore.scheduler.FSRS_Scheduler` class will be implemented using `py-fsrs` for its core scheduling logic. It will be designed to consume FSRS parameters (`w`), which can be default values or those optimized by `FSRS-Optimizer`.
    *   Both `fsrs` and `fsrs-optimizer` will be project dependencies, and are already listed in `requirements.txt`.
    *   The runtime scheduling component (Subtask 19.2) can proceed independently of resolving the current segmentation fault issue with `fsrs-optimizer` imports.
    *   Resolving the `fsrs-optimizer` import issue remains important for the full FSRS workflow, specifically for enabling the offline parameter optimization capability.
*   **Next Steps:**
    *   Proceed with Subtask 19.2: Implement the `FSRS_Scheduler` class in `cultivation/flashcore/scheduler.py` using `py-fsrs` for runtime scheduling.
    *   Create/update `cultivation/flashcore/config.py` to hold default FSRS parameters (`w`) for `py-fsrs`.
    *   Subsequently, address the `fsrs-optimizer` import segmentation fault to enable the offline parameter optimization workflow.
    *   Ensure both `fsrs` and `fsrs-optimizer` are correctly managed in `requirements.txt` (already confirmed).
