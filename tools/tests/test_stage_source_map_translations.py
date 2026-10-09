#!/usr/bin/env python3
"""Fail-closed smoke tests for source-level Vietnamese map text insertion."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_source_map_translations import encode_text, patch_labeled_block, plan_rows, prioritized_rows


class SourceStagingTests(unittest.TestCase):
    codes={"M":0xC7,"ẹ":0x21,":":0xF0," ":0x00,"n":0xE2,
           "h":0xDC,"à":0x16,"!":0xAB,"a":0xD5,"b":0xD6,
           "c":0xD7,"q":0xE5,"u":0xE9,"á":0x17}

    def test_accents_controls(self):
        self.assertEqual(encode_text("Mẹ: nhà!\\p$",self.codes,26),
                         bytes([0xC7,0x21,0xF0,0,0xE2,0xDC,0x16,0xAB,0xFB,0xFF]))

    def test_exact_labeled_assembly_replacement(self):
        source=('Other:\n\t.string "hello$"\n\n'
                'Name:\n\t.string "one\\n"\n\t.string "two$"\n\n'
                'After:\n\t.string "done$"\n')
        updated=patch_labeled_block(source,"Name","one\\ntwo$",b"\xC7\xFF")
        self.assertIn("Name:\n\t.byte 0xC7, 0xFF\n",updated)
        self.assertIn('\t.string "hello$"',updated)
        self.assertIn('\t.string "done$"',updated)
        self.assertNotIn('\t.string "one\\n"',updated)

    def test_fail_closed_source_drift(self):
        with self.assertRaisesRegex(ValueError,"not exact pinned match"):
            patch_labeled_block('Name:\n\t.string "wrong$"\n',
                                "Name","right$",b"\xFF")

    def test_fail_closed_no_label(self):
        with self.assertRaisesRegex(ValueError,"0 source labels"):
            patch_labeled_block('Wrong:\n\t.string "text$"\n',
                                "Name","text$",b"\xFF")

    def test_dynamic_tokens_not_supported(self):
        with self.assertRaisesRegex(ValueError,"unsupported dynamic"):
            encode_text("Mẹ: {PLAYER}$",self.codes,26)

    def test_unknown_glyph_rejected(self):
        with self.assertRaisesRegex(ValueError,"missing Vietnamese glyph"):
            encode_text("Mẹ Æ$",self.codes,26)

    def test_early_terminator_rejected(self):
        with self.assertRaisesRegex(ValueError,"early terminator"):
            encode_text("a$b$",self.codes,26)

    def test_control_byte_collision_rejected(self):
        with self.assertRaisesRegex(ValueError,"collides with control byte"):
            encode_text("a$",{"a":0xFD},26)

    def test_line_length_rejected(self):
        with self.assertRaisesRegex(ValueError,"exceeds"):
            encode_text("a"*27+"$",self.codes,26)

    def test_non_nfc_rejected(self):
        with self.assertRaisesRegex(ValueError,"non-NFC"):
            encode_text("a\u0301$",self.codes,26)

    def test_stable_priority_is_early_game_first(self):
        labels=[
            {"source_file":"data/maps/AbandonedShip/scripts.inc","source_label":"A"},
            {"source_file":"data/maps/LittlerootTown/scripts.inc","source_label":"FIRST"},
            {"source_file":"data/maps/OldaleTown/scripts.inc","source_label":"NEXT"},
            {"source_file":"data/maps/LittlerootTown/scripts.inc","source_label":"SECOND"},
        ]
        ordered=prioritized_rows(labels,[
            "data/maps/LittlerootTown/","data/maps/OldaleTown/"])
        self.assertEqual([x["source_label"] for x in ordered],
                         ["FIRST","SECOND","NEXT","A"])

    def test_prioritized_staging_honors_limit(self):
        rows=[
            {"category":"map-story","source_file":"data/maps/AbandonedShip/scripts.inc",
             "source_label":"OLD","english":"a$","vietnamese":"b$"},
            {"category":"map-story","source_file":"data/maps/LittlerootTown/scripts.inc",
             "source_label":"INTRO","english":"a$","vietnamese":"b$"},
        ]
        chosen,_=plan_rows(rows,self.codes,"data/maps/",26,1,False,
                           ["data/maps/LittlerootTown/"])
        self.assertEqual([r["source_label"] for r,_ in chosen],["INTRO"])

    def test_limited_map_selection(self):
        rows=[{"category":"map-story",
               "source_file":"data/maps/LittlerootTown/scripts.inc",
               "source_label":"X","english":"a$","vietnamese":"b$"},
              {"category":"battle",
               "source_file":"data/maps/LittlerootTown/scripts.inc",
               "source_label":"Y","english":"a$","vietnamese":"b$"}]
        chosen,_=plan_rows(rows,self.codes,"data/maps/LittlerootTown/",26,20)
        self.assertEqual(len(chosen),1)


if __name__=="__main__":unittest.main()
