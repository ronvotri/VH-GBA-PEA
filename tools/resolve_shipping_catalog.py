#!/usr/bin/env python3
"""Resolve source-catalog text against an exact released Arena ROM.

Safety model:
- Never scans/repoints pointer-like values.
- First choice is exact byte equality at the source-build ROM offset.
- A shipping offset is recorded only when the encoded English source bytes
  exactly match the released ROM at that offset.
- No ROM bytes are modified.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_ARENA_SHA256 = "a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def strip_comment(rhs: str) -> str:
    # Charmap comments begin with @ after the byte expression.
    # No supported right-hand byte token itself contains @.
    return rhs.split("@", 1)[0].strip()


def parse_charmap(path: Path) -> tuple[dict[str, bytes], dict[str, bytes]]:
    chars: dict[str, bytes] = {}
    tokens: dict[str, bytes] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("@") or "=" not in line:
            continue
        lhs, rhs = line.split("=", 1)
        lhs = lhs.strip()
        rhs = strip_comment(rhs)
        if not rhs:
            continue
        try:
            payload = bytes(int(x, 16) for x in rhs.split())
        except ValueError:
            continue
        if lhs.startswith("'"):
            try:
                ch = ast.literal_eval(lhs)
            except Exception:
                continue
            if isinstance(ch, str):
                # Keep the first English/Latin mapping when a source character
                # is defined more than once in language-specific sections.
                chars.setdefault(ch, payload)
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", lhs):
            tokens.setdefault(lhs, payload)
    return chars, tokens


def encode_source_text(text: str, chars: dict[str, bytes], tokens: dict[str, bytes]) -> tuple[bytes | None, str]:
    out = bytearray()
    i = 0
    while i < len(text):
        if text.startswith(r"\n", i):
            out.extend(chars.get(r"\n", b"\xFE"))
            i += 2
            continue
        if text.startswith(r"\p", i):
            out.extend(chars.get(r"\p", b"\xFB"))
            i += 2
            continue
        if text.startswith(r"\l", i):
            out.extend(chars.get(r"\l", b"\xFA"))
            i += 2
            continue

        if text[i] == "{":
            close = text.find("}", i + 1)
            if close < 0:
                return None, "unclosed-control"
            inside = text[i + 1:close].strip()
            parts = inside.split()
            if not parts:
                return None, "empty-control"
            head = parts[0]
            if head not in tokens:
                return None, f"unknown-token:{head}"
            out.extend(tokens[head])
            for arg in parts[1:]:
                if arg in tokens:
                    out.extend(tokens[arg])
                    continue
                try:
                    # pokeemerald source control arguments are ordinary source
                    # numbers; decimal by default, 0x... accepted explicitly.
                    value = int(arg, 0)
                except ValueError:
                    return None, f"unknown-arg:{inside}"
                if not 0 <= value <= 0xFF:
                    return None, f"arg-out-of-range:{inside}"
                out.append(value)
            i = close + 1
            continue

        ch = text[i]
        payload = chars.get(ch)
        if payload is None:
            return None, f"unknown-char:U+{ord(ch):04X}"
        out.extend(payload)
        i += 1

    return bytes(out), "ok"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--shipping-rom", type=Path, required=True)
    ap.add_argument("--charmap", type=Path, required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-json", type=Path)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--expected-sha256", default=EXPECTED_ARENA_SHA256)
    args = ap.parse_args()

    actual_sha = sha256_file(args.shipping_rom)
    if actual_sha.lower() != args.expected_sha256.lower():
        raise SystemExit(
            f"Refusing to resolve wrong ROM: got {actual_sha}, expected {args.expected_sha256}"
        )

    rom = args.shipping_rom.read_bytes()
    chars, tokens = parse_charmap(args.charmap)
    rows = list(csv.DictReader(args.catalog.open(encoding="utf-8")))
    if not rows:
        raise SystemExit("Catalog is empty")

    status_counts = Counter()
    category_counts: dict[str, Counter] = defaultdict(Counter)
    encode_errors = Counter()

    for row in rows:
        encoded, enc_status = encode_source_text(row.get("english", ""), chars, tokens)
        category = row.get("category", "unknown")
        row["shipping_rom_offset"] = ""
        if encoded is None:
            status = f"encode-unresolved:{enc_status}"
            encode_errors[enc_status] += 1
        elif not row.get("build_rom_offset"):
            status = "unresolved:no-build-symbol"
        else:
            try:
                offset = int(row["build_rom_offset"], 16)
            except ValueError:
                status = "unresolved:invalid-build-offset"
            else:
                end = offset + len(encoded)
                if 0 <= offset < len(rom) and end <= len(rom) and rom[offset:end] == encoded:
                    row["shipping_rom_offset"] = f"0x{offset:08X}"
                    status = "verified:exact-source-bytes-at-build-offset"
                else:
                    status = "unresolved:build-offset-bytes-differ"

        row["shipping_match_status"] = status
        status_counts[status] += 1
        category_counts[category][status] += 1

    fieldnames = list(rows[0].keys())
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    if args.out_json:
        args.out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "schema_version": 1,
        "shipping_rom_sha256": actual_sha,
        "expected_shipping_sha256": args.expected_sha256,
        "total_entries": len(rows),
        "verified_shipping_entries": status_counts["verified:exact-source-bytes-at-build-offset"],
        "status_counts": dict(status_counts),
        "category_status_counts": {k: dict(v) for k, v in sorted(category_counts.items())},
        "encode_errors": dict(encode_errors.most_common()),
        "safety": {
            "rom_modified": False,
            "pointer_scan": False,
            "pointer_writes": 0,
            "mass_repoint": False,
            "shipping_offset_rule": "record only exact encoded source bytes at the build offset",
        },
    }
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
