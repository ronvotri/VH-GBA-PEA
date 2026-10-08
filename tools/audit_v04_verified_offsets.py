#!/usr/bin/env python3
"""Read-only comparison of exact shipping-verified source text spans in v0.4.

Equal bytes at a verified source offset do NOT prove runtime references in v0.4
still point there. This tool never marks writes/skips safe; it only measures
baseline bytes for a subsequent source-reference-aware integration plan.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from resolve_shipping_catalog import encode_source_text, parse_charmap
from verify_local_rom_baselines import (
    CLEAN_SHA256, V04_SHA256, hash_bytes, verify_bytes
)


def compare_verified_span(
    clean: bytes, v04: bytes, offset: int, encoded_source: bytes
) -> str:
    end = offset + len(encoded_source)
    if offset < 0 or end > len(clean) or end > len(v04):
        return "unresolved:offset-out-of-range"
    if clean[offset:end] != encoded_source:
        return "refused:source-bytes-not-equal-clean-rom"
    if v04[offset:end] == encoded_source:
        return "source-bytes-identical-at-original-offset"
    return "source-bytes-differ-at-original-offset"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--clean-rom", type=Path, required=True)
    ap.add_argument("--v04-rom", type=Path, required=True)
    ap.add_argument("--charmap", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    clean, v04 = args.clean_rom.read_bytes(), args.v04_rom.read_bytes()
    verify_bytes(clean, CLEAN_SHA256, "clean shipping Arena 0.13.0")
    verify_bytes(v04, V04_SHA256, "v0.4 Text Cluster Pass")
    chars, tokens = parse_charmap(args.charmap)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    if not isinstance(plan, list):
        raise SystemExit("REFUSED: plan is not a JSON array")

    status_counts = Counter()
    category_counts: dict[str, Counter] = defaultdict(Counter)
    results = []
    for row in plan:
        identity = row.get("identity", "")
        category = row.get("category", "")
        shipping_off = row.get("shipping_rom_offset", "")
        shipping_match = row.get("shipping_match_status", "")
        if not shipping_off or not shipping_match.startswith("verified:"):
            state = "blocked:shipping-layout-unresolved"
        else:
            source, enc_status = encode_source_text(
                row.get("english", ""), chars, tokens
            )
            if source is None:
                state = f"unresolved:source-encode:{enc_status}"
            else:
                try:
                    off = int(shipping_off, 16)
                except ValueError:
                    state = "refused:invalid-shipping-offset"
                else:
                    state = compare_verified_span(clean, v04, off, source)
        if state.startswith("refused:"):
            raise SystemExit(f"REFUSED: {identity}: {state}")
        status_counts[state] += 1
        category_counts[category][state] += 1
        results.append({
            "identity": identity,
            "category": category,
            "source_text_comparison": row.get("source_text_comparison", ""),
            "shipping_rom_offset": shipping_off,
            "v04_source_offset_byte_status": state,
            "v04_reference_integrity_checked": False,
            "binary_write_or_skip_authorized": False,
        })

    summary = {
        "schema_version": 1,
        "clean_rom_sha256": hash_bytes(clean),
        "v04_rom_sha256": hash_bytes(v04),
        "plan_entries": len(plan),
        "status_counts": dict(status_counts),
        "category_status_counts": {
            k: dict(v) for k, v in sorted(category_counts.items())
        },
        "safe_write_count": 0,
        "safe_skip_count": 0,
        "safety": {
            "rom_modified": False,
            "rom_output_written": False,
            "pointer_scans": 0,
            "pointer_writes": 0,
            "runtime_reference_verification_performed": False,
            "source_offset_byte_equal_not_assumed_safe_to_skip": True,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
