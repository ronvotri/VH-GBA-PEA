#!/usr/bin/env python3
"""Build a source-provenance text catalog for Pokémon Emerald Arena.

This intentionally does *not* patch or repoint ROM pointers. It scans the built
source tree for named text objects / script strings, joins them to ELF symbols,
and records source-level reference sites. Shipping-ROM addresses stay unresolved
unless a later, explicit resolver proves them.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

ROM_BASE = 0x08000000
ROM_LIMIT = 0x0A000000  # 32 MiB GBA ROM address window
TEXT_EXTS = {".c", ".h", ".inc", ".s", ".S"}
SKIP_PARTS = {".git", "build", "build_tools", "graphics", "sound", "audio", "tools"}

SYM_RE = re.compile(r"^([0-9A-Fa-f]{8})\s+([A-Za-z?])\s+(\S+)$")
ASM_LABEL_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_.$]*):{1,2}\s*(?:@.*)?$")
ASM_STRING_RE = re.compile(r'\.string\s+"((?:\\.|[^"\\])*)"')
C_DECL_RE = re.compile(
    r"\bconst\s+u8\s+([A-Za-z_][A-Za-z0-9_]*)\s*\[[^\]]*\]\s*=\s*(?:_\s*\(|COMPOUND_STRING\s*\()",
    re.MULTILINE,
)
C_STRING_RE = re.compile(r'"((?:\\.|[^"\\])*)"')
IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
HUNK_RE = re.compile(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,(\d+))?\s+@@")


@dataclass
class Symbol:
    address: int
    sym_type: str
    name: str
    next_address: int | None = None


@dataclass
class Entry:
    source_label: str
    source_kind: str
    category: str
    arena_provenance: str
    source_file: str
    source_line: int
    build_address: str
    build_rom_offset: str
    symbol_type: str
    original_allocation_upper_bound: int | None
    allocation_status: str
    english: str
    english_source_chars: int
    control_tokens: str
    reference_count: int
    reference_sites: str
    shipping_rom_offset: str
    shipping_match_status: str
    vietnamese: str
    translation_status: str
    patch_strategy: str
    notes: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_run(args: list[str], cwd: Path | None = None) -> str:
    try:
        p = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, check=False)
    except OSError:
        return ""
    return p.stdout if p.returncode == 0 else ""


def load_symbols(sym_path: Path) -> dict[str, Symbol]:
    by_name: dict[str, Symbol] = {}
    syms: list[Symbol] = []
    for raw in sym_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = SYM_RE.match(raw.strip())
        if not m:
            continue
        addr = int(m.group(1), 16)
        if not (ROM_BASE <= addr < ROM_LIMIT):
            continue
        s = Symbol(addr, m.group(2), m.group(3))
        syms.append(s)
        # Prefer first occurrence for duplicate names; nm order is address-sorted.
        by_name.setdefault(s.name, s)

    unique_addrs = sorted({s.address for s in syms})
    next_for_addr = {a: unique_addrs[i + 1] if i + 1 < len(unique_addrs) else None
                     for i, a in enumerate(unique_addrs)}
    for s in by_name.values():
        s.next_address = next_for_addr.get(s.address)
    return by_name


def iter_source_files(workspace: Path) -> Iterable[Path]:
    for root_name in ("data", "src", "include", "asm"):
        root = workspace / root_name
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix not in TEXT_EXTS:
                continue
            rel_parts = set(p.relative_to(workspace).parts)
            if rel_parts & SKIP_PARTS:
                continue
            yield p


def decode_source_literal(parts: list[str]) -> str:
    # Keep pokeemerald control escapes exactly as source text (\\n, \\p, \\l,
    # placeholders, etc.). Only collapse escaped quote/backslash so CSV is readable.
    raw = "".join(parts)
    raw = raw.replace(r'\"', '"')
    raw = raw.replace(r'\\', '\\')
    return raw


def control_tokens(text: str) -> str:
    toks = re.findall(r"\\(?:n|p|l|[vch]\\h[0-9A-Fa-f]{2}|[A-Za-z]+)|\{[^{}]+\}", text)
    return " ".join(toks)


def category_for(path: str, label: str, provenance: str) -> str:
    low = path.lower()
    ll = label.lower()
    if provenance in {"arena-added", "arena-changed"} and ("arena" in low or "arena" in ll):
        return "arena-only"
    if path.startswith("data/maps/"):
        return "map-story"
    if "battle" in low or ll.startswith("battle") or "battle" in ll:
        return "battle"
    if path.startswith("data/text/"):
        return "system-text"
    if any(x in low for x in ("debug", "test")):
        return "debug-internal"
    if path.startswith(("src/", "data/")):
        return "system-ui"
    return "other"


def changed_line_ranges(workspace: Path) -> tuple[dict[str, list[tuple[int, int]]], set[str]]:
    ranges: dict[str, list[tuple[int, int]]] = defaultdict(list)
    diff = safe_run(["git", "diff", "--unified=0", "--no-color", "HEAD", "--", "data", "src", "include", "asm"], cwd=workspace)
    current: str | None = None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            continue
        m = HUNK_RE.match(line)
        if m and current:
            start = int(m.group(1))
            count = int(m.group(2) or "1")
            if count > 0:
                ranges[current].append((start, start + count - 1))
    untracked_raw = safe_run(["git", "ls-files", "--others", "--exclude-standard", "--", "data", "src", "include", "asm"], cwd=workspace)
    untracked = {x.strip().replace("\\", "/") for x in untracked_raw.splitlines() if x.strip()}
    return ranges, untracked


def provenance_for(rel: str, line: int, ranges: dict[str, list[tuple[int, int]]], untracked: set[str]) -> str:
    if rel in untracked:
        return "arena-added"
    for a, b in ranges.get(rel, ()):
        if a <= line <= b:
            return "arena-changed"
    return "vanilla-base"


def parse_asm_file(path: Path, workspace: Path, symbols: dict[str, Symbol], ranges, untracked) -> list[dict]:
    rel = path.relative_to(workspace).as_posix()
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out: list[dict] = []
    i = 0
    while i < len(lines):
        lm = ASM_LABEL_RE.match(lines[i])
        if not lm:
            i += 1
            continue
        label = lm.group(1)
        start_line = i + 1
        parts: list[str] = []
        j = i + 1
        while j < len(lines):
            if ASM_LABEL_RE.match(lines[j]):
                break
            sm = ASM_STRING_RE.search(lines[j])
            if sm:
                parts.append(sm.group(1))
                j += 1
                continue
            # Allow comments/blank lines inside a text definition, but stop on
            # the first real non-string directive/instruction.
            s = lines[j].strip()
            if not s or s.startswith(("@", "//")):
                j += 1
                continue
            if parts:
                break
            j += 1
        if parts:
            out.append({
                "label": label,
                "kind": "asm-string",
                "file": rel,
                "line": start_line,
                "english": decode_source_literal(parts),
                "provenance": provenance_for(rel, start_line, ranges, untracked),
            })
        i = max(i + 1, j)
    return out


def find_matching_paren(text: str, open_pos: int) -> int | None:
    depth = 0
    in_string = False
    escaped = False
    i = open_pos
    while i < len(text):
        c = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                in_string = False
        else:
            if c == '"':
                in_string = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return None


def parse_c_file(path: Path, workspace: Path, symbols: dict[str, Symbol], ranges, untracked) -> list[dict]:
    rel = path.relative_to(workspace).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    out: list[dict] = []
    claimed_macro_opens: set[int] = set()

    # Named const-u8 string definitions.
    for m in C_DECL_RE.finditer(text):
        label = m.group(1)
        open_pos = text.find("(", m.start(), m.end())
        if open_pos < 0:
            continue
        close = find_matching_paren(text, open_pos)
        if close is None:
            continue
        body = text[open_pos + 1:close]
        parts = C_STRING_RE.findall(body)
        if not parts:
            continue
        line = text.count("\n", 0, m.start()) + 1
        claimed_macro_opens.add(open_pos)
        out.append({
            "label": label,
            "kind": "c-named-string",
            "file": rel,
            "line": line,
            "english": decode_source_literal(parts),
            "provenance": provenance_for(rel, line, ranges, untracked),
        })

    # Anonymous _()/COMPOUND_STRING() strings. Keep them in the catalog because
    # they can be player-facing even when the compiler gives no stable source label.
    macro_re = re.compile(r"(?:\bCOMPOUND_STRING\s*|(?<![A-Za-z0-9_])_)\(")
    for m in macro_re.finditer(text):
        open_pos = text.find("(", m.start(), m.end())
        if open_pos in claimed_macro_opens:
            continue
        close = find_matching_paren(text, open_pos)
        if close is None:
            continue
        body = text[open_pos + 1:close]
        parts = C_STRING_RE.findall(body)
        if not parts:
            continue
        line = text.count("\n", 0, m.start()) + 1
        label = f"@anon:{rel}:{line}"
        out.append({
            "label": label,
            "kind": "c-anonymous-string",
            "file": rel,
            "line": line,
            "english": decode_source_literal(parts),
            "provenance": provenance_for(rel, line, ranges, untracked),
        })
    return out


def collect_reference_sites(files: list[Path], workspace: Path, labels: set[str], definitions: dict[str, tuple[str, int]]) -> tuple[dict[str, list[str]], Counter]:
    refs: dict[str, list[str]] = defaultdict(list)
    counts: Counter = Counter()
    for p in files:
        rel = p.relative_to(workspace).as_posix()
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, 1):
            # Fast reject before tokenization.
            if not any(ch.isalpha() or ch == "_" for ch in line):
                continue
            for token in set(IDENT_RE.findall(line)):
                if token not in labels:
                    continue
                if definitions.get(token) == (rel, lineno):
                    continue
                counts[token] += 1
                if len(refs[token]) < 32:
                    refs[token].append(f"{rel}:{lineno}")
    return refs, counts


def strategy_for(category: str, build_offset: int | None, has_symbol: bool) -> str:
    if build_offset is not None and build_offset < 0x1F0000:
        return "protected-region: source-verify-only"
    if not has_symbol:
        return "unresolved: locate exact compiled bytes first"
    if category == "arena-only":
        return "translate; in-place if fits; verified-reference repoint only if needed"
    return "translate; in-place if fits; verified-reference repoint only if needed"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--sym", type=Path, required=True)
    ap.add_argument("--build-rom", type=Path)
    ap.add_argument("--expected-shipping-sha256", default="a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b")
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    workspace = args.workspace.resolve()
    symbols = load_symbols(args.sym)
    ranges, untracked = changed_line_ranges(workspace)
    files = sorted(iter_source_files(workspace))

    raw_entries: list[dict] = []
    for p in files:
        if p.suffix.lower() in {".inc", ".s"} or p.suffix == ".S":
            raw_entries.extend(parse_asm_file(p, workspace, symbols, ranges, untracked))
        if p.suffix.lower() in {".c", ".h"}:
            raw_entries.extend(parse_c_file(p, workspace, symbols, ranges, untracked))

    # Deduplicate exact same source definitions; preserve same English at different labels.
    seen = set()
    deduped = []
    for e in raw_entries:
        k = (e["label"], e["file"], e["line"], e["english"])
        if k in seen:
            continue
        seen.add(k)
        deduped.append(e)
    raw_entries = deduped

    named_labels = {e["label"] for e in raw_entries if not e["label"].startswith("@anon:")}
    definitions = {e["label"]: (e["file"], e["line"]) for e in raw_entries if e["label"] in named_labels}
    refs, ref_counts = collect_reference_sites(files, workspace, named_labels, definitions)

    entries: list[Entry] = []
    for e in raw_entries:
        label = e["label"]
        sym = symbols.get(label)
        build_offset = sym.address - ROM_BASE if sym else None
        upper = None
        if sym and sym.next_address is not None and sym.next_address > sym.address:
            gap = sym.next_address - sym.address
            # Huge gaps are rarely meaningful as a text allocation bound.
            if 0 < gap <= 0x10000:
                upper = gap
        category = category_for(e["file"], label, e["provenance"])
        ref_list = refs.get(label, [])
        extra_refs = ref_counts.get(label, 0) - len(ref_list)
        ref_text = "; ".join(ref_list)
        if extra_refs > 0:
            ref_text += f"; … +{extra_refs} more"
        entries.append(Entry(
            source_label=label,
            source_kind=e["kind"],
            category=category,
            arena_provenance=e["provenance"],
            source_file=e["file"],
            source_line=e["line"],
            build_address=(f"0x{sym.address:08X}" if sym else ""),
            build_rom_offset=(f"0x{build_offset:08X}" if build_offset is not None else ""),
            symbol_type=(sym.sym_type if sym else ""),
            original_allocation_upper_bound=upper,
            allocation_status=("next-symbol upper bound" if upper is not None else "unresolved"),
            english=e["english"],
            english_source_chars=len(e["english"]),
            control_tokens=control_tokens(e["english"]),
            reference_count=int(ref_counts.get(label, 0)),
            reference_sites=ref_text,
            shipping_rom_offset="",
            shipping_match_status="unresolved: build hash/layout must not be assumed shipping-identical",
            vietnamese="",
            translation_status="untranslated/cataloged",
            patch_strategy=strategy_for(category, build_offset, sym is not None),
            notes="",
        ))

    # Stable order: user-facing map/story first, then Arena-touched, then by source.
    cat_rank = {"map-story": 0, "arena-only": 1, "system-text": 2, "system-ui": 3, "battle": 4, "other": 5, "debug-internal": 9}
    prov_rank = {"arena-added": 0, "arena-changed": 1, "vanilla-base": 2}
    entries.sort(key=lambda x: (cat_rank.get(x.category, 8), prov_rank.get(x.arena_provenance, 9), x.source_file, x.source_line, x.source_label))

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(Entry.__dataclass_fields__.keys())
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for e in entries:
            w.writerow(asdict(e))
    args.out_json.write_text(json.dumps([asdict(e) for e in entries], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    build_sha = sha256_file(args.build_rom) if args.build_rom and args.build_rom.exists() else None
    summary = {
        "schema_version": 1,
        "total_entries": len(entries),
        "named_entries": sum(not e.source_label.startswith("@anon:") for e in entries),
        "anonymous_entries": sum(e.source_label.startswith("@anon:") for e in entries),
        "symbol_mapped_entries": sum(bool(e.build_address) for e in entries),
        "entries_with_source_references": sum(e.reference_count > 0 for e in entries),
        "category_counts": dict(Counter(e.category for e in entries)),
        "arena_provenance_counts": dict(Counter(e.arena_provenance for e in entries)),
        "build_rom_sha256": build_sha,
        "expected_shipping_sha256": args.expected_shipping_sha256,
        "build_matches_expected_shipping": (build_sha == args.expected_shipping_sha256) if build_sha else None,
        "safety": {
            "mass_repoint": False,
            "shipping_offsets_assumed_from_build": False,
            "pointer_writes_performed": 0,
            "note": "Catalog only. Build addresses are provenance hints; shipping ROM offsets remain unresolved until exact byte/source alignment is proven."
        },
    }
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
