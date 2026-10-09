#!/usr/bin/env python3
"""Strict source-first battle-message C translation staging (NO ROM pointer edits).

Only complete, static, variable-free messages in the pinned src/battle_message.c
are eligible. Source English and C label must match exactly. Dynamic templates
with {B_*} require separate semantics/width handling and are not touched.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from stage_source_map_translations import encode_text
from wrap_vietnamese_map_text import auto_wrap_script_text


def replace_battle_c_literal(source:str,label:str,english:str,payload:bytes)->str:
    if not re.fullmatch(r"(?:sText|gText)_[A-Za-z0-9_]+",label):
        raise ValueError("invalid battle C label")
    pattern=re.compile(
        r'(?m)^(?P<head>[ \t]*(?:(?:static|const)\s+)*const\s+u8\s+'
        +re.escape(label)
        +r'\[\]\s*=\s*)_\("(?P<english>(?:\\.|[^"\\])*)"\);(?P<trail>[^\r\n]*)$'
    )
    matches=list(pattern.finditer(source))
    if len(matches)!=1:
        raise ValueError("missing or duplicate battle C symbol")
    m=matches[0]
    if m.group("english")!=english:
        raise ValueError("battle C English source drift")
    if len(payload)<2 or payload[-1]!=0xFF or 0xFF in payload[:-1]:
        raise ValueError("invalid battle C terminator")
    initializer="{"+", ".join(f"0x{byte:02X}" for byte in payload)+"}"
    return source[:m.start()]+m.group("head")+initializer+";"+m.group("trail")+source[m.end():]


def stage_battle_messages(rows:list[dict],source:str,codes:dict[str,int],
                          limit:int=80,max_segment:int=26,auto_wrap:bool=False):
    accepted=[];skipped=Counter()
    for row in rows:
        if len(accepted)>=limit:
            break
        if row.get("category")!="battle" or row.get("source_file")!="src/battle_message.c":
            continue
        english=row.get("english","")
        authored=row.get("vietnamese","")
        label=row.get("source_label","")
        if not english or not authored or english==authored:
            continue
        # Deliberately skip fragments concatenated with runtime names, prefixes
        # and all variable-width battle buffers / engine pause or color tokens.
        if "{" in english or "}" in english or "{" in authored or "}" in authored:
            skipped["dynamic/engine control token"]+=1
            continue
        if (len(english)<11 or english!=english.strip() or
                authored!=authored.strip() or
                not english[0].isupper()):
            skipped["short or concatenated battle fragment"]+=1
            continue
        if english.count(r"\p")!=authored.count(r"\p"):
            skipped["battle page-control count changed"]+=1
            continue
        try:
            with_end=authored if authored.endswith("$") else authored+"$"
            try:
                payload=encode_text(with_end,codes,max_segment)
                compiled=with_end
            except ValueError as exc:
                if not auto_wrap or not str(exc).startswith("line exceeds "):
                    raise
                compiled=auto_wrap_script_text(with_end,max_segment)
                payload=encode_text(compiled,codes,max_segment)
            updated=replace_battle_c_literal(source,label,english,payload)
        except ValueError as exc:
            skipped[str(exc)]+=1
            continue
        source=updated
        accepted.append({"label":label,"source_file":"src/battle_message.c",
                         "english":english,"authored_vietnamese":authored,
                         "compiled_vietnamese":compiled,
                         "encoded_bytes":len(payload),
                         "auto_wrapped":compiled!=with_end})
    return source,accepted,dict(skipped)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace",type=Path,required=True)
    ap.add_argument("--plan",type=Path,required=True)
    ap.add_argument("--codebook",type=Path,required=True)
    ap.add_argument("--limit",type=int,default=80)
    ap.add_argument("--max-segment",type=int,default=26)
    ap.add_argument("--auto-wrap",action="store_true")
    ap.add_argument("--apply",action="store_true")
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args()
    if not 1<=a.limit<=200 or not 10<=a.max_segment<=30:
        ap.error("limit 1..200; max-segment 10..30")
    plan=json.loads(a.plan.read_text(encoding="utf-8"))
    book=json.loads(a.codebook.read_text(encoding="utf-8"))
    codes={ch:int(value,16) for ch,value in book["glyph_bytes"].items()}
    workspace=a.workspace.resolve()
    path=(workspace/"src/battle_message.c").resolve()
    if not path.is_relative_to(workspace) or not path.is_file():
        raise SystemExit("REFUSED: missing pinned C battle source")
    source=path.read_text(encoding="utf-8")
    replacement,accepted,rejected=stage_battle_messages(
        plan,source,codes,a.limit,a.max_segment,a.auto_wrap)
    if a.apply:
        path.write_text(replacement,encoding="utf-8")
    report={"mode":"apply" if a.apply else "dry-run",
            "source_file":"src/battle_message.c",
            "labels_staged":len(accepted),
            "auto_wrapped_labels":sum(row["auto_wrapped"] for row in accepted),
            "skipped_reasons":rejected,
            "translated":accepted,
            "battle_variables_touched":False,
            "battle_font_rendering_tested":False,
            "rom_modified_by_tool":False}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                        encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="translated"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
