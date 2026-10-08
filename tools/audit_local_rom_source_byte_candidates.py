#!/usr/bin/env python3
"""Read-only clean/v0.4 ROM audit at attested and source-byte-exact build offsets.

An exact English byte match at a build offset is only a *candidate* shipping
location, never permission to repoint, patch or skip a v0.4 translation.
Requires the full upstream pinned pret charmap, not a hand-built partial map.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from resolve_shipping_catalog import encode_source_text, parse_charmap
from verify_local_rom_baselines import CLEAN_SHA256, V04_SHA256, verify_bytes

CATEGORIES = {"map-story", "system-text", "system-ui", "battle", "arena-only"}


def assess(row: dict[str, str], clean: bytes, v04: bytes,
           chars: dict[str, bytes], tokens: dict[str, bytes]) -> dict:
    """Classify one source row without granting a binary write or skip."""
    verified = bool(
        row.get("shipping_rom_offset")
        and row.get("shipping_match_status", "").startswith("verified:")
    )
    offset_text = row.get("shipping_rom_offset") if verified else row.get("build_rom_offset", "")
    base = {
        "identity": (
            f'{row.get("source_label", "")}@@'
            f'{row.get("source_file", "")}:{row.get("source_line", "")}'
        ),
        "category": row.get("category", ""),
        "offset_origin": "checkpoint-attested" if verified else "source-build-candidate",
        "offset": offset_text or "",
        "source_byte_status": "unresolved",
        "v04_at_offset": "unresolved",
        "encoded_source_length": None,
        "runtime_reference_verified": False,
        "binary_write_authorized": False,
        "binary_skip_authorized": False,
    }
    if not offset_text:
        base["source_byte_status"] = "blocked:no-offset"
        return base

    encoded, encode_status = encode_source_text(row.get("english", ""), chars, tokens)
    if encoded is None:
        base["source_byte_status"] = "blocked:english-encode:" + encode_status
        if verified:
            raise ValueError(base["identity"] + ": attested row cannot encode English")
        return base
    if not encoded:
        base["source_byte_status"] = "blocked:zero-byte-source"
        return base
    try:
        if not offset_text.lower().startswith("0x"):
            raise ValueError("offset is not hexadecimal with 0x prefix")
        off = int(offset_text, 16)
    except ValueError:
        base["source_byte_status"] = "blocked:invalid-offset"
        if verified:
            raise ValueError(base["identity"] + ": invalid attested offset")
        return base
    if off < 0 or off + len(encoded) > len(clean) or off + len(encoded) > len(v04):
        base["source_byte_status"] = "blocked:out-of-ROM"
        if verified:
            raise ValueError(base["identity"] + ": attested offset is out of ROM")
        return base

    if clean[off:off + len(encoded)] != encoded:
        base["source_byte_status"] = "blocked:source-bytes-differ"
        if verified:
            raise ValueError(base["identity"] + ": exact shipping checkpoint contradicted by clean ROM")
        return base

    base["encoded_source_length"] = len(encoded)
    base["source_byte_status"] = (
        "checkpoint-attested" if verified else "candidate:byte-exact-at-build-offset"
    )
    base["v04_at_offset"] = (
        "source-identical" if v04[off:off + len(encoded)] == encoded
        else "source-different"
    )
    return base


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--clean-rom", type=Path, required=True)
    ap.add_argument("--v04-rom", type=Path, required=True)
    ap.add_argument("--charmap", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    clean, v04 = args.clean_rom.read_bytes(), args.v04_rom.read_bytes()
    verify_bytes(clean, CLEAN_SHA256, "clean shipping Arena 0.13.0")
    verify_bytes(v04, V04_SHA256, "Vietnamese v0.4")
    chars, tokens = parse_charmap(args.charmap)
    with args.catalog.open(newline="", encoding="utf-8") as f:
        source = [r for r in csv.DictReader(f) if r.get("category") in CATEGORIES]
    identities = [
        f'{r.get("source_label", "")}@@{r.get("source_file", "")}:{r.get("source_line", "")}'
        for r in source
    ]
    if len(set(identities)) != len(identities):
        raise SystemExit("REFUSED: duplicate source catalog identities")
    detail = [assess(r, clean, v04, chars, tokens) for r in source]
    counts = Counter(r["source_byte_status"] for r in detail)
    by_category: dict[str, Counter] = defaultdict(Counter)
    by_v04 = Counter()
    for row in detail:
        by_category[row["category"]][row["source_byte_status"]] += 1
        if row["v04_at_offset"] != "unresolved":
            by_v04[row["v04_at_offset"]] += 1
    report = {
        "schema_version": 1,
        "user_facing_rows": len(detail),
        "status_counts": dict(counts),
        "category_status_counts": {c: dict(v) for c, v in sorted(by_category.items())},
        "v04_byte_counts_at_matched_offsets": dict(by_v04),
        "first_0x1F0000_bytes_clean_equal_to_v04": clean[:0x1F0000] == v04[:0x1F0000],
        "runtime_reference_verified_rows": 0,
        "write_authorized_rows": 0,
        "skip_authorized_rows": 0,
        "safety": {
            "source_build_offset_exact_match_is_only_candidate": True,
            "v04_source_identity_is_not_safe_noop": True,
            "rom_modified": False,
            "pointer_writes": 0,
            "mass_repoint": False,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.summary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
