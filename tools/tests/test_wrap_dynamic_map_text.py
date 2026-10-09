#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from wrap_dynamic_map_text import display_cells,wrap_dynamic_text
from stage_dynamic_map_translations import encode_dynamic,stage

GLYPHS={"M":0xC7,"ẹ":0x5A,":":0xF0," ":0x00,",":0xB8,
        "c":0xD7,"o":0xE3,"n":0xE2,"y":0xED,"ê":0x1C,
        "t":0xE8,"ớ":0x0E,"i":0xDD,"r":0xE6,"ồ":0x04,"à":0x16,
        "đ":0x56,"ã":0x21,"!":0xAB,"ở":0x0F,"v":0xEA,
        "d":0xD8,"ò":0x22,"m":0xE1,"h":0xDC,"ạ":0x1E,"k":0xDF,"ơ":0xF5,"u":0xE9}
TOKENS={"PLAYER":b"\xFD\x01","RIVAL":b"\xFD\x06"}


class DynamicWrapTests(unittest.TestCase):
    def test_dynamic_name_counts_seven(self):
        self.assertEqual(display_cells("{PLAYER},"),8)

    def test_reflow_name_first_dialogue(self):
        original=r"Mẹ: {PLAYER}, tới nơi rồi con yêu!\pCon vào nhà nhé!$"
        changed=wrap_dynamic_text(original)
        self.assertIn(r"con yêu!\p",changed)
        self.assertIn(r"\n",changed)
        self.assertEqual(changed.count(r"\p"),original.count(r"\p"))

    def test_keeps_exact_name_sequence(self):
        original=r"{PLAYER} thắng rồi, còn {RIVAL} thì sao?$"
        changed=wrap_dynamic_text(original)
        self.assertEqual(changed.count("{PLAYER}"),1)
        self.assertEqual(changed.count("{RIVAL}"),1)
        self.assertTrue(changed.endswith("$"))

    def test_explicit_third_line_becomes_scroll(self):
        original=r"Mẹ: {PLAYER}, tới nơi rồi con yêu!\nCon vào nhà nhé!$"
        changed=wrap_dynamic_text(original)
        self.assertIn(r"\l",changed)

    def test_blocks_unapproved_variable(self):
        with self.assertRaisesRegex(ValueError,"unknown variable"):
            wrap_dynamic_text("{STR_VAR_1} con yêu!$")

    def test_blocks_oversize_atomic_word(self):
        with self.assertRaisesRegex(ValueError,"wider than line"):
            wrap_dynamic_text("a"*27+"$")

    def test_blocks_double_space(self):
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            wrap_dynamic_text(r"Mẹ:  {PLAYER}!$")

    def test_stage_opt_in_wrapping(self):
        source='X:\n\t.string "MOM: {PLAYER}!$"\n'
        row={"category":"map-story","source_file":"data/maps/A/scripts.inc",
             "source_label":"X","english":"MOM: {PLAYER}!$",
             "vietnamese":"Mẹ: {PLAYER}, tới nơi rồi con yêu!$"}
        rejected,rejected_rows,_=stage([row],{"data/maps/A/scripts.inc":source},
                                        GLYPHS,TOKENS,"data/maps/",30,26,False)
        self.assertFalse(rejected_rows)
        fixed,rows,issues=stage([row],{"data/maps/A/scripts.inc":source},
                                GLYPHS,TOKENS,"data/maps/",30,26,True)
        self.assertEqual(len(rows),1,issues)
        self.assertTrue(rows[0]["auto_wrapped"])
        self.assertIn(r"\n",rows[0]["compiled_vietnamese"])
        self.assertIn(".byte",fixed["data/maps/A/scripts.inc"])


if __name__=="__main__":
    unittest.main()
