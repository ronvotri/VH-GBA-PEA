#!/usr/bin/env python3
"""Lossless source-described GBA move/item C array stage regression tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_source_descriptions import (
    find_description_block,replace_description,stage_descriptions
)

MOVE_SRC = (
    'static const u8 sPoundDescription[] = _(\n'
    '    "Pounds the foe with\\n"\n'
    '    "forelegs or tail.");\n\n'
    'static const u8 sOtherDescription[] = _(\n'
    '    "Other move\\n"\n'
    '    "here.");\n'
)
ITEM_SRC = (
    'static const u8 sMasterBallDesc[] = _(\n'
    '    "The best BALL that\\n"\n'
    '    "catches a POKéMON\\n"\n'
    '    "without fail.");\n\n'
    'static const u8 sDummyDesc[] = _(\n'
    '    "?????");\n'
)
GLYPHS={"a":0xD5,"b":0xD6,"c":0xD7," ":0x00,
        ".":0xAD,"X":0xBE,"!":0xAB}

def row(file,label,english,vietnamese):
    return {"source_file":file,"category":"system-ui",
            "source_label":label,"english":english,
            "vietnamese":vietnamese}


class DescriptionSourceTests(unittest.TestCase):
    def test_extract_actual_move_style(self):
        start,end,head,english=find_description_block(
            MOVE_SRC,"sPoundDescription")
        self.assertEqual(english,r"Pounds the foe with\nforelegs or tail.")
        self.assertTrue(MOVE_SRC[start:end].endswith('tail.");\n'))
        self.assertIn("sPoundDescription",head)

    def test_extract_actual_three_line_item(self):
        _,_,_,english=find_description_block(ITEM_SRC,"sMasterBallDesc")
        self.assertEqual(english,r"The best BALL that\ncatches a POKéMON\nwithout fail.")

    def test_replace_move_preserves_other_source(self):
        replaced=replace_description(
            MOVE_SRC,"sPoundDescription",
            r"Pounds the foe with\nforelegs or tail.",
            b"\xD5\xFE\xD6\xFF","move")
        self.assertIn(
            "static const u8 sPoundDescription[] = {0xD5, 0xFE, 0xD6, 0xFF};",
            replaced)
        self.assertIn('"Other move\\n"',replaced)

    def test_replace_item_preserves_pointer_label(self):
        replaced=replace_description(
            ITEM_SRC,"sMasterBallDesc",
            r"The best BALL that\ncatches a POKéMON\nwithout fail.",
            b"\xD5\xFE\xD6\xFE\xD7\xFF","item")
        self.assertIn(
            "static const u8 sMasterBallDesc[] = {0xD5, 0xFE, 0xD6, 0xFE, 0xD7, 0xFF};",
            replaced)
        self.assertIn("sDummyDesc",replaced)

    def test_exact_source_drift_fails(self):
        with self.assertRaisesRegex(ValueError,"source drift"):
            replace_description(MOVE_SRC,"sPoundDescription","wrong",
                                b"\xD5\xFF","move")

    def test_missing_and_duplicate_label_refused(self):
        with self.assertRaisesRegex(ValueError,"missing or duplicate"):
            find_description_block(MOVE_SRC,"sUnknownDescription")
        with self.assertRaisesRegex(ValueError,"missing or duplicate"):
            find_description_block(MOVE_SRC+MOVE_SRC,"sPoundDescription")

    def test_move_fixed_two_lines_staged(self):
        rows=[row("src/data/text/move_descriptions.h","sPoundDescription",
                  r"Pounds the foe with\nforelegs or tail.",r"abc abc\nabc abc.")]
        src,installed,skipped=stage_descriptions(rows,MOVE_SRC,GLYPHS,"move")
        self.assertEqual(len(installed),1,skipped)
        self.assertEqual(installed[0]["visible_lines"],2)
        self.assertIn("0xFE",src)
        self.assertIn("0xFF",src)

    def test_item_fixed_three_lines_staged(self):
        rows=[row("src/data/text/item_descriptions.h","sMasterBallDesc",
                  r"The best BALL that\ncatches a POKéMON\nwithout fail.",
                  r"abc abc\nabc abc\nabc abc.")]
        src,installed,skipped=stage_descriptions(rows,ITEM_SRC,GLYPHS,"item")
        self.assertEqual(len(installed),1,skipped)
        self.assertEqual(installed[0]["visible_lines"],3)
        self.assertEqual(src.count("0xFE"),2)

    def test_page_overflow_rejected(self):
        rows=[row("src/data/text/move_descriptions.h","sPoundDescription",
                  r"Pounds the foe with\nforelegs or tail.",
                  r"abc abc\nabc abc\nabc.")]
        _,accepted,reject=stage_descriptions(rows,MOVE_SRC,GLYPHS,"move")
        self.assertFalse(accepted)
        self.assertIn("description line count differs from English",reject)

    def test_unknown_glyph_rejected(self):
        rows=[row("src/data/text/move_descriptions.h","sPoundDescription",
                  r"Pounds the foe with\nforelegs or tail.",
                  r"Z Z\nabc.")]
        _,accepted,reject=stage_descriptions(rows,MOVE_SRC,GLYPHS,"move")
        self.assertFalse(accepted)
        self.assertTrue(any("missing Vietnamese glyph" in k for k in reject))

    def test_dynamic_placeholder_is_not_deleted(self):
        rows=[row("src/data/text/item_descriptions.h","sMasterBallDesc",
                  r"The best BALL that\ncatches a POKéMON\nwithout fail.",
                  r"{STR_VAR_1}\nabc\nabc")]
        _,accepted,reject=stage_descriptions(rows,ITEM_SRC,GLYPHS,"item")
        self.assertFalse(accepted)
        self.assertIn("dynamic/control variable left for separate engine",reject)

    def test_overlong_line_never_force_wrapped(self):
        rows=[row("src/data/text/move_descriptions.h","sPoundDescription",
                  r"Pounds the foe with\nforelegs or tail.",
                  "a"*27+r"\nabc")]
        _,accepted,reject=stage_descriptions(rows,MOVE_SRC,GLYPHS,"move")
        self.assertFalse(accepted)
        self.assertTrue(any("line exceeds" in x for x in reject))


if __name__=="__main__":
    unittest.main()
