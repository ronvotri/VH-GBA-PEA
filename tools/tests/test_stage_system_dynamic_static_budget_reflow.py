#!/usr/bin/env python3
"""No unbounded VAR width is guessed; source native page words stay identical."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stage_system_dynamic_static_budget_reflow import (
    LAYOUT, TOKEN, compile_dynamic, segment_reflow, stage,
)
from stage_safe_system_dynamic_variables import VARIABLE_BYTES

CODES = {ch: i + 1 for i, ch in enumerate(" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,.!?")}
FILE = "data/text/trainers.inc"
EN = r"Hello {STR_VAR_1}!\nHow are you?\pCome {PLAYER}!$"
VI = r"Chao ban than men {STR_VAR_1}! Chuc vui ve\nHom nay the nao?\pXin moi {PLAYER} vao day nha!$"
SRC = (
    'Call::\n\t.string "Hello {STR_VAR_1}!\\nHow are you?\\pCome {PLAYER}!$"\n'
    'Other::\n\t.string "a$"\n'
)
ROW = {"category": "system-text", "source_file": FILE, "source_label": "Call",
       "english": EN, "vietnamese": VI}


class SourceStaticBudgetReflowTests(unittest.TestCase):
    def test_reflow_long_translation_without_assuming_str_var_length(self):
        compiled, data, pages = compile_dynamic(EN, VI, CODES, VARIABLE_BYTES)
        self.assertEqual(compiled.count(r"\p"), 1)
        self.assertEqual(TOKEN.findall(compiled), TOKEN.findall(EN))
        self.assertIn(b"\xfd\x02", data)
        self.assertIn(b"\xfd\x01", data)
        self.assertEqual(data[-1], 0xFF)
        for en_page, vi_page, compiled_page, proof in zip(
            EN[:-1].split(r"\p"), VI[:-1].split(r"\p"),
            compiled[:-1].split(r"\p"), pages
        ):
            self.assertEqual(LAYOUT.sub(" ", vi_page).split(),
                             LAYOUT.sub(" ", compiled_page).split())
            for segment in proof["per_segment_static_budgets"]:
                if segment["tokens"]:
                    self.assertLessEqual(
                        segment["dynamic_static_cells"],
                        segment["source_static_budget"])
        self.assertGreater(pages[0]["result_scroll_lines"], 2)

    def test_source_replacement_preserves_unrelated_symbols(self):
        sources, accepted, skipped = stage(
            [ROW], {FILE: SRC}, CODES, VARIABLE_BYTES)
        self.assertEqual(len(accepted), 1, skipped)
        self.assertEqual(accepted[0]["page_count"], 2)
        self.assertIn("Call::\n\t.byte ", sources[FILE])
        self.assertIn('Other::\n\t.string "a$"', sources[FILE])

    def test_reject_unbounded_core_and_unbreakable_words(self):
        with self.assertRaisesRegex(ValueError, "dynamic core cannot fit"):
            compile_dynamic(r"a {STR_VAR_1}$",
                            r"helloworld{STR_VAR_1}foo$",
                            CODES, VARIABLE_BYTES)
        with self.assertRaisesRegex(ValueError, "unbreakable static word"):
            compile_dynamic(r"Come {PLAYER}$",
                            r"abcdefghijklmnopqrstuvwxyzabc {PLAYER}$",
                            CODES, VARIABLE_BYTES)

    def test_reject_variable_move_control_diff_page_diff_and_unknowns(self):
        invalid = [
            (EN, VI.replace("{STR_VAR_1}", "{STR_VAR_2}")),
            (EN, VI.replace(r"\n", r"\l")),
            (EN, VI.replace(r"\p", r"\l")),
            (EN, VI.replace("{PLAYER}", "{PLAYER}{RIVAL}")),
            (EN, VI.replace("{PLAYER}", "{PAUSE 16}")),
            (EN, VI.replace("Chao", "Chào")),
            (EN, VI.replace("Chao", "Chao  ")),
            (r"Hello {STR_VAR_1}!\nHow are you?$",
             r"Hello!\nHow are {STR_VAR_1}?$"),
        ]
        for en, vi in invalid:
            with self.subTest(en=en, vi=vi):
                with self.assertRaises(ValueError):
                    compile_dynamic(en, vi, CODES, VARIABLE_BYTES)

    def test_source_drift_and_duplicate_owners_rejected(self):
        _, accepted, rejected = stage(
            [ROW], {FILE: SRC.replace("Hello", "WRONG")}, CODES, VARIABLE_BYTES)
        self.assertEqual(accepted, [])
        self.assertTrue(rejected)
        with self.assertRaisesRegex(ValueError, "duplicate source"):
            stage([ROW, ROW], {FILE: SRC}, CODES, VARIABLE_BYTES)
        with self.assertRaisesRegex(ValueError, "charmap"):
            stage([ROW], {FILE: SRC}, CODES,
                  {**VARIABLE_BYTES, "STR_VAR_1": b"\xfd\x09"})


if __name__ == "__main__":
    unittest.main()
