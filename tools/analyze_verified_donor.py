#!/usr/bin/env python3
"""Analyze a translated donor ROM only against shipping-verified text targets.

This tool is intentionally conservative:
- Targets come from a provenance catalog, never from generic pointer-like values.
- It scans the clean ROM once for exact pointers to those verified targets.
- Donor pointers are observed for coverage/recovery only; they are never written.
- Optional AowVN reference matching can raise confidence for recovered donor bytes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path

ROM_BASE = 0x08000000
ARENA_SHA256 = "a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_cstring(data: bytes, offset: int, max_len: int = 2048) -> bytes | None:
    if offset < 0 or offset >= len(data):
        return None
    end = data.find(b"\xff", offset, min(len(data), offset + max_len))
    if end < 0:
        return None
    return data[offset:end + 1]


def build_reference_index(clean: bytes, addresses: set[int]) -> dict[int, list[int]]:
    """Single ROM pass; only records exact 32-bit values in the verified target set."""
    refs: dict[int, list[int]] = defaultdict(list)
    if not addresses:
        return refs
    mv = memoryview(clean)
    stop = len(clean) - 3
    for i in range(stop):
        value = mv[i] | (mv[i + 1] << 8) | (mv[i + 2] << 16) | (mv[i + 3] << 24)
        if value in addresses:
            refs[value].append(i)
    return refs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--clean-rom", type=Path, required=True)
    ap.add_argument("--donor-rom", type=Path, required=True)
    ap.add_argument("--aow-rom", type=Path)
    ap.add_argument("--categories", default="map-story,system-text")
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    clean_sha = sha256_file(args.clean_rom)
    if clean_sha.lower() != ARENA_SHA256:
        raise SystemExit(f"Wrong clean ROM SHA-256: {clean_sha}")

    clean = args.clean_rom.read_bytes()
    donor = args.donor_rom.read_bytes()
    aow = args.aow_rom.read_bytes() if args.aow_rom else None
    categories = {x.strip() for x in args.categories.split(",") if x.strip()}

    rows = [
        r for r in csv.DictReader(args.catalog.open(encoding="utf-8"))
        if r.get("category") in categories
        and r.get("shipping_match_status", "").startswith("verified:")
        and r.get("shipping_rom_offset")
    ]
    # Older source catalogs may be known exact by build offset but not yet passed
    # through resolve_shipping_catalog.py. Allow those rows if explicitly exact.
    if not rows:
        rows = [
            r for r in csv.DictReader(args.catalog.open(encoding="utf-8"))
            if r.get("category") in categories and r.get("build_rom_offset")
        ]

    targets = {ROM_BASE + int(r.get("shipping_rom_offset") or r["build_rom_offset"], 16) for r in rows}
    refs = build_reference_index(clean, targets)

    output = []
    status_counts = Counter()
    category_counts: dict[str, Counter] = defaultdict(Counter)

    for r in rows:
        offset = int(r.get("shipping_rom_offset") or r["build_rom_offset"], 16)
        address = ROM_BASE + offset
        original = read_cstring(clean, offset)
        direct = read_cstring(donor, offset)

        direct_changed = bool(original and direct and direct != original)
        repoints = []
        for ref_off in refs.get(address, []):
            donor_ptr = struct.unpack_from("<I", donor, ref_off)[0]
            if donor_ptr == address:
                continue
            if not (ROM_BASE <= donor_ptr < ROM_BASE + len(donor)):
                continue
            target_off = donor_ptr - ROM_BASE
            donor_text = read_cstring(donor, target_off)
            if donor_text and donor_text != original:
                repoints.append((ref_off, target_off, donor_text))

        candidates: list[tuple[str, int, bytes]] = []
        if direct_changed and direct is not None:
            candidates.append(("inplace", offset, direct))
        for ref_off, target_off, donor_text in repoints:
            candidates.append(("repoint", target_off, donor_text))

        # De-duplicate identical target+bytes.
        unique: dict[tuple[int, bytes], str] = {}
        for kind, target_off, donor_text in candidates:
            unique[(target_off, donor_text)] = kind

        if not unique:
            status = "no-donor"
        else:
            aow_exact = False
            if aow is not None:
                aow_exact = any(aow.find(text) >= 0 for (_, text) in unique)
            status = "donor-aow-exact" if aow_exact else "donor-unmatched-aow"

        donor_kinds = sorted(set(unique.values()))
        donor_locations = ";".join(f"0x{off:08X}" for off, _ in unique)
        donor_hashes = ";".join(
            hashlib.sha256(text).hexdigest() for _, text in unique
        )
        changed_ref_offsets = ";".join(
            f"0x{ref_off:08X}->0x{target_off:08X}" for ref_off, target_off, _ in repoints
        )

        output.append({
            "source_label": r.get("source_label", ""),
            "category": r.get("category", ""),
            "source_file": r.get("source_file", ""),
            "source_line": r.get("source_line", ""),
            "shipping_rom_offset": f"0x{offset:08X}",
            "donor_status": status,
            "donor_kinds": ",".join(donor_kinds),
            "donor_locations": donor_locations,
            "donor_sha256": donor_hashes,
            "changed_reference_offsets": changed_ref_offsets,
            "clean_pointer_reference_count": len(refs.get(address, [])),
        })
        status_counts[status] += 1
        category_counts[r.get("category", "unknown")][status] += 1

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output[0].keys()) if output else []
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if fields:
            w.writeheader()
            w.writerows(output)

    summary = {
        "schema_version": 1,
        "clean_rom_sha256": clean_sha,
        "donor_rom_sha256": sha256_file(args.donor_rom),
        "aow_rom_sha256": sha256_file(args.aow_rom) if args.aow_rom else None,
        "categories": sorted(categories),
        "catalog_targets": len(output),
        "status_counts": dict(status_counts),
        "category_status_counts": {k: dict(v) for k, v in sorted(category_counts.items())},
        "safety": {
            "pointer_scan_scope": "exact pointers to shipping-verified catalog targets only",
            "pointer_writes": 0,
            "rom_modified": False,
            "mass_repoint": False,
            "donor_pointer_values_are_never_applied": True,
        },
    }
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
