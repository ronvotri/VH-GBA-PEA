#!/usr/bin/env python3
"""Reserve *actually free* Latin slots for đ/ì, preserving native Pokéblock.

This is a new source byte-encoding plan, NOT a ROM patch. All generated
source bytes require matching v0.6 raster glyph transplantation before play.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path

from plan_collision_free_vietnamese_font import parse_english_single_byte_occupancy

NATIVE = {"PK":(0x53,), "PKMN":(0x53,0x54),
          "POKEBLOCK":(0x55,0x56,0x57,0x58,0x59)}
RELOCATION = {
    "đ":{"source":0x56,"target":0x33,"width_reference_ascii":"d","width_reference_byte":0xD8},
    "ì":{"source":0x59,"target":0x37,"width_reference_ascii":"i","width_reference_byte":0xDD},
}
RESERVED_ASCII={"=":0x35,";":0x36}
BAD_OLD_PROPOSAL=0x35


def plan_v06(book:dict[str,str],charmap:str)->tuple[dict[str,str],dict]:
    english=charmap.split("@ Hiragana",1)[0]
    if "POKEBLOCK   = 55 56 57 58 59" not in english:
        raise ValueError("pinned Pokéblock token does not match")
    for marker in ("'='         = 35","';'         = 36",
                   "'d'         = D8","'i'         = DD"):
        if marker not in english:
            raise ValueError("pinned ASCII/special font charmap changed")
    occupied=parse_english_single_byte_occupancy(charmap)
    original={ch:int(b,16) for ch,b in book.items()}
    target=dict(original)
    used=set(original.values())
    for char,rule in RELOCATION.items():
        source,slot=rule["source"],rule["target"]
        if original.get(char)!=source:
            raise ValueError(f"untrusted v0.5 glyph slot for {char}")
        if slot in occupied or slot in used:
            raise ValueError(f"new glyph byte {slot:#04x} is occupied")
        if slot in range(0x53,0x5A) or slot>=0xFA:
            raise ValueError("would collide with native/control glyph")
        target[char]=slot
    for required in ("f","w","z","ấ","ằ","ắ","d","i"):
        if required not in target:
            raise ValueError(f"missing anchored glyph {required}")
    if [target[c] for c in ("f","w","z","ấ","ằ","ắ")]!=[0xDA,0xEB,0xEE,0x30,0x31,0x32]:
        raise ValueError("earlier v0.5 English-vs-accent repair drifted")
    groups=defaultdict(list)
    for char,value in target.items():
        groups[value].append(char)
    conflicts={f"{k:#04x}":v for k,v in groups.items() if len(v)>1}
    if conflicts:
        raise ValueError(f"still overlapping font encodings: {conflicts}")
    for key,sequence in NATIVE.items():
        if any(v in sequence for char,v in target.items() if ord(char)>127):
            raise ValueError(f"native {key} bytes collide with a Vietnamese glyph")
    report={
        "schema_version":3,
        "source_codebook":"v0.5",
        "status":"FONT_ART_NOT_GRAFTED_DO_NOT_RELEASE",
        "new_relocations":[dict(accent=c,**{k:(f"0x{v:02X}" if isinstance(v,int) else v)
                                         for k,v in rule.items()})
                           for c,rule in RELOCATION.items()],
        "native_special_bytes_preserved":{k:[f"0x{x:02X}" for x in v] for k,v in NATIVE.items()},
        "equals_sign_0x35_protected":True,
        "unique_vietnamese_bytes":True,
        "source_count":len(target),
        "runtime_emulator_verified":False,
    }
    return {c:f"0x{v:02X}" for c,v in target.items()},report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--v05-codebook",type=Path,required=True)
    p.add_argument("--charmap",type=Path,required=True)
    p.add_argument("--out-codebook",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    old=json.loads(a.v05_codebook.read_text(encoding="utf-8"))
    if old.get("schema_version")!=2:
        raise SystemExit("REFUSED: input not the pinned v0.5 plan")
    glyphs,report=plan_v06(old["glyph_bytes"],a.charmap.read_text(encoding="utf-8"))
    output={"schema_version":3,"status":"requires glyph relocation; do NOT use with original donor graphics",
            "source_v04_sha256":old["source_v04_sha256"],"glyph_bytes":glyphs,
            "required_relocations":old["required_relocations"]+report["new_relocations"],
            "unsupported_chars":old["unsupported_chars"],
            "font_special_controls_safe":False}
    a.out_codebook.parent.mkdir(parents=True,exist_ok=True)
    a.out_codebook.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
