#!/usr/bin/env python3
"""Read-only integrity preflight for the exact Emerald Arena ROM baselines.

This utility never copies or modifies ROM data. It only verifies pinned hashes
and reports structural differences before later, separately reviewed patching.
Do not upload copyrighted ROMs to the public repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

CLEAN_SHA256 = "a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b"
V03_SHA256 = "8234d3945fc6d3a87a9669887a114114904b85c00fd9b3ddd026aaea40d636ec"
V04_SHA256 = "c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9"
TITLE_GUARD_END = 0x1F0000


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compare_bytes(a: bytes, b: bytes) -> dict[str, int | bool]:
    shared = min(len(a), len(b))
    changed = sum(x != y for x, y in zip(a, b))
    return {
        "identical": a == b,
        "shared_length": shared,
        "changed_bytes_in_shared_region": changed,
        "length_difference": len(b) - len(a),
    }


def verify_bytes(data: bytes, expected: str, label: str) -> None:
    actual = hash_bytes(data)
    if actual != expected:
        raise SystemExit(
            f"REFUSED: wrong {label} SHA-256: {actual}; expected {expected}"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clean-rom", type=Path, required=True)
    ap.add_argument("--v04-rom", type=Path, required=True)
    ap.add_argument("--v03-rom", type=Path, default=None)
    ap.add_argument("--summary", type=Path, default=None)
    args = ap.parse_args()

    clean = args.clean_rom.read_bytes()
    v04 = args.v04_rom.read_bytes()
    verify_bytes(clean, CLEAN_SHA256, "clean shipping Arena 0.13.0")
    verify_bytes(v04, V04_SHA256, "v0.4 Text Cluster Pass")

    report = {
        "schema_version": 1,
        "baseline_verified": True,
        "clean_rom": {"sha256": CLEAN_SHA256, "size_bytes": len(clean)},
        "v04_rom": {"sha256": V04_SHA256, "size_bytes": len(v04)},
        "v04_vs_clean": compare_bytes(clean, v04),
        "v03_title_guard_verified": None,
        "title_guard_end_exclusive": f"0x{TITLE_GUARD_END:08X}",
        "safety": {
            "rom_modified": False,
            "rom_output_written": False,
            "pointer_writes": 0,
            "repointing": False,
            "no_shipping_offset_assumptions": True,
        },
    }

    if args.v03_rom is not None:
        v03 = args.v03_rom.read_bytes()
        verify_bytes(v03, V03_SHA256, "v0.3 stable")
        if len(v03) < TITLE_GUARD_END or len(v04) < TITLE_GUARD_END:
            raise SystemExit("REFUSED: ROM shorter than guarded title region")
        intact = v03[:TITLE_GUARD_END] == v04[:TITLE_GUARD_END]
        report["v03_title_guard_verified"] = intact
        report["v03_rom"] = {"sha256": V03_SHA256, "size_bytes": len(v03)}
        if not intact:
            raise SystemExit(
                "REFUSED: v0.4 and v0.3 differ in protected 0x000000-0x1EFFFF region"
            )

    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(output, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
