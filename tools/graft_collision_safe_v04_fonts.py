#!/usr/bin/env python3
"""PRIVATE experimental font graft for SOURCE-BUILT Vietnamese Arena ROMs.

The v0.4 donor repurposes original Latin f/w/z glyph slots. With the
collision-safe source codebook, move their accented donor glyph pictures into
Latin 0x30/0x31/0x32, restore stock f/w/z, and carry widths into new slots.
This never mutates pointers/scripts and refuses writing without an exact
source-built ROM SHA256 and a v2 collision-safe codebook plan.

CRITICAL: donor v0.4 does not include these accent shapes in Small/SmallNarrow
fonts; this internal glyph graft does NOT make small-font rendering complete.
Do not distribute output or claim visual/gameplay QA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from import_v04_glyphs_into_source_build import (
    ATTESTED_CLEAN_OFFSETS, CLEAN_SHA256, FONT_NAMES,
    GLYPH_BLOCK_SIZE, ROM_BYTES, V04_SHA256, checked_rom,
    overlay_fonts, read_symbol_offsets,
)
from plan_collision_free_vietnamese_font import (
    RELOCATION, GLYPH_BYTES_PER_CODEPOINT,
)

FONT_WIDTH_BYTES=0x100
UNVERIFIED_SMALL_FONTS={
    "gFontSmallNarrowLatinGlyphs","gFontSmallLatinGlyphs",
}


def graft_collision_safe_font(
    clean:bytes,donor:bytes,built:bytes,source_offsets:dict[str,int],
    target_offsets:dict[str,int],safe_book:dict[str,str],
) -> tuple[bytes,dict]:
    if source_offsets != ATTESTED_CLEAN_OFFSETS:
        raise ValueError("expected exact clean-shipping font symbol offsets")
    for accent,(english,src,dst) in RELOCATION.items():
        if safe_book.get(english) != f"0x{src:02X}" or safe_book.get(accent) != f"0x{dst:02X}":
            raise ValueError(f"source-built codebook does not reserve {accent}")
    result,baseline_diff=overlay_fonts(clean,donor,built,source_offsets,target_offsets)
    out=bytearray(result)
    target_font_ranges=[]
    missing={}
    restored=[]
    for name in FONT_NAMES:
        old=source_offsets[name]
        new=target_offsets[name]
        ref_width=old+GLYPH_BLOCK_SIZE
        tgt_width=new+GLYPH_BLOCK_SIZE
        if clean[ref_width:ref_width+FONT_WIDTH_BYTES]!=built[tgt_width:tgt_width+FONT_WIDTH_BYTES]:
            raise ValueError(f"{name}: source width table layout diverges")
        if donor[ref_width:ref_width+FONT_WIDTH_BYTES]!=clean[ref_width:ref_width+FONT_WIDTH_BYTES]:
            raise ValueError(f"{name}: donor edited font widths unexpectedly")
        changed=[]
        for accent,(english,source_code,slot) in RELOCATION.items():
            old_ascii=old+source_code*GLYPH_BYTES_PER_CODEPOINT
            new_ascii=new+source_code*GLYPH_BYTES_PER_CODEPOINT
            new_acc=new+slot*GLYPH_BYTES_PER_CODEPOINT
            donor_glyph=donor[old_ascii:old_ascii+GLYPH_BYTES_PER_CODEPOINT]
            stock_glyph=clean[old_ascii:old_ascii+GLYPH_BYTES_PER_CODEPOINT]
            if donor_glyph==stock_glyph:
                # In v0.4 Small/SmallNarrow glyphs never learned Vietnamese.
                if name not in UNVERIFIED_SMALL_FONTS:
                    raise ValueError(f"{name}: expected modified donor accent {accent}")
                missing.setdefault(name,[]).append(accent)
            else:
                # Move actual accented graphic and preserve original English.
                out[new_acc:new_acc+GLYPH_BYTES_PER_CODEPOINT]=donor_glyph
                # Width source is a safe starting point, NOT visual pixel QA.
                out[tgt_width+slot]=clean[ref_width+source_code]
                changed.append(accent)
            out[new_ascii:new_ascii+GLYPH_BYTES_PER_CODEPOINT]=stock_glyph
        restored.append({"font":name,
                         "reassigned_diacritics":changed,
                         "source_glyph_differences":baseline_diff[name]})
        target_font_ranges.append((new,new+GLYPH_BLOCK_SIZE+FONT_WIDTH_BYTES))
    # Explicitly forbid all writes beyond the five glyph + width ranges.
    for index,(before,after) in enumerate(zip(built,out)):
        if before!=after and not any(start<=index<end
                                      for start,end in target_font_ranges):
            raise ValueError(f"unexpected non-font write at {index:#x}")
    summary={
        "result_sha256":hashlib.sha256(out).hexdigest(),
        "font_styles":restored,
        "small_font_missing_accents":missing,
        "english_f_w_z_shapes_restored":True,
        "font_data_only_changes":True,
        "text_or_pointer_writes":0,
        "pixel_accuracy_and_emulator_tested":False,
        "release_ready":False,
    }
    if set(missing) != UNVERIFIED_SMALL_FONTS:
        raise ValueError("unexpected unsupported font style set")
    return bytes(out),summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clean",type=Path,required=True)
    ap.add_argument("--v04",type=Path,required=True)
    ap.add_argument("--source-built",type=Path,required=True)
    ap.add_argument("--expected-source-sha256",required=True)
    ap.add_argument("--reference-sym",type=Path,required=True)
    ap.add_argument("--target-sym",type=Path,required=True)
    ap.add_argument("--safe-codebook",type=Path,required=True)
    ap.add_argument("--output",type=Path)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    if args.output and args.output.resolve() in {
        args.clean.resolve(),args.v04.resolve(),args.source_built.resolve()}:
        ap.error("refusing to overwrite input ROMs")
    clean=checked_rom(args.clean,CLEAN_SHA256,"clean Arena")
    donor=checked_rom(args.v04,V04_SHA256,"Vietnamese v0.4")
    built=checked_rom(args.source_built,args.expected_source_sha256.lower(),
                      "source-built Arena")
    original=read_symbol_offsets(args.reference_sym.read_text(encoding="utf-8"))
    compiled=read_symbol_offsets(args.target_sym.read_text(encoding="utf-8"))
    book=json.loads(args.safe_codebook.read_text(encoding="utf-8"))
    if book.get("schema_version") != 2 or book.get("status","").find("requires glyph relocation")<0:
        raise SystemExit("REFUSED: source codebook is not collision-safe v2")
    modified,info=graft_collision_safe_font(
        clean,donor,built,original,compiled,book["glyph_bytes"])
    info["input_source_sha256"]=hashlib.sha256(built).hexdigest()
    info["state"]="PRIVATE FONT-SHAPE EXPERIMENT; SMALL FONT ACCENTS MISSING"
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_bytes(modified)
    print(json.dumps(info,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
