#!/usr/bin/env python3
"""Read-only ELF32 + GBA internal-gap inventory, NOT a ROM-space allocator.

PT_LOAD file-backed intervals are linker evidence for *coverage*, not proof
that bytes between those intervals can be overwritten. Unreferenced tables,
fixed-address overlays, emulator quirks, or custom Arena loaders may still
read gap bytes. Never use this audit to move symbols or create pointers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_source_rom_headroom import (
    GBA_BASE, MAX_ROM_SIZE, loadable_rom_segments,
)


def audit_internal_gaps(elf: bytes, rom: bytes, min_report_bytes: int = 64) -> dict:
    if len(rom) != MAX_ROM_SIZE:
        raise ValueError("expected exactly 32MiB padded GBA source image")
    if not 0 <= min_report_bytes <= MAX_ROM_SIZE:
        raise ValueError("invalid gap reporting threshold")

    segments = sorted(loadable_rom_segments(elf), key=lambda r: r["lma"])
    ranges = []
    cursor = 0
    covered = 0
    gaps = []
    for seg in segments:
        start = seg["lma"] - GBA_BASE
        end = seg["end_offset"]
        if start < cursor:
            raise ValueError("overlapping linker PT_LOAD intervals")
        if end <= start or end > MAX_ROM_SIZE:
            raise ValueError("invalid linker-backed ROM interval")
        ranges.append({
            "elf_segment_index": seg["segment"],
            "start_rom_offset": hex(start),
            "end_rom_offset_exclusive": hex(end),
            "file_backed_bytes": end - start,
        })
        if start > cursor:
            blob = rom[cursor:start]
            length = start - cursor
            ff_count = blob.count(0xFF)
            zero_count = blob.count(0)
            if ff_count == length:
                kind = "all_ff"
            elif zero_count == length:
                kind = "all_zero"
            else:
                kind = "mixed_or_other"
            gaps.append({
                "start_rom_offset": hex(cursor),
                "end_rom_offset_exclusive": hex(start),
                "length_bytes": length,
                "all_ff_bytes": ff_count,
                "all_zero_bytes": zero_count,
                "byte_class": kind,
                "ELF_uncovered_only_not_proven_free": True,
            })
        cursor = end
        covered += end - start

    # The region from the last linker interval to 0x02000000 GBA bytes is
    # already accounted for by the separate contiguous-headroom guard.
    inside_gap_bytes = sum(g["length_bytes"] for g in gaps)
    if covered + inside_gap_bytes != cursor:
        raise ValueError("ELF interval accounting mismatch")
    tail = MAX_ROM_SIZE - cursor
    if tail < 0:
        raise ValueError("ELF linker high water exceeds ROM")
    ranked = sorted(gaps, key=lambda g: (-g["length_bytes"], g["start_rom_offset"]))
    return {
        "schema_version": 1,
        "source_ROM_sha256": hashlib.sha256(rom).hexdigest(),
        "ELF_sha256": hashlib.sha256(elf).hexdigest(),
        "total_ROM_capacity_bytes": MAX_ROM_SIZE,
        "linker_file_backed_bytes": covered,
        "linker_high_water_bytes": cursor,
        "linker_contiguous_tail_headroom_bytes": tail,
        "ELF_uncovered_internal_gap_count": len(gaps),
        "ELF_uncovered_internal_bytes": inside_gap_bytes,
        "internal_gaps_all_ff_bytes": sum(
            g["length_bytes"] for g in gaps if g["byte_class"] == "all_ff"),
        "internal_gaps_all_zero_bytes": sum(
            g["length_bytes"] for g in gaps if g["byte_class"] == "all_zero"),
        "internal_gaps_mixed_or_other_bytes": sum(
            g["length_bytes"] for g in gaps if g["byte_class"] == "mixed_or_other"),
        "ELF_file_backed_segments": ranges,
        "internal_gaps": [g for g in ranked if g["length_bytes"] >= min_report_bytes],
        "minimum_reported_gap_bytes": min_report_bytes,
        "accounting_exact": covered + inside_gap_bytes + tail == MAX_ROM_SIZE,
        "proved_safe_reclaimable_bytes": 0,
        "pointer_or_symbol_changes": 0,
        "ROM_or_font_modified": False,
        "uncovered_means_unreferenced": False,
        "automatic_gap_insertion_permitted": False,
        "emulator_or_gameplay_verified": False,
        "release_ready": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--min-report-bytes", type=int, default=64)
    args = parser.parse_args()
    report = audit_internal_gaps(
        args.elf.read_bytes(), args.rom.read_bytes(), args.min_report_bytes)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        k: v for k, v in report.items() if k not in (
            "ELF_file_backed_segments", "internal_gaps")},
        ensure_ascii=False, indent=2))
    print("Largest ELF-uncovered internal spans (NOT automatically writable):")
    for item in report["internal_gaps"][:10]:
        print(item["start_rom_offset"], item["length_bytes"], item["byte_class"])


if __name__ == "__main__":
    main()
