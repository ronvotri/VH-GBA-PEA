#!/usr/bin/env python3
"""Reject any v0.6 Pokéblock/PKMN/= damage before releasing a patched font."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import import_v04_glyphs_into_source_build as loader
import graft_collision_safe_v04_fonts as v05
import graft_v06_pokeblock_safe_fonts as v06
from plan_collision_free_vietnamese_font import RELOCATION as OLD
from plan_v06_pokeblock_safe_font import RELOCATION as NEW

class GraftV06Tests(unittest.TestCase):
    def setUp(self):
        self.size=0x4000
        self.offsets={n:0x1000+i*0x4500 for i,n in enumerate(v06.FONT_NAMES)}
        self.clean=bytearray(0x20000)
        self.donor=bytearray(self.clean)
        self.book={
            "f":"0xDA","w":"0xEB","z":"0xEE","ấ":"0x30","ằ":"0x31",
            "ắ":"0x32","đ":"0x33","ì":"0x37","d":"0xD8","i":"0xDD"}
        for name,base in self.offsets.items():
            for x,(english,src,target) in enumerate(OLD.values()):
                self.clean[base+src*64]=0x15
                self.clean[base+self.size+src]=5
                self.clean[base+self.size+target]=4
            for code in list(v06.SPECIAL_CODES)+list(v06.ASCII_PUNCT):
                self.clean[base+code*64]=0x26
                self.clean[base+self.size+code]=6
            for char,r in NEW.items():
                self.clean[base+self.size+r["width_reference_byte"]]=5
                self.clean[base+self.size+r["target"]]=4
        self.donor[:]=self.clean
        for name,base in self.offsets.items():
            for english,src,target in OLD.values():
                if name not in v05.UNVERIFIED_SMALL_FONTS:
                    self.donor[base+src*64]=0x51
            for char,r in NEW.items():
                # A real v0.4 picture for đ exists in Small but not SmallNarrow.
                available=(name not in v05.UNVERIFIED_SMALL_FONTS or
                          (name=="gFontSmallLatinGlyphs" and char=="đ"))
                if available:
                    self.donor[base+r["source"]*64]=0x51
            # The real donor also damages several native token slots, but
            # does not contain every accent in every Small style.
            for code in (0x55,0x57,0x58):
                if name!="gFontSmallNarrowLatinGlyphs":
                    self.donor[base+code*64]=0x51

    def apply(self,book=None):
        with patch.object(v06,"ATTESTED_CLEAN_OFFSETS",self.offsets),\
             patch.object(v06,"ATTESTED_SOURCE_FONT_OFFSETS",self.offsets),\
             patch.object(v06,"GLYPH_BLOCK_SIZE",self.size),\
             patch.object(v05,"ATTESTED_CLEAN_OFFSETS",self.offsets),\
             patch.object(v05,"GLYPH_BLOCK_SIZE",self.size),\
             patch.object(loader,"GLYPH_BLOCK_SIZE",self.size),\
             patch.object(loader,"ROM_BYTES",len(self.clean)):
            return v06.graft_v06_font(
                bytes(self.clean),bytes(self.donor),bytes(self.clean),
                self.offsets,self.offsets,book if book is not None else self.book)

    def test_glyphs_moved_but_special_tokens_restored(self):
        out,meta=self.apply()
        self.assertFalse(meta["release_ready"])
        self.assertTrue(meta["native_pokeblock_55_to_59_restored_all_five"])
        for name,base in self.offsets.items():
            for code in list(v06.SPECIAL_CODES)+list(v06.ASCII_PUNCT):
                self.assertEqual(out[base+code*64:base+(code+1)*64],
                                 self.clean[base+code*64:base+(code+1)*64])
                self.assertEqual(out[base+self.size+code],
                                 self.clean[base+self.size+code])
            for char,rule in NEW.items():
                self.assertNotEqual(
                    out[base+rule["target"]*64:base+(rule["target"]+1)*64],
                    self.clean[base+rule["target"]*64:base+(rule["target"]+1)*64])

    def test_reject_glyph_alias_into_equals_sign(self):
        with self.assertRaisesRegex(ValueError,"new byte"):
            self.apply({**self.book,"ì":"0x35"})

    def test_reject_glyph_alias_into_pokeblock(self):
        with self.assertRaisesRegex(ValueError,"collides"):
            self.apply({**self.book,"é":"0x56"})

    def test_preserve_non_font_data(self):
        out,_=self.apply()
        self.assertEqual(out[:0x1000],self.clean[:0x1000])
        self.assertEqual(out[0x17000:],self.clean[0x17000:])

    def test_wrong_compiled_source_symbol_positions_refused(self):
        # Baseline pokeemerald.sym must not be used for SOURCE_LEVEL_FONT.sym.
        with self.assertRaisesRegex(ValueError,"wrong v0.6 target"):
            v06.require_pinned_target_symbols(v06.ATTESTED_CLEAN_OFFSETS)

    def test_pinned_2093_source_build_identity(self):
        self.assertEqual(
            v06.PINNED_SOURCE_SHA256,
            "5cae1a20698fcd7036ccdc0f2bdbc0c0c80d942380ab48611fb3ec816ebcab7f")
        self.assertEqual(
            v06.ATTESTED_SOURCE_FONT_OFFSETS["gFontNormalLatinGlyphs"],
            0x73BD9C)
        shifted=dict(v06.ATTESTED_SOURCE_FONT_OFFSETS)
        shifted["gFontNormalLatinGlyphs"]+=4
        with self.assertRaisesRegex(ValueError,"wrong v0.6 target"):
            v06.require_pinned_target_symbols(shifted)

    def test_requires_exact_clean_source_font_geometry(self):
        with patch.object(v06,"ATTESTED_CLEAN_OFFSETS",self.offsets),\
             patch.object(v06,"ATTESTED_SOURCE_FONT_OFFSETS",self.offsets):
            with self.assertRaisesRegex(ValueError,"mismatched"):
                v06.graft_v06_font(
                    bytes(self.clean),bytes(self.donor),bytes(self.clean),
                    {**self.offsets,"gFontNormalLatinGlyphs":0x17000},
                    self.offsets,self.book)

if __name__=="__main__":
    unittest.main()
