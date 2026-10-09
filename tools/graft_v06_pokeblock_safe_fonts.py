#!/usr/bin/env python3
"""Private v0.6 Arena font graft: preserve Pokéblock/PKMN and English f/w/z.

This supersedes the old v0.5 *font graft*, never the source translation
manifest. It requires a matching v0.6 source-ROM SHA and exact symbol maps.
No copyrighted ROM or bitmap is stored in the public repository. This is not
rendering/emulator QA, and result must NOT be distributed untested.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import graft_collision_safe_v04_fonts as old_graft
from import_v04_glyphs_into_source_build import (
    ATTESTED_CLEAN_OFFSETS,CLEAN_SHA256,V04_SHA256,FONT_NAMES,
    GLYPH_BLOCK_SIZE,checked_rom,read_symbol_offsets,
)
from plan_v06_pokeblock_safe_font import RELOCATION as NEW_RELOCATION
from pokemon_gba_font_glyphs import decode_glyph,synthesize_small_from_narrow

GLYPH_BYTES=64
SPECIAL_CODES=(0x53,0x54,0x55,0x56,0x57,0x58,0x59)
ASCII_PUNCT=(0x34,0x35,0x36)
SMALL_FONTS=old_graft.UNVERIFIED_SMALL_FONTS


def graft_v06_font(clean:bytes,donor:bytes,built:bytes,
                   source_offsets:dict[str,int],target_offsets:dict[str,int],
                   glyphs:dict[str,str])->tuple[bytes,dict]:
    for character,rule in NEW_RELOCATION.items():
        if glyphs.get(character)!=f'0x{rule["target"]:02X}':
            raise ValueError(f"v0.6 codebook lacks new byte {character}")
        if glyphs.get(rule["width_reference_ascii"])!=f'0x{rule["width_reference_byte"]:02X}':
            raise ValueError(f"unexpected base ASCII for {character}")
    if any(int(v,16) in SPECIAL_CODES for ch,v in glyphs.items()
           if ord(ch)>127):
        raise ValueError("v0.6 codebook still collides with PKMN or Pokéblock")
    if any(int(v,16)==0x35 for ch,v in glyphs.items() if ch!="="):
        raise ValueError("glyph codebook would overwrite the native equals sign")
    if source_offsets!=ATTESTED_CLEAN_OFFSETS:
        raise ValueError("mismatched clean font offsets")
    # Old three accents ấ/ằ/ắ already move out of f/w/z slots.
    patched,first=old_graft.graft_collision_safe_font(
        clean,donor,built,source_offsets,target_offsets,glyphs)
    out=bytearray(patched)
    synthetic=[]
    audit=[]
    for font in FONT_NAMES:
        old=source_offsets[font]
        new=target_offsets[font]
        width_old=old+GLYPH_BLOCK_SIZE
        width_new=new+GLYPH_BLOCK_SIZE
        if clean[width_old:width_old+0x100]!=built[width_new:width_new+0x100]:
            raise ValueError(f"{font}: source font width tables disagree")
        for char,rule in NEW_RELOCATION.items():
            src,target=rule["source"],rule["target"]
            start=old+src*GLYPH_BYTES
            glyph=donor[start:start+GLYPH_BYTES]
            stock=clean[start:start+GLYPH_BYTES]
            synthetic_here=glyph==stock
            if synthetic_here:
                if font not in SMALL_FONTS:
                    raise ValueError(f"{font}: no real donor glyph for {char}")
                narrow=source_offsets["gFontNarrowLatinGlyphs"]
                narrow_src=narrow+src*GLYPH_BYTES
                sample=donor[narrow_src:narrow_src+GLYPH_BYTES]
                if sample==clean[narrow_src:narrow_src+GLYPH_BYTES]:
                    raise ValueError(f"{char}: donor Narrow font is not localized")
                narrow_ascii_width=clean[narrow+GLYPH_BLOCK_SIZE+rule["width_reference_byte"]]
                if not 1<=narrow_ascii_width<=8:
                    raise ValueError(f"{char}: unsupported narrow base width")
                glyph=synthesize_small_from_narrow(sample,narrow_ascii_width)
                synthetic.append(f"{font}:{char}")
            # New glyph must have actual colored pixels, not an all-blank tile.
            picture=decode_glyph(glyph)
            if not any(color in (1,2) for row in picture for color in row):
                raise ValueError(f"{font}:{char} generated a blank glyph")
            offset=new+target*GLYPH_BYTES
            out[offset:offset+GLYPH_BYTES]=glyph
            char_width=clean[width_old+rule["width_reference_byte"]]
            if not 1<=char_width<=16:
                raise ValueError(f"{font}:{char} unsuitable Latin character width")
            out[width_new+target]=char_width
            audit.append({"font":font,"character":char,"slot":f"0x{target:02X}",
                          "synthetic":synthetic_here,"width":char_width})
        # Restore every native multi-byte icon, not merely slots for đ/ì.
        for code in SPECIAL_CODES:
            a=old+code*GLYPH_BYTES
            b=new+code*GLYPH_BYTES
            out[b:b+GLYPH_BYTES]=clean[a:a+GLYPH_BYTES]
            out[width_new+code]=clean[width_old+code]
        # Original '=' 0x35 and adjacent LV/semicolon are always protected.
        for code in ASCII_PUNCT:
            a=old+code*GLYPH_BYTES
            b=new+code*GLYPH_BYTES
            out[b:b+GLYPH_BYTES]=clean[a:a+GLYPH_BYTES]
            out[width_new+code]=clean[width_old+code]
        # Avoid false confidence based only on the fact we wrote the expected
        # sequence: assert the final result equals the clean original.
        for code in (*SPECIAL_CODES,*ASCII_PUNCT):
            a=old+code*GLYPH_BYTES
            b=new+code*GLYPH_BYTES
            if out[b:b+GLYPH_BYTES]!=clean[a:a+GLYPH_BYTES]:
                raise ValueError(f"{font}: protected native font slot damaged")
            if out[width_new+code]!=clean[width_old+code]:
                raise ValueError(f"{font}: protected native width damaged")
    font_ranges=[(target_offsets[name],target_offsets[name]+GLYPH_BLOCK_SIZE+0x100)
                 for name in FONT_NAMES]
    for p,(a,b) in enumerate(zip(built,out)):
        if a!=b and not any(left<=p<right for left,right in font_ranges):
            raise ValueError(f"non-font ROM modification at 0x{p:X}")
    info={
        "stage":"v06 PRIVATE FONT-ONLY RASTER EXPERIMENT",
        "previous_v05_graft":first["result_sha256"],
        "new_accent_glyphs":audit,
        "synthetic_small_font_glyphs":synthetic,
        "native_pokeblock_55_to_59_restored_all_five":True,
        "native_pkmn_53_to_54_restored_all_five":True,
        "native_equals_0x35_restored_all_five":True,
        "ASCII_f_w_z_preserved":True,
        "font_only_writes":True,
        "pointer_writes":0,
        "emulator_rendering_tested":False,
        "release_ready":False,
        "result_sha256":hashlib.sha256(out).hexdigest(),
    }
    return bytes(out),info


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("clean","v04","source-built","reference-sym","target-sym","safe-codebook","report"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--expected-source-sha256",required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    if a.output and a.output.resolve() in {a.clean.resolve(),a.v04.resolve(),a.source_built.resolve()}:
        p.error("output must not overwrite source or donor ROM")
    clean=checked_rom(a.clean,CLEAN_SHA256,"clean Arena shipping")
    donor=checked_rom(a.v04,V04_SHA256,"v0.4 font donor")
    built=checked_rom(a.source_built,a.expected_source_sha256.lower(),"v0.6 source build")
    book=json.loads(a.safe_codebook.read_text(encoding="utf-8"))
    if book.get("schema_version")!=3 or "requires glyph relocation" not in book.get("status",""):
        raise SystemExit("REFUSED: only tracked v0.6 font codebook allowed")
    result,qa=graft_v06_font(
        clean,donor,built,
        read_symbol_offsets(a.reference_sym.read_text(encoding="utf-8")),
        read_symbol_offsets(a.target_sym.read_text(encoding="utf-8")),
        book["glyph_bytes"])
    qa["exact_source_input_sha256"]=hashlib.sha256(built).hexdigest()
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_bytes(result)
    print(json.dumps(qa,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
