#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pokemon_gba_font_glyphs import decode_glyph,encode_glyph,synthesize_small_from_narrow


class GlyphCodecTests(unittest.TestCase):
    def test_byte_size_and_image_roundtrip(self):
        pixels=[[0]*16 for _ in range(16)]
        for y in range(2,12):
            pixels[y][3]=1
            pixels[y][4]=2
        for y in range(4,12):
            pixels[y][9]=1
        encoded=encode_glyph(pixels)
        self.assertEqual(len(encoded),64)
        self.assertEqual(decode_glyph(encoded),pixels)

    def test_high_low_byte_halfrow_order(self):
        pixels=[[0]*16 for _ in range(16)]
        pixels[0][:8]=[1,2,1,0,2,0,1,2]
        encoded=encode_glyph(pixels)
        self.assertEqual(encoded[0],0b10000110)
        self.assertEqual(encoded[1],0b01100100)
        self.assertEqual(decode_glyph(encoded)[0][:8],pixels[0][:8])

    def test_reserved_color_three_decodes_as_blank(self):
        self.assertTrue(all(v==0 for row in decode_glyph(b"\xff"*64) for v in row))

    def test_small_font_fit_and_baseline(self):
        pixels=[[0]*16 for _ in range(16)]
        for y in range(13):
            pixels[y][2]=1
        compact=decode_glyph(synthesize_small_from_narrow(encode_glyph(pixels),5))
        self.assertTrue(all(compact[y][2]==1 for y in range(12)))
        self.assertTrue(all(v==0 for row in compact[12:] for v in row))

    def test_reject_oversized_narrow_glyph(self):
        with self.assertRaisesRegex(ValueError,"1..8"):
            synthesize_small_from_narrow(bytes(64),9)

    def test_reject_invalid_palette(self):
        pixels=[[0]*16 for _ in range(16)]
        pixels[0][0]=3
        with self.assertRaisesRegex(ValueError,"background/foreground/shadow"):
            encode_glyph(pixels)

    def test_reject_bad_compressed_size(self):
        with self.assertRaisesRegex(ValueError,"64-byte"):
            decode_glyph(b"\x00"*63)


if __name__=="__main__":
    unittest.main()
