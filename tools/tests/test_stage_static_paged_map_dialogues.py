#!/usr/bin/env python3
"""Multi-page Vietnamese dialogue integration must preserve each authored page."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_static_paged_map_dialogues import compile_paged,page_words,stage

GLYPHS={ch:i+1 for i,ch in enumerate(" abcdefghijklmnopqrstuvwxyz,.!?")}
FILE="data/maps/Route101/scripts.inc"


class StaticPagedMapTests(unittest.TestCase):
    def test_reflow_inside_two_pages_keeps_original_word_pages(self):
        english=r"abc\nabc\pabc\nabc$"
        authored=(r"abc def ghi jkl mno pqr stu vwx yza bcd efg hij"
                  r"\pabc def ghi jkl mno pqr stu vwx yza bcd efg hij$")
        compiled,payload=compile_paged(english,authored,GLYPHS,11)
        self.assertEqual(page_words(english,compiled),page_words(english,authored))
        self.assertEqual(compiled.count(r"\p"),1)
        self.assertIn(r"\n",compiled)
        self.assertIn(r"\l",compiled)
        self.assertNotIn(r"\p\p",compiled)
        self.assertEqual(payload[-1],0xFF)
        self.assertEqual(payload.count(b"\xfb"),1)

    def test_refuses_missing_or_extra_page(self):
        with self.assertRaisesRegex(ValueError,"page-count drift"):
            compile_paged(r"abc\pabc$",r"abc def$",GLYPHS)
        with self.assertRaisesRegex(ValueError,"page-count drift"):
            compile_paged(r"abc\pabc$",r"abc\pdef\pghi$",GLYPHS)

    def test_refuses_non_paginated_english_source(self):
        with self.assertRaisesRegex(ValueError,"not a paginated"):
            compile_paged(r"abc\nabc$",r"abc\pdef$",GLYPHS)

    def test_refuses_variable_unknown_control_and_empty_pages(self):
        for value in (r"abc\p{PLAYER}$",r"abc\p{STR_VAR_1}$",
                      r"abc\pdef\vghi$",r"abc\p$",r"\pabc$",
                      r"abc\p def$",r"abc\pdef  ghi$"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    compile_paged(r"abc\pabc$",value,GLYPHS)

    def test_cannot_move_word_across_authored_page(self):
        english=r"abc\pabc$"
        first=r"abc def\pghi jkl$"
        second=r"abc\pdef ghi jkl$"
        a,_=compile_paged(english,first,GLYPHS,26)
        b,_=compile_paged(english,second,GLYPHS,26)
        self.assertNotEqual(page_words(english,a),page_words(english,b))

    def test_stages_only_exact_pinned_source_with_original_symbol(self):
        row={"category":"map-story","source_file":FILE,"source_label":"Text",
             "english":r"abc\pabc$","vietnamese":r"abc def\pghi jkl$"}
        source='Text::\n\t.string "abc\\pabc$"\nOther::\n\t.string "abc$"\n'
        result,accepted,rejected=stage([row],{FILE:source},GLYPHS,25,26)
        self.assertEqual(len(accepted),1,rejected)
        self.assertIn("Text::\n\t.byte ",result[FILE])
        self.assertIn('Other::\n\t.string "abc$"',result[FILE])
        self.assertEqual(accepted[0]["page_word_counts"],[2,2])
        self.assertTrue(accepted[0]["authored_page_word_order_preserved"])
        result,accepted,rejected=stage(
            [row],{FILE:source.replace("abc\\pabc$","ENGLISH-DRIFT$")},
            GLYPHS,25,26)
        self.assertEqual(len(accepted),0)
        self.assertTrue(any("English source is not exact" in key for key in rejected))

    def test_reject_missing_encoded_glyph(self):
        with self.assertRaisesRegex(ValueError,"missing Vietnamese glyph"):
            compile_paged(r"abc\pabc$",r"abc\pđẹp$",GLYPHS)


if __name__=="__main__":
    unittest.main()
