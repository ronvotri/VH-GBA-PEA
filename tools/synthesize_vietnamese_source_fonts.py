#!/usr/bin/env python3
"""Experimental source-ROM font synthesis using the game's own ASCII glyph art.

Unlike private v0.4 donor grafts, synthesizes Vietnamese tone marks from stock
Latin base glyphs inside the exact source-compiled ROM. No font assets or ROMs
are stored in the public repo. Experimental visuals, NOT gameplay certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

from import_v04_glyphs_into_source_build import (
    FONT_NAMES, GLYPH_BLOCK_SIZE, ROM_BYTES, read_symbol_offsets
)
from graft_v06_pokeblock_safe_fonts import (
    PINNED_3360_SOURCE_SHA256, ATTESTED_3360_FONT_OFFSETS,
    PINNED_BIRCH_3360_SOURCE_SHA256, ATTESTED_BIRCH_3360_FONT_OFFSETS,
    PINNED_BIRCH_3363_SOURCE_SHA256, ATTESTED_BIRCH_3363_FONT_OFFSETS,
    PINNED_BIRCH_3364_SOURCE_SHA256, ATTESTED_BIRCH_3364_FONT_OFFSETS,
    require_pinned_target_symbols
)
from pokemon_gba_font_glyphs import decode_glyph, encode_glyph

GLYPH_BYTES = 64
PROTECTED_CODES = set(range(0x53, 0x5A)) | {0x34, 0x35, 0x36}
TONE = {"\u0301":"acute", "\u0300":"grave", "\u0309":"hook",
        "\u0303":"tilde", "\u0323":"dot"}
STRUCTURAL = {"\u0302":"circumflex", "\u0306":"breve", "\u031B":"horn"}


def accent_recipe(letter: str) -> tuple[str,list[str]]:
    if letter in ("đ", "Đ"):
        return ("d" if letter=="đ" else "D"), ["bar"]
    chars=unicodedata.normalize("NFD",letter)
    if len(chars)<2 or not chars[0].isascii() or not chars[0].isalpha():
        raise ValueError("character cannot be constructed from stock ASCII: "+repr(letter))
    marks=[]
    for c in chars[1:]:
        if c in STRUCTURAL:
            marks.append(STRUCTURAL[c])
        elif c in TONE:
            marks.append(TONE[c])
        else:
            raise ValueError("unsupported combining mark: "+repr(c))
    # NFD orders combining marks by canonical combining class; Vietnamese
    # below-dot may appear before the vowel's breve/circumflex. Draw the
    # structural mark first and tonal accent second for stable rasterization.
    marks.sort(key=lambda mark:0 if mark in ("circumflex","breve","horn") else 1)
    return chars[0],marks


def compose(stock:list[list[int]], marks:list[str], width:int)->tuple[list[list[int]],int]:
    """Make a 16x16 2bpp cell; keep existing base letter and shadow colors."""
    cells=[(x,y) for y,row in enumerate(stock) for x,c in enumerate(row) if c in (1,2)]
    if not cells or not 1<=width<=16:
        raise ValueError("blank/bad-width ASCII source glyph")
    left=min(x for x,_ in cells)
    right=max(x for x,_ in cells)
    top=min(y for _,y in cells)
    bottom=max(y for _,y in cells)
    upper=[x for x in range(left,right+1)]
    middle=(left+right)//2
    has_above=any(m!="dot" and m!="bar" and m!="horn" for m in marks)
    double=sum(m in ("acute","grave","hook","tilde","circumflex","breve") for m in marks)>1
    shift=min(4 if double else (3 if has_above else 0),15-bottom)
    if "dot" in marks and bottom+shift>13:
        shift=max(-top,13-bottom)
    out=[[0]*16 for _ in range(16)]
    for y,row in enumerate(stock):
        yy=y+shift
        if 0<=yy<16:
            for x,p in enumerate(row):
                out[yy][x]=p

    def point(x,y):
        if 0<=x<16 and 0<=y<16:
            out[y][x]=1

    # The upper marks use compact 1px/2px strokes: recognizable at GBA scale.
    cap=max(0,top+shift-1)
    for mark in marks:
        if mark=="bar":
            y=top+shift+min(4,(bottom-top)//2)
            for x in range(max(0,middle-2),min(15,middle+3)):
                point(x,y)
        elif mark=="horn":
            x=min(14,right+1)
            y=max(0,top+shift)
            point(x,y);point(x+1,max(0,y-1));point(x+1,max(0,y-2))
        elif mark=="dot":
            point(middle,min(15,bottom+shift+2))
            if middle+1<=15: point(middle+1,min(15,bottom+shift+2))
        elif mark=="circumflex":
            y=max(1,cap-(2 if double else 0))
            point(middle-2,y);point(middle-1,y-1);point(middle,y-2)
            point(middle+1,y-1);point(middle+2,y)
        elif mark=="breve":
            y=max(0,cap-(2 if double else 0))
            point(middle-2,y);point(middle-1,y+1)
            point(middle,y+1);point(middle+1,y+1);point(middle+2,y)
        elif mark=="acute":
            y=max(0,cap)
            point(middle-1,y);point(middle,y-1);point(middle+1,max(0,y-2))
        elif mark=="grave":
            y=max(0,cap)
            point(middle+1,y);point(middle,y-1);point(middle-1,max(0,y-2))
        elif mark=="hook":
            y=max(1,cap)
            point(middle,y-1);point(middle+1,y-1);point(middle+1,y)
            point(middle,y+1)
        elif mark=="tilde":
            y=max(0,cap)
            point(middle-2,y);point(middle-1,max(0,y-1))
            point(middle,y);point(middle+1,y+1);point(middle+2,y)
        else:
            raise ValueError("unknown diacritic "+mark)
    used=[x for row in out for x in row]
    if 1 not in used:
        raise ValueError("synthesized glyph lost visible foreground pixels")
    rightmost=max(x for row in out for x,p in enumerate(row) if p in (1,2))
    return out,max(width,rightmost+1)


def synthesize_fonts(rom:bytes, offsets:dict[str,int],
                     glyphs:dict[str,str])->tuple[bytes,dict]:
    source_sha=hashlib.sha256(rom).hexdigest()
    if len(rom)!=ROM_BYTES or source_sha not in (
            PINNED_3360_SOURCE_SHA256,PINNED_BIRCH_3360_SOURCE_SHA256,
            PINNED_BIRCH_3363_SOURCE_SHA256,PINNED_BIRCH_3364_SOURCE_SHA256):
        raise ValueError("source ROM is not an independently attested 3,360-text build")
    require_pinned_target_symbols(offsets,source_sha)
    codes={ch:int(value,16) for ch,value in glyphs.items()}
    if len(set(codes.values()))!=len(codes):
        raise ValueError("source codebook contains colliding codepoints")
    protected=PROTECTED_CODES | {val for ch,val in codes.items() if ch.isascii()}
    accented=[]
    for ch,dst in codes.items():
        if ch.isascii() or not ch.isalpha():
            continue
        if dst in protected:
            raise ValueError("accent overwrites native Pokémon/ASCII glyph")
        base,marks=accent_recipe(ch)
        if base not in codes:
            raise ValueError("missing base letter "+base)
        accented.append((ch,dst,codes[base],marks))
    if len(accented)<45:
        raise ValueError("not enough safe Vietnamese accented glyphs")
    out=bytearray(rom)
    ledger=[]
    for font in FONT_NAMES:
        offset=offsets[font]
        for ch,dst,base,marks in accented:
            base_start=offset+base*GLYPH_BYTES
            pixels=decode_glyph(rom[base_start:base_start+GLYPH_BYTES])
            base_width=rom[offset+GLYPH_BLOCK_SIZE+base]
            generated,width=compose(pixels,marks,base_width)
            target_start=offset+dst*GLYPH_BYTES
            out[target_start:target_start+GLYPH_BYTES]=encode_glyph(generated)
            out[offset+GLYPH_BLOCK_SIZE+dst]=width
            ledger.append({"font":font,"glyph":ch,"code":dst,"base_code":base,"width":width})
        for code in protected:
            where=offset+code*GLYPH_BYTES
            assert out[where:where+GLYPH_BYTES]==rom[where:where+GLYPH_BYTES]
            assert out[offset+GLYPH_BLOCK_SIZE+code]==rom[offset+GLYPH_BLOCK_SIZE+code]
    spans=[(offsets[f],offsets[f]+GLYPH_BLOCK_SIZE+0x100) for f in FONT_NAMES]
    changed=sum(x!=y for x,y in zip(rom,out))
    if not changed:
        raise ValueError("font synthesis produced no changes")
    if any(a!=b and not any(lo<=i<hi for lo,hi in spans)
           for i,(a,b) in enumerate(zip(rom,out))):
        raise ValueError("non-font ROM byte changed")
    report={"source_sha256":source_sha,
        "result_sha256":hashlib.sha256(out).hexdigest(),
        "glyphs_per_font":len(accented),"font_styles":len(FONT_NAMES),
        "generated_glyphs":len(ledger),"font_only_byte_changes":changed,
        "native_ascii_and_pokeblock_preserved":True,
        "no_non_font_writes":True,"synthetic_unreviewed_visuals":True,
        "emulator_tested":False,"release_ready":False}
    return bytes(out),report


def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ("source-built","sym","codebook","report"):
        ap.add_argument("--"+name,required=True,type=Path)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    raw=args.source_built.read_bytes()
    offsets=read_symbol_offsets(args.sym.read_text(encoding="utf-8"))
    book=json.loads(args.codebook.read_text(encoding="utf-8"))
    if book.get("schema_version")!=3:
        ap.error("requires collision-safe v0.6 codebook")
    result,report=synthesize_fonts(raw,offsets,book["glyph_bytes"])
    if args.output:
        if args.output.resolve()==args.source_built.resolve():
            ap.error("refusing to overwrite certified input ROM")
        args.output.write_bytes(result)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
