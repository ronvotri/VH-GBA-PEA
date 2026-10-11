#!/usr/bin/env python3
"""Duplicate payload audit must remain conservative and source-address agnostic."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_duplicate_source_payloads import audit_duplicate_payloads


class DuplicateMapPayloadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for filename, text in {
            "data/maps/A/scripts.inc": (
                "Intro::\n\t.byte 0xC7, 0xFF\n"
                "Other::\n\t.byte 0xC7, 0xFF\n"
                "Different::\n\t.byte 0xD7, 0xFF\n"),
            "data/maps/B/scripts.inc": "FarAway::\n\t.byte 0xC7, 0xFF\n",
        }.items():
            path = self.root / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    @staticmethod
    def report(rows, dynamic=False):
        key = "accepted" if dynamic else "translated"
        return {"mode": "apply", "labels_staged": len(rows), key: rows}

    @staticmethod
    def row(file, label, dynamic=False):
        if dynamic:
            return {"file": file, "label": label}
        return {"source_file": file, "label": label}

    def test_finds_same_file_byte_duplicates_with_no_mutations(self):
        a = "data/maps/A/scripts.inc"
        b = "data/maps/B/scripts.inc"
        reports = [
            self.report([self.row(a, "Intro"), self.row(a, "Other"),
                         self.row(a, "Different")]),
            self.report([self.row(b, "FarAway", True)], dynamic=True),
        ]
        before = (self.root/a).read_bytes()
        result = audit_duplicate_payloads(self.root, reports)
        self.assertEqual(result["source_owned_map_labels_checked"], 4)
        self.assertEqual(result["same_file_exact_duplicate_groups"], 1)
        self.assertEqual(result["same_file_theoretical_duplicate_payload_bytes"], 2)
        self.assertEqual(result["cross_file_exact_duplicate_groups"], 1)
        self.assertEqual(result["actual_linker_bytes_reclaimed"], 0)
        self.assertFalse(result["pointer_references_or_layout_safety_proven"])
        self.assertEqual(before, (self.root/a).read_bytes())

    def test_reject_duplicate_stage_source_owner(self):
        a = "data/maps/A/scripts.inc"
        report = self.report([self.row(a, "Intro")])
        with self.assertRaisesRegex(ValueError, "duplicate prior"):
            audit_duplicate_payloads(self.root, [report, report])

    def test_reject_missing_or_drifting_sources(self):
        missing = self.report([self.row("data/maps/X/scripts.inc", "Foo")])
        with self.assertRaisesRegex(ValueError, "missing or unsafe"):
            audit_duplicate_payloads(self.root, [missing])
        source = self.root/"data/maps/A/scripts.inc"
        source.write_text('Intro::\n\t.string "English$"\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing staged"):
            audit_duplicate_payloads(
                self.root,[self.report([self.row("data/maps/A/scripts.inc", "Intro")])])

    def test_fail_closed_report_mode_and_count(self):
        a = "data/maps/A/scripts.inc"
        report = self.report([self.row(a, "Intro")])
        report["mode"] = "dry-run"
        with self.assertRaisesRegex(ValueError, "applied source"):
            audit_duplicate_payloads(self.root, [report])
        report["mode"] = "apply"
        report["labels_staged"] = 2
        with self.assertRaisesRegex(ValueError, "report count"):
            audit_duplicate_payloads(self.root, [report])


if __name__ == "__main__":
    unittest.main()
