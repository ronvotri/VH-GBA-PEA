#!/usr/bin/env python3
"""Read-only audit for exact duplicate ROM-source dialogue byte payloads.

This does NOT alias assembly labels, move pointers, edit byte arrays, claim
linker savings, or import new glyph artwork. Identifies candidate repeated
FF-terminated data for a later source-owner and runtime-reference review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from verify_compiled_source_strings import extract_asm_payload, validate_byte_string


def audit_duplicate_payloads(workspace: Path, reports: list[dict]) -> dict:
    root = workspace.resolve()
    seen_owners = set()
    sources = {}
    rows = []
    for index, report in enumerate(reports):
        if report.get("mode") != "apply":
            raise ValueError("only exact applied source reports accepted")
        items = report.get("accepted") if "accepted" in report else report.get("translated")
        if not isinstance(items, list) or len(items) != report.get("labels_staged"):
            raise ValueError("report count and rows disagree")
        for entry in items:
            file = entry.get("source_file") or entry.get("file")
            label = entry.get("label")
            if (not isinstance(file, str) or not file.startswith("data/maps/")
                    or not isinstance(label, str) or not label):
                raise ValueError("not a source-owned map dialogue")
            owner = (file, label)
            if owner in seen_owners:
                raise ValueError("duplicate prior map/dynamic source owner")
            seen_owners.add(owner)
            path = (root / file).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError("missing or unsafe source text path")
            if file not in sources:
                sources[file] = path.read_text(encoding="utf-8")
            payload = extract_asm_payload(sources[file], label)
            validate_byte_string(payload, label)
            rows.append((file, label, payload, index))
    if not rows:
        raise ValueError("no source-owned map strings to audit")
    by_file = defaultdict(list)
    by_payload = defaultdict(list)
    for file, label, payload, origin in rows:
        by_file[(file, payload)].append(label)
        by_payload[payload].append((file, label))
    same_file = []
    for (file, payload), labels in sorted(
        by_file.items(), key=lambda item: (item[0][0], item[0][1])):
        if len(labels) < 2:
            continue
        same_file.append({
            "source_file": file,
            "label_count": len(labels),
            "source_labels": sorted(labels),
            "payload_size_bytes": len(payload),
            "encoded_sha256": hashlib.sha256(payload).hexdigest(),
            "theoretical_removed_duplicate_bytes": (len(labels)-1)*len(payload),
        })
    cross_file = [
        {"file_count": len({f for f, _ in owners}),
         "label_count": len(owners),
         "encoded_sha256": hashlib.sha256(payload).hexdigest(),
         "payload_size_bytes": len(payload)}
        for payload, owners in by_payload.items()
        if len({f for f, _ in owners}) > 1
    ]
    cross_file.sort(key=lambda x: (-x["label_count"], x["encoded_sha256"]))
    return {
        "schema_version": 1,
        "source_owned_map_labels_checked": len(rows),
        "applied_reports_checked": len(reports),
        "same_file_exact_duplicate_groups": len(same_file),
        "same_file_duplicate_label_count": sum(x["label_count"]-1 for x in same_file),
        "same_file_theoretical_duplicate_payload_bytes": sum(
            x["theoretical_removed_duplicate_bytes"] for x in same_file),
        "cross_file_exact_duplicate_groups": len(cross_file),
        "same_file_groups": same_file,
        "cross_file_groups": cross_file,
        "pointer_references_or_layout_safety_proven": False,
        "actual_linker_bytes_reclaimed": 0,
        "ROM_data_or_font_modified": False,
        "experimental_aliasing_permitted": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--report", type=Path, action="append", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in a.report]
    result = audit_duplicate_payloads(a.workspace, reports)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("same_file_groups", "cross_file_groups")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
