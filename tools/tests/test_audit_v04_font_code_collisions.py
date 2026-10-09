#!/usr/bin/env python3
"""Binary glyph collision audit must catch mixed English/Vietnamese damage."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import audit_v04_font_code_collisions as report


class FontCollisionTests(unittest.TestCase):
    def setUp(self):
        self.clean=bytearray(0x800)
        self.donor=bytearray(self.clean)
        self.offsets={name:i*0x100 for i,name in enumerate(report.FONT_NAMES)}
        self.charmap="'f' = DA\n'w' = EB\n'z' = EE\n@ Hiragana\n'f' = 00\n"
        self.book={"f":0xDA,"ấ":0xDA,"w":0xEB,"ằ":0xEB,"z":0xEE,
                   "ắ":0xEE,"Ừ":0x50,"ừ":0x50}

    def test_detects_damaged_english_f(self):
        self.donor[self.offsets["gFontNormalLatinGlyphs"]+0xDA*64]=3
        with patch.object(report,"ROM_BYTES",len(self.clean)):
            r=report.collision_report(bytes(self.clean),bytes(self.donor),
                                      self.book,self.charmap,self.offsets)
        self.assertTrue(r["has_english_rendering_hazard"])
        ascii_codes={item["original_english_ascii"][0] for item in r["stock_ascii_collisions"]}
        self.assertEqual(ascii_codes,{"f","w","z"})
        self.assertTrue(r["read_only"])
        self.assertFalse(r["auto_patch_authorized"])

    def test_ambiguous_upper_and_lowercase(self):
        with patch.object(report,"ROM_BYTES",len(self.clean)):
            r=report.collision_report(bytes(self.clean),bytes(self.donor),
                                      self.book,self.charmap,self.offsets)
        self.assertIn({"slot":"0x50","labels":["Ừ","ừ"]},
                      r["ambiguous_vietnamese_duplicate_slots"])

    def test_unchanged_donor_not_a_proven_visual_bug(self):
        with patch.object(report,"ROM_BYTES",len(self.clean)):
            r=report.collision_report(bytes(self.clean),bytes(self.donor),
                                      self.book,self.charmap,self.offsets)
        self.assertFalse(r["has_english_rendering_hazard"])

    def test_english_language_scope_excludes_japanese_reuse(self):
        d=report.original_ascii_letters(self.charmap)
        self.assertEqual(d["f"],0xDA)
        self.assertNotEqual(d["f"],0)

    def test_reject_invalid_slot(self):
        with self.assertRaisesRegex(ValueError,"control range"):
            report.font_slot_changes(bytes(self.clean),bytes(self.donor),0xFE,self.offsets)


if __name__=="__main__":
    unittest.main()
