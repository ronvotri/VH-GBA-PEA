#!/usr/bin/env python3
"""Tests for no-pointer, no-overlap glyph import from private v0.4."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import import_v04_glyphs_into_source_build as fonts


class FontImportTests(unittest.TestCase):
    def setUp(self):
        self.blocks={name:0x100+i*0x120 for i,name in enumerate(fonts.FONT_NAMES)}
        self.clean=bytearray(b"\x7A"*0x2000)
        self.donor=bytearray(self.clean)
        for i,name in enumerate(fonts.FONT_NAMES):
            self.donor[self.blocks[name]+i]=0x30+i

    def overlay(self, rebuilt=None, target=None):
        with patch.object(fonts,"ROM_BYTES",len(self.clean)),patch.object(
                fonts,"GLYPH_BLOCK_SIZE",0x100):
            return fonts.overlay_fonts(bytes(self.clean),bytes(self.donor),
                bytes(self.clean) if rebuilt is None else rebuilt,
                self.blocks,self.blocks if target is None else target)

    def test_only_donor_font_bytes_change(self):
        out,count=self.overlay()
        self.assertEqual(sum(count.values()),5)
        self.assertEqual(sum(x!=y for x,y in zip(out,self.clean)),5)
        for name,off in self.blocks.items():
            self.assertEqual(out[off:off+0x100],self.donor[off:off+0x100])
        self.assertEqual(out[:0x100],self.clean[:0x100])

    def test_mismatch_rebuilt_font_fails(self):
        altered=bytearray(self.clean)
        altered[self.blocks[fonts.FONT_NAMES[0]]]=0x00
        with self.assertRaisesRegex(ValueError,"differs from clean"):
            self.overlay(bytes(altered))

    def test_overlap_blocks_fails(self):
        positions=dict(self.blocks)
        positions[fonts.FONT_NAMES[1]]=positions[fonts.FONT_NAMES[0]]
        with self.assertRaisesRegex(ValueError,"overlapping"):
            self.overlay(target=positions)

    def test_missing_symbols_fails(self):
        with self.assertRaisesRegex(ValueError,"incomplete"):
            fonts.read_symbol_offsets("08100000 R gFontNormalLatinGlyphs")

    def test_duplicate_symbols_fails(self):
        lines="\n".join(
            f"{0x08000000+at:08x} R {name}" for name,at in self.blocks.items())
        with self.assertRaisesRegex(ValueError,"duplicate"):
            fonts.read_symbol_offsets(lines+"\n"+lines.splitlines()[0])

    def test_symbol_maps_from_pinned_rom_addresses(self):
        lines="\n".join(
            f"{0x08000000+at:08x} R {name}" for name,at in self.blocks.items())
        self.assertEqual(fonts.read_symbol_offsets(lines),self.blocks)


if __name__=="__main__":
    unittest.main()
