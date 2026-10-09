#!/usr/bin/env python3
"""Prove synthetic Vietnamese glyph strokes respect stock font and byte safety."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from synthesize_vietnamese_source_fonts import accent_recipe,compose
from pokemon_gba_font_glyphs import encode_glyph,decode_glyph

class SynthVietnameseFontTests(unittest.TestCase):
    def setUp(self):
        self.pix=[[0]*16 for _ in range(16)]
        for y in range(3,12):
            for x in range(2,6):
                self.pix[y][x]=1 if x==2 or y in (3,11) else 2

    def test_vietnamese_tone_and_shape_combination(self):
        self.assertEqual(accent_recipe("ấ"),("a",["circumflex","acute"]))
        self.assertEqual(accent_recipe("ỡ"),("o",["horn","tilde"]))
        self.assertEqual(accent_recipe("ặ"),("a",["breve","dot"]))
        self.assertEqual(accent_recipe("đ"),("d",["bar"]))
        self.assertEqual(accent_recipe("Đ"),("D",["bar"]))

    def test_unsupported_character_fails(self):
        with self.assertRaisesRegex(ValueError,"cannot be constructed"):
            accent_recipe("§")

    def test_composition_foreground_and_2bpp_roundtrip(self):
        original=decode_glyph(encode_glyph(self.pix))
        for marks in (["grave"],["circumflex","acute"],
                      ["horn","hook"],["breve","dot"],["bar"]):
            with self.subTest(marks=marks):
                rendered,width=compose(original,marks,7)
                self.assertTrue(7<=width<=16)
                self.assertNotEqual(rendered,original)
                self.assertTrue(any(c==1 for row in rendered for c in row))
                self.assertEqual(decode_glyph(encode_glyph(rendered)),rendered)

    def test_reject_blank_or_bad_width(self):
        with self.assertRaisesRegex(ValueError,"blank/bad-width"):
            compose([[0]*16 for _ in range(16)],["acute"],7)
        with self.assertRaisesRegex(ValueError,"blank/bad-width"):
            compose(self.pix,["acute"],17)

if __name__=="__main__":
    unittest.main()
