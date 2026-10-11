#!/usr/bin/env python3
"""Never compact the wrong Arena/pokeemerald linker or lose section owners."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compact_arena_linker_gaps import compact_linker_text

HEADER = """ENTRY(Start)
/* Modify the following load addresses as needed to make more room.
   declarations below and their references further down to get rid of the gaps. */
__anim_mon_load_address = 0x8c00000;
__gfx_load_address = 0x8d00000;
SECTIONS {
    multiboot_data : { *(.rodata) }
    anim_mon_front_pic_data __anim_mon_load_address :
    ALIGN(4) { src/anim_mon_front_pics.o(.rodata); } > ROM =0
    gfx_data __gfx_load_address :
    ALIGN(4) { src/graphics.o(.rodata); } > ROM =0
    extra : { src/*.o(.rodata); } > ROM =0
}
"""


class CompactArenaLinkerTests(unittest.TestCase):
    def test_preserve_section_contents_remove_only_two_fixed_anchors(self):
        changed = compact_linker_text(HEADER)
        self.assertNotIn("__anim_mon_load_address", changed)
        self.assertNotIn("__gfx_load_address", changed)
        self.assertIn("anim_mon_front_pic_data :", changed)
        self.assertIn("gfx_data :", changed)
        self.assertIn("src/anim_mon_front_pics.o(.rodata)", changed)
        self.assertIn("src/graphics.o(.rodata)", changed)
        self.assertIn("extra : { src/*.o(.rodata); }", changed)
        self.assertEqual(changed.count("SECTION"), HEADER.count("SECTION"))

    def test_refuses_wrong_version_fixed_addresses(self):
        self.assertRaisesRegex(
            ValueError, "expected exact Arena",
            compact_linker_text, HEADER.replace("0x8d00000", "0x8c00000"))

    def test_refuses_any_third_symbol_reference(self):
        bad = HEADER.replace(
            "extra :", "extra : /* __gfx_load_address */")
        with self.assertRaisesRegex(ValueError, "expected exact Arena"):
            compact_linker_text(bad)

    def test_refuses_unknown_section_owner(self):
        with self.assertRaisesRegex(ValueError, "unrecognized Arena section"):
            compact_linker_text(HEADER.replace(
                "gfx_data __gfx_load_address :", "gfx_data :"))

    def test_refuses_unknown_linker_and_double_application(self):
        with self.assertRaisesRegex(ValueError, "unrecognized original"):
            compact_linker_text(HEADER.replace(
                "/* Modify the following load addresses as needed to make more room.",
                "/* modified anchor */"))
        compacted = compact_linker_text(HEADER)
        with self.assertRaises(ValueError):
            compact_linker_text(compacted)


if __name__ == "__main__":
    unittest.main()
