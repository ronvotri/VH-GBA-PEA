#!/usr/bin/env python3
"""Plan a non-destructive Latin-glyph relocation for Vietnamese source builds.

A *source-build plan*, not a GBA patch. The original v0.4 replaced three
English Latin glyph slots (f,w,z) with (ấ,ằ,ắ) in selected fonts. This script
assigns those three Vietnamese glyphs previously unassigned code points
0x30..0x32 while keeping the original English letters unchanged. It also
excludes case-ambiguous uppercase Ừ, which shares a donor glyph byte with ừ.
The corresponding glyph transplantation must happen before ROM release.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

RELOCATION = {"ấ": ("f",0xDA,0x30),
              "ằ": ("w",0xEB,0x31),
              "ắ": ("z",0xEE,0x32)}
QUARANTINED={"Ừ"}  # old v0.4 codebook aliases uppercase/lowercase at 0x50
GLYPH_BYTES_PER_CODEPOINT=64


def parse_english_single_byte_occupancy(charmap: str) -> set[int]:
    """Only Latin-mode definitions before the '@ Hiragana' section apply."""
    first=charmap.split("@ Hiragana",1)
    if len(first)!=2:
        raise ValueError("missing pinned English/Japanese charmap boundary")
    used=set()
    for line in first[0].splitlines():
        line=line.split("@",1)[0].strip()
        if not line or "=" not in line:
            continue
        # Some legitimate keys CONTAIN '=', notably the literal '='
        # character ('=' = 35). Split on the final assignment operator,
        # never the equals sign within a quoted character literal.
        value=line.rsplit("=",1)[1].strip()
        # e.g "'f' = DA", "'=' = 35", or "PKMN = 53 54".
        match=re.match(r"([0-9A-Fa-f]{2})(?:\s|$)",value)
        if match:
            used.add(int(match.group(1),16))
    return used


def plan_mapping(glyph_bytes:dict[str,str],charmap:str)->tuple[dict,dict]:
    source={ch:int(byte,16) for ch,byte in glyph_bytes.items()}
    used=parse_english_single_byte_occupancy(charmap)
    intended=set(source.values())
    result=dict(source)
    verified=[]
    for accent,(ascii_char,original_byte,target_byte) in RELOCATION.items():
        if source.get(ascii_char)!=original_byte or source.get(accent)!=original_byte:
            raise ValueError(f"untrusted collision source for {accent}/{ascii_char}")
        if target_byte in used:
            raise ValueError(f"target 0x{target_byte:02X} occupied by pinned charmap")
        if target_byte in intended:
            raise ValueError(f"target 0x{target_byte:02X} occupied by inferred codebook")
        if target_byte>=0xFA:
            raise ValueError("target is an engine control byte")
        result[accent]=target_byte
        verified.append({"accent":accent,"ascii_original":ascii_char,
                         "source_code":f"0x{original_byte:02X}",
                         "reserved_code":f"0x{target_byte:02X}",
                         "glyph_bytes_per_font":GLYPH_BYTES_PER_CODEPOINT})
    for letter in QUARANTINED:
        if letter in result:
            del result[letter]
    reversed_slots=defaultdict(list)
    for letter,byte in result.items():
        reversed_slots[byte].append(letter)
    duplicate={f"0x{byte:02X}":letters for byte,letters in reversed_slots.items()
               if len(letters)>1}
    if duplicate:
        raise ValueError(f"unresolved ambiguous byte mappings: {duplicate}")
    report={
        "schema_version":1,
        "status":"PLAN_ONLY_NO_DONOR_FONT_IMPORTED",
        "source_collision_relocations":verified,
        "quarantined_unsupported_chars":sorted(QUARANTINED),
        "codepoints":len(result),
        "original_english_f_w_z_preserved":all(
            result.get(ch)==code for ch,code in (("f",0xDA),("w",0xEB),("z",0xEE))),
        "codebook_is_byte_injective":True,
        "font_built_or_emulator_tested":False,
        "safe_to_distribute_game_ROM":False,
    }
    return {c:f"0x{v:02X}" for c,v in result.items()},report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--codebook",type=Path,required=True)
    ap.add_argument("--charmap",type=Path,required=True)
    ap.add_argument("--out-codebook",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args()
    original=json.loads(a.codebook.read_text(encoding="utf-8"))
    book,info=plan_mapping(original["glyph_bytes"],
                           a.charmap.read_text(encoding="utf-8"))
    output={
        "schema_version":2,
        "status":"requires glyph relocation; do NOT use with original v0.4 font",
        "source_v04_sha256":original["input_v04_sha256"],
        "glyph_bytes":book,
        "required_relocations":info["source_collision_relocations"],
        "unsupported_chars":info["quarantined_unsupported_chars"],
    }
    a.out_codebook.parent.mkdir(parents=True,exist_ok=True)
    a.out_codebook.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",
                              encoding="utf-8")
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",
                        encoding="utf-8")
    print(json.dumps(info,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
