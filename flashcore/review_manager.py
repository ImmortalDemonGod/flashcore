*** Begin Patch
*** Update File: flashcore/review_manager.py
@@
 class ReviewSessionManager:
@@
         return self.db.get_due_card_count(
             deck_name=self.deck_name, on_date=today
         )
+
+# Backwards compatibility shim
+# The original public API exposed a ``ReviewManager`` class. Tests and external
+# code import ``ReviewManager`` from this module. The refactor introduced the
+# more descriptive ``ReviewSessionManager`` but omitted the legacy name,
+# causing an ImportError. We provide a thin alias that retains the original
+# semantics without altering behaviour.
+
+class ReviewManager(ReviewSessionManager):
+    """Compatibility wrapper for legacy imports.
+
+    It inherits all functionality from :class:`ReviewSessionManager` and
+    exists solely to satisfy code that expects ``ReviewManager`` to be present.
+    """
+
+    pass
*** End Patch
*** End Patch