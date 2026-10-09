#!/usr/bin/env python3
"""Independent file-level attestation for source-first Vietnamese staging.

Checks that every staged label in each report really has a source-owned byte
array with one terminal FF. It does not trust only the totals printed by the
staging tools. No ROM bytes or graphics assets are touched.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

LABEL_RE=re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ASM_LABEL_RE=r"(?m)^\s*{label}:{{1,2}}\s*(?:@[^\r\n]*)?$"
ASM_LINE_RE=re.compile(r"^\s*\.byte\s+(.+?)\s*$")
ASM_HEX_RE=re.compile(r"0x([0-9A-Fa-f]{2})")
C_HEX_RE=re.compile(r"(?m)^\s*(?:static\s+)?const\s+u8\s+{label}\[\]\s*=\s*\{{([^}}]+)\}};",re.S)


def extract_asm_payload(source: str, label: str) -> bytes:
    if not LABEL_RE.fullmatch(label):
        raise ValueError("invalid source label")
    pat=re.compile(ASM_LABEL_RE.format(label=re.escape(label)))
    matches=list(pat.finditer(source))
    if len(matches)!=1:
        raise ValueError(f"{label}: expected one source label, got {len(matches)}")
    result=[]
    lines=source[matches[0].end():].splitlines()
    for line in lines:
        if not line.strip():
            if result: break
            continue
        if line.lstrip().startswith("@"):continue
        match=ASM_LINE_RE.fullmatch(line)
        if not match:break
        values=ASM_HEX_RE.findall(match.group(1))
        if not values or re.sub(r"(?:0x[0-9A-Fa-f]{2}|[\s,])+","",match.group(1)):
            raise ValueError(f"{label}: unexpected .byte syntax")
        result.extend(int(x,16) for x in values)
    if not result:
        raise ValueError(f"{label}: missing staged .byte payload")
    return bytes(result)


def extract_c_payload(source: str, label: str) -> bytes:
    if not LABEL_RE.fullmatch(label):
        raise ValueError("invalid source label")
    pat=re.compile(C_HEX_RE.pattern.format(label=re.escape(label)),C_HEX_RE.flags)
    matches=list(pat.finditer(source))
    if len(matches)!=1:
        raise ValueError(f"{label}: expected one C literal, got {len(matches)}")
    values=ASM_HEX_RE.findall(matches[0].group(1))
    if not values or re.sub(r"(?:0x[0-9A-Fa-f]{2}|[\s,])+","",matches[0].group(1)):
        raise ValueError(f"{label}: invalid compiled C byte list")
    return bytes(int(x,16) for x in values)


def validate_byte_string(payload: bytes, label: str):
    if len(payload)<2 or payload[-1]!=0xFF or 0xFF in payload[:-1]:
        raise ValueError(f"{label}: invalid or embedded terminal FF")
    for i,b in enumerate(payload):
        if b==0xFD and (i+1>=len(payload)-1 or payload[i+1]>0x2E):
            raise ValueError(f"{label}: unapproved dynamic/control byte")


def validate_stages(workspace:Path, reports:dict[str,dict]) -> dict:
    seen=set()
    sizes=[]
    kinds=Counter()
    for group,report in reports.items():
        rows=report.get("translated") if group!="dynamic" else report.get("accepted")
        if not isinstance(rows,list) or len(rows)!=report.get("labels_staged"):
            raise ValueError(f"{group}: report count does not match translated rows")
        if report.get("mode")!="apply":
            raise ValueError(f"{group}: dry-run report is not installed")
        for row in rows:
            label=row["label"]
            if label in seen:raise ValueError(f"{label}: duplicate source integration")
            seen.add(label)
            relative=row.get("source_file") or row.get("file")
            if group in ("ui","battle-c") and not relative:
                relative=report.get("source_file")
            if not relative or not isinstance(relative,str):
                raise ValueError(f"{label}: missing file")
            source_path=(workspace/relative).resolve()
            if not source_path.is_relative_to(workspace.resolve()) or not source_path.is_file():
                raise ValueError(f"{label}: missing or unsafe source file")
            if group in ("ui","battle-c"):
                if group=="ui" and relative!="src/strings.c":
                    raise ValueError("unexpected UI source file")
                if group=="battle-c" and relative!="src/battle_message.c":
                    raise ValueError("unexpected battle C source file")
                payload=extract_c_payload(source_path.read_text(encoding="utf-8"),label)
            else:
                if group=="battle" and not relative.startswith("data/text/"):
                    raise ValueError("battle source path wrong")
                if group in ("map","dynamic") and not relative.startswith("data/maps/"):
                    raise ValueError("map source path wrong")
                payload=extract_asm_payload(source_path.read_text(encoding="utf-8"),label)
            validate_byte_string(payload,label)
            sizes.append(len(payload))
            kinds[group]+=1
    if not sizes:raise ValueError("no source translations installed")
    return {"checked_unique_source_labels":len(seen),
            "source_groups":dict(kinds),
            "longest_encoded_payload":max(sizes),
            "all_labels_have_exact_terminal_ff":True,
            "cross_group_duplicates":0,
            "rom_modified":False,
            "emulator_tested":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    for group in ("map","ui","dynamic","battle","battle-c"):
        p.add_argument("--"+group,type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    reports={name:json.loads(getattr(a,name.replace("-","_")).read_text(encoding="utf-8"))
             for name in ("map","ui","dynamic","battle","battle-c")}
    output=validate_stages(a.workspace,reports)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
