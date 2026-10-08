#!/usr/bin/env python3
"""Unit tests for strict read-only ROM preflight helpers."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_local_rom_baselines.py"
SPEC = importlib.util.spec_from_file_location("verify_local_rom_baselines", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class VerifyRomBaselinesTests(unittest.TestCase):
    def test_hash_bytes_stable(self):
        self.assertEqual(
            verify.hash_bytes(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_compare_bytes_counts_changes_and_length(self):
        result = verify.compare_bytes(b"abcd", b"axcde")
        self.assertEqual(result["changed_bytes_in_shared_region"], 1)
        self.assertEqual(result["length_difference"], 1)
        self.assertEqual(result["shared_length"], 4)
        self.assertFalse(result["identical"])

    def test_refuses_wrong_baseline_hash(self):
        with self.assertRaisesRegex(SystemExit, "REFUSED"):
            verify.verify_bytes(b"not-a-rom", verify.CLEAN_SHA256, "clean")

    def test_accepts_matching_hash_only(self):
        verify.verify_bytes(b"abc", verify.hash_bytes(b"abc"), "fixture")


if __name__ == "__main__":
    unittest.main()
