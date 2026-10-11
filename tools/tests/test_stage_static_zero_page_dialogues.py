#!/usr/bin/env python3
"""Zero-page static dialogues may reflow ONLY layout, never pagination or tokens."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage_static_zero_page_dialogues import (
    compile_zero_page, exclude_exact_source_owners, stage,
)

CODES={ch:i+1 for i,ch in enumerate(
    "abc defghijklmnopqrstuvwxyz,.!?A")}
FILE="data/maps/Route101/scripts.inc"


class StaticZeroPageTests(unittest.TestCase):
    def test_static_reflow_preserves_every_word_and_uses_native_scroll(self):
        en=r"abc\nabc$"
        vi=r"abc def ghi jkl mno pqr stu vwx yza bcd efg hij$"
        reformatted,payload=compile_zero_page(en,vi,CODES,11)
        self.assertEqual(reformatted.replace(r"\n"," ").replace(r"\l"," ").split(),
                         vi[:-1].split())
        self.assertIn(r"\n",reformatted)
        self.assertIn(r"\l",reformatted)
        self.assertNotIn(r"\p",reformatted)
        self.assertEqual(payload[-1],0xFF)

    def test_reject_any_pagination_or_variables_even_if_both_source_and_vi_match(self):
        for vi in (r"abc\pdef$", r"abc {PLAYER} def$", r"abc {STR_VAR_1} def$"):
            with self.subTest(vi=vi):
                with self.assertRaises(ValueError):
                    compile_zero_page("abc$",vi,CODES)
        with self.assertRaisesRegex(ValueError,"page-control"):
            compile_zero_page(r"abc\pdef$",r"abc def$",CODES)

    def test_reject_unknown_escapes_and_ambiguous_layout(self):
        for vi in (r"abc\vdef$", "abc  def$", r"abc\n def$",
                   "abc\n\nabc$", "abc\n def$", "abc\tdef$"):
            with self.subTest(vi=vi):
                with self.assertRaises(ValueError):
                    compile_zero_page("abc$",vi,CODES)

    def test_source_patch_preserves_original_label_identity(self):
        row={"category":"map-story","source_file":FILE,"source_label":"Msg",
             "english":r"abc\nabc$","vietnamese":r"abc def ghi jkl$"}
        en='Msg::\n\t.string "abc\\nabc$"\nOther::\n\t.string "abc$"\n'
        updated,accepted,skipped=stage([row],{FILE:en},CODES,5,11)
        self.assertEqual(len(accepted),1,skipped)
        self.assertIn("Msg::",updated[FILE])
        self.assertIn("\t.byte ",updated[FILE])
        self.assertIn('Other::\n\t.string "abc$"',updated[FILE])
        self.assertTrue(accepted[0]["source_line_layout_changed"])
        self.assertEqual(accepted[0]["source_page_breaks"],0)

    def test_skip_missing_or_mismatched_english_source(self):
        row={"category":"map-story","source_file":FILE,"source_label":"Msg",
             "english":r"abc\nabc$","vietnamese":r"abc def$"}
        updated,accepted,skipped=stage([row],{FILE:'Msg::\n\t.string "WRONG$"\n'},CODES)
        self.assertFalse(accepted)
        self.assertTrue(any("English source is not exact" in reason for reason in skipped))

    def test_exclusion_reports_need_unique_source_owners(self):
        rows=[{"category":"map-story","source_file":FILE,"source_label":"Msg"},
              {"category":"map-story","source_file":FILE,"source_label":"Other"}]
        rep={"mode":"apply","labels_staged":1,
             "translated":[{"source_file":FILE,"label":"Msg"}]}
        rest,count=exclude_exact_source_owners(rows,[rep])
        self.assertEqual(count,1)
        self.assertEqual(rest,[rows[1]])
        with self.assertRaisesRegex(ValueError,"duplicate"):
            exclude_exact_source_owners(rows,[rep,rep])
        with self.assertRaisesRegex(ValueError,"missing from authoritative"):
            exclude_exact_source_owners(rows,[{"mode":"apply","labels_staged":1,
                 "translated":[{"source_file":FILE,"label":"NONEXISTENT"}]}])


if __name__=="__main__":
    unittest.main()
