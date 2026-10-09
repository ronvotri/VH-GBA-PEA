#!/usr/bin/env python3
"""The string provenance auditor must never mistake graphics/code for text."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from triage_shared_owner_provenance import classify_symbol, nearest_symbol


class OwnerProvenanceTests(unittest.TestCase):
    def test_graphic_sprite_word_is_not_text(self):
        self.assertEqual(classify_symbol("gMonFrontPic_Numel", "R"),
                         "incidental-graphic-word")

    def test_graphic_title_map_word_is_not_text(self):
        self.assertEqual(classify_symbol("gRaySceneTakesFlight_Bg_Tilemap", "R"),
                         "incidental-graphic-word")

    def test_function_bytes_are_not_text_references(self):
        self.assertEqual(classify_symbol("MoveWordSelectCursor", "t"),
                         "incidental-code-word")
        self.assertEqual(classify_symbol("LoopedTask_CloseMonMarkingsWindow", "t"),
                         "incidental-code-word")

    def test_named_game_script_is_plausible_not_approved(self):
        self.assertEqual(classify_symbol("Route114_EventScript_Nolan", "D"),
                         "plausible-named-owner")

    def test_named_pointer_table_is_plausible_not_approved(self):
        self.assertEqual(classify_symbol("sApprenticeHeldItemTexts", "r"),
                         "plausible-named-owner")

    def test_unknown_data_symbol_requires_review(self):
        self.assertEqual(classify_symbol("gMysteriousBinary", "R"),
                         "needs-source-review")

    def test_nearest_symbol_is_preceding(self):
        symbols = [(5, "a", "D"), (14, "b", "R"), (60, "c", "t")]
        self.assertIsNone(nearest_symbol(symbols, 3))
        self.assertEqual(nearest_symbol(symbols, 18), (14, "b", "R"))


if __name__ == "__main__":
    unittest.main()
