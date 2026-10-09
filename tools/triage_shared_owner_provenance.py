#!/usr/bin/env python3
"""Read-only ROM reference provenance triage. NEVER authorizes ROM writes.

Requires exact clean Arena and exact 2084 baseline plus GitHub Actions symbol
artifact and static QA ZIP. Checks four-byte values at all byte alignments,
then classifies the nearest source-build symbol. A matching 32-bit word is NOT
proof of a real pointer. Every potential repair still needs source ownership QA.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import io
import json
import re
import struct
import zipfile
from collections import Counter
from pathlib import Path

CLEAN_SHA = "a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b"
TEST2084_SHA = "575515ff66f640e22b77a38d06395ce3e53a9c459c1e34ab6ebd125f12d34859"
ROM_BASE = 0x08000000
PROTECTED_END = 0x001F0000


def pointer_occurrences(data: bytes, target: int):
    needle = struct.pack("<I", target)
    offset = 0
    while True:
        position = data.find(needle, offset)
        if position < 0:
            return
        yield position
        offset = position + 1


def nearest_symbol(symbols, site):
    index = bisect.bisect_right([s[0] for s in symbols], site) - 1
    return symbols[index] if index >= 0 else None


def classify_symbol(name, kind):
    # Explicitly flag chance four-byte matches inside graphics or executable
    # instructions: these are not authenticated string-pointer references.
    if name.startswith("gMonFrontPic_") or ("_Bg_" in name and "Tilemap" in name):
        return "incidental-graphic-word"
    if kind in ("t", "T"):
        return "incidental-code-word"
    if "_EventScript_" in name or any(
        word in name for word in ("Messages", "Texts", "TextGroup", "DescriptionPointers")
    ):
        return "plausible-named-owner"
    return "needs-source-review"


def read_unique_zip_member(zip_path: Path, ending: str):
    with zipfile.ZipFile(zip_path) as z:
        names = [name for name in z.namelist() if name.endswith(ending)]
        if len(names) != 1:
            raise ValueError(f"Expected exactly one {ending}, got {names}")
        return z.read(names[0])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clean-rom", type=Path, required=True)
    ap.add_argument("--test2084-rom", type=Path, required=True)
    ap.add_argument("--static-qa-zip", type=Path, required=True)
    ap.add_argument("--symbol-artifact", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    clean, donor = a.clean_rom.read_bytes(), a.test2084_rom.read_bytes()
    for name, blob, expected in (
        ("clean", clean, CLEAN_SHA), ("2084", donor, TEST2084_SHA)
    ):
        digest = hashlib.sha256(blob).hexdigest()
        if len(blob) != 0x02000000 or digest != expected:
            raise SystemExit(f"REFUSED: wrong {name} ROM ({digest})")

    flagged = json.loads(read_unique_zip_member(a.static_qa_zip,
                                                "patched-span-interior-references.json"))
    pointer_rows = list(csv.DictReader(io.StringIO(read_unique_zip_member(
        a.static_qa_zip, "pointer-anomalies.csv").decode("utf-8-sig"))))
    protected_sites = {int(r["site"], 16) for r in pointer_rows}
    symbols = []
    for line in read_unique_zip_member(a.symbol_artifact, "pokeemerald.sym").decode(
            "utf-8", errors="replace").splitlines():
        m = re.match(r"^([A-Fa-f0-9]{8})\s+([A-Za-z])\s+(\S+)", line)
        if m:
            at = int(m.group(1), 16) - ROM_BASE
            if 0 <= at < len(clean):
                symbols.append((at, m.group(3), m.group(2)))
    symbols.sort()

    output = []
    for row in flagged:
        offset = int(row["offset"], 16)
        old_sites = list(pointer_occurrences(clean, ROM_BASE + offset))
        unchanged = [site for site in old_sites
                     if struct.unpack_from("<I", donor, site)[0] == ROM_BASE + offset]
        near = [site for site in unchanged if PROTECTED_END <= site < offset
                and offset - site <= 0x4000]
        other = [site for site in unchanged if site not in near]
        evidence = []
        for site in other:
            symbol = nearest_symbol(symbols, site)
            if symbol is None:
                evidence.append({"site": hex(site), "classification": "no-symbol"})
                continue
            at, name, kind = symbol
            evidence.append({"site": hex(site), "symbol": name,
                             "symbol_type": kind, "relative_byte": site-at,
                             "classification": classify_symbol(name, kind)})
        historical_intersections = sorted(set(old_sites) & protected_sites)
        output.append({
            "label": row["label"], "text_offset": row["offset"],
            "clean_original_reference_count": len(old_sites),
            "still_unchanged_reference_count": len(unchanged),
            "near_owner_reference_sites": [hex(site) for site in near],
            "other_reference_symbol_evidence": evidence,
            "historical_repair_sites": [hex(site) for site in historical_intersections],
            "unmodified_original_text_required_for_suffixes": True,
            "safe_to_auto_repoint": False
        })
    tally = Counter(e["classification"] for row in output
                    for e in row["other_reference_symbol_evidence"])
    payload = {"schema_version": 1, "rom_baseline": "test2084 only",
               "total_shared_candidates": len(output),
               "historical_source_repair_sites": len(protected_sites),
               "nonlocal_symbol_classes": dict(tally),
               "rom_modified": False, "write_authorized": 0, "rows": output}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({k:v for k,v in payload.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
