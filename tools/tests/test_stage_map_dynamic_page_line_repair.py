#!/usr/bin/env python3
"""Tests for dynamic NPC original-page reflow without changed authoring."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage_map_dynamic_page_line_repair import (
    compile_line_repaired_page, stage, LAYOUT, TOKEN,
)
from stage_safe_system_dynamic_variables import VARIABLE_BYTES

CODES = {ch: i + 1 for i, ch in enumerate(
    " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,.!?")}
FILE = "data/maps/Route101/scripts.inc"
EN = r"hello {STR_VAR_1}!\ncome to Hoenn\pHi {PLAYER}!\lHello again$"
VI = r"Hello dear {STR_VAR_1}! please come to our town\lThe day is very nice\pHi {PLAYER}! i am so happy here$"
SRC = (
    'Dialogue::\n'
    '\t.string "hello {STR_VAR_1}!\\ncome to Hoenn\\pHi {PLAYER}!\\lHello again$"\n'
    'Other::\n\t.string "a$"\n'
)
ROW = {
    "category": "map-story", "source_file": FILE,
    "source_label": "Dialogue", "english": EN, "vietnamese": VI,
}


class RepairMapNativeLinesTests(unittest.TestCase):
    def test_accept_changed_native_line_control_only(self):
        rendered, payload, proof = compile_line_repaired_page(
            EN, VI, CODES, VARIABLE_BYTES)
        self.assertEqual(rendered.count(r"\p"), 1)
        self.assertIn(b"\xfd\x02", payload)
        self.assertIn(b"\xfd\x01", payload)
        self.assertEqual(payload[-1], 0xFF)
        self.assertEqual(len(proof), 2)
        for src, new in zip(VI[:-1].split(r"\p"),
                            rendered[:-1].split(r"\p")):
            self.assertEqual(LAYOUT.sub(" ", src).split(),
                             LAYOUT.sub(" ", new).split())
        self.assertEqual(TOKEN.findall(rendered), TOKEN.findall(EN))
        self.assertLessEqual(
            proof[0]["compiled_variable_line_static_cells"],
            proof[0]["original_variable_line_budget"])

    def test_write_exact_symbol_while_preserving_unrelated(self):
        updated, rows, skipped = stage(
            [ROW], {FILE: SRC}, CODES, VARIABLE_BYTES)
        self.assertEqual(len(rows), 1, skipped)
        self.assertIn("Dialogue::\n\t.byte ", updated[FILE])
        self.assertIn('Other::\n\t.string "a$"', updated[FILE])

    def test_refuse_page_moves_variable_changes_and_unknowns(self):
        bad = [
            VI.replace(r"\p", r"\l"),
            VI.replace("{STR_VAR_1}", "{STR_VAR_2}"),
            VI.replace("{PLAYER}", "{RIVAL}"),
            VI.replace("Hello", "HỪllo"),
            VI.replace("dear", "a" * 35),
            VI.replace("Hello", "Hello  "),
            VI.replace("Hello", "Hello\n"),
        ]
        for candidate in bad:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    compile_line_repaired_page(
                        EN, candidate, CODES, VARIABLE_BYTES)

    def test_refuse_multiple_source_variable_lines_per_page(self):
        en = r"hi {STR_VAR_1}\nbye {PLAYER}$"
        vi = r"hello {STR_VAR_1} and {PLAYER}$"
        with self.assertRaisesRegex(ValueError, "multiple variable-bearing"):
            compile_line_repaired_page(en, vi, CODES, VARIABLE_BYTES)

    def test_source_drift_and_duplicate_identity_fail_closed(self):
        _, accepted, skipped = stage(
            [ROW], {FILE: SRC.replace("hello", "WRONG")},
            CODES, VARIABLE_BYTES)
        self.assertFalse(accepted)
        self.assertTrue(skipped)
        with self.assertRaisesRegex(ValueError, "duplicate dynamic source"):
            stage([ROW, ROW], {FILE: SRC}, CODES, VARIABLE_BYTES)
        with self.assertRaisesRegex(ValueError, "unverified GBA runtime"):
            stage([ROW], {FILE: SRC}, CODES,
                  {**VARIABLE_BYTES, "STR_VAR_1": b"\xfd\x2F"})


if __name__ == "__main__":
    unittest.main()
