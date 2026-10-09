#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plan_collision_free_vietnamese_font import (
    parse_english_single_byte_occupancy, plan_mapping,RELOCATION,
)


class CollisionFreePlanTests(unittest.TestCase):
    charmap=(
        "' ' = 00\n'f' = DA\n'w' = EB\n'z' = EE\n"
        "LV = 34\nEXTRA = F7 00\n@ Hiragana\n'ぃ' = 30\n")
    book={"f":"0xDA","w":"0xEB","z":"0xEE",
          "ấ":"0xDA","ằ":"0xEB","ắ":"0xEE",
          "Ừ":"0x50","ừ":"0x50","M":"0xC7"}

    def test_planned_diacritics_have_unique_new_latin_slots(self):
        out,report=plan_mapping(self.book,self.charmap)
        self.assertEqual(out["ấ"],"0x30")
        self.assertEqual(out["ằ"],"0x31")
        self.assertEqual(out["ắ"],"0x32")
        self.assertEqual([out[ch] for ch in "fwz"],["0xDA","0xEB","0xEE"])
        self.assertTrue(report["codebook_is_byte_injective"])
        self.assertFalse(report["safe_to_distribute_game_ROM"])

    def test_uppercase_ambiguous_case_excluded(self):
        out,_=plan_mapping(self.book,self.charmap)
        self.assertNotIn("Ừ",out)
        self.assertEqual(out["ừ"],"0x50")

    def test_literal_equals_sign_assignment_is_always_reserved(self):
        marked=self.charmap.replace("LV = 34","LV = 34\n'=' = 35")
        used=parse_english_single_byte_occupancy(marked)
        self.assertIn(0x35,used)
        self.assertNotIn(0x33,used)

    def test_japanese_reuse_does_not_block_latin_slot(self):
        used=parse_english_single_byte_occupancy(self.charmap)
        self.assertEqual({0x30,0x31,0x32}&used,set())
        self.assertIn(0xF7,used)

    def test_reserved_slot_collision_fails(self):
        with self.assertRaisesRegex(ValueError,"occupied by pinned charmap"):
            plan_mapping(self.book,self.charmap.replace("LV = 34","LV = 30"))

    def test_codebook_collision_fails(self):
        with self.assertRaisesRegex(ValueError,"occupied by inferred codebook"):
            plan_mapping({**self.book,"custom":"0x31"},self.charmap)

    def test_source_mapping_drift_fails(self):
        with self.assertRaisesRegex(ValueError,"untrusted collision source"):
            plan_mapping({**self.book,"ấ":"0x41"},self.charmap)

    def test_glyph_plan_requires_not_game_release(self):
        _,r=plan_mapping(self.book,self.charmap)
        self.assertEqual(len(r["source_collision_relocations"]),3)
        self.assertFalse(r["font_built_or_emulator_tested"])


if __name__=="__main__":
    unittest.main()
