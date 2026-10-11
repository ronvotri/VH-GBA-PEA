#!/usr/bin/env python3
"""Attest all previously verified 6005 labels and newly bounded names."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_page_bounded_system_dynamic import compile_source_pair,page_words
from stage_safe_system_dynamic_variables import VARIABLE_BYTES
from verify_safe_system_dynamic_variables import verify as verify_prior
from verify_zero_page_system_additive import read_reports,SYSTEM_REPORTS,MAP_REPORTS
from verify_compiled_source_strings import (
    validate_stages,extract_asm_payload,validate_byte_string,
)

PRIOR=SYSTEM_REPORTS+(
    "SOURCE_LITERAL_LF_SYSTEM_ADDITIVE_STAGE.json",
    "SOURCE_PAGED_LITERAL_LF_SYSTEM_ADDITIVE_STAGE.json",
    "SOURCE_SAFE_DYNAMIC_SYSTEM_ADDITIVE_STAGE.json",
)
NEW="SOURCE_PAGE_BOUNDED_SYSTEM_DYNAMIC_STAGE.json"


def verify(workspace:Path,artifact:Path,rom_path:Path,sym_path:Path,
           font_report:Path,headroom_report:Path,codebook_path:Path)->dict:
    previous=verify_prior(
        workspace,artifact,rom_path,sym_path,font_report,
        headroom_report,codebook_path)
    if (previous["total_compiled_source_labels"]!=6005
            or previous["new_pinned_dynamic_system_source_labels"]!=31
            or previous["system_source_owners_previously_attested"]!=1165):
        raise ValueError("previous 6005 source proof changed")
    system=read_reports(artifact,PRIOR,"data/text/")
    maps=read_reports(artifact,MAP_REPORTS,"data/maps/")
    old_system={(r["source_file"],r["label"])
                for a in system for r in a["translated"]}
    old_map={(r.get("source_file") or r.get("file"),r["label"])
             for a in maps for r in a.get("translated",a.get("accepted"))}
    if len(old_system)!=1196 or len(old_map)!=2867:
        raise ValueError("old source-owning label count changed")
    report=json.loads((artifact/NEW).read_text(encoding="utf-8"))
    rows=report.get("translated")
    n=len(rows) if isinstance(rows,list) else -1
    if (report.get("mode")!="apply" or not 0<=n<=750
            or report.get("labels_staged")!=n
            or report.get("previously_compiled_system_owner_exclusions")!=1196
            or not report.get("engine_KUN_empty_both_genders_verified")
            or not report.get("all_runtime_token_bytes_verified")
            or not report.get("all_authored_page_words_and_variables_preserved")
            or report.get("max_runtime_PLAYER_RIVAL_cells")!=7
            or report.get("raw_ROM_pointer_writes")!=0
            or report.get("v04_donor_font_changed")):
        raise ValueError("untrusted bounded dynamic report")
    if rows:
        test=validate_stages(workspace,{"system-text":report})
        if test["checked_unique_source_labels"]!=n:
            raise ValueError("new source owner validation failed")
    font_data=json.loads(codebook_path.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs={k:int(v,16) for k,v in font_data.items()}
    _,tokens=parse_charmap(workspace/"charmap.txt")
    if any(tokens.get(k)!=v for k,v in VARIABLE_BYTES.items()):
        raise ValueError("wrong named runtime variable bytes")
    rom=rom_path.read_bytes()
    addresses={}
    for addr,symbol in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_path.read_text(encoding="utf-8")
    ):
        addresses.setdefault(symbol,[]).append(int(addr,16))
    seen=set()
    for row in rows:
        name=(row.get("source_file"),row.get("label"))
        if (not name[0] or not name[1] or not name[0].startswith("data/text/")
                or name in seen or name in old_system or name in old_map):
            raise ValueError(f"duplicate/unsafe source owner {name}")
        seen.add(name)
        en,vi,compiled=row["english"],row["authored_vietnamese"],row["vietnamese"]
        if (row["source_page_count"]!=en.count(r"\p")+1
                or row.get("page_count")!=len(page_words(vi))
                or page_words(vi)!=page_words(compiled)):
            raise ValueError("Vietnamese words/page positions drifted")
        rendered,payload,pages=compile_source_pair(
            en,vi,glyphs,tokens,True,26)
        if rendered!=compiled or pages!=row.get("pages"):
            raise ValueError("independent native reflow does not match")
        source_path=(workspace/name[0]).resolve()
        if not source_path.is_relative_to(workspace.resolve()):
            raise ValueError("source owner escapes workspace")
        assembled=extract_asm_payload(
            source_path.read_text(encoding="utf-8"),name[1])
        validate_byte_string(assembled,name[1])
        if assembled!=payload:
            raise ValueError("compiled payload differs from expected GBA encoding")
        loc=addresses.get(name[1],[])
        if len(loc)!=1:
            raise ValueError(f"unlinked/ambiguous GBA symbol {name[1]}")
        pos=loc[0]-0x08000000
        if pos<0 or rom[pos:pos+len(payload)]!=payload:
            raise ValueError(f"ROM byte mismatch for translated source symbol {name[1]}")
    return {
        "already_compiled_source_labels":6005,
        "new_bounded_name_system_labels":n,
        "combined_source_compiled_labels":6005+n,
        "prior_system_source_owners_revalidated":1196,
        "prior_map_source_owners_revalidated":2867,
        "new_source_labels_byte_verified":n,
        "per_page_runtime_variable_sequence_and_words_preserved":True,
        "max_PLAYER_and_RIVAL_display_cells":7,
        "KUN_gender_suffix_is_empty_and_verified":True,
        "source_rom_sha256":previous["source_rom_sha256"],
        "rom_tail_headroom_bytes":previous["source_rom_tail_free_bytes"],
        "private_v04_font_applied":False,
        "emulator_qa":False,"release_ready":False,
    }


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--artifact",type=Path,required=True)
    p.add_argument("--rom",type=Path,required=True)
    p.add_argument("--sym",type=Path,required=True)
    p.add_argument("--font-audit",type=Path,required=True)
    p.add_argument("--headroom",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=verify(
        a.workspace,a.artifact,a.rom,a.sym,a.font_audit,a.headroom,a.codebook)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
