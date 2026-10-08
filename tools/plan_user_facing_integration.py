#!/usr/bin/env python3
"""Plan safe integration for every user-facing translation row.

This tool never modifies a ROM. It reconciles the authoritative source catalog
against all translation manifests, then reports which rows already have a
verified shipping ROM offset and which still require shipping-layout
resolution before any binary integration can be attempted.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

USER_FACING = ("map-story", "arena-only", "system-text", "system-ui", "battle")


def identity(row: dict[str, str]) -> str:
    return f'{row.get("source_label","")}@@{row.get("source_file","")}:{row.get("source_line","")}'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--translations", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    with args.catalog.open(encoding="utf-8", newline="") as f:
        all_rows = list(csv.DictReader(f))
    rows = [r for r in all_rows if r.get("category") in USER_FACING]

    by_identity = {identity(r): r for r in rows}
    by_label: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        by_label[r.get("source_label", "")].append(r)

    translated: dict[str, str] = {}
    owner: dict[str, str] = {}
    unresolved_keys: list[dict[str, object]] = []
    duplicate_rows: list[dict[str, str]] = []

    for path in sorted(args.translations.rglob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        manifest_scope = doc.get("scope")
        if manifest_scope not in USER_FACING:
            continue
        translations = doc.get("translations")
        if not isinstance(translations, dict):
            continue
        for key, text in translations.items():
            row = by_identity.get(key)
            if row is None:
                candidates = by_label.get(key, [])
                if len(candidates) == 1:
                    row = candidates[0]
                else:
                    unresolved_keys.append({
                        "manifest": str(path),
                        "key": key,
                        "candidate_count": len(candidates),
                    })
                    continue
            if row.get("category") != manifest_scope:
                unresolved_keys.append({
                    "manifest": str(path),
                    "key": key,
                    "reason": "scope-mismatch",
                    "manifest_scope": manifest_scope,
                    "catalog_category": row.get("category", ""),
                })
                continue
            row_id = identity(row)
            if row_id in translated:
                duplicate_rows.append({
                    "identity": row_id,
                    "first_manifest": owner[row_id],
                    "duplicate_manifest": str(path),
                })
                continue
            translated[row_id] = text
            owner[row_id] = str(path)

    missing = [r for r in rows if identity(r) not in translated]
    if unresolved_keys or duplicate_rows or missing:
        raise SystemExit(
            "coverage mismatch: "
            f"rows={len(rows)} translated={len(translated)} "
            f"unresolved_keys={len(unresolved_keys)} "
            f"duplicates={len(duplicate_rows)} missing={len(missing)}"
        )

    status = Counter()
    category_status: dict[str, Counter] = defaultdict(Counter)
    source_comparison = Counter()
    category_source_comparison: dict[str, Counter] = defaultdict(Counter)
    layout_by_text_status: dict[str, Counter] = defaultdict(Counter)
    plan = []

    for r in rows:
        row_id = identity(r)
        off = r.get("shipping_rom_offset", "")
        match = r.get("shipping_match_status", "")
        if off and match.startswith("verified:"):
            state = "ready:verified-shipping-offset"
        else:
            state = "blocked:needs-shipping-resolution"
        status[state] += 1
        category_status[r.get("category", "")][state] += 1

        # A manifest entry identical to the *English source* is NOT an
        # established no-op on the v0.4 donor. v0.4 could already contain
        # different bytes at that position. Never waive baseline comparison.
        comparison = (
            "source-identical"
            if translated[row_id] == r.get("english", "")
            else "source-changed"
        )
        source_comparison[comparison] += 1
        category_source_comparison[r.get("category", "")][comparison] += 1
        layout_by_text_status[comparison][state] += 1

        plan.append({
            "identity": row_id,
            "source_label": r.get("source_label", ""),
            "category": r.get("category", ""),
            "manifest": owner[row_id],
            "source_file": r.get("source_file", ""),
            "source_line": r.get("source_line", ""),
            "english": r.get("english", ""),
            "vietnamese": translated[row_id],
            "source_text_comparison": comparison,
            "v04_baseline_byte_comparison": "unresolved:requires-exact-v0.4-rom",
            "is_safe_to_skip_binary_write": False,
            "shipping_rom_offset": off,
            "shipping_match_status": match,
            "original_allocation_upper_bound": r.get("original_allocation_upper_bound", ""),
            "reference_count": r.get("reference_count", ""),
            "reference_sites": r.get("reference_sites", ""),
            "catalog_patch_strategy": r.get("patch_strategy", ""),
            "integration_status": state,
            "encoded_fit_status": "unresolved:needs-v0.4-vietnamese-byte-encoding",
            "planned_binary_action": (
                "defer:check-v0.4-baseline-before-skipping-or-restoring-source"
                if comparison == "source-identical"
                else "defer:verify-v0.4-layout-encoding-and-references"
            ),
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "schema_version": 1,
        "catalog_user_facing_rows": len(rows),
        "translation_rows": len(translated),
        "categories": list(USER_FACING),
        "integration_status_counts": dict(status),
        "category_status_counts": {
            k: dict(v) for k, v in sorted(category_status.items())
        },
        "source_text_comparison_counts": dict(source_comparison),
        "category_source_text_comparison_counts": {
            k: dict(v) for k, v in sorted(category_source_comparison.items())
        },
        "shipping_layout_by_source_text_comparison": {
            k: dict(v) for k, v in sorted(layout_by_text_status.items())
        },
        "baseline_rom_byte_comparisons_performed": 0,
        "rows_safe_to_skip_binary_write": 0,
        "excluded_debug_internal_rows": sum(
            1 for r in all_rows if r.get("category") == "debug-internal"
        ),
        "safety": {
            "rom_modified": False,
            "pointer_scan": False,
            "pointer_writes": 0,
            "mass_repoint": False,
            "build_offsets_assumed_shipping_identical": False,
            "source_identical_assumed_v04_identical": False,
            "v04_baseline_bytes_verified": False,
        },
    }
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
