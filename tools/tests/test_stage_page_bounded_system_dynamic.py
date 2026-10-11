#!/usr/bin/env python3
"""Bounds on player's name and strict per-page variable/word preservation."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_page_bounded_system_dynamic import (
    compile_source_pair, page_words, render_width,stage,
)
from stage_safe_system_dynamic_variables import VARIABLE_BYTES
CODE={ch:i+1 for i,ch in enumerate(" abcdefghijklmnopqrstuvwxyz,.!?")}
FILE="data/text/trainers.inc"
EN=r"hey {PLAYER}!\ncome on\pbye {RIVAL}$"
VI=r"hello {PLAYER}! welcome here\ntoday\pgoodbye {RIVAL} tomorrow$"
SRC='Start::\n\t.string "hey {PLAYER}!\\ncome on\\pbye {RIVAL}$"\nOther::\n\t.string "a$"\n'
ROW={"category":"system-text","source_file":FILE,
     "source_label":"Start","english":EN,"vietnamese":VI}

class BoundedNameReflowTests(unittest.TestCase):
    def test_page_local_dynamic_wrap_longer_than_english(self):
        compiled,blob,descriptions=compile_source_pair(
            EN,VI,CODE,VARIABLE_BYTES,True,26)
        self.assertEqual(page_words(compiled),page_words(VI))
        self.assertEqual(compiled.count(r"\p"),1)
        self.assertEqual(len(descriptions),2)
        self.assertEqual(descriptions[0]["variables"],["PLAYER"])
        self.assertEqual(descriptions[1]["variables"],["RIVAL"])
        self.assertIn(b"\xfd\x01",blob)
        self.assertIn(b"\xfd\x06",blob)
        self.assertEqual(blob[-1],0xff)
        changed,rows,rejected=stage(
            [ROW],{FILE:SRC},CODE,VARIABLE_BYTES,True,width=26)
        self.assertEqual(len(rows),1,rejected)
        self.assertIn("Start::\n\t.byte ",changed[FILE])
        self.assertIn('Other::\n\t.string "a$"',changed[FILE])

    def test_kun_requires_independent_engine_check(self):
        en=r"hi {PLAYER}{KUN}$"
        vi=r"hello {PLAYER}{KUN} friend$"
        with self.assertRaisesRegex(ValueError,"KUN blank-suffix"):
            compile_source_pair(en,vi,CODE,VARIABLE_BYTES,False)
        value,blob,_=compile_source_pair(en,vi,CODE,VARIABLE_BYTES,True)
        self.assertIn(b"\xfd\x05",blob)
        self.assertEqual(page_words(value),page_words(vi))

    def test_str_var_unknown_and_page_moved_rejected(self):
        bad=[
            (EN,r"hello {STR_VAR_1}! welcome here\ntoday\pbye {RIVAL}$"),
            (EN,r"hello {RIVAL}! welcome here\ntoday\pbye {PLAYER}$"),
            (EN,r"hello {PLAYER}! welcome here\ptoday\pbye {RIVAL}$"),
            (r"hi {STR_VAR_1}$",r"hello {STR_VAR_1} friend$"),
            (EN,"hello {PLAYER}! welcome here\ntoday\\pbye {RIVAL}$"),
        ]
        for en,vi in bad:
            with self.subTest(en=en,vi=vi):
                with self.assertRaises(ValueError):
                    compile_source_pair(en,vi,CODE,VARIABLE_BYTES,True)

    def test_unbreakable_word_and_glyph_and_source_drift(self):
        with self.assertRaisesRegex(ValueError,"one quoted word"):
            compile_source_pair(r"hi {PLAYER}$",
                                "abcdefghijklmnopqrstuvwyz{PLAYER}$",
                                CODE,VARIABLE_BYTES,True)
        with self.assertRaisesRegex(ValueError,"missing/unsafe glyph"):
            compile_source_pair(r"hi {PLAYER}$","hi đ {PLAYER}$",
                                CODE,VARIABLE_BYTES,True)
        _,accepted,rejected=stage([ROW],{FILE:SRC.replace("hey","wrong")},
                                  CODE,VARIABLE_BYTES,True)
        self.assertFalse(accepted)
        self.assertTrue(rejected)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            stage([ROW,ROW],{FILE:SRC},CODE,VARIABLE_BYTES,True)
        self.assertEqual(render_width("{PLAYER}{KUN}?"),8)

if __name__=="__main__":
    unittest.main()
