#!/usr/bin/env python3
"""ROM high-water capacity guards must read ELF addresses, not padded bytes."""
import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audit_source_rom_headroom as audit


def make_elf(segments):
    """Minimal valid ARM ELF32 with PT_LOAD program headers."""
    phoff = 52
    raw = bytearray(0x400 + len(segments) * 0x100)
    raw[:16] = b"\x7fELF" + bytes([1, 1, 1, 0]) + bytes(8)
    struct.pack_into(
        "<HHIIIIIHHHHHH", raw, 16,
        2, 40, 1, audit.GBA_BASE, phoff, 0, 0, 52, 32,
        len(segments), 0, 0, 0)
    for i, (load_address, size) in enumerate(segments):
        pos = 0x200 + i * 0x100
        struct.pack_into(
            "<IIIIIIII", raw, phoff + 32*i,
            1, pos, load_address, load_address,
            size, size, 5, 4)
        raw[pos:pos+size] = bytes([0xE0+i]) * size
    return bytes(raw)


class ROMHeadroomTests(unittest.TestCase):
    def setUp(self):
        self.capacity = 512
        self.gba_limit = audit.GBA_BASE + self.capacity
        self.patchers = [
            patch.object(audit, "GBA_LIMIT", self.gba_limit),
            patch.object(audit, "MAX_ROM_SIZE", self.capacity),
        ]
        for p in self.patchers:
            p.start()
            self.addCleanup(p.stop)
        self.rom = bytes([0xFF])*self.capacity

    def test_32MiB_padding_not_mistaken_for_free_linker_space(self):
        elf = make_elf([
            (audit.GBA_BASE, 128),
            (audit.GBA_BASE+384, 16),
        ])
        report = audit.audit_rom_capacity(elf, self.rom, minimum_free_bytes=112)
        self.assertEqual(report["linker_occupied_bytes"], 400)
        self.assertEqual(report["linker_free_bytes"], 112)
        self.assertEqual(report["rom_load_segments"], 2)
        self.assertTrue(report["rom_file_padded_not_used_as_free_space_metric"])

    def test_insufficient_linker_headroom_fails_closed(self):
        elf = make_elf([
            (audit.GBA_BASE, 128),
            (audit.GBA_BASE+384, 16),
        ])
        with self.assertRaisesRegex(ValueError, "linker headroom 112 bytes below"):
            audit.audit_rom_capacity(elf, self.rom, minimum_free_bytes=113)

    def test_ram_load_segments_do_not_count_as_rom(self):
        elf = make_elf([
            (audit.GBA_BASE, 128),
            (0x02000000, 64),
        ])
        report = audit.audit_rom_capacity(elf, self.rom, minimum_free_bytes=384)
        self.assertEqual(report["linker_occupied_bytes"], 128)
        self.assertEqual(report["rom_load_segments"], 1)

    def test_overlapping_source_rom_load_segments_refused(self):
        elf = make_elf([
            (audit.GBA_BASE, 128),
            (audit.GBA_BASE+64, 48),
        ])
        with self.assertRaisesRegex(ValueError, "overlapping"):
            audit.loadable_rom_segments(elf)

    def test_out_of_range_rom_load_segment_refused(self):
        elf = make_elf([(audit.GBA_BASE, 128), (audit.GBA_BASE+500, 30)])
        with self.assertRaisesRegex(ValueError, "exceeds GBA"):
            audit.loadable_rom_segments(elf)

    def test_wrong_architecture_or_truncated_header_refused(self):
        with self.assertRaisesRegex(ValueError, "missing ELF binary"):
            audit.loadable_rom_segments(b"nothing")
        elf = bytearray(make_elf([(audit.GBA_BASE, 128)]))
        struct.pack_into("<H", elf, 18, 3)
        with self.assertRaisesRegex(ValueError, "expected ARM"):
            audit.loadable_rom_segments(bytes(elf))
        truncated = bytearray(make_elf([(audit.GBA_BASE, 128)]))
        struct.pack_into("<I", truncated, 28, len(truncated)+1)
        with self.assertRaisesRegex(ValueError, "truncated"):
            audit.loadable_rom_segments(bytes(truncated))

    def test_rom_must_be_padded_to_exact_capacity(self):
        elf = make_elf([(audit.GBA_BASE, 128)])
        with self.assertRaisesRegex(ValueError, "32MiB padded"):
            audit.audit_rom_capacity(elf, self.rom[:-1], 0)


if __name__ == "__main__":
    unittest.main()
