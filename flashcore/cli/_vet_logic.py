*** Begin Patch
*** Update File: flashcore/cli/_vet_logic.py
@@
 def _validate_and_normalize_card(
     raw_card_dict: Dict[str, Any], deck_name: str
 ):
-    pass
+    """Normalize a raw card dictionary before Pydantic validation.
+
+    The audit identified that the *s* (score) field, if present, should be
+    removed because ``Card`` is declared with ``extra="forbid"``.  The
+    original implementation in :mod:`flashcore.parser` calls
+    ``card_data.pop("s", None)`` before constructing a ``Card`` instance.
+
+    Here we mirror that behaviour.  ``raw_card_dict`` may contain arbitrary
+    keys; we copy it to avoid mutating caller data and then remove the
+    ``"s"`` key if present.  After the pop the dict is passed to
+    ``Card(**mapped_card_dict, deck_name=deck_name)``.
+    """
+    # Make a shallow copy to avoid side‑effects on the caller's dict
+    mapped_card_dict = dict(raw_card_dict)
+    # Remove the score field if present – it is not defined on Card
+    mapped_card_dict.pop("s", None)
+    try:
+        return Card(**mapped_card_dict, deck_name=deck_name)
+    except ValidationError as err:
+        console.print(f"[red]Card validation error:[/red] {err}")
+        raise
*** End Patch