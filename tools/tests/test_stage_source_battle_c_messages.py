#!/usr/bin/env python3
"""Tests for conservative variable-free battle C source replacement."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_source_battle_c_messages import (
    replace_battle_c_literal,stage_battle_messages
)

CODEBOOK={"K":0xC6,"h":0xDC,"ô":0xD1,"n":0xE2,"g":0xDA,
          " ":0x00,"t":0xE8,"ể":0x37,"c":0xD7,"ạ":0x38,"y":0xED,
          "!":0xAB,"T":0xCC,"r":0xE6,"ờ":0x39,"m":0xE1,
          "ư":0xE7,"đ":0x56,"ã":0x21,"b":0xD6,"ắ":0x32,
          "ắ":0x32,"x":0xEC,"u":0xE9}
EN=r"Can't escape!\p"
VI=r"Không thể chạy!\p"
SRC=(
    'static const u8 sText_CantEscape[] = _("Can\\x27t escape!\\p");\n'
    'static const u8 sText_Other[] = _("Other string.");\n'
).replace("Can\\x27t","Can't")


class BattleCSourceTests(unittest.TestCase):
    def test_exact_source_replace_and_keep_other(self):
        updated=replace_battle_c_literal(SRC,"sText_CantEscape",EN,b"\xD0\xFB\xFF")
        self.assertIn("sText_CantEscape[] = {0xD0, 0xFB, 0xFF};",updated)
        self.assertIn('sText_Other[] = _("Other string.");',updated)

    def test_mismatched_english_rejected(self):
        with self.assertRaisesRegex(ValueError,"English source drift"):
            replace_battle_c_literal(SRC,"sText_CantEscape","Not original",
                                     b"\xD0\xFF")

    def test_duplicate_symbol_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            replace_battle_c_literal(SRC+SRC,"sText_CantEscape",EN,b"\xD0\xFF")

    def test_invalid_early_terminator_rejected(self):
        with self.assertRaisesRegex(ValueError,"terminator"):
            replace_battle_c_literal(SRC,"sText_CantEscape",EN,b"\xFF\xD0\xFF")

    def test_safely_stages_static_battle_message(self):
        row={"category":"battle","source_file":"src/battle_message.c",
             "source_label":"sText_CantEscape","english":EN,"vietnamese":VI}
        source,installed,skipped=stage_battle_messages([row],SRC,CODEBOOK,80,26,True)
        self.assertEqual(len(installed),1,skipped)
        self.assertEqual(installed[0]["label"],"sText_CantEscape")
        self.assertIn("0xFF",source)
        self.assertNotIn('sText_CantEscape[] = _("',source)

    def test_rejects_dynamic_battle_variable(self):
        row={"category":"battle","source_file":"src/battle_message.c",
             "source_label":"sText_CantEscape","english":r"{B_BUFF1} escaped!",
             "vietnamese":r"{B_BUFF1} thoát!"}
        _,installed,rejected=stage_battle_messages([row],SRC,CODEBOOK)
        self.assertEqual(installed,[])
        self.assertIn("dynamic/engine control token",rejected)

    def test_page_control_is_not_removed(self):
        row={"category":"battle","source_file":"src/battle_message.c",
             "source_label":"sText_CantEscape","english":EN,
             "vietnamese":"Không thể chạy!"}
        _,installed,rejected=stage_battle_messages([row],SRC,CODEBOOK)
        self.assertFalse(installed)
        self.assertIn("battle page-control count changed",rejected)

    def test_short_fragments_not_staged(self):
        row={"category":"battle","source_file":"src/battle_message.c",
             "source_label":"sText_StatSharply","english":" sharply ",
             "vietnamese":" đột ngột "}
        _,installed,skipped=stage_battle_messages([row],SRC,CODEBOOK)
        self.assertFalse(installed)
        self.assertIn("short or concatenated battle fragment",skipped)


if __name__=="__main__":
    unittest.main()
