#!/usr/bin/env python3
"""Apply every authored Vietnamese manifest to a pristine Arena source tree.

Source-level only: string literals are rewritten in place and the compiler and
linker re-lay text and references, so no ROM pointer is ever touched. Labels and
`@anon:file:line:col` anchors are located exactly as build_source_text_catalog.py
does, so the tree must be the pinned, not-yet-translated workspace.

A translation is skipped (English kept) and reported when its placeholders do
not match the English source or it uses a character the charmap cannot encode.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from build_source_text_catalog import (ASM_LABEL_RE, ASM_STRING_RE, C_DECL_RE, C_STRING_RE,
                                       decode_source_literal, find_matching_paren,
                                       iter_source_files)
from vietnamese_text_metrics import Metrics

PLACEHOLDER_RE = re.compile(r"\{[^{}]+\}")
# Typography the stock font has no glyph for, mapped to its closest stock character.
FALLBACK = {"—": "-", "–": "-", "°": "º", " ": " ", "\t": " "}
SPLIT_AFTER = re.compile(r"(\\[npl])")


def load_translations(root: Path) -> tuple[dict[str, str], list[str]]:
    merged: dict[str, str] = {}
    conflicts: list[str] = []
    for path in sorted(root.glob("*/*.vi.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for key, value in data.get("translations", {}).items():
            if key in merged and merged[key] != value:
                conflicts.append(key)
                continue
            merged[key] = value
    return merged, conflicts


def charmap_chars(charmap: Path) -> set[str]:
    chars: set[str] = set()
    for line in charmap.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^'(\\?.)'\s*=", line)
        if m:
            chars.add(m.group(1)[-1])
    return chars


def normalise(vi: str, english: str) -> str:
    vi = unicodedata.normalize("NFC", vi).replace("\r\n", "\n")
    # Authoring sometimes stored a real line feed where the source control is \n.
    vi = vi.replace("\n", "\\n")
    for src, dst in FALLBACK.items():
        vi = vi.replace(src, dst)
    if english.endswith("$") and not vi.endswith("$"):
        vi += "$"
    elif not english.endswith("$") and vi.endswith("$"):
        vi = vi[:-1]
    return vi


def problem(vi: str, english: str, chars: set[str]) -> str | None:
    if Counter(PLACEHOLDER_RE.findall(vi)) != Counter(PLACEHOLDER_RE.findall(english)):
        return "placeholder-mismatch"
    plain = PLACEHOLDER_RE.sub("", vi)
    plain = re.sub(r"\\.", "", plain)
    missing = sorted({c for c in plain if c not in chars and c != "$"})
    if missing:
        return "unencodable:" + "".join(missing)
    if vi.count("$") != english.count("$"):
        return "early-terminator"
    return None


# Game terms the project keeps in English; never reduced to an initial.
KEEP_WHOLE = {"HP", "PP", "EXP", "LV", "ID", "PC", "TM", "HM", "CONTEST", "POKéMON", "POKéDEX",
              "POKéNAV", "POKéBLOCK", "BADGE", "TRAINER", "BP", "SP", "ATK", "DEF", "OT"}


# Labels the user wants spelled out: they sit in windows with room to spare.
NEVER_ABBREVIATE = {"THÔNG TIN", "TÙY CHỌN", "VẬT PHẨM", "ÂM THANH", "TỐC ĐỘ"}
NEVER_ABBREVIATE_FILES = {"src/data/text/nature_names.h"}


# Arena's 3x5 HUD lettering only has A-Z, 0-9 and a few signs: accented letters
# silently disappear. The user chose to keep these strings in English.
TINY_HUD_FILES = {"src/arena_capture.inc"}
TINY_HUD_LABELS = {("src/realtime_arena.c", "help"), ("src/realtime_arena.c", "sQualityTabs")}


def abbreviate_label(vi: str, budget: int, metrics) -> str:
    """Project convention for labels that overflow: TẤN CÔNG -> T.CÔNG.

    Only plain all-caps multi-word labels qualify. Words are reduced to their
    initial from the left, one at a time, until the label fits; the last word
    is always kept whole."""
    words = vi.split(" ")
    if len(words) < 2 or any(not w.isalpha() or w != w.upper() for w in words):
        return vi
    short = vi
    for n in range(1, len(words)):
        head = [w + " " if w in KEEP_WHOLE else w[0] + "." for w in words[:n]]
        short = "".join(head) + " ".join(words[n:])
        if metrics.width(short) <= budget:
            break
    return short


def literal_chunks(vi: str) -> list[str]:
    """Split after line/page controls so the source stays readable."""
    parts = SPLIT_AFTER.split(vi)
    chunks, cur = [], ""
    for part in parts:
        cur += part
        if SPLIT_AFTER.fullmatch(part):
            chunks.append(cur)
            cur = ""
    if cur or not chunks:
        chunks.append(cur)
    return [c.replace('"', '\\"') for c in chunks]


def plan_asm(text: str, rel: str):
    """Yield (label, english, first_line, string_line_indexes, indent)."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        lm = ASM_LABEL_RE.match(lines[i])
        if not lm:
            i += 1
            continue
        parts, idx = [], []
        j = i + 1
        while j < len(lines):
            if ASM_LABEL_RE.match(lines[j]):
                break
            sm = ASM_STRING_RE.search(lines[j])
            if sm:
                parts.append(sm.group(1))
                idx.append(j)
                j += 1
                continue
            s = lines[j].strip()
            if not s or s.startswith(("@", "//")):
                j += 1
                continue
            if parts:
                break
            j += 1
        if parts:
            yield lm.group(1), decode_source_literal(parts), idx, i + 1
        i = max(i + 1, j)


def plan_c(text: str, rel: str):
    """Yield (label, english, body_start, body_end) for named and anonymous strings."""
    claimed: set[int] = set()
    for m in C_DECL_RE.finditer(text):
        open_pos = text.find("(", m.start(), m.end())
        close = find_matching_paren(text, open_pos) if open_pos >= 0 else None
        if close is None:
            continue
        parts = C_STRING_RE.findall(text[open_pos + 1:close])
        if not parts:
            continue
        claimed.add(open_pos)
        yield (m.group(1), decode_source_literal(parts), open_pos + 1, close,
               text.count("\n", 0, m.start()) + 1)
    macro_re = re.compile(r"(?:\bCOMPOUND_STRING\s*|(?<![A-Za-z0-9_])_)\(")
    for m in macro_re.finditer(text):
        open_pos = text.find("(", m.start(), m.end())
        if open_pos in claimed:
            continue
        close = find_matching_paren(text, open_pos)
        if close is None:
            continue
        parts = C_STRING_RE.findall(text[open_pos + 1:close])
        if not parts:
            continue
        line = text.count("\n", 0, m.start()) + 1
        column = m.start() - (text.rfind("\n", 0, m.start()) + 1) + 1
        yield f"@anon:{rel}:{line}:{column}", decode_source_literal(parts), open_pos + 1, close, line


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--translations", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--skip-keys", type=Path, help="JSON list of keys to leave in English")
    ap.add_argument("--charmap", type=Path, help="charmap to validate against (default: workspace)")
    ap.add_argument("--sites-out", type=Path, help="write every applied site with its English")
    ap.add_argument("--reflow-width", type=int, default=0,
                    help="re-wrap script dialogue pages whose lines exceed this many pixels")
    ap.add_argument("--abbreviate-labels", action="store_true",
                    help="shorten overflowing all-caps labels as T.CÔNG / P.THỦ (needs --reflow-width)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ws = args.workspace.resolve()
    translations, conflicts = load_translations(args.translations)
    skip = set(json.loads(args.skip_keys.read_text(encoding="utf-8"))) if args.skip_keys else set()
    chars = charmap_chars(args.charmap or ws / "charmap.txt")
    applied: dict[str, str] = {}
    skipped: dict[str, str] = {}
    unchanged = 0
    seen_keys: set[str] = set()
    named_sites: Counter = Counter()
    sites: list[dict] = []
    reflowed = 0
    too_many_lines: dict[str, int] = {}
    tiny_hud_kept_english = 0
    abbreviated: dict[str, list[str]] = {}
    labels_over: dict[str, int] = {}
    metrics = Metrics(ws) if args.reflow_width else None

    for path in sorted(iter_source_files(ws)):
        rel = path.relative_to(ws).as_posix()
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        newline = "\r\n" if "\r\n" in text else "\n"
        edits: list[tuple[int, int, str]] = []  # (start, end, replacement) on `text`
        is_asm = path.suffix.lower() in {".inc", ".s"}
        is_c = path.suffix.lower() in {".c", ".h", ".inc"}

        def want(label: str, english: str, line: int) -> str | None:
            nonlocal unchanged
            # Duplicate labels are keyed in the manifests as label@@file:line.
            key = next((k for k in (f"{label}@@{rel}:{line}", label) if k in translations), None)
            if key is None or key in skip:
                return None
            seen_keys.add(key)
            vi = normalise(translations[key], english)
            if vi == english:
                unchanged += 1
                return None
            why = problem(vi, english, chars)
            if why:
                skipped[f"{rel}::{label}"] = why
                return None
            return vi

        if is_asm:
            lines = text.splitlines(keepends=True)
            offsets, pos = [], 0
            for ln in lines:
                offsets.append(pos)
                pos += len(ln)
            for label, english, idx, line in plan_asm(text, rel):
                vi = want(label, english, line)
                if vi is None:
                    continue
                if (metrics and rel.startswith("data/")
                        and metrics.widest(vi) > max(args.reflow_width, metrics.widest(english))):
                    vi = metrics.reflow(vi, args.reflow_width)
                    reflowed += 1
                sites.append({"site": f"{rel}::{label}", "kind": "asm", "english": english, "vi": vi})
                first = lines[idx[0]]
                indent = first[:len(first) - len(first.lstrip())]
                block = "".join(f'{indent}.string "{c}"{newline}' for c in literal_chunks(vi))
                edits.append((offsets[idx[0]], offsets[idx[0]] + len(lines[idx[0]]), block))
                for k in idx[1:]:
                    edits.append((offsets[k], offsets[k] + len(lines[k]), ""))
                applied[f"{rel}::{label}"] = vi
                named_sites[label] += 1
        if is_c:
            # Budget for multi-line C text: the widest line the English of this file uses.
            multi = [e for _, e, _, _, _ in plan_c(text, rel) if re.search(r"\\[npl]", e)] if metrics else []
            c_budget = max((metrics.widest(e) for e in multi), default=0)
            c_lines = max((metrics.max_page_lines(e) for e in multi), default=0)
            c_scroll = any("\\p" in e or "\\l" in e for e in multi)
            # Data tables are homogeneous lists drawn in one window: the widest English
            # entry is the budget. Elsewhere each label is held to its own English.
            singles = ([e for _, e, _, _, _ in plan_c(text, rel) if not re.search(r"\\[npl]", e)]
                       if metrics and rel.startswith("src/data/") else [])
            label_budget = max((metrics.width(e) for e in singles), default=0)
            for label, english, start, end, line in plan_c(text, rel):
                vi = want(label, english, line)
                if vi is None:
                    continue
                if metrics and re.search(r"\\[npl]", english) and c_budget:
                    if metrics.widest(vi) > max(c_budget, metrics.widest(english)):
                        vi = metrics.reflow(vi, c_budget, scroll=c_scroll)
                        reflowed += 1
                        if not c_scroll and metrics.max_page_lines(vi) > c_lines:
                            too_many_lines[f"{rel}::{label}"] = metrics.max_page_lines(vi)
                elif (metrics and args.abbreviate_labels and vi not in NEVER_ABBREVIATE
                      and rel not in NEVER_ABBREVIATE_FILES):
                    budget = max(label_budget, metrics.width(english))
                    if metrics.width(vi) > budget:
                        short = abbreviate_label(vi, budget, metrics)
                        if short != vi:
                            abbreviated[f"{rel}::{label}"] = [vi, short]
                            vi = short
                        if metrics.width(vi) > budget:
                            labels_over[f"{rel}::{label}"] = metrics.width(vi) - budget
                if rel in TINY_HUD_FILES or (rel, label) in TINY_HUD_LABELS:
                    tiny_hud_kept_english += 1
                    continue
                sites.append({"site": f"{rel}::{label}", "kind": "c", "english": english, "vi": vi})
                body = text[start:end]
                first_q, last_q = body.find('"'), body.rfind('"')
                literal = " ".join(f'"{c}"' for c in literal_chunks(vi))
                edits.append((start + first_q, start + last_q + 1, literal))
                applied[f"{rel}::{label}"] = vi
                named_sites[label] += 1

        if edits and not args.dry_run:
            edits.sort()
            for (s1, e1, _), (s2, _, _) in zip(edits, edits[1:]):
                if s2 < e1:
                    raise SystemExit(f"{rel}: overlapping edits at {s1}/{s2}")
            for start, end, rep in reversed(edits):
                text = text[:start] + rep + text[end:]
            path.write_bytes(text.encode("utf-8"))

    report = {
        "schema_version": 1,
        "manifest_entries": len(translations),
        "manifest_key_conflicts": sorted(conflicts),
        "applied_sites": len(applied),
        "reflowed_strings": reflowed,
        "fixed_windows_with_too_many_lines": too_many_lines,
        "tiny_hud_strings_kept_english": tiny_hud_kept_english,
        "labels_abbreviated": abbreviated,
        "single_line_strings_still_wider_than_budget": labels_over,
        "identical_to_english": unchanged,
        "skipped": skipped,
        "skip_reasons": dict(Counter(v.split(":")[0] for v in skipped.values())),
        "keys_not_found_in_source": sorted(set(translations) - seen_keys - skip),
        "labels_applied_at_multiple_sites": {k: v for k, v in named_sites.items() if v > 1},
    }
    if args.sites_out:
        args.sites_out.write_text(json.dumps(sites, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: (v if not isinstance(v, (dict, list)) else len(v))
                      for k, v in report.items()}, ensure_ascii=False))
    print("skip reasons:", report["skip_reasons"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
