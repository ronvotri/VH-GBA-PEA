#!/usr/bin/env python3
"""Source-owned naming controls: retain GBA button graphics and newline bytes.

Only exact runtime src/strings.c labels are permitted. Generic C UI staging
deliberately refuses these special placeholders. No donor ROM is required.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from stage_source_ui_translations import replace_c_string
from verify_compiled_source_strings import extract_c_payload

SOURCE="src/strings.c"
EXPECTED={
    "gText_MoveOkBack":{
        "english":"{DPAD_NONE}MOVE  {A_BUTTON}OK  {B_BUTTON}BACK",
        "vietnamese":"{DPAD_NONE}Di chuyển  {A_BUTTON}OK  {B_BUTTON}Quay lại",
        "max_cells":30,
    },
    "gText_YesNo":{
        "english":r"YES\nNO",
        "vietnamese":r"Có\nKhông",
        "max_cells":8,
    },
}
PINNED={
    "A_BUTTON":bytes((0xF8,0x00)),
    "B_BUTTON":bytes((0xF8,0x01)),
    "DPAD_NONE":bytes((0xF8,0x0C)),
}
MARKER=re.compile(r"\{[A-Z0-9_]+\}|\\n")

def ordered_controls(text:str)->tuple[str,...]:
    controls=tuple(x.group(0) for x in MARKER.finditer(text))
    remainder=MARKER.sub("",text)
    if any(c in remainder for c in "{}\\"):
        raise ValueError("unsupported braces / GBA special token")
    return controls

def verify_charmap(charmap:str)->None:
    for token,byt in PINNED.items():
        digits=f"{byt[0]:02X} {byt[1]:02X}"
        if len(re.findall(r"(?m)^"+token+r"\s*=\s*"+re.escape(digits)+r"\s*$",charmap))!=1:
            raise ValueError("mismatched GBA button charmap "+token)

def encode(text:str,glyphs:dict[str,int],max_cells:int)->bytes:
    if unicodedata.normalize("NFC",text)!=text:
        raise ValueError("non-normalized Vietnamese")
    out=bytearray()
    cells=0
    i=0
    while i<len(text):
        if text.startswith(r"\n",i):
            out.append(0xFE);i+=2;cells=0
        elif text[i]=="{":
            end=text.find("}",i+1)
            token=text[i+1:end] if end>=0 else ""
            if token not in PINN:raise ValueError("unsupported controller icon")
            out.extend(PINNED[token]);cells+=1;i=end+1
        else:
            ch=text[i]
            if ch in "{}\\" or ch in "\r\n\t$":
                raise ValueError("unexpected engine control or terminator")
            code=glyphs.get(ch)
            if code is None or not 0<=code<0xF8:
                raise ValueError(f"font glyph absent or colliding: {ch!r}")
            out.append(code);cells+=1;i+=1
        if cells>max_cells:raise ValueError("GBA naming screen/control text too wide")
    out.append(0xFF)
    if out.count(0xFF)!=1 or out[-1]!=0xFF:
        raise ValueError("invalid GBA text terminator")
    return bytes(out)

def stage(rows:list[dict],source:str,charmap:str,glyphs:dict[str,int]):
    verify_charmap(charmap)
    changed=source
    installed=[]
    for label,spec in EXPECTED.items():
        found=[r for r in rows if r.get("source_label")==label]
        if len(found)!=1:
            raise ValueError("ambiguous or missing runtime label "+label)
        row=found[0]
        if row.get("category")!="system-ui" or row.get("source_file")!=SOURCE:
            raise ValueError("runtime source file/category drift")
        en=row.get("english")
        vi=row.get("vietnamese")
        if en!=spec["english"] or vi!=spec["vietnamese"]:
            raise ValueError("source/translation authority drift "+label)
        if ordered_controls(en)!=ordered_controls(vi):
            raise ValueError("button/page control signature drift "+label)
        payload=encode(vi,glyphs,spec["max_cells"])
        changed=replace_c_string(changed,label,en,payload)
        if extract_c_payload(changed,label)!=payload:
            raise ValueError("source byte mismatch "+label)
        installed.append({"label":label,"source_file":SOURCE,"english":en,
                          "vietnamese":vi,"original_control_order":list(ordered_controls(en)),
                          "payload_hex":payload.hex(),"max_cells":spec["max_cells"]})
    return changed,installed

def validate_linked_bytes(rom:bytes,elf_symbols:str,source:str,
                          rows:list[dict])->list[dict]:
    checked=[]
    for row in rows:
        label=row["label"]
        addresses=re.findall(r"(?m)^([0-9A-Fa-f]+)\s+\w\s+"+re.escape(label)+r"$",elf_symbols)
        if len(addresses)!=1:raise ValueError("linked C label missing or duplicated "+label)
        address=int(addresses[0],16)
        if not 0x08000000<=address<0x0A000000:raise ValueError("symbol outside GBA ROM")
        offset=address-0x08000000
        payload=bytes.fromhex(row["payload_hex"])
        if extract_c_payload(source,label)!=payload:
            raise ValueError("source C bytes drift "+label)
        if rom[offset:offset+len(payload)]!=payload:
            raise ValueError("compiled ROM bytes mismatch "+label)
        if row["label"]=="gText_MoveOkBack":
            for pin in PINNED.values():
                if payload.count(pin)!=1:raise ValueError("controller icon missing/duplicated")
        if row["label"]=="gText_YesNo" and payload.count(0xFE)!=1:
            raise ValueError("YES/NO newline not retained")
        checked.append({"label":label,"rom_offset":f"0x{offset:08X}",
                        "sha256":hashlib.sha256(payload).hexdigest(),
                        "icons_and_linebreak_verified":True})
    return checked

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path)
    p.add_argument("--codebook",type=Path)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--rom",type=Path)
    p.add_argument("--sym",type=Path)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    root=a.workspace.resolve()
    path=(root/SOURCE).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        p.error("wrong runtime C source")
    c_source=path.read_text(encoding="utf-8")
    if a.rom:
        if a.apply or not a.sym or not a.report.is_file():
            p.error("--rom needs an existing applied --report and --sym")
        record=json.loads(a.report.read_text(encoding="utf-8"))
        if record.get("mode")!="apply" or record.get("labels_staged")!=2:
            p.error("unauthorized prior source stage")
        checks=validate_linked_bytes(a.rom.read_bytes(),
            a.sym.read_text(encoding="utf-8"),c_source,record["translated"])
        record.update({"linked_ROM_verified":True,"linked_checks":checks,
                       "emulator_tested":False,"release_ready":False})
    else:
        if not a.plan or not a.codebook:
            p.error("required --plan and --codebook")
        plan=json.loads(a.plan.read_text(encoding="utf-8"))
        book=json.loads(a.codebook.read_text(encoding="utf-8"))
        glyphs={ch:int(code,16) for ch,code in book["glyph_bytes"].items()}
        changed,translated=stage(plan,c_source,
           (root/"charmap.txt").read_text(encoding="utf-8"),glyphs)
        if a.apply:path.write_text(changed,encoding="utf-8")
        record={"mode":"apply" if a.apply else "dry-run",
                "labels_staged":len(translated),
                "source_file":SOURCE,
                "translated":translated,
                "button_and_newline_sequence_preserved":True,
                "linked_ROM_verified":False,
                "emulator_tested":False,"release_ready":False}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
