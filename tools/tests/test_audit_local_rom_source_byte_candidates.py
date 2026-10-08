#!/usr/bin/env python3
"""Safety tests: local ROM source byte candidates remain read-only."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_local_rom_source_byte_candidates import assess


class LocalROMCandidateAuditTests(unittest.TestCase):
    def setUp(self):
        self.clean = b"\x00" * 8 + b"\xbb\xff" + b"\x00" * 8
        self.v04 = b"\x00" * 8 + b"\xbc\xff" + b"\x00" * 8
        self.chars = {"A": b"\xbb", "$": b"\xff"}
        self.tokens = {}
        self.row = {
            "source_label": "Title", "source_file": "data/test.inc", "source_line": "5",
            "category": "system-ui", "english": "A$",
            "build_rom_offset": "0x00000008",
            "shipping_rom_offset": "", "shipping_match_status": "",
        }

    def test_exact_build_candidate_is_not_a_verified_write(self):
        r = assess(self.row, self.clean, self.v04, self.chars, self.tokens)
        self.assertEqual(r["source_byte_status"], "candidate:byte-exact-at-build-offset")
        self.assertEqual(r["v04_at_offset"], "source-different")
        self.assertFalse(r["runtime_reference_verified"])
        self.assertFalse(r["binary_write_authorized"])
        self.assertFalse(r["binary_skip_authorized"])

    def test_same_source_bytes_in_v04_still_not_a_safe_skip(self):
        r = assess(self.row, self.clean, self.clean, self.chars, self.tokens)
        self.assertEqual(r["v04_at_offset"], "source-identical")
        self.assertFalse(r["binary_skip_authorized"])

    def test_attested_checkpoint_mismatch_is_rejected(self):
        row = dict(self.row, shipping_rom_offset="0x0000000A",
                   shipping_match_status="verified:checkpoint")
        with self.assertRaisesRegex(ValueError, "checkpoint contradicted"):
            assess(row, self.clean, self.v04, self.chars, self.tokens)

    def test_unknown_symbol_is_blocked(self):
        row = dict(self.row, shipping_rom_offset="", build_rom_offset="")
        r = assess(row, self.clean, self.v04, self.chars, self.tokens)
        self.assertEqual(r["source_byte_status"], "blocked:no-offset")
        self.assertFalse(r["binary_write_authorized"])

    def test_bad_candidate_offset_stays_blocked(self):
        row = dict(self.row, build_rom_offset="0xZZZZ")
        r = assess(row, self.clean, self.v04, self.chars, self.tokens)
        self.assertEqual(r["source_byte_status"], "blocked:invalid-offset")


if __name__ == "__main__":
    unittest.main()
