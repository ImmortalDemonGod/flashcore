*** Begin Patch
*** Update File: flashcore/cli/_vet_logic.py
@@
-    # 3. Validate with the Pydantic model
-    card_obj = Card(**mapped_card_dict, deck_name=deck_name)
+    # 3. Ensure the score field 's' is removed before validation so
+    #    Pydantic does not raise a ValidationError.
+    #    This mirrors the behaviour in flashcore/parser.py.
+    mapped_card_dict.pop("s", None)
+    card_obj = Card(**mapped_card_dict, deck_name=deck_name)
*** End Patch
