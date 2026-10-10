#!/usr/bin/env python3
"""Install the runtime Birch Pokemon C string without touching its PAUSE 96/page bytes."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from stage_source_map_translations import encode_text
from stage_source_ui_translations import replace_c_string

LABEL="gText_ThisIsAPokemon"
OWNER="src/strings.c"
ENGLISH=r"This is what we call a “POKéMON.”{PAUSE 96}\p"
SUFFIX=r"{PAUSE 96}\p"
CONTROL=bytes((0xFC,0x08,0x60,0xFB,0xFF))

def encode(rows,codes,charmap):
    candidates=[x for x in rows if x.get("source_label")==LABEL]
    if len(candidates)!=1:
        raise ValueError("runtime Birch label missing or ambiguous")
    row=candidates[0]
    if (row.get("category")!="system-ui" or row.get("source_file")!=OWNER
            or row.get("english")!=ENGLISH):
        raise ValueError("runtime Birch source drift")
    vi=row.get("vietnamese","")
    if not vi.endswith(SUFFIX) or vi.count(SUFFIX)!=1:
        raise ValueError("PAUSE 96/page signature changed")
    words=vi[:-len(SUFFIX)]
    if not words or any(ch in words for ch in "{}\\$\r\n\t"):
        raise ValueError("unsupported token or newline in intro")
    if not re.search(r"(?m)^PAUSE\s*=\s*FC\s+08\b",charmap):
        raise ValueError("unverified original PAUSE FC 08 charmap control")
    payload=encode_text(words+"$",codes,26)[:-1]+CONTROL
    if payload.count(0xFF)!=1 or not payload.endswith(CONTROL):
        raise ValueError("source engine control was corrupted")
    return payload,vi

def verify_rom(rom,symbols,record):
    refs=re.findall(r"(?m)^([0-9a-fA-F]+)\s+\w\s+"+LABEL+r"$",symbols)
    if len(refs)!=1: raise ValueError("C runtime symbol not unique")
    addr=int(refs[0],16)
    if not 0x08000000<=addr<0x0A000000: raise ValueError("symbol outside ROM")
    offset=addr-0x08000000
    payload=bytes.fromhex(record["payload_hex"])
    if rom[offset:offset+len(payload)]!=payload:
        raise ValueError("translated runtime bytes not present at linked symbol")
    result=dict(record)
    result.update({"compiled_rom_byte_verified":True,
                   "rom_offset":f"0x{offset:08X}","release_ready":False})
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",required=True,type=Path)
    p.add_argument("--plan",type=Path)
    p.add_argument("--codebook",type=Path)
    p.add_argument("--charmap",type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--verify-rom",type=Path)
    p.add_argument("--sym",type=Path)
    a=p.parse_args()
    if a.verify_rom:
        if not a.sym or a.apply: p.error("verification needs --sym, never --apply")
        prior=json.loads(a.report.read_text(encoding="utf-8"))
        if prior.get("mode")!="apply" or prior.get("source_label")!=LABEL:
            p.error("untrusted source stage report")
        record=verify_rom(a.verify_rom.read_bytes(),
                          a.sym.read_text(encoding="utf-8"),prior)
    else:
        if not (a.plan and a.codebook and a.charmap):
            p.error("staging needs --plan, --codebook, --charmap")
        root=a.workspace.resolve()
        path=(root/OWNER).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            p.error("unsafe C source path")
        rows=json.loads(a.plan.read_text(encoding="utf-8"))
        glyphs={k:int(v,16) for k,v in
            json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"].items()}
        data,vi=encode(rows,glyphs,a.charmap.read_text(encoding="utf-8"))
        original=path.read_text(encoding="utf-8")
        rewritten=replace_c_string(original,LABEL,ENGLISH,data)
        if a.apply: path.write_text(rewritten,encoding="utf-8")
        record={"mode":"apply" if a.apply else "dry-run",
                "source_label":LABEL,"source_file":OWNER,
                "labels_staged":1,"vietnamese":vi,"english":ENGLISH,
                "payload_hex":data.hex(),"pause_96_preserved":True,
                "page_and_terminator_preserved":True,
                "compiled_rom_byte_verified":False,"release_ready":False}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
