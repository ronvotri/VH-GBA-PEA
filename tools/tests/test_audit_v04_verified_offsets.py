#!/usr/bin/env python3
"""Regression tests for source-offset byte comparison: no write authorization."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_v04_verified_offsets import compare_verified_span


class V04VerifiedOffsetAuditTests(unittest.TestCase):
    def test_matching_original_bytes_are_only_a_byte_observation(self):
        self.assertEqual(
            compare_verified_span(b"ORIGINAL", b"ORIGINAL", 0, b"ORIGINAL"),
            "source-bytes-identical-at-original-offset",
        )

    def test_v04_change_is_reported_without_pointer_inference(self):
        self.assertEqual(
            compare_verified_span(b"ORIGINAL", b"MODIFIED", 0, b"ORIGINAL"),
            "source-bytes-differ-at-original-offset",
        )

    def test_wrong_clean_source_bytes_fail_closed(self):
        self.assertEqual(
            compare_verified_span(b"ORIGINAL", b"ORIGINAL", 0, b"DIFFERENT"),
            "refused:source-bytes-not-equal-clean-rom",
        )

    def test_out_of_range_is_unresolved(self):
        self.assertEqual(
            compare_verified_span(b"AB", b"AB", 1, b"BB"),
            "unresolved:offset-out-of-range",
        )


if __name__ == "__main__":
    unittest.main()
