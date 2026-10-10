#!/usr/bin/env python3
"""Fail-closed source- and linker-owned QA for additive static battle dialogs.

The release baseline is NOT altered; all messages are compiled from source in
an isolated 5299-source-labelled tree with unchanged GBA font banks.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

from verify_compiled_source_strings import validate_stages, extract_asm_payload

ARTIFACT=Path("artifact")
TRIAL=Path("battle-scroll-source-trial")
NEW="SOURCE_BATTLE_SCROLL_REFLOW_STAGE.json"
ATTEST="SOURCE_BATTLE_SCROLL_REFLOW_ATTESTATION.json"
SYM="SOURCE_BATTLE_SCROLL_REFLOW_FONT.sym"
OTHER=(
    "SOURCE_LEVEL_BATTLE_C_PILOT.json",
    "SOURCE_SYSTEM_TEXT_STAGE.json",
    "SOURCE_BIRCH_NARRATIVE_STAGE.json",
    "SOURCE_BIRCH_DYNAMIC_STAGE.json",
    "SOURCE_SYSTEM_TEXT_SECOND_STAGE.json",
    "SOURCE_SYSTEM_SCROLL_REFLOW_STAGE.json",
    "SOURCE_MAP_SCROLL_REFLOW_STAGE.json",
)
BASE_SOURCE_COUNT=5299
OLD_BATTLE_COUNT=196


def read(name:str)->dict:
    return json.loads((ARTIFACT/name).read_text(encoding="utf-8"))


def source_signature(value:str)->list[str]:
    return re.findall(r"\\[npl]",value)


def visible_words(value:str)->list[str]:
    assert value.endswith("$"),value
    return re.sub(r"\\[npl]"," ",value[:-1]).split()


def verify_pre()->None:
    old=read("SOURCE_LEVEL_BATTLE_PILOT.json")
    new=read(NEW)
    prior=read("SOURCE_ARENA_NATIVE_POPUP_ATTESTATION.json")
    n=new["labels_staged"]
    assert prior["combined_source_compiled_labels"]==BASE_SOURCE_COUNT,prior
    assert old["mode"]=="apply" and old["labels_staged"]==OLD_BATTLE_COUNT,old
    assert new["mode"]=="apply" and new["category"]=="battle",new
    assert new["previously_staged_label_exclusions"]==OLD_BATTLE_COUNT,new
    assert 20<=n<=1000,("no safe additional battle strings",new["skipped_reasons"])
    assert len(new["translated"])==n,new
    assert new["page_scroll_reflowed_labels"]==n,new
    old_labels={row["label"] for row in old["translated"]}
    new_labels={row["label"] for row in new["translated"]}
    assert len(old_labels)==OLD_BATTLE_COUNT and len(new_labels)==n
    other_labels=set()
    for fn in OTHER:
        obj=read(fn)
        rows=obj["translated"]
        assert obj["mode"]=="apply" and len(rows)==obj["labels_staged"],fn
        other_labels.update(row["label"] for row in rows)
    assert not new_labels.intersection(old_labels|other_labels),"duplicate prior source label"
    for row in new["translated"]:
        assert row["source_file"].startswith("data/text/"),row
        assert row["auto_wrapped"] and row["page_scroll_reflowed"],row
        before=row["authored_vietnamese"]
        after=row["vietnamese"]
        english=row["english"]
        assert "{" not in english and "{" not in before and "{" not in after,row
        assert source_signature(english)==source_signature(before),row["label"]
        assert visible_words(before)==visible_words(after),row["label"]
        assert before.count(r"\p")==after.count(r"\p"),row["label"]
    verified=validate_stages(TRIAL,{"battle":new})
    assert verified["checked_unique_source_labels"]==n,verified
    pair=validate_stages(TRIAL,{"old_battle":old,"new_battle":new})
    assert pair["checked_unique_source_labels"]==OLD_BATTLE_COUNT+n,pair
    result={
        "previous_source_compiled_labels":BASE_SOURCE_COUNT,
        "new_unique_static_battle_labels":n,
        "combined_source_compiled_labels":BASE_SOURCE_COUNT+n,
        "prior_assembly_battle_labels_excluded":OLD_BATTLE_COUNT,
        "no_cross_stage_label_duplicates":True,
        "english_control_order_preserved":True,
        "word_order_and_page_breaks_preserved":True,
        "staged_source_bytes_verified":True,
        "all_new_ROM_linker_payloads_verified":False,
        "tiny_ASCII_HUD_untouched":True,
        "stock_fonts_only":True,
        "v04_font_grafted":False,
        "battle_gameplay_tested":False,
        "release_ready":False,
    }
    (ARTIFACT/ATTEST).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PASS additive static battle source stage:",n,"new labels; total",BASE_SOURCE_COUNT+n)


def verify_post()->None:
    result=read(ATTEST)
    stage=read(NEW)
    n=stage["labels_staged"]
    assert result["new_unique_static_battle_labels"]==n,result
    rom=(TRIAL/"pokeemerald.gba").read_bytes()
    symbols=(ARTIFACT/SYM).read_text(encoding="utf-8")
    found:dict[str,list[int]]={}
    for addr,name in re.findall(r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",symbols):
        found.setdefault(name,[]).append(int(addr,16))
    for row in stage["translated"]:
        name=row["label"]
        addresses=found.get(name,[])
        assert len(addresses)==1,(name,addresses)
        addr=addresses[0]
        assert 0x08000000<=addr<0x0A000000,(name,addr)
        payload=extract_asm_payload((TRIAL/row["source_file"]).read_text(encoding="utf-8"),name)
        offset=addr-0x08000000
        assert rom[offset:offset+len(payload)]==payload,("linked GBA battle bytes differ",name)
    result["all_new_ROM_linker_payloads_verified"]=True
    result["actual_GBA_linker_payloads_checked"]=n
    (ARTIFACT/ATTEST).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PASS exact battle GBA ROM/linker payloads:",n)


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("phase",choices=("pre","post"))
    args=parser.parse_args()
    if args.phase=="pre":
        verify_pre()
    else:
        verify_post()

if __name__=="__main__":
    main()
