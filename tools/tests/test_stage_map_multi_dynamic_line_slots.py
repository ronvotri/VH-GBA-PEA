#!/usr/bin/env python3
"""Native source-line identity for multi-variable NPC pages is immutable."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage_map_multi_dynamic_line_slots import (
    compile_aligned_multi_dynamic, stage, TOKEN, LAYOUT
)
from stage_safe_system_dynamic_variables import VARIABLE_BYTES

CODES = {ch: i + 1 for i, ch in enumerate(
    " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,.!?")}
FILE = "data/maps/LittlerootTown_Test/scripts.inc"
EN = r"Hello {STR_VAR_1}!\nHi {PLAYER}!\pBye friend$"
VI = r"Hello long {STR_VAR_1}! now later\lWelcome {PLAYER}! today\pBye buddy$"
SRC = (
    'Dialogue::\n'
    '\t.string "Hello {STR_VAR_1}!\\nHi {PLAYER}!\\pBye friend$"\n'
    'Untouched::\n\t.string "a$"\n'
)
ROW = {
    "category": "map-story", "source_file": FILE,
    "source_label": "Dialogue", "english": EN, "vietnamese": VI,
}


class MultipleNativeVariableLineTests(unittest.TestCase):
    def test_dynamic_slots_compile_with_changed_control_style(self):
        output, data, pages = compile_aligned_multi_dynamic(
            EN, VI, CODES, VARIABLE_BYTES)
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[0]["variable_line_slots"], 2)
        self.assertEqual(output.count(r"\p"), EN.count(r"\p"))
        self.assertIn(b"\xfd\x02", data)
        self.assertIn(b"\xfd\x01", data)
        self.assertEqual(data[-1], 0xff)
        for original, compiled in zip(
            VI[:-1].split(r"\p"), output[:-1].split(r"\p")
        ):
            self.assertEqual(
                LAYOUT.sub(" ", original).split(),
                LAYOUT.sub(" ", compiled).split())
        self.assertEqual(TOKEN.findall(output), TOKEN.findall(EN))
        for slot in pages[0]["per_source_slot"]:
            if slot["source_variables"]:
                self.assertLessEqual(
                    slot["compiled_dynamic_static_cells"],
                    slot["source_static_budget"])
        result, accepted, skipped = stage(
            [ROW], {FILE: SRC}, CODES, VARIABLE_BYTES)
        self.assertEqual(len(accepted), 1, skipped)
        self.assertIn("Dialogue::\n\t.byte ", result[FILE])
        self.assertIn('Untouched::\n\t.string "a$"', result[FILE])

    def test_moved_source_slot_and_page_rejected(self):
        examples = [
            VI.replace("{STR_VAR_1}", "{STR_VAR_2}"),
            VI.replace("{PLAYER}", "{RIVAL}"),
            VI.replace(r"\lWelcome", r"\l"),
            VI.replace(r"\lWelcome", r"\pWelcome"),
            VI.replace(r"\lWelcome", " Welcome"),
            VI.replace("Hello", "Héllo"),
            VI.replace("Hello", "Hello  "),
            VI.replace("Hello", "Hello\n"),
        ]
        for translated in examples:
            with self.subTest(translated=translated):
                with self.assertRaises(ValueError):
                    compile_aligned_multi_dynamic(
                        EN, translated, CODES, VARIABLE_BYTES)

    def test_refuse_single_variable_line_or_unmatched_slots(self):
        with self.assertRaisesRegex(ValueError, "not a multi-variable"):
            compile_aligned_multi_dynamic(
                r"Hi {PLAYER}!\nWelcome friend$",
                r"Yo {PLAYER}!\lHello friend$",
                CODES, VARIABLE_BYTES)
        with self.assertRaisesRegex(ValueError, "line-slot count"):
            compile_aligned_multi_dynamic(
                EN, r"Hello {STR_VAR_1}! hi {PLAYER}!\pBye buddy$",
                CODES, VARIABLE_BYTES)

    def test_exact_english_source_ownership_and_duplicate_owners(self):
        _, accepted, rejected = stage(
            [ROW], {FILE: SRC.replace("Hello", "WRONG")},
            CODES, VARIABLE_BYTES)
        self.assertEqual(accepted, [])
        self.assertTrue(rejected)
        with self.assertRaisesRegex(ValueError, "duplicate source owner"):
            stage([ROW, ROW], {FILE: SRC}, CODES, VARIABLE_BYTES)
        with self.assertRaisesRegex(ValueError, "unverified engine"):
            stage([ROW], {FILE: SRC}, CODES,
                  {**VARIABLE_BYTES, "PLAYER": b"\xfd\xA7"})


if __name__ == "__main__":
    unittest.main()
