#!/usr/bin/env python3
"""Refuse Arena native-menu source drift and preserve fixed u8 arrays."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_arena_native_popup import patch_one_line,SPECS

class ArenaNativePopupTests(unittest.TestCase):
    def setUp(self):
        self.codes={ch:ord(ch)%240 for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz -:"}
        self.codes.update({"â":1,"ổ":2,"đ":3,"ể":4,"é":5,"ả":6,
                          "i":7,"L":8,"ê":9,"n":10,"P":11,"h":12})
    def test_narrow_move_direction_fits(self):
        src='\n'*329+'static const u8 sMoveDirections[4][7] = {_("UP"),_("RIGHT"),_("DOWN"),_("LEFT")};\n'
        updated,encoded=patch_one_line(src,330,"UP","Lên","sMoveDirections",0,7,self.codes)
        self.assertIn("{0x08",updated)
        self.assertLessEqual(len(encoded),7)
        self.assertIn('_("RIGHT")',updated)
    def test_array_capacity_fails_closed(self):
        src='\n'*329+'static const u8 sMoveDirections[4][7] = {_("UP"),_("RIGHT"),_("DOWN"),_("LEFT")};\n'
        with self.assertRaisesRegex(ValueError,"overflow"):
            patch_one_line(src,330,"UP","ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                           "sMoveDirections",0,7,self.codes)
    def test_wrong_source_line_refused(self):
        src='\n'*329+'static const u8 sMoveDirections[4][7] = {_("RIGHT"),_("DOWN")};\n'
        with self.assertRaisesRegex(ValueError,"drift"):
            patch_one_line(src,330,"UP","Lên","sMoveDirections",0,7,self.codes)
    def test_tiny_hud_is_not_in_native_stage(self):
        self.assertTrue(all(symbol not in {"sCaptureHint","sCaptureMiss","sQualityTabs","help"}
                            for _,_,_,_,symbol,_,_ in SPECS))
    def test_inventory_exactly_seventeen_source_owners(self):
        self.assertEqual(len(SPECS),17)
        self.assertEqual(len({(line,label) for line,label,*_ in SPECS}),17)
if __name__=="__main__":unittest.main()
