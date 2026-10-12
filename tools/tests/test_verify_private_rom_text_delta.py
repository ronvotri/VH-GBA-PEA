#!/usr/bin/env python3
"""Private-ROM text delta safety without storing or exposing any GBA binary."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_private_rom_text_delta import verify


class PrivateDeltaTests(unittest.TestCase):
    def setUp(self):
        self.rom = b"BOOT" + b"\x00" * 60
        self.patched = self.rom[:16] + b"\x11\x12\x13\x14" + self.rom[20:]
        self.spans = [{
            "offset": "0x10", "before_hex": "00000000",
            "after_hex": "11121314",
        }]

    def check(self, source=None, target=None, spans=None):
        return verify(
            self.rom if source is None else source,
            self.patched if target is None else target,
            self.spans if spans is None else spans,
            protected_prefix=4)

    def test_exact_text_only_range(self):
        report = self.check()
        self.assertEqual(report["actual_byte_changes"], 4)
        self.assertEqual(report["unexpected_byte_changes"], 0)
        self.assertFalse(report["font_banks_attested"])
        self.assertFalse(report["emulator_QA_passed"])
        self.assertFalse(report["release_ready"])

    def test_reject_unexpected_changes_and_header(self):
        outside = bytearray(self.patched)
        outside[32] = 0x42
        with self.assertRaisesRegex(ValueError, "non-text bytes"):
            self.check(target=bytes(outside))
        header = bytearray(self.patched)
        header[1] = 0x42
        with self.assertRaisesRegex(ValueError, "startup/title"):
            self.check(target=bytes(header))

    def test_reject_original_mismatch_overlap_resize(self):
        with self.assertRaisesRegex(ValueError, "source original"):
            self.check(spans=[{**self.spans[0], "before_hex": "01000000"}])
        with self.assertRaisesRegex(ValueError, "overlapping"):
            self.check(spans=self.spans + [self.spans[0]])
        with self.assertRaisesRegex(ValueError, "resized"):
            self.check(spans=[{**self.spans[0], "after_hex": "1112"}])

    def test_reject_pointers_into_modified_text_interiors(self):
        rom = bytearray(self.rom)
        rom[40:44] = (0x08000011).to_bytes(4, "little")
        patched = bytearray(rom)
        patched[16:20] = b"\x11\x12\x13\x14"
        with self.assertRaisesRegex(ValueError, "pointer into modified text interior"):
            self.check(source=bytes(rom), target=bytes(patched))


if __name__ == "__main__":
    unittest.main()
