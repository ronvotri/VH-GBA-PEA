#!/usr/bin/env python3
"""Zero-page system staging must preserve authored text and refuse dynamics."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage_static_paged_system_text import exclude_source_owners
from stage_static_zero_page_system_text import stage_system_zero_page

GLYPHS = {ch: i + 1 for i, ch in enumerate(" abcdefghijklmnopqrstuvwxyz,.!?")}
FILE = "data/text/trainers.inc"
ROW = {
    "category": "system-text", "source_file": FILE, "source_label": "TextIntro",
    "english": r"abc\nabc$", "vietnamese": r"abc def ghi jkl mno pqr$",
}
SOURCE = 'TextIntro::\n\t.string "abc\\nabc$"\nOther::\n\t.string "abc$"\n'


class SystemZeroPageTests(unittest.TestCase):
    def test_accepts_exact_owner_and_keeps_all_words(self):
        sources, rows, rejected = stage_system_zero_page(
            [ROW], {FILE: SOURCE}, GLYPHS, width=11
        )
        self.assertEqual(len(rows), 1, rejected)
        self.assertEqual(rows[0]["source_page_breaks"], 0)
        self.assertEqual(rows[0]["authored_page_breaks"], 0)
        self.assertEqual(rows[0]["word_count"], 6)
        self.assertIn("TextIntro::\n\t.byte ", sources[FILE])
        self.assertIn('Other::\n\t.string "abc$"', sources[FILE])

    def test_rejects_dynamic_unknown_controls_pages_and_missing_glyphs(self):
        for value in (
            r"abc {PLAYER}$", r"abc\pdef$", r"abc\vdef$",
            r"abc\nđẹp$", r"abc  def$", "abc\nabc$",
        ):
            with self.subTest(value=value):
                changed, rows, errors = stage_system_zero_page(
                    [{**ROW, "vietnamese": value}], {FILE: SOURCE}, GLYPHS
                )
                self.assertFalse(rows)
                self.assertTrue(errors)
                self.assertEqual(changed[FILE], SOURCE)

    def test_owner_exclusions_and_wrong_english_are_strict(self):
        prior = {"mode": "apply", "labels_staged": 1, "translated": [
            {"source_file": FILE, "label": "TextIntro"}
        ]}
        pending, skipped = exclude_source_owners([ROW], [prior])
        self.assertFalse(pending)
        self.assertEqual(skipped, 1)
        _, rows, errors = stage_system_zero_page(
            [ROW], {FILE: SOURCE.replace("abc\\nabc$", "wrong$")}, GLYPHS
        )
        self.assertFalse(rows)
        self.assertTrue(any("English source is not exact" in e for e in errors))

    def test_rejects_duplicates_and_non_system_categories(self):
        with self.assertRaisesRegex(ValueError, "duplicated"):
            stage_system_zero_page([ROW, ROW], {FILE: SOURCE}, GLYPHS)
        _, rows, _ = stage_system_zero_page(
            [{**ROW, "category": "map-story"}], {FILE: SOURCE}, GLYPHS
        )
        self.assertFalse(rows)


if __name__ == "__main__":
    unittest.main()
