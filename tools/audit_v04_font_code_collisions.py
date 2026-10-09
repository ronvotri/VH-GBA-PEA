#!/usr/bin/env python3
"""Detect stock-English/Vietnamese glyph slot collisions BEFORE a ROM font graft.

Read-only, SHA-locked comparison of private clean Arena and Vietnamese v0.4.
A ROM can build successfully while English letters render as Vietnamese accents
because the v0.4 font repurposes their identical one-byte glyph indices.
NEVER treat a successful font block copy as proof of bilingual safety.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from import_v04_glyphs_into_source_build import (
    ATTESTED_CLEAN_OFFSETS,
    CLEAN_SHA256,
    FONT_NAMES,
    GLYPH_BLOCK_SIZE,
    ROM_BYTES,
    V04_SHA256,
    checked_rom,
)

CHAR_GLYPH_BYTES=64
ORIGINAL_ENGLISH_RE = re.compile(r"""^'([^']+)'\s*=\s*([0-9A-Fa-f]{2})\s*(?:@.*)?$""")


def original_ascii_letters(charmap: str) -> dict[str, int]:
    """Restrict to the English map before Japanese repeats its byte values."""
    english=charmap.split("@ Hiragana",1)[0]
    letters={}
    for line in english.splitlines():
        match=ORIGINAL_ENGLISH_RE.match(line.strip())
        if match and len(match.group(1))==1 and match.group(1).isascii() and match.group(1).isalpha():
            letters[match.group(1)]=int(match.group(2),16)
    if set("fwz") - set(letters):
        raise ValueError("not the expected pinned Hoenn English charmap")
    return letters


def font_slot_changes(clean: bytes, donor: bytes, code: int,
                      offsets: dict[str,int]) -> dict[str,int]:
    if not 0<=code<0xFA:
        raise ValueError("glyph index collides with text control range")
    counts={}
    for name in FONT_NAMES:
        base=offsets[name]+code*CHAR_GLYPH_BYTES
        if base<0 or base+CHAR_GLYPH_BYTES>len(clean) or base+CHAR_GLYPH_BYTES>len(donor):
            raise ValueError("glyph span out of range")
        counts[name]=sum(x!=y for x,y in zip(clean[base:base+CHAR_GLYPH_BYTES],
                                             donor[base:base+CHAR_GLYPH_BYTES]))
    return counts


def collision_report(clean:bytes,donor:bytes,
                     codebook:dict[str,int],charmap:str,
                     offsets:dict[str,int]=ATTESTED_CLEAN_OFFSETS) -> dict:
    if len(clean)!=len(donor) or len(clean)!=ROM_BYTES:
        raise ValueError("unexpected source ROM size")
    ascii_codes=original_ascii_letters(charmap)
    original_by_byte=defaultdict(list)
    for letter,index in ascii_codes.items():
        original_by_byte[index].append(letter)
    vi_by_byte=defaultdict(list)
    for letter,index in codebook.items():
        vi_by_byte[index].append(letter)
    collisions=[]
    for code,letters in sorted(original_by_byte.items()):
        nonascii=[ch for ch in vi_by_byte.get(code,[]) if ch not in letters]
        if nonascii:
            collisions.append({
                "slot":f"0x{code:02X}",
                "original_english_ascii":letters,
                "translated_codebook_letters":nonascii,
                "glyph_donor_change_bytes":font_slot_changes(clean,donor,code,offsets),
            })
    ambiguous=[{"slot":f"0x{code:02X}","labels":labels}
               for code,labels in sorted(vi_by_byte.items()) if
               len([ch for ch in labels if ord(ch)>127])>1]
    return {
        "schema_version":1,
        "stock_ascii_collisions":collisions,
        "ambiguous_vietnamese_duplicate_slots":ambiguous,
        "has_english_rendering_hazard":any(
            any(x["glyph_donor_change_bytes"].values()) for x in collisions),
        "read_only":True,
        "auto_patch_authorized":False,
        "visual_emulator_validation_complete":False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clean",type=Path,required=True)
    ap.add_argument("--v04",type=Path,required=True)
    ap.add_argument("--codebook",type=Path,required=True)
    ap.add_argument("--charmap",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    clean=checked_rom(args.clean,CLEAN_SHA256,"clean 0.13.0")
    donor=checked_rom(args.v04,V04_SHA256,"Vietnamese v0.4")
    book=json.loads(args.codebook.read_text(encoding="utf-8"))
    glyphs={ch:int(byte,16) for ch,byte in book["glyph_bytes"].items()}
    report=collision_report(clean,donor,glyphs,args.charmap.read_text(encoding="utf-8"))
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
