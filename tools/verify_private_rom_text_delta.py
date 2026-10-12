#!/usr/bin/env python3
"""Verify an existing private ROM text-only patch without distributing a ROM.

Inputs are local-only byte files and a JSON list of approved text spans:
  [{"offset":"0x200000", "before_hex":"ABCD", "after_hex":"1234"}]
Span bytes must match the source/target exactly, all *actual* changes must
belong to these spans, byte lengths cannot change, and the protected
startup/title region must not change. Does NOT attest gameplay or font
raster compatibility; ROMs and private font artwork are never uploaded.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from bisect import bisect_right
from pathlib import Path


def verify(source: bytes, target: bytes, spans: list[dict],
           *, protected_prefix: int = 0x1F0000) -> dict:
    if not source or len(source) != len(target):
        raise ValueError("ROM size changed or empty ROM")
    if not 0 <= protected_prefix <= len(source):
        raise ValueError("invalid protected prefix")
    if source[:protected_prefix] != target[:protected_prefix]:
        raise ValueError("protected startup/title region changed")
    normalized = []
    for i, rec in enumerate(spans):
        if not isinstance(rec, dict):
            raise ValueError("non-object text span")
        try:
            raw_off = rec["offset"]
            offset = int(raw_off, 16) if isinstance(raw_off, str) else int(raw_off)
            before = bytes.fromhex(rec["before_hex"])
            after = bytes.fromhex(rec["after_hex"])
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError(f"invalid span record {i}") from exc
        if (offset < protected_prefix or not before
                or len(before) != len(after)
                or offset + len(before) > len(source)):
            raise ValueError(f"out-of-range, resized or protected text span {i}")
        if source[offset:offset + len(before)] != before:
            raise ValueError(f"source original bytes mismatched at span {i}")
        if target[offset:offset + len(after)] != after:
            raise ValueError(f"target translated bytes mismatched at span {i}")
        normalized.append((offset, offset + len(before), before, after))
    normalized.sort()
    for a, b in zip(normalized, normalized[1:]):
        if a[1] > b[0]:
            raise ValueError("overlapping text modifications are forbidden")
    changed = sum(a != b for a, b in zip(source, target))
    allowed = sum(sum(x != y for x, y in zip(before, after))
                  for _, _, before, after in normalized)
    if changed != allowed:
        raise ValueError("non-text bytes changed outside approved ranges")
    # Count references into the interior of changed strings by all 4
    # possible source-pointer alignments, fail closed before declaring safe.
    changed_interiors = sorted(
        (start + 1, end) for start, end, before, after in normalized
        if before != after and end - start > 1
    )
    starts = [start for start, _ in changed_interiors]
    # One linear scan over candidate 32-bit little-endian pointers, not one
    # full-ROM scan per text label (390 labels would be prohibitively slow).
    for p in range(0, len(source) - 3):
        value = int.from_bytes(source[p:p + 4], "little")
        if not 0x08000000 <= value < 0x08000000 + len(source):
            continue
        target_off = value - 0x08000000
        pos = bisect_right(starts, target_off) - 1
        if pos >= 0 and target_off < changed_interiors[pos][1]:
            raise ValueError("potential source ROM pointer into modified text interior")
    return {
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "target_sha256": hashlib.sha256(target).hexdigest(),
        "rom_size": len(source),
        "approved_text_spans": len(normalized),
        "actual_byte_changes": changed,
        "unexpected_byte_changes": 0,
        "title_prefix_unchanged": True,
        "font_banks_attested": False,
        "emulator_QA_passed": False,
        "release_ready": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--patched", type=Path, required=True)
    ap.add_argument("--spans", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--protected-prefix", type=lambda x: int(x, 0),
                    default=0x1F0000)
    a = ap.parse_args()
    records = json.loads(a.spans.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise SystemExit("expected JSON array of private source-owned spans")
    result = verify(a.base.read_bytes(), a.patched.read_bytes(),
                    records, protected_prefix=a.protected_prefix)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
