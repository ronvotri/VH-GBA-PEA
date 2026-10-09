#!/usr/bin/env python3
"""Read-only GBA text-reference opcode provenance. NEVER authorizes ROM writes.

Source-build .sym != authenticated shipping-ROM layout. Even an exact matching
script opcode or data-table word is supporting evidence, not patch approval.
"""
from __future__ import annotations
import argparse, bisect, hashlib, json, re, struct, zipfile
from collections import Counter
from pathlib import Path

CLEAN_SHA = "a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b"
V5_SHA = "575515ff66f640e22b77a38d06395ce3e53a9c459c1e34ab6ebd125f12d34859"
ROM_BASE = 0x08000000


def read_member(path: Path, basename: str) -> bytes:
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist()
                 if n.rsplit("/", 1)[-1] == basename]
        if len(names) != 1:
            raise ValueError(f"Expected one {basename}, got {names}")
        return archive.read(names[0])


def parse_sym(data: bytes):
    rows = []
    for line in data.decode("utf-8", errors="replace").splitlines():
        match = re.match(r"^([0-9A-Fa-f]{8})\s+([A-Za-z])\s+(\S+)", line)
        if match:
            off = int(match.group(1), 16) - ROM_BASE
            if 0 <= off < 0x2000000:
                rows.append((off, match.group(2), match.group(3)))
    return sorted(rows)


def script_opcode_evidence(data: bytes, site: int, owner_start: int,
                           kind: str, symbol_name: str) -> str:
    if not (0 <= site <= len(data) - 4 and 0 <= owner_start < len(data)):
        return "invalid-reference-range"
    if (symbol_name.startswith("gMonFrontPic_")
            or ("_Bg_" in symbol_name and "Tilemap" in symbol_name)):
        return "incidental-graphics-data"
    if kind.lower() == "t":
        return "incidental-executable-code"
    if "_EventScript_" in symbol_name:
        if site >= owner_start + 2 and data[site-2:site] == b"\x0f\x00":
            return "candidate:script-loadword-opcode-0F"
        if data[owner_start] == 0x5c and site-owner_start in (6, 10, 14, 16):
            return "candidate:trainerbattle-opcode-5C"
        return "candidate:event-script-other-command"
    if any(term in symbol_name for term in (
            "Texts", "Messages", "TextGroup", "DescriptionPointers", "HintTexts")):
        if site >= owner_start and (site-owner_start) % 4 == 0:
            return "candidate:aligned-data-pointer-table"
        return "review:unaligned-data-table-site"
    return "review:unknown-data-owner"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", type=Path, required=True)
    parser.add_argument("--test2084", type=Path, required=True)
    parser.add_argument("--qa-zip", type=Path, required=True)
    parser.add_argument("--symbol-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    clean, test = args.clean.read_bytes(), args.test2084.read_bytes()
    for label, binary, digest in [
        ("clean", clean, CLEAN_SHA), ("test2084", test, V5_SHA)
    ]:
        if len(binary) != 0x2000000 or hashlib.sha256(binary).hexdigest() != digest:
            raise SystemExit(f"Unexpected {label} binary: REFUSED")

    flagged = json.loads(read_member(args.qa_zip, "patched-span-interior-references.json"))
    symbols = parse_sym(read_member(args.symbol_zip, "pokeemerald.sym"))
    starts = [s[0] for s in symbols]
    classified = []
    for row in flagged:
        off = int(row["offset"], 16)
        word = struct.pack("<I", ROM_BASE + off)
        cursor = 0
        sites = []
        while True:
            pos = clean.find(word, cursor)
            if pos < 0:
                break
            cursor = pos + 1
            if clean[pos:pos+4] != test[pos:pos+4]:
                continue
            if 0x1f0000 <= pos < off and off-pos <= 0x4000:
                continue  # Previously treated nearby owners
            index = bisect.bisect_right(starts, pos) - 1
            if index < 0:
                continue
            owner_start, kind, name = symbols[index]
            sites.append({
                "literal_site": f"0x{pos:08X}",
                "pointer_value": f"0x{ROM_BASE+off:08X}",
                "symbol": name,
                "symbol_type": kind,
                "symbol_address": f"0x{owner_start:08X}",
                "offset_within_symbol": pos-owner_start,
                "byte_pattern_before_site": clean[max(pos-4, 0):pos].hex(),
                "classification": script_opcode_evidence(
                    clean, pos, owner_start, kind, name),
                "reference_is_exact_clean_and_test2084": True,
                "safe_to_repoint": False
            })
        if sites:
            classified.append({
                "source_label": row["label"], "source_offset": row["offset"],
                "sites": sites, "patch_authorized": False
            })

    tally = Counter(s["classification"] for row in classified for s in row["sites"])
    output = {
        "schema_version": 1,
        "analysis_rom": "clean + older v5-2084; NOT latest guarded ROM",
        "source_symbol_map": "pinned source build, shipping pointer provenance unverified",
        "referenced_source_rows": len(classified),
        "site_classifications": dict(sorted(tally.items())),
        "rom_modified": False,
        "automatic_patch_allowed": False,
        "rows": classified,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps({k:v for k,v in output.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
