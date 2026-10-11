#!/usr/bin/env python3
"""Exact source C identity and bounded Vietnamese UI strings never drift."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stage_ability_matchcall_source_text import (
    FILES, compile_one, replace_owned_literal, stage,
)

ABILITY = "src/data/text/abilities.h"
MATCH_CALL = "src/data/text/match_call_messages.h"
SOURCE = {
    ABILITY: (
        'static const u8 sDrizzleDescription[] = _("Summons rain in battle.");\n'
        'static const u8 sTraceDescription[] = _("Copies special ability.");\n'
    ),
    MATCH_CALL: (
        'const u8 gText_MatchCallAromaLady_Rose_Strategy[] = _("Becalm fighting emotions.");\n'
        'const u8 gText_MatchCallAromaLady_Rose_Pokemon[] = _("Fragrant GRASS POKéMON.");\n'
    ),
}
ROWS = [
    {"source_file": ABILITY, "category": "system-ui",
     "source_label": "sDrizzleDescription",
     "english": "Summons rain in battle.",
     "vietnamese": "Gọi mưa khi vào trận."},
    {"source_file": MATCH_CALL, "category": "system-ui",
     "source_label": "gText_MatchCallAromaLady_Rose_Strategy",
     "english": "Becalm fighting emotions.",
     "vietnamese": "Giữ bình tĩnh khi đấu."},
]
GLYPHS = {
    ch: i + 1 for i, ch in enumerate(
        " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789.!?,-éọiưữìếấàĩđậ")
}


class AbilityMatchcallSourceTests(unittest.TestCase):
    def test_compile_both_original_C_UI_owners(self):
        result, rows, reasons = stage(ROWS, dict(SOURCE), GLYPHS)
        self.assertEqual(len(rows), 2, reasons)
        self.assertIn("sDrizzleDescription[] = {0x", result[ABILITY])
        self.assertIn("gText_MatchCallAromaLady_Rose_Strategy[] = {0x",
                      result[MATCH_CALL])
        self.assertIn(
            'sTraceDescription[] = _("Copies special ability.");',
            result[ABILITY])
        self.assertIn(
            'gText_MatchCallAromaLady_Rose_Pokemon[] = _("Fragrant GRASS POKéMON.");',
            result[MATCH_CALL])
        self.assertTrue(all(r["source_static_line_budget_preserved"] for r in rows))
        self.assertTrue(all(r["vietnamese"] == r["authored_vietnamese"] for r in rows))
        for r in rows:
            self.assertLessEqual(
                r["translated_static_cells"], r["original_static_cells"])

    def test_never_modify_words_to_force_fit_or_drop_accents(self):
        for authored in (
            "Gọi mưa khi vào trận và còn nhiều nữa.",
            "Gọi mưa khi vào trận. ",
            "Gọi  mưa khi vào trận.",
            "Gọi mưa {PLAYER} khi vào trận.",
            r"Gọi mưa\nkhi vào trận.",
            "Gọi mưa khi vào trậnnnnnnnnn.",
            "Gọi mưa khi vào trận$",
            "Gọi mưa khi vào trận\tttt",
            "Gọi mưa khi vào trậỪn.",
        ):
            with self.subTest(authored=authored):
                with self.assertRaises(ValueError):
                    compile_one(ROWS[0]["english"], authored, GLYPHS, 32)

    def test_wrong_source_and_ambiguous_symbols_refused(self):
        english = ROWS[0]["english"]
        vn = ROWS[0]["vietnamese"]
        payload = compile_one(english, vn, GLYPHS)
        with self.assertRaisesRegex(ValueError, "drifted"):
            replace_owned_literal(
                SOURCE[ABILITY], ABILITY, "sDrizzleDescription",
                "Changed original", payload)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            replace_owned_literal(
                SOURCE[ABILITY] + SOURCE[ABILITY], ABILITY,
                "sDrizzleDescription", english, payload)
        with self.assertRaisesRegex(ValueError, "unsupported"):
            replace_owned_literal(
                SOURCE[ABILITY], ABILITY,
                "gText_MatchCallAromaLady_Rose_Strategy", english, payload)
        _, rows, skipped = stage(
            [ROWS[0]], {ABILITY: SOURCE[ABILITY].replace("Summons", "WRONG")},
            GLYPHS)
        self.assertFalse(rows)
        self.assertTrue(skipped)

    def test_reject_duplicate_and_wrong_category(self):
        with self.assertRaisesRegex(ValueError, "duplicate C owner"):
            stage([ROWS[0], ROWS[0]], dict(SOURCE), GLYPHS)
        _, accepted, _ = stage([
            {**ROWS[0], "category": "battle"}], dict(SOURCE), GLYPHS)
        self.assertEqual(accepted, [])
        _, accepted, _ = stage([
            {**ROWS[0], "source_file": "src/strings.c"}],
            dict(SOURCE), GLYPHS)
        self.assertEqual(accepted, [])


if __name__ == "__main__":
    unittest.main()
