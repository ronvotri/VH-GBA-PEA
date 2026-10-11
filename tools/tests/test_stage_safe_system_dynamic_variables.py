#!/usr/bin/env python3
"""Only native-line-nonexpanding source-owned variables are admissible."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_safe_system_dynamic_variables import (
    VARIABLE_BYTES,lines_with_matching_dynamic_slots,encode,stage,
)

CODE={ch:i+1 for i,ch in enumerate(" abcdefghijklmnopqrstuvwxyz,.!?")}
PATH="data/text/trainers.inc"
EN=r"hello {PLAYER}!\ngood morning$"
VI=r"hi {PLAYER}!\ngood day$"
ROW={"category":"system-text","source_file":PATH,
     "source_label":"Welcome","english":EN,"vietnamese":VI}
SOURCE='Welcome::\n\t.string "hello {PLAYER}!\\ngood morning$"\nSecond::\n\t.string "hello$"\n'


class DynamicNonexpansionTests(unittest.TestCase):
    def test_native_slot_and_rom_control_bytes(self):
        lines=lines_with_matching_dynamic_slots(EN,VI)
        self.assertEqual(lines[0]["tokens"],["PLAYER"])
        self.assertLess(lines[0]["vietnamese_static_cells"],
                        lines[0]["english_static_cells"])
        blob=encode(VI,CODE,VARIABLE_BYTES)
        self.assertIn(b"\xfd\x01",blob)
        self.assertIn(b"\xfe",blob)
        self.assertEqual(blob[-1],0xff)
        updated,rows,skipped=stage([ROW],{PATH:SOURCE},CODE,VARIABLE_BYTES)
        self.assertEqual(len(rows),1,skipped)
        self.assertIn("Welcome::\n\t.byte ",updated[PATH])
        self.assertIn('Second::\n\t.string "hello$"',updated[PATH])

    def test_extra_text_page_move_and_unverified_tokens_rejected(self):
        invalid=[
            r"hello {PLAYER}!\ngood morning sunshine$",
            r"hello {PLAYER}!\pgood day$",
            r"hi!\ngood {PLAYER} day$",
            r"hi {STR_VAR_1}!\ngood day$",
            r"hi {PLAYER}{BATTLE_PARTNER}!\ngood day$",
            "hi {PLAYER}!\ngood day$",
            r"hi {PLAYER}!\ngood ầy$",
        ]
        for value in invalid:
            with self.subTest(value=value):
                changed,rows,skip=stage([{**ROW,"vietnamese":value}],
                                        {PATH:SOURCE},CODE,VARIABLE_BYTES)
                self.assertEqual(rows,[])
                self.assertTrue(skip)
                self.assertEqual(changed[PATH],SOURCE)

    def test_multi_variable_token_order_preserved(self):
        en=r"hello {STR_VAR_1} and {STR_VAR_2}\nsee you$"
        vi=r"hi {STR_VAR_1} va {STR_VAR_2}\nbye$"
        chunks=lines_with_matching_dynamic_slots(en,vi)
        self.assertEqual(chunks[0]["tokens"],["STR_VAR_1","STR_VAR_2"])
        blob=encode(vi,CODE,VARIABLE_BYTES)
        self.assertIn(b"\xfd\x02",blob)
        self.assertIn(b"\xfd\x03",blob)

    def test_source_drift_and_wrong_charmap_refused(self):
        _,rows,skipped=stage([ROW],{PATH:SOURCE.replace("hello", "WRONG")},
                             CODE,VARIABLE_BYTES)
        self.assertFalse(rows)
        self.assertTrue(any("English source is not exact" in k for k in skipped))
        with self.assertRaisesRegex(ValueError,"pinned charmap"):
            stage([ROW],{PATH:SOURCE},CODE,{**VARIABLE_BYTES,"PLAYER":b"\xfd\x02"})
        with self.assertRaisesRegex(ValueError,"duplicate"):
            stage([ROW,ROW],{PATH:SOURCE},CODE,VARIABLE_BYTES)


if __name__=="__main__":
    unittest.main()
