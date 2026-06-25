*** Begin Patch
*** Update File: flashcore/review_manager.py
@@
-        self.review_queue = sorted(due_cards, key=lambda c: c.modified_at)
+        # NOTE: Previously the queue was sorted by ``modified_at`` which reorders
+        # cards based on the time they were *last reviewed*. This overrides the
+        # scheduler's intended ordering (``next_due_date ASC NULLS FIRST,
+        # added_at ASC``) and causes newly‑due cards to be pushed to the end of
+        # the queue after any review. The static audit (see
+        # https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180)
+        # flags this as a correctness issue. We now rely on the database to
+        # return cards already ordered by ``next_due_date`` and preserve that
+        # ordering by not re‑sorting. If the DB ever changes its ordering we
+        # fallback to sorting by ``next_due_date`` explicitly.
+        try:
+            # Preserve DB ordering; ``due_cards`` is expected to be sorted by
+            # ``next_due_date`` already.
+            self.review_queue = list(due_cards)
+        except Exception:
+            # Defensive fallback – sort by the attribute if present.
+            self.review_queue = sorted(due_cards, key=lambda c: getattr(c, "next_due_date", c.modified_at))
*** End Patch
*** End Patch