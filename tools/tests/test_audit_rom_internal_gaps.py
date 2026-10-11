#!/usr/bin/env python3
"""An uncovered ELF address is NOT proof of spare writable game ROM space."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audit_source_rom_headroom as capacity
import audit_rom_internal_gaps as gaps
from test_audit_source_rom_headroom import make_elf


class InternalGapTests(unittest.TestCase):
    def setUp(self):
        self.size = 512
        for target, attribute, value in (
            (capacity, "GBA_LIMIT", capacity.GBA_BASE + self.size),
            (capacity, "MAX_ROM_SIZE", self.size),
            (gaps, "MAX_ROM_SIZE", self.size),
        ):
            p = patch.object(target, attribute, value)
            p.start()
            self.addCleanup(p.stop)

    def test_internal_ff_gap_is_distinct_from_contiguous_end_headroom(self):
        elf = make_elf([(capacity.GBA_BASE, 128),
                        (capacity.GBA_BASE + 384, 16)])
        rom = bytes([0xFF]) * self.size
        result = gaps.audit_internal_gaps(elf, rom)
        self.assertEqual(result["linker_file_backed_bytes"], 144)
        self.assertEqual(result["linker_high_water_bytes"], 400)
        self.assertEqual(result["ELF_uncovered_internal_bytes"], 256)
        self.assertEqual(result["linker_contiguous_tail_headroom_bytes"], 112)
        self.assertEqual(result["internal_gaps_all_ff_bytes"], 256)
        self.assertEqual(result["ELF_uncovered_internal_gap_count"], 1)
        self.assertEqual(result["internal_gaps"][0]["start_rom_offset"], "0x80")
        self.assertTrue(result["accounting_exact"])
        self.assertFalse(result["automatic_gap_insertion_permitted"])
        self.assertEqual(result["proved_safe_reclaimable_bytes"], 0)

    def test_mixed_gap_cannot_be_called_blank(self):
        elf = make_elf([(capacity.GBA_BASE, 64),
                        (capacity.GBA_BASE + 320, 64)])
        rom = bytearray([0xFF] * self.size)
        rom[120] = 0x00
        rom[300] = 0x42
        snapshot = bytes(rom)
        result = gaps.audit_internal_gaps(elf, rom)
        self.assertEqual(result["ELF_uncovered_internal_bytes"], 256)
        self.assertEqual(result["internal_gaps_mixed_or_other_bytes"], 256)
        self.assertEqual(result["internal_gaps"][0]["byte_class"], "mixed_or_other")
        self.assertEqual(result["proved_safe_reclaimable_bytes"], 0)
        self.assertEqual(bytes(rom), snapshot)

    def test_zero_filled_uncovered_area_still_not_reclaimable(self):
        elf = make_elf([(capacity.GBA_BASE, 128),
                        (capacity.GBA_BASE + 384, 16)])
        rom = bytearray([0xFF] * self.size)
        rom[128:384] = bytes(256)
        result = gaps.audit_internal_gaps(elf, rom)
        self.assertEqual(result["internal_gaps_all_zero_bytes"], 256)
        self.assertEqual(result["proved_safe_reclaimable_bytes"], 0)

    def test_gap_threshold_hides_detail_not_totals(self):
        elf = make_elf([(capacity.GBA_BASE, 128),
                        (capacity.GBA_BASE + 384, 16)])
        result = gaps.audit_internal_gaps(elf, bytes(512), 300)
        self.assertEqual(result["ELF_uncovered_internal_bytes"], 256)
        self.assertEqual(result["internal_gaps"], [])
        self.assertEqual(result["ELF_uncovered_internal_gap_count"], 1)

    def test_no_internal_gaps_does_not_count_end_padding_as_gap(self):
        elf = make_elf([(capacity.GBA_BASE, 400)])
        result = gaps.audit_internal_gaps(elf, bytes(512))
        self.assertEqual(result["ELF_uncovered_internal_bytes"], 0)
        self.assertEqual(result["ELF_uncovered_internal_gap_count"], 0)
        self.assertEqual(result["linker_contiguous_tail_headroom_bytes"], 112)

    def test_refuse_bad_padded_rom_or_threshold_or_overlap(self):
        elf = make_elf([(capacity.GBA_BASE, 128)])
        with self.assertRaisesRegex(ValueError, "32MiB padded"):
            gaps.audit_internal_gaps(elf, bytes(511))
        with self.assertRaisesRegex(ValueError, "invalid gap"):
            gaps.audit_internal_gaps(elf, bytes(512), -1)
        overlap = make_elf([(capacity.GBA_BASE, 128),
                            (capacity.GBA_BASE + 64, 64)])
        with self.assertRaisesRegex(ValueError, "overlapping"):
            gaps.audit_internal_gaps(overlap, bytes(512))


if __name__ == "__main__":
    unittest.main()
