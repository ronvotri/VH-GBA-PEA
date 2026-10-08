#!/usr/bin/env python3
"""Regression tests for the read-only user-facing integration planner."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLANNER = Path(__file__).resolve().parents[1] / "plan_user_facing_integration.py"
FIELDS = (
    "source_label", "source_file", "source_line", "category", "english",
    "shipping_rom_offset", "shipping_match_status",
)

class IntegrationPlannerTests(unittest.TestCase):
    def run_planner(self, rows, manifests):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        catalog = root / "catalog.csv"
        with catalog.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        trans_dir = root / "translations"
        trans_dir.mkdir()
        for i, (scope, dictionary) in enumerate(manifests):
            (trans_dir / f"part-{i}.json").write_text(
                json.dumps({"schema_version": 1, "scope": scope,
                            "translations": dictionary}, ensure_ascii=False),
                encoding="utf-8",
            )
        output = root / "plan.json"
        summary = root / "summary.json"
        result = subprocess.run(
            [sys.executable, str(PLANNER),
             "--catalog", str(catalog), "--translations", str(trans_dir),
             "--out", str(output), "--summary", str(summary)],
            capture_output=True, text=True,
        )
        return result, output, summary

    def test_source_identity_never_proves_v04_noop(self):
        rows = [
            {"source_label": "gText_Name", "source_file": "src/strings.c",
             "source_line": "10", "category": "system-ui",
             "english": "PIKACHU", "shipping_rom_offset": "",
             "shipping_match_status": ""},
            {"source_label": "gText_Menu", "source_file": "src/strings.c",
             "source_line": "11", "category": "system-ui",
             "english": "START", "shipping_rom_offset": "",
             "shipping_match_status": ""},
            {"source_label": "BattleString", "source_file": "src/battle.c",
             "source_line": "20", "category": "battle",
             "english": "Fainted!", "shipping_rom_offset": "0x00000060",
             "shipping_match_status": "verified:exact-source-bytes-at-build-offset"},
            {"source_label": "Debug", "source_file": "src/test.c",
             "source_line": "30", "category": "debug-internal",
             "english": "TEST", "shipping_rom_offset": "",
             "shipping_match_status": ""},
        ]
        manifests = [
            ("system-ui", {
                "gText_Name@@src/strings.c:10": "PIKACHU",
                "gText_Menu@@src/strings.c:11": "BẮT ĐẦU",
            }),
            ("battle", {"BattleString@@src/battle.c:20": "Đã gục!"}),
        ]
        result, output, summary = self.run_planner(rows, manifests)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(output.read_text(encoding="utf-8"))
        report = json.loads(summary.read_text(encoding="utf-8"))
        self.assertEqual(report["catalog_user_facing_rows"], 3)
        self.assertEqual(report["excluded_debug_internal_rows"], 1)
        self.assertEqual(report["source_text_comparison_counts"],
                         {"source-identical": 1, "source-changed": 2})
        self.assertEqual(report["rows_safe_to_skip_binary_write"], 0)
        self.assertEqual(report["baseline_rom_byte_comparisons_performed"], 0)
        self.assertFalse(any(p["is_safe_to_skip_binary_write"] for p in plan))
        self.assertEqual(plan[0]["source_text_comparison"], "source-identical")
        self.assertIn("baseline-before-skipping", plan[0]["planned_binary_action"])
        self.assertEqual(report["integration_status_counts"],
                         {"blocked:needs-shipping-resolution": 2,
                          "ready:verified-shipping-offset": 1})

    def test_cross_scope_manifest_does_not_count_as_coverage(self):
        rows = [{"source_label": "Label", "source_file": "src/battle.c",
                 "source_line": "12", "category": "battle", "english": "TEXT",
                 "shipping_rom_offset": "", "shipping_match_status": ""}]
        result, _, _ = self.run_planner(
            rows, [("system-ui", {"Label@@src/battle.c:12": "BẢN DỊCH"})]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("coverage mismatch", result.stderr)

    def test_duplicate_source_catalog_identity_fails(self):
        row = {"source_label": "Label", "source_file": "src/test.c",
               "source_line": "42", "category": "system-ui", "english": "OPEN",
               "shipping_rom_offset": "", "shipping_match_status": ""}
        result, _, _ = self.run_planner(
            [row, dict(row)],
            [("system-ui", {"Label@@src/test.c:42": "Mở"})]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate catalog source identities", result.stderr)

    def test_malformed_verified_shipping_offset_is_blocked(self):
        row = {"source_label": "Label", "source_file": "src/test.c",
               "source_line": "42", "category": "system-ui", "english": "OPEN",
               "shipping_rom_offset": "0xNOTHEX",
               "shipping_match_status": "verified:exact-source-bytes-at-build-offset"}
        result, output, summary = self.run_planner(
            [row], [("system-ui", {"Label@@src/test.c:42": "Mở"})]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(summary.read_text(encoding="utf-8"))
        self.assertEqual(report["integration_status_counts"],
                         {"blocked:invalid-verified-shipping-offset": 1})
        self.assertFalse(json.loads(output.read_text(encoding="utf-8"))[0]
                         ["is_safe_to_skip_binary_write"])

    def test_outside_rom_verified_shipping_offset_is_blocked(self):
        row = {"source_label": "Label", "source_file": "src/test.c",
               "source_line": "42", "category": "system-ui", "english": "OPEN",
               "shipping_rom_offset": "0x02000000",
               "shipping_match_status": "verified:exact-source-bytes-at-build-offset"}
        result, _, summary = self.run_planner(
            [row], [("system-ui", {"Label@@src/test.c:42": "Mở"})]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(summary.read_text(encoding="utf-8"))
        self.assertEqual(report["integration_status_counts"],
                         {"blocked:invalid-verified-shipping-offset": 1})

    def test_duplicate_catalog_identity_fails(self):
        rows = [{"source_label": "Label", "source_file": "src/battle.c",
                 "source_line": "12", "category": "battle", "english": "TEXT",
                 "shipping_rom_offset": "", "shipping_match_status": ""}]
        result, _, _ = self.run_planner(
            rows, [
                ("battle", {"Label@@src/battle.c:12": "Dịch"}),
                ("battle", {"Label@@src/battle.c:12": "Dịch"}),
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("coverage mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
