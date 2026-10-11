#!/usr/bin/env python3
"""Read-only diagnostic: Unicode/glyph blockers in the translated source plan.

This is NOT a glyph generator, font patcher or ROM release attestation.
Counts only visible characters outside literal GBA script controls and
{ENGINE_TOKENS}. Every source owner counts at most once per missing glyph.
"""
from __future__ import annotations
import argparse
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


GBA_NEWLINES = ("n", "l", "p")
PROTECTED_SLOTS = set(range(0x53, 0x5A)) | {0x35}


def validate_codebook(codebook: dict) -> dict[str, int]:
    glyphs = codebook.get("glyph_bytes", {})
    if not isinstance(glyphs, dict) or not glyphs:
        raise ValueError("missing font codebook glyph bytes")
    slots = {}
    for char, raw in glyphs.items():
        if not isinstance(char, str) or len(char) != 1:
            raise ValueError("invalid Unicode glyph key")
        try:
            slot = int(raw, 16)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid codebook byte: {char}") from exc
        if not 0 <= slot < 0xFA or slot in PROTECTED_SLOTS:
            raise ValueError(f"glyph collides with native Pokéblock/control byte: {char}")
        if slot in slots:
            raise ValueError(f"shared glyph slot between {slots[slot]} and {char}")
        slots[slot] = char
    return {char: int(raw, 16) for char, raw in glyphs.items()}


def visible_glyphs(source: str) -> tuple[str, list[str]]:
    """Scan a single .string value. Unknown escapes are separate controls."""
    if not source or not source.endswith("$") or source.count("$") != 1:
        return "", ["malformed GBA text terminator"]
    i = 0
    chars = []
    control_issues = []
    body = source[:-1]
    while i < len(body):
        c = body[i]
        if c == "\\":
            if i + 1 < len(body) and body[i + 1] in GBA_NEWLINES:
                i += 2
                continue
            control_issues.append("unknown GBA backslash control")
            i += 2 if i + 1 < len(body) else 1
        elif c == "{":
            end = body.find("}", i + 1)
            if end < 0 or "{" in body[i + 1:end] or not body[i + 1:end]:
                control_issues.append("unbalanced GBA runtime placeholder")
                i += 1
            else:
                i = end + 1
        elif c == "}":
            control_issues.append("stray GBA close brace")
            i += 1
        elif c in "\r\n\t":
            control_issues.append("literal control whitespace")
            i += 1
        else:
            chars.append(c)
            i += 1
    if unicodedata.normalize("NFC", source) != source:
        control_issues.append("non-NFC authored Unicode")
    return "".join(chars), sorted(set(control_issues))


def summarize(rows: list[dict], glyphs: dict[str, int]) -> dict:
    categories = defaultdict(Counter)
    per_glyph = Counter()
    raw_occurrences = Counter()
    reason_counts = Counter()
    examples = defaultdict(list)
    seen = set()
    blocked = 0
    eligible = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("untrusted source plan row")
        label = row.get("source_label", "")
        file = row.get("source_file", "")
        category = row.get("category", "unknown")
        vi = row.get("vietnamese", "")
        if not isinstance(vi, str) or not isinstance(file, str) or not isinstance(label, str):
            raise ValueError("malformed source plan fields")
        owner = (file, label, str(row.get("source_line", "")))
        if not file or not label:
            continue
        if owner in seen:
            raise ValueError(f"duplicate source owner in glyph report: {owner}")
        seen.add(owner)
        eligible += 1
        visible, issues = visible_glyphs(vi)
        missing = set(visible) - glyphs.keys()
        if missing or issues:
            blocked += 1
            categories[category]["blocked"] += 1
        categories[category]["total"] += 1
        if missing:
            categories[category]["missing_glyph"] += 1
        for ch in missing:
            per_glyph[ch] += 1
            raw_occurrences[ch] += visible.count(ch)
            if len(examples[ch]) < 3:
                examples[ch].append({
                    "source_file": file, "source_label": label,
                    "source_line": str(row.get("source_line", "")),
                    "category": category,
                })
        for issue in issues:
            reason_counts[issue] += 1
    glyph_rows = [{
        "character": ch,
        "unicode_codepoint": f"U+{ord(ch):04X}",
        "rows_blocked": count,
        "instances": raw_occurrences[ch],
        "examples": examples[ch],
    } for ch, count in sorted(
        per_glyph.items(), key=lambda item: (-item[1], ord(item[0]))
    )]
    return {
        "status": "READ_ONLY_GLYPH_INVENTORY_NOT_A_FONT_PATCH",
        "source_plan_distinct_rows": eligible,
        "candidate_rows_with_unsupported_glyph_or_control": blocked,
        "codebook_characters": len(glyphs),
        "glyph_inventory": glyph_rows,
        "total_unique_missing_characters": len(glyph_rows),
        "categories": {k: dict(v) for k, v in sorted(categories.items())},
        "non_glyph_text_issues": dict(reason_counts),
        "native_PKMN_Pokeblock_byte_ranges_reserved": True,
        "synthetic_glyphs_generated": False,
        "v04_approved_font_grafted": False,
        "release_ready": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--codebook", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    if not isinstance(plan, list):
        raise SystemExit("source integration plan must be a JSON row array")
    book = json.loads(a.codebook.read_text(encoding="utf-8"))
    glyphs = validate_codebook(book)
    result = summarize(plan, glyphs)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps({
        key: value for key, value in result.items()
        if key not in ("glyph_inventory", "categories")
    }, ensure_ascii=False, indent=2))
    print("Top missing source glyphs:", [
        (r["character"], r["rows_blocked"])
        for r in result["glyph_inventory"][:20]
    ])


if __name__ == "__main__":
    main()
