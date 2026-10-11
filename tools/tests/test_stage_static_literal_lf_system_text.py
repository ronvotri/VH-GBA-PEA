#!/usr/bin/env python3
"""Tests for exact native-control LF normalization of source system text."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage_static_literal_lf_system_text import stage_literal_lf

CODES = {c: i + 1 for i, c in enumerate(" abcdefghijklmnopqrstuvwxyz,.!?")}
FILE = "data/text/trainers.inc"
SOURCE = 'Hello::\n\t.string "abc\\nabc$"\nOther::\n\t.string "abc$"\n'
ROW = {"category": "system-text", "source_file": FILE,
       "source_label": "Hello", "english": r"abc\nabc$",
       "vietnamese": "abc def\nghi jkl$"}


class SystemLiteralLFTests(unittest.TestCase):
    def test_exact_native_newline_normalized_without_loss(self):
        updated, records, skipped = stage_literal_lf(
            [ROW], {FILE: SOURCE}, CODES, width=11
        )
        self.assertEqual(len(records), 1, skipped)
        self.assertEqual(records[0]["literal_LF_count"], 1)
        self.assertEqual(records[0]["word_count"], 4)
        self.assertTrue(records[0]["native_control_signature_preserved"])
        self.assertIn("Hello::\n\t.byte ", updated[FILE])
        self.assertIn('Other::\n\t.string "abc$"', updated[FILE])

    def test_refuse_added_or_moved_control(self):
        for en, vi in (
            (r"abc\lxyz$", "abc\nxyz$"),
            (r"abc\nxyz$", "abc\nxyz\npqr$"),
            (r"abc\pxyz$", "abc\nxyz$"),
            (r"abc\nxyz$", "abc {PLAYER}\nxyz$"),
            (r"abc\nxyz$", "abc  \nxyz$"),
            (r"abc\nxyz$", "abc\tdef\nxyz$"),
            (r"abc\nxyz$", "abc đ\nxyz$"),
        ):
            with self.subTest(en=en, vi=vi):
                new, rows, rejected = stage_literal_lf(
                    [{**ROW, "english": en, "vietnamese": vi}],
                    {FILE: SOURCE}, CODES
                )
                self.assertFalse(rows)
                self.assertTrue(rejected)
                self.assertEqual(new[FILE], SOURCE)

    def test_wrong_english_refused_and_unrelated_rows_ignored(self):
        new, records, rejected = stage_literal_lf(
            [ROW], {FILE: SOURCE.replace("abc\\nabc$", "WRONG$")}, CODES
        )
        self.assertFalse(records)
        self.assertTrue(any("English source is not exact" in x for x in rejected))
        _, records, _ = stage_literal_lf([
            {**ROW, "category": "map-story"}], {FILE: SOURCE}, CODES)
        self.assertFalse(records)
        _, records, _ = stage_literal_lf([
            {**ROW, "vietnamese": r"abc def\nghi jkl$"}],
            {FILE: SOURCE}, CODES)
        self.assertFalse(records)

    def test_duplicate_owner_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicated source manifest"):
            stage_literal_lf([ROW, ROW], {FILE: SOURCE}, CODES)


if __name__ == "__main__":
    unittest.main()
