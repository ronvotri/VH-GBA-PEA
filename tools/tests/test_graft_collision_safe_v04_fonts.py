#!/usr/bin/env python3
"""Private font transplant tests: never destroy English f/w/z or other ROM."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import import_v04_glyphs_into_source_build as importer
import graft_collision_safe_v04_fonts as graft
from plan_collision_free_vietnamese_font import RELOCATION


class AccentRelocationTests(unittest.TestCase):
    def setUp(self):
        self.glyph_size=0x4000
        self.positions={name:0x1000+i*0x4500 for i,name in enumerate(graft.FONT_NAMES)}
        self.clean=bytearray(b"\x00"*0x20000)
        self.donor=bytearray(self.clean)
        self.codebook={
            "f":"0xDA","w":"0xEB","z":"0xEE",
            "ấ":"0x30","ằ":"0x31","ắ":"0x32"
        }
        for name,offset in self.positions.items():
            for ch,old,slot in RELOCATION.values():
                self.clean[offset+old*64]=0x11
                self.clean[offset+self.glyph_size+old]=5
                self.clean[offset+self.glyph_size+slot]=3
                if name not in graft.UNVERIFIED_SMALL_FONTS:
                    self.donor[offset+old*64]=0x99
        # Since donor initially copied before source edits, sync all untouched
        # font bytes to the final clean source; retain modified accents.
        for name,offset in self.positions.items():
            for i in range(self.glyph_size+0x100):
                if (name not in graft.UNVERIFIED_SMALL_FONTS and
                    any(i==old*64 for _,old,_ in RELOCATION.values())):
                    continue
                self.donor[offset+i]=self.clean[offset+i]

    def run_copy(self,codebook=None):
        with patch.object(graft,"ATTESTED_CLEAN_OFFSETS",self.positions),\
             patch.object(graft,"GLYPH_BLOCK_SIZE",self.glyph_size),\
             patch.object(importer,"GLYPH_BLOCK_SIZE",self.glyph_size),\
             patch.object(importer,"ROM_BYTES",len(self.clean)):
            return graft.graft_collision_safe_font(
                bytes(self.clean),bytes(self.donor),bytes(self.clean),
                self.positions,self.positions,
                codebook if codebook is not None else self.codebook)

    def test_original_ascii_glyphs_restored(self):
        updated,report=self.run_copy()
        for name,base in self.positions.items():
            for _,old,slot in RELOCATION.values():
                self.assertEqual(updated[base+old*64],0x11)
                if name not in graft.UNVERIFIED_SMALL_FONTS:
                    self.assertEqual(updated[base+slot*64],0x99)
                    self.assertEqual(updated[base+self.glyph_size+slot],5)
        self.assertTrue(report["english_f_w_z_shapes_restored"])
        self.assertFalse(report["release_ready"])

    def test_does_not_touch_non_font_bytes(self):
        result,_=self.run_copy()
        self.assertEqual(result[:0x1000],self.clean[:0x1000])
        self.assertEqual(result[-0x2000:],self.clean[-0x2000:])

    def test_missing_small_font_accent_art_reported(self):
        _,r=self.run_copy()
        self.assertEqual(set(r["small_font_missing_accents"]),
                         graft.UNVERIFIED_SMALL_FONTS)
        self.assertEqual(
            r["small_font_missing_accents"]["gFontSmallLatinGlyphs"],
            ["ấ","ằ","ắ"])

    def test_wrong_source_codebook_refused(self):
        with self.assertRaisesRegex(ValueError,"does not reserve"):
            self.run_copy({**self.codebook,"ấ":"0xDA"})

    def test_source_width_table_drift_refused(self):
        self.clean[self.positions["gFontNormalLatinGlyphs"]+self.glyph_size+0xDA]=7
        with self.assertRaises(ValueError):
            self.run_copy()


if __name__=="__main__":
    unittest.main()
