#!/usr/bin/env python3
"""Map dynamic substitutions keep their exact owners and native GBA controls."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage_dynamic_map_static_budget import stage
from stage_safe_system_dynamic_variables import VARIABLE_BYTES
from stage_system_dynamic_static_budget_reflow import (
    compile_dynamic, LAYOUT, TOKEN,
)

FILE = "data/maps/Route101/scripts.inc"
ENGLISH = r"hello {STR_VAR_1}!\ngood morning\pbye {PLAYER}$"
VIETNAMESE = r"hello friend {STR_VAR_1}! long talk\ngood day\pbye {PLAYER} dear friend$"
CODES = {ch: i + 1 for i, ch in
         enumerate(" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,.!?")}
ROW = {
    "category": "map-story", "source_file": FILE, "source_label": "Route101Text",
    "english": ENGLISH, "vietnamese": VIETNAMESE,
}
SRC = (
    'Route101Text::\n'
    '\t.string "hello {STR_VAR_1}!\\ngood morning\\pbye {PLAYER}$"\n'
    'StillHere::\n\t.string "a$"\n'
)


class SafeMapDynamicTests(unittest.TestCase):
    def test_source_owned_map_reflow_and_exact_word_order(self):
        sources, rows, skipped = stage(
            [ROW], {FILE: SRC}, CODES, VARIABLE_BYTES, width=26)
        self.assertEqual(len(rows), 1, skipped)
        self.assertEqual(rows[0]["page_count"], 2)
        rendered = rows[0]["vietnamese"]
        for original, converted in zip(
            VIETNAMESE[:-1].split(r"\p"),
            rendered[:-1].split(r"\p"),
        ):
            self.assertEqual(
                LAYOUT.sub(" ", original).split(),
                LAYOUT.sub(" ", converted).split())
        self.assertEqual(
            TOKEN.findall(rendered),
            TOKEN.findall(ENGLISH))
        self.assertIn("Route101Text::\n\t.byte ", sources[FILE])
        self.assertIn('StillHere::\n\t.string "a$"', sources[FILE])

    def test_safe_rejection_of_unsafe_map_strings(self):
        invalid = [
            VIETNAMESE.replace("{STR_VAR_1}", "{STR_VAR_3}"),
            VIETNAMESE.replace(r"\p", r"\n"),
            VIETNAMESE.replace(r"\n", r"\l"),
            VIETNAMESE.replace("hello", "hẻllo"),
            VIETNAMESE.replace("hello", "hello  "),
            VIETNAMESE.replace("{PLAYER}", "{FOO}"),
        ]
        for vietnamese in invalid:
            with self.subTest(vietnamese=vietnamese):
                unchanged, rows, skipped = stage(
                    [{**ROW, "vietnamese": vietnamese}],
                    {FILE: SRC}, CODES, VARIABLE_BYTES)
                self.assertEqual(rows, [])
                self.assertTrue(skipped)
                self.assertEqual(unchanged[FILE], SRC)

    def test_unrelated_owner_and_dupes_are_not_touched(self):
        _, rows, _ = stage(
            [{**ROW, "category": "system-text"}],
            {FILE: SRC}, CODES, VARIABLE_BYTES)
        self.assertEqual(rows, [])
        _, rows, skipped = stage(
            [ROW], {FILE: SRC.replace("hello", "WRONG")},
            CODES, VARIABLE_BYTES)
        self.assertFalse(rows)
        self.assertTrue(skipped)
        with self.assertRaisesRegex(ValueError, "duplicate plan map owner"):
            stage([ROW, ROW], {FILE: SRC}, CODES, VARIABLE_BYTES)
        with self.assertRaisesRegex(ValueError, "unpinned"):
            stage([ROW], {FILE: SRC}, CODES,
                  {**VARIABLE_BYTES, "PLAYER": b"\xfd\x09"})

    def test_original_source_static_cell_budget_not_exceeded(self):
        compiled, payload, details = compile_dynamic(
            ENGLISH, VIETNAMESE, CODES, VARIABLE_BYTES, 26)
        self.assertIn(b"\xfd\x02", payload)
        self.assertIn(b"\xfd\x01", payload)
        self.assertEqual(payload[-1], 0xff)
        self.assertEqual(len(details), 2)
        for page in details:
            for line in page["per_segment_static_budgets"]:
                if line["tokens"]:
                    self.assertLessEqual(
                        line["dynamic_static_cells"],
                        line["source_static_budget"])


if __name__ == "__main__":
    unittest.main()
