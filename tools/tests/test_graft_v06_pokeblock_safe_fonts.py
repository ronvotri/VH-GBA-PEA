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

    def test_bundled_3666_source_C_UI_SHA_and_glyph_bank_profile(self):
        self.assertEqual(v06.PINNED_C_UI_3666_SOURCE_SHA256,
                         "f9a31e14e763e6f71adbd02930d5e7d35365fb8f392b717cbb7834244c15d41c")
        self.assertEqual(v06.ATTESTED_C_UI_3666_FONT_OFFSETS[
                         "gFontNormalLatinGlyphs"],0x73AF54)
        v06.require_pinned_target_symbols(v06.ATTESTED_C_UI_3666_FONT_OFFSETS,
                                           v06.PINNED_C_UI_3666_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3366_FONT_OFFSETS,
                                               v06.PINNED_C_UI_3666_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_C_UI_3666_FONT_OFFSETS,
                                               v06.PINNED_BIRCH_3366_SOURCE_SHA256)

    def test_naming_controls_3774_exact_SHA_and_glyph_offsets(self):
        self.assertEqual(v06.PINNED_NAMING_3774_SOURCE_SHA256,
                         "3eb605c00fe2e00e02aa90cba994738c029a821c307264f492ea04e0f438e631")
        self.assertEqual(v06.ATTESTED_NAMING_3774_FONT_OFFSETS["gFontNormalLatinGlyphs"],0x73AF7C)
        v06.require_pinned_target_symbols(v06.ATTESTED_NAMING_3774_FONT_OFFSETS,
                                           v06.PINNED_NAMING_3774_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_C_UI_3666_FONT_OFFSETS,
                                               v06.PINNED_NAMING_3774_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_NAMING_3774_FONT_OFFSETS,
                                               v06.PINNED_C_UI_3666_SOURCE_SHA256)

    def test_system_second_3894_exact_SHA_and_font_pair(self):
        self.assertEqual(v06.PINNED_SYSTEM_SECOND_3894_SOURCE_SHA256,
                         "7bf9b814a415f814c51c2e900638fda8ee9c87b533688d828f4134336e316bd9")
        offsets=v06.ATTESTED_SYSTEM_SECOND_3894_FONT_OFFSETS
        self.assertEqual(offsets["gFontSmallNarrowLatinGlyphs"],0x71A588)
        self.assertEqual(offsets["gFontNormalLatinGlyphs"],0x73AD88)
        v06.require_pinned_target_symbols(offsets,
                                           v06.PINNED_SYSTEM_SECOND_3894_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_NAMING_3774_FONT_OFFSETS,
                                               v06.PINNED_SYSTEM_SECOND_3894_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(offsets,
                                               v06.PINNED_NAMING_3774_SOURCE_SHA256)

    def test_dynamic_birch_3366_SHA_paired_with_five_font_symbols(self):
        self.assertEqual(v06.PINNED_BIRCH_3366_SOURCE_SHA256,
                         "a887c81b426c11be12257b66286166b11ac50b4081e06782792f5ce972e97cd0")
        self.assertEqual(v06.ATTESTED_BIRCH_3366_FONT_OFFSETS[
                         "gFontNormalLatinGlyphs"],0x73AEF8)
        v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3366_FONT_OFFSETS,
                                           v06.PINNED_BIRCH_3366_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3364_FONT_OFFSETS,
                                               v06.PINNED_BIRCH_3366_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3366_FONT_OFFSETS,
                                               v06.PINNED_BIRCH_3364_SOURCE_SHA256)

    def test_real_runtime_C_3364_source_SHA_symbol_profile(self):
        self.assertEqual(v06.PINNED_BIRCH_3364_SOURCE_SHA256,
                         "5b63c67009140c309aa1f6339df2abef158e6bb43aa4cb08b6f6e557e5967ea5")
        self.assertEqual(v06.ATTESTED_BIRCH_3364_FONT_OFFSETS[
                         "gFontNormalLatinGlyphs"],0x73AEFC)
        v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3364_FONT_OFFSETS,
                                           v06.PINNED_BIRCH_3364_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3363_FONT_OFFSETS,
                                               v06.PINNED_BIRCH_3364_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3364_FONT_OFFSETS,
                                               v06.PINNED_BIRCH_3363_SOURCE_SHA256)

    def test_birch_3363_source_profile_is_sha_and_font_paired(self):
        self.assertEqual(v06.PINNED_BIRCH_3363_SOURCE_SHA256,
                         "af67fe4775bf29a110b77573667ac397c6933174e1bd6a470e7927f870d9d77f")
        self.assertEqual(v06.ATTESTED_BIRCH_3363_FONT_OFFSETS[
                         "gFontNormalLatinGlyphs"],0x73AF08)
        v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3363_FONT_OFFSETS,
                                           v06.PINNED_BIRCH_3363_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3360_FONT_OFFSETS,
                                               v06.PINNED_BIRCH_3363_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3363_FONT_OFFSETS,
                                               v06.PINNED_BIRCH_3360_SOURCE_SHA256)

    def test_birch_reflow_source_profile_pairs_its_own_symbols(self):
        self.assertEqual(v06.PINNED_BIRCH_3360_SOURCE_SHA256,
                         "c1756599fa7ffd227c073891ab43765aff3442bf0b6a15aa07efb624dbcc6f78")
        self.assertEqual(v06.ATTESTED_BIRCH_3360_FONT_OFFSETS[
                         "gFontNormalLatinGlyphs"],0x73AF8C)
        v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3360_FONT_OFFSETS,
                                           v06.PINNED_BIRCH_3360_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_3360_FONT_OFFSETS,
                                               v06.PINNED_BIRCH_3360_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(v06.ATTESTED_BIRCH_3360_FONT_OFFSETS,
                                               v06.PINNED_3360_SOURCE_SHA256)

    def test_pinned_3360_source_font_profile_is_exactly_paired(self):
        self.assertEqual(
            v06.PINNED_3360_SOURCE_SHA256,
            "9e804a005210d59d4dc1806d387d3b50ee412ab9e7f5df0f56d5f27e43407f7a")
        self.assertEqual(
            v06.ATTESTED_3360_FONT_OFFSETS["gFontNormalLatinGlyphs"],0x73AF98)
        v06.require_pinned_target_symbols(
            v06.ATTESTED_3360_FONT_OFFSETS,v06.PINNED_3360_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(
                v06.ATTESTED_SOURCE_FONT_OFFSETS,v06.PINNED_3360_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(
                v06.ATTESTED_3360_FONT_OFFSETS,v06.PINNED_SOURCE_SHA256)

    def test_real_donor_graft_accepts_exact_3894_profile_not_synthetic(self):
        self.assertEqual(v06.PINNED_SYSTEM_SECOND_3894_SOURCE_SHA256,
                         "7bf9b814a415f814c51c2e900638fda8ee9c87b533688d828f4134336e316bd9")
        v06.require_pinned_target_symbols(
            v06.ATTESTED_SYSTEM_SECOND_3894_FONT_OFFSETS,
            v06.PINNED_SYSTEM_SECOND_3894_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(
                v06.ATTESTED_NAMING_3774_FONT_OFFSETS,
                v06.PINNED_SYSTEM_SECOND_3894_SOURCE_SHA256)

    def test_v04_donor_profile_4406_sha_paired_and_protected(self):
        self.assertEqual(v06.PINNED_SYSTEM_SCROLL_4406_SOURCE_SHA256,
                         "ae37ecd0af0b3c0d5976fa1dacf6a5009ca2ecb3367f125c6c202ef77c4358d3")
        offsets=v06.ATTESTED_SYSTEM_SCROLL_4406_FONT_OFFSETS
        self.assertEqual(offsets["gFontNormalLatinGlyphs"],0x73AB24)
        v06.require_pinned_target_symbols(
            offsets,v06.PINNED_SYSTEM_SCROLL_4406_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError,"not paired"):
            v06.require_pinned_target_symbols(
                v06.ATTESTED_SYSTEM_SECOND_3894_FONT_OFFSETS,
                v06.PINNED_SYSTEM_SCROLL_4406_SOURCE_SHA256)

    def test_unattested_source_sha_rejected(self):
        with self.assertRaisesRegex(ValueError,"no attested font profile"):
            v06.require_pinned_target_symbols(
                v06.ATTESTED_3360_FONT_OFFSETS,"f"*64)

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
             patch.object(v06,"ATTESTED_SOURCE_FONT_OFFSETS",self.offsets),\
             patch.object(v06,"GLYPH_BLOCK_SIZE",self.size):
            with self.assertRaisesRegex(ValueError,"mismatched"):
                v06.graft_v06_font(
                    bytes(self.clean),bytes(self.donor),bytes(self.clean),
                    {**self.offsets,"gFontNormalLatinGlyphs":0x17000},
                    self.offsets,self.book)

if __name__=="__main__":
    unittest.main()
