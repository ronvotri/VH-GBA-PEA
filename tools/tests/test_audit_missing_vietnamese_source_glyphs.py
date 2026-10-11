#!/usr/bin/env python3
"""Missing glyph inventory neither changes authors' text nor creates font art."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_missing_vietnamese_source_glyphs import (
    summarize, validate_codebook, visible_glyphs,
)


class MissingGlyphInventoryTests(unittest.TestCase):
    def test_native_controls_and_dynamic_tokens_not_mistaken_for_glyphs(self):
        chars, issues = visible_glyphs(
            r"Đi nhé {PLAYER}{STR_VAR_1}!\nỪ rồi.\pTới {RIVAL}!$")
        self.assertEqual(issues, [])
        self.assertIn("Ừ", chars)
        self.assertNotIn("{", chars)
        self.assertNotIn("}", chars)
        self.assertNotIn("\\", chars)
        self.assertNotIn("PLAYER", chars)
        self.assertNotIn("$", chars)

    def test_count_distinct_source_rows_per_missing_glyph(self):
        rows = [
            {"source_file": "data/maps/A/scripts.inc", "source_label": "A",
             "category": "map-story", "vietnamese": "Ừ Ừ đ$"},
            {"source_file": "data/text/t.inc", "source_label": "B",
             "category": "system-text", "vietnamese": r"Ồ!\nỪ$"},
            {"source_file": "src/battle.c", "source_label": "C",
             "category": "battle", "vietnamese": "đ$"},
        ]
        seen = [(r["source_file"], r["source_label"]) for r in rows]
        report = summarize(rows, {"đ": 0x33, " ": 0})
        self.assertEqual(
            [(r["source_file"], r["source_label"]) for r in rows], seen)
        self.assertEqual(report["source_plan_distinct_rows"], 3)
        self.assertEqual(report["candidate_rows_with_unsupported_glyph_or_control"], 2)
        missing = {row["character"]: row for row in report["glyph_inventory"]}
        self.assertEqual(missing["Ừ"]["rows_blocked"], 2)
        self.assertEqual(missing["Ừ"]["instances"], 3)
        self.assertEqual(missing["Ồ"]["rows_blocked"], 1)
        self.assertFalse(report["synthetic_glyphs_generated"])
        self.assertFalse(report["v04_approved_font_grafted"])

    def test_codebook_avoids_pokeblock_equals_and_colliding_glyphs(self):
        good = validate_codebook({"glyph_bytes": {
            "a": "0xD5", "đ": "0x33", "ì": "0x37"
        }})
        self.assertEqual(good["đ"], 0x33)
        for blocked in (0x35, 0x53, 0x56, 0x59, 0xFD, 0xFF):
            with self.subTest(blocked=blocked):
                with self.assertRaisesRegex(ValueError, "collides"):
                    validate_codebook({"glyph_bytes": {"đ": hex(blocked)}})
        with self.assertRaisesRegex(ValueError, "shared glyph slot"):
            validate_codebook({"glyph_bytes": {
                "a": "0xD5", "ă": "0xD5"
            }})

    def test_unknown_escape_is_separate_from_unicode_mismatch(self):
        chars, issues = visible_glyphs(r"Xin \q {PLAYER}!$")
        self.assertIn("unknown GBA backslash control", issues)
        self.assertNotIn("q", chars)
        _, issues = visible_glyphs("Đây\nlà$".replace("\n", "\t"))
        self.assertIn("literal control whitespace", issues)
        with self.assertRaisesRegex(ValueError, "duplicate source owner"):
            summarize([
                {"source_file": "x", "source_label": "Y",
                 "vietnamese": "a$"},
                {"source_file": "x", "source_label": "Y",
                 "vietnamese": "b$"},
            ], {"a": 0x01, "b": 0x02})


if __name__ == "__main__":
    unittest.main()
