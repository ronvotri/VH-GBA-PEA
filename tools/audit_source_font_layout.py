#!/usr/bin/env python3
"""SHA-based source-build font compatibility audit; read-only, no ROM asset upload."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from import_v04_glyphs_into_source_build import (
    FONT_NAMES,GLYPH_BLOCK_SIZE,ROM_BYTES,read_symbol_offsets)

CLEAN_GLYPH_SHA256={
    "gFontSmallNarrowLatinGlyphs":"fec295e5dc794a6cc9c5b642e78c7019fb0becf44e90e9b096c9e39fab36076c",
    "gFontSmallLatinGlyphs":"3d1493d9d22fcd1e9b85299af88ea98980107018ec36bcc04b73bc927f8fa820",
    "gFontNarrowLatinGlyphs":"3e1f45e425ebd58e870840e468bd4af5ef427b8dfa928dccf4909a83d39b41a9",
    "gFontShortLatinGlyphs":"d3de13b611cdc84929a2eb1057ecc662e2cc065a78634c498e098991c9d9ad26",
    "gFontNormalLatinGlyphs":"9df725adb5e41ab40cde0bddc88e00f5014157aad2d8030662b934ad155f287d",
}


def audit_font_blocks(rom:bytes,offsets:dict[str,int],
                      expected:dict[str,str]=CLEAN_GLYPH_SHA256)->dict[str,str]:
    if len(rom)!=ROM_BYTES:raise ValueError("unexpected ROM size")
    found={}
    for name in FONT_NAMES:
        off=offsets[name]
        if off<0 or off+GLYPH_BLOCK_SIZE>len(rom):
            raise ValueError(f"{name}: out-of-range source font")
        digest=hashlib.sha256(rom[off:off+GLYPH_BLOCK_SIZE]).hexdigest()
        if digest!=expected[name]:
            raise ValueError(f"{name}: compiled font differs from clean glyph layout")
        found[name]=digest
    return found


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path,required=True)
    p.add_argument("--sym",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    rom=a.rom.read_bytes()
    offsets=read_symbol_offsets(a.sym.read_text(encoding="utf-8"))
    digests=audit_font_blocks(rom,offsets)
    result={"schema_version":1,"glyph_blocks_matched_clean":len(digests),
            "source_rom_sha256":hashlib.sha256(rom).hexdigest(),
            "source_font_offsets":{k:hex(offsets[k]) for k in FONT_NAMES},
            "source_glyph_sha256":digests,
            "donor_font_patched":False,"private_donor_rom_required_for_next_step":True,
            "emulator_glyph_rendering_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
