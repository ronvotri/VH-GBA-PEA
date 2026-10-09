#!/usr/bin/env python3
"""Import only verified v0.4 Latin glyph blocks into a source-built ROM.

Private/local inputs: clean released Arena 0.13.0, user's Vietnamese v0.4,
source-built ROM and its matching .sym file. This is a strict font-data
operation: no text, reference, pointer, save or title graphics writes.
Never upload original/donor ROMs to public GitHub.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

CLEAN_SHA256="a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b"
V04_SHA256="c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9"
FONT_NAMES=(
    "gFontSmallNarrowLatinGlyphs",
    "gFontSmallLatinGlyphs",
    "gFontNarrowLatinGlyphs",
    "gFontShortLatinGlyphs",
    "gFontNormalLatinGlyphs",
)
GLYPH_BLOCK_SIZE=0x8000
ROM_BYTES=0x2000000
ATTESTED_CLEAN_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x0071DEA0,
    "gFontSmallLatinGlyphs":0x007260A0,
    "gFontNarrowLatinGlyphs":0x0072E2A0,
    "gFontShortLatinGlyphs":0x007364A0,
    "gFontNormalLatinGlyphs":0x0073E6A0,
}


def read_symbol_offsets(source: str) -> dict[str,int]:
    found={}
    for line in source.splitlines():
        m=re.fullmatch(r"([0-9A-Fa-f]{8})\s+([A-Za-z])\s+(\S+)",line)
        if not m or m.group(3) not in FONT_NAMES:
            continue
        name=m.group(3)
        if name in found:
            raise ValueError(f"duplicate font symbol {name}")
        address=int(m.group(1),16)
        if not 0x08000000<=address<0x0A000000:
            raise ValueError(f"font symbol is outside ROM: {name}")
        found[name]=address-0x08000000
    if set(found)!=set(FONT_NAMES):
        raise ValueError("font symbol map incomplete")
    return found


def overlay_fonts(clean:bytes, donor:bytes, rebuilt:bytes,
                  reference_offsets:dict[str,int],
                  target_offsets:dict[str,int]) -> tuple[bytes,dict[str,int]]:
    if len(clean)!=ROM_BYTES or len(donor)!=ROM_BYTES or len(rebuilt)!=ROM_BYTES:
        raise ValueError("ROM inputs must be exactly 32 MiB")
    out=bytearray(rebuilt)
    counts={}
    allocated=[]
    for name in FONT_NAMES:
        a=reference_offsets[name]
        b=target_offsets[name]
        if not (0<=a<=ROM_BYTES-GLYPH_BLOCK_SIZE
                and 0<=b<=ROM_BYTES-GLYPH_BLOCK_SIZE):
            raise ValueError(f"{name}: font range is out of ROM")
        if any(b<end and start<b+GLYPH_BLOCK_SIZE
               for start,end in allocated):
            raise ValueError("overlapping target font blocks")
        allocated.append((b,b+GLYPH_BLOCK_SIZE))
        previous=clean[a:a+GLYPH_BLOCK_SIZE]
        corrected=donor[a:a+GLYPH_BLOCK_SIZE]
        if rebuilt[b:b+GLYPH_BLOCK_SIZE]!=previous:
            raise ValueError(f"{name}: rebuilt source glyphs differ from clean reference")
        counts[name]=sum(x!=y for x,y in zip(previous,corrected))
        out[b:b+GLYPH_BLOCK_SIZE]=corrected
    if not any(counts.values()):
        raise ValueError("donor contains no Latin font delta")
    return bytes(out),counts


def checked_rom(path:Path,sha:str,label:str)->bytes:
    data=path.read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    if len(data)!=ROM_BYTES or digest!=sha:
        raise SystemExit(f"REFUSED: {label} is not the SHA-locked exact input: {digest}")
    return data


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--clean",type=Path,required=True)
    p.add_argument("--v04",type=Path,required=True)
    p.add_argument("--source-built",type=Path,required=True)
    p.add_argument("--expected-source-sha256",help="Required when writing; exact source-built ROM hash")
    p.add_argument("--reference-sym",type=Path,required=True)
    p.add_argument("--target-sym",type=Path,required=True)
    p.add_argument("--out",type=Path)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    if a.out and (a.out.resolve() in {a.clean.resolve(),a.v04.resolve(),a.source_built.resolve()}):
        p.error("refusing to overwrite a source/donor ROM")
    clean=checked_rom(a.clean,CLEAN_SHA256,"released Arena")
    donor=checked_rom(a.v04,V04_SHA256,"Vietnamese v0.4")
    rebuilt=a.source_built.read_bytes()
    if len(rebuilt)!=ROM_BYTES:
        raise SystemExit("REFUSED: unexpected source build ROM size")
    source_digest=hashlib.sha256(rebuilt).hexdigest()
    if a.out and not a.expected_source_sha256:
        raise SystemExit("REFUSED: output requires --expected-source-sha256")
    if a.expected_source_sha256 and source_digest!=a.expected_source_sha256.lower():
        raise SystemExit("REFUSED: source-built ROM SHA-256 differs from pinned expected hash")
    reference=read_symbol_offsets(a.reference_sym.read_text(encoding="utf-8"))
    if reference!=ATTESTED_CLEAN_OFFSETS:
        raise SystemExit("REFUSED: source symbol font offsets are not the checked clean layout")
    target=read_symbol_offsets(a.target_sym.read_text(encoding="utf-8"))
    result,counts=overlay_fonts(clean,donor,rebuilt,reference,target)
    diff=sum(x!=y for x,y in zip(rebuilt,result))
    if diff!=sum(counts.values()):
        raise SystemExit("REFUSED: modified bytes outside font-owned ranges")
    report={
        "mode":"apply" if a.out else "read-only",
        "source_rom_sha256":source_digest,
        "output_sha256":hashlib.sha256(result).hexdigest(),
        "font_byte_changes":counts,
        "total_changed_bytes":diff,
        "text_pointer_writes":0,
        "font_geometry_stable":True,
        "glyph_shapes_visually_verified":False,
        "gameplay_emulator_tested":False,
    }
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_bytes(result)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
