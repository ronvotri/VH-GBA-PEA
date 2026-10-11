#!/usr/bin/env python3
"""Fail-closed additive QA for source-authored literal-LF NPC scroll messages.

Starts from the 5,556-label compiled source tree, not an older isolated trial.
Literal JSON newlines are first normalized only when the complete English
script-control signature matches. A third visible line can then use native
GBA scroll without changing words or page breaks. NO donor/ROM pointer writes.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from stage_source_map_translations import normalize_authored_linefeeds
from verify_compiled_source_strings import extract_asm_payload, validate_stages

ROOT = Path("artifact")
WORK = Path("literal-lf-scroll-additive-trial")
STAGE = "SOURCE_ADDITIVE_LITERAL_LF_SCROLL_STAGE.json"
ATTEST = "SOURCE_ADDITIVE_LITERAL_LF_SCROLL_ATTESTATION.json"
SYM = "SOURCE_ADDITIVE_LITERAL_LF_SCROLL_FONT.sym"
PREVIOUS_MAP = (
    "SOURCE_LEVEL_VIETNAMESE_PILOT.json",
    "SOURCE_EXPANDED_MAP_STAGE.json",
    "SOURCE_EXPANDED_MAP_LF_STAGE.json",
    "SOURCE_MAP_SCROLL_REFLOW_STAGE.json",
)
OLD_DYNAMIC = "SOURCE_LEVEL_DYNAMIC_PILOT.json"
BASE = 5556


def read(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def signature(s: str) -> list[str]:
    return re.findall(r"\\[npl]", s)


def words(s: str) -> list[str]:
    if not s.endswith("$") or s.count("$") != 1:
        raise ValueError("missing single terminal dollar")
    return re.sub(r"\\[npl]", " ", s[:-1]).split()


def verify_pre() -> None:
    old = [read(f) for f in PREVIOUS_MAP]
    dynamic = read(OLD_DYNAMIC)
    new = read(STAGE)
    parent = read("SOURCE_BATTLE_SCROLL_REFLOW_ATTESTATION.json")
    n = new["labels_staged"]
    assert parent["combined_source_compiled_labels"] == BASE, parent
    assert parent["all_new_ROM_linker_payloads_verified"], parent
    assert new["mode"] == "apply" and new["category"] == "map-story"
    assert new["source_prefix"] == "data/maps/"
    assert 1 <= n <= 1000, ("no additional safely integrated LF-scroll strings", new["skipped_reasons"])
    assert n == len(new["translated"]), new
    assert new["literal_newlines_normalized"] == n, new
    assert new["page_scroll_reflowed_labels"] == n, new

    old_ids: set[tuple[str, str]] = set()
    for report in old:
        assert report["mode"] == "apply"
        assert len(report["translated"]) == report["labels_staged"]
        for row in report["translated"]:
            owner = (row["source_file"], row["label"])
            assert owner not in old_ids, ("old source label duplicate", owner)
            old_ids.add(owner)
    assert new["previously_staged_label_exclusions"] == len(old_ids), new

    assert dynamic["mode"] == "apply"
    assert dynamic["labels_staged"] == len(dynamic["accepted"]), dynamic
    for row in dynamic["accepted"]:
        owner = (row["file"], row["label"])
        assert owner not in old_ids, ("earlier map/dynamic owner overlap", owner)
        old_ids.add(owner)

    new_ids: set[tuple[str, str]] = set()
    for row in new["translated"]:
        owner = (row["source_file"], row["label"])
        assert row["source_file"].startswith("data/maps/"), owner
        assert owner not in old_ids and owner not in new_ids, ("restaged source owner", owner)
        new_ids.add(owner)
        original = row["authored_vietnamese"]
        compiled = row["vietnamese"]
        assert "\n" in original and "\n" not in compiled, owner
        assert row["literal_newlines_normalized"] and row["auto_wrapped"], owner
        assert row["page_scroll_reflowed"], owner
        assert all("{" not in s and "}" not in s for s in (row["english"], original, compiled)), owner
        normalized = normalize_authored_linefeeds(row["english"], original)
        assert signature(row["english"]) == signature(normalized), owner
        assert original.count("$") == compiled.count("$") == 1, owner
        assert words(normalized) == words(compiled), owner
        assert row["english"].count(r"\p") == compiled.count(r"\p"), owner
        assert r"\l" in compiled, owner

    checks = validate_stages(WORK, {"map": new})
    assert checks["checked_unique_source_labels"] == n, checks
    report = {
        "previous_compiled_unique_source_labels": BASE,
        "new_unique_literal_lf_scroll_labels": n,
        "combined_compiled_source_labels": BASE + n,
        "prior_map_and_dynamic_owner_count": len(old_ids),
        "exact_original_english_control_order_checked": True,
        "original_vietnamese_words_and_page_breaks_preserved": True,
        "no_duplicate_previously_compiled_source_owners": True,
        "source_payloads_verified": True,
        "linked_ROM_payloads_verified": False,
        "stock_source_font_only": True,
        "user_approved_v04_font_grafted": False,
        "emulator_gameplay_qa_passed": False,
        "release_ready": False,
    }
    (ROOT / ATTEST).write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("PASS additive source-owned LF-scroll texts", n, "total", BASE+n)


def verify_post() -> None:
    report = read(ATTEST)
    stage = read(STAGE)
    n = stage["labels_staged"]
    assert report["new_unique_literal_lf_scroll_labels"] == n
    rom = (WORK / "pokeemerald.gba").read_bytes()
    sym = (ROOT / SYM).read_text(encoding="utf-8")
    refs: dict[str, list[int]] = {}
    for address, name in re.findall(r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$", sym):
        refs.setdefault(name, []).append(int(address, 16))
    for row in stage["translated"]:
        label = row["label"]
        addresses = refs.get(label, [])
        assert len(addresses) == 1, ("ambiguous linker source label", label, addresses)
        addr = addresses[0]
        assert 0x08000000 <= addr < 0x0A000000, (label, addr)
        payload = extract_asm_payload((WORK / row["source_file"]).read_text(encoding="utf-8"), label)
        pos = addr-0x08000000
        assert pos >= 0 and rom[pos:pos+len(payload)] == payload, ("GBA linker mismatch", label)
    report["linked_ROM_payloads_verified"] = True
    report["exact_GBA_linker_labels_checked"] = n
    (ROOT / ATTEST).write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("PASS linker-addressed GBA bytes for", n, "new literal-LF source labels")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("pre", "post"))
    opts = parser.parse_args()
    if opts.phase == "pre":
        verify_pre()
    else:
        verify_post()
