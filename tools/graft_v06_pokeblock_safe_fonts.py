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

# Compiled source text and font addresses were independently attested by the
# exact 2,093-label v0.6 Actions artifact. A new compiler layout requires a
# NEW audit/checkpoint; never silently accept the older baseline .sym.
PINNED_SOURCE_SHA256="5cae1a20698fcd7036ccdc0f2bdbc0c0c80d942380ab48611fb3ec816ebcab7f"
ATTESTED_SOURCE_FONT_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x71B59C,
    "gFontSmallLatinGlyphs":0x72379C,
    "gFontNarrowLatinGlyphs":0x72B99C,
    "gFontShortLatinGlyphs":0x733B9C,
    "gFontNormalLatinGlyphs":0x73BD9C,
}

# Independent compiler + font-symbol audit, GitHub Actions 37973599855.
# Distinct from the earlier 2,093-label release-gated source trial.
PINNED_3360_SOURCE_SHA256="9e804a005210d59d4dc1806d387d3b50ee412ab9e7f5df0f56d5f27e43407f7a"
ATTESTED_3360_FONT_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x71A798,
    "gFontSmallLatinGlyphs":0x722998,
    "gFontNarrowLatinGlyphs":0x72AB98,
    "gFontShortLatinGlyphs":0x732D98,
    "gFontNormalLatinGlyphs":0x73AF98,
}

# The Professor Birch welcome sentence was brought into the 500-label
# system-text batch after a glyph-safe reflow. Exact CI artifact from
# run 38027431812 (source SHA + compiler-generated SOURCE_SHORT_C_UI_FONT.sym).
PINNED_BIRCH_3360_SOURCE_SHA256="c1756599fa7ffd227c073891ab43765aff3442bf0b6a15aa07efb624dbcc6f78"
ATTESTED_BIRCH_3360_FONT_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x71A78C,
    "gFontSmallLatinGlyphs":0x72298C,
    "gFontNarrowLatinGlyphs":0x72AB8C,
    "gFontShortLatinGlyphs":0x732D8C,
    "gFontNormalLatinGlyphs":0x73AF8C,
}

# Independent CI #38032748175: +3 exact Birch narrative labels on the
# immutable 3,360 source branch; all five clean Latin stock fonts attested.
PINNED_BIRCH_3363_SOURCE_SHA256="af67fe4775bf29a110b77573667ac397c6933174e1bd6a470e7927f870d9d77f"
ATTESTED_BIRCH_3363_FONT_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x71A708,
    "gFontSmallLatinGlyphs":0x722908,
    "gFontNarrowLatinGlyphs":0x72AB08,
    "gFontShortLatinGlyphs":0x732D08,
    "gFontNormalLatinGlyphs":0x73AF08,
}

# Runtime Birch C text compiler build: CI 38037695443. Exact ELF symbols,
# SHA and real engine FC 08 60 FB FF suffix independently ROM-byte attested.
PINNED_BIRCH_3364_SOURCE_SHA256="5b63c67009140c309aa1f6339df2abef158e6bb43aa4cb08b6f6e557e5967ea5"
ATTESTED_BIRCH_3364_FONT_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x71A6FC,
    "gFontSmallLatinGlyphs":0x7228FC,
    "gFontNarrowLatinGlyphs":0x72AAFC,
    "gFontShortLatinGlyphs":0x732CFC,
    "gFontNormalLatinGlyphs":0x73AEFC,
}

# Exact independently attested Birch PLAYER + KUN source trial from CI
# 38042181252. Two late name-dialogue pointers resolved; no gameplay QA yet.
PINNED_BIRCH_3366_SOURCE_SHA256="a887c81b426c11be12257b66286166b11ac50b4081e06782792f5ce972e97cd0"
ATTESTED_BIRCH_3366_FONT_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x71A6F8,
    "gFontSmallLatinGlyphs":0x7228F8,
    "gFontNarrowLatinGlyphs":0x72AAF8,
    "gFontShortLatinGlyphs":0x732CF8,
    "gFontNormalLatinGlyphs":0x73AEF8,
}

# FULL PASS Actions #38045294719: +300 source-owned C UI labels,
# including main menu and real naming-screen title. All five font
# glyph banks are untouched stock art at these exactly SHA-paired offsets.
PINNED_C_UI_3666_SOURCE_SHA256="f9a31e14e763e6f71adbd02930d5e7d35365fb8f392b717cbb7834244c15d41c"
ATTESTED_C_UI_3666_FONT_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x71A754,
    "gFontSmallLatinGlyphs":0x722954,
    "gFontNarrowLatinGlyphs":0x72AB54,
    "gFontShortLatinGlyphs":0x732D54,
    "gFontNormalLatinGlyphs":0x73AF54,
}

# CI #38071665529 independent source SHA / stock-font ELF geometry.
PINNED_NAMING_3774_SOURCE_SHA256="3eb605c00fe2e00e02aa90cba994738c029a821c307264f492ea04e0f438e631"
ATTESTED_NAMING_3774_FONT_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x71A77C,
    "gFontSmallLatinGlyphs":0x72297C,
    "gFontNarrowLatinGlyphs":0x72AB7C,
    "gFontShortLatinGlyphs":0x732D7C,
    "gFontNormalLatinGlyphs":0x73AF7C,
}



# CI #38077592184 FULL PASS: 120 NEW system-text labels added to 3774;
# SHA-locked all five untouched source Latin glyph banks and ELF symbols.
PINNED_SYSTEM_SECOND_3894_SOURCE_SHA256="7bf9b814a415f814c51c2e900638fda8ee9c87b533688d828f4134336e316bd9"
ATTESTED_SYSTEM_SECOND_3894_FONT_OFFSETS={
    "gFontSmallNarrowLatinGlyphs":0x71A588,
    "gFontSmallLatinGlyphs":0x722788,
    "gFontNarrowLatinGlyphs":0x72A988,
    "gFontShortLatinGlyphs":0x732B88,
    "gFontNormalLatinGlyphs":0x73AD88,
}


def require_pinned_target_symbols(target_offsets:dict[str,int],
                                  source_sha256:str=PINNED_SOURCE_SHA256)->None:
    profiles={
        PINNED_SOURCE_SHA256:ATTESTED_SOURCE_FONT_OFFSETS,
        PINNED_3360_SOURCE_SHA256:ATTESTED_3360_FONT_OFFSETS,
        PINNED_BIRCH_3360_SOURCE_SHA256:ATTESTED_BIRCH_3360_FONT_OFFSETS,
        PINNED_BIRCH_3363_SOURCE_SHA256:ATTESTED_BIRCH_3363_FONT_OFFSETS,
        PINNED_BIRCH_3364_SOURCE_SHA256:ATTESTED_BIRCH_3364_FONT_OFFSETS,
        PINNED_BIRCH_3366_SOURCE_SHA256:ATTESTED_BIRCH_3366_FONT_OFFSETS,
        PINNED_C_UI_3666_SOURCE_SHA256:ATTESTED_C_UI_3666_FONT_OFFSETS,
        PINNED_NAMING_3774_SOURCE_SHA256:ATTESTED_NAMING_3774_FONT_OFFSETS,
        PINNED_SYSTEM_SECOND_3894_SOURCE_SHA256:ATTESTED_SYSTEM_SECOND_3894_FONT_OFFSETS,
    }
    expected=profiles.get(source_sha256.lower())
    if expected is None:
        raise ValueError("unrecognized v0.6 source build SHA; no attested font profile")
    if target_offsets!=expected:
        raise ValueError("wrong v0.6 target .sym: source SHA and font symbol map are not paired")
    spans=sorted((a,a+GLYPH_BLOCK_SIZE+0x100)
                 for a in target_offsets.values())
    if any(a<0 or b>0x2000000 for a,b in spans):
        raise ValueError("v0.6 font graphics/width table outside ROM")
    if any(spans[i][1]>spans[i+1][0] for i in range(len(spans)-1)):
        raise ValueError("overlapping v0.6 font graphics/width tables")


def graft_v06_font(clean:bytes,donor:bytes,built:bytes,
                   source_offsets:dict[str,int],target_offsets:dict[str,int],
                   glyphs:dict[str,str],
                   source_build_sha256:str=PINNED_SOURCE_SHA256)->tuple[bytes,dict]:
    require_pinned_target_symbols(target_offsets,source_build_sha256)
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
        "attested_source_profile_sha256":source_build_sha256.lower(),
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
    if a.expected_source_sha256.lower() not in (PINNED_SOURCE_SHA256,PINNED_3360_SOURCE_SHA256,PINNED_BIRCH_3360_SOURCE_SHA256,PINNED_BIRCH_3363_SOURCE_SHA256,PINNED_BIRCH_3364_SOURCE_SHA256,PINNED_BIRCH_3366_SOURCE_SHA256,
        PINNED_C_UI_3666_SOURCE_SHA256,PINNED_NAMING_3774_SOURCE_SHA256):
        p.error("source SHA256 has no attested v0.6 font geometry profile")
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
        book["glyph_bytes"],a.expected_source_sha256.lower())
    qa["exact_source_input_sha256"]=hashlib.sha256(built).hexdigest()
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_bytes(result)
    print(json.dumps(qa,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
