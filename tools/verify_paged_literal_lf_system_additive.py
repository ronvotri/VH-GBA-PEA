#!/usr/bin/env python3
"""Independently verify paginated LF additions and all pre-existing owners.

Only source-linked ELF/GBA bytes and original-word/page preservation qualify.
The previously approved v0.4 Vietnamese donor art is NOT in the source ROM.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from stage_source_map_translations import normalize_authored_linefeeds
from stage_static_paged_map_dialogues import page_words
from verify_compiled_source_strings import (
    extract_asm_payload,validate_byte_string,validate_stages,
)
from verify_literal_lf_system_additive import attest as attest_prior
from verify_zero_page_system_additive import read_reports,MAP_REPORTS,SYSTEM_REPORTS

PRIOR_SYSTEM = SYSTEM_REPORTS+("SOURCE_LITERAL_LF_SYSTEM_ADDITIVE_STAGE.json",)
NEW_REPORT = "SOURCE_PAGED_LITERAL_LF_SYSTEM_ADDITIVE_STAGE.json"


def attest(workspace:Path,artifact:Path,rom_file:Path,sym_file:Path,
           font_report:Path,space_report:Path)->dict:
    prior=attest_prior(
        workspace,artifact,rom_file,sym_file,font_report,space_report)
    if (prior["total_source_compiled_labels"]!=5974
            or prior["new_native_LF_normalized_system_labels"]!=5):
        raise ValueError("5974 source baseline not confirmed")
    reports=read_reports(artifact,PRIOR_SYSTEM,"data/text/")
    map_reports=read_reports(artifact,MAP_REPORTS,"data/maps/")
    system_owners={(r["source_file"],r["label"])
                   for stage in reports for r in stage["translated"]}
    map_owners={(r.get("source_file") or r.get("file"),r["label"])
                for stage in map_reports
                for r in stage.get("translated",stage.get("accepted"))}
    if len(system_owners)!=1165 or len(map_owners)!=2867:
        raise ValueError("previous source owner count drift")
    report=json.loads((artifact/NEW_REPORT).read_text(encoding="utf-8"))
    rows=report.get("translated")
    n=len(rows) if isinstance(rows,list) else -1
    if (report.get("mode")!="apply"
            or report.get("labels_staged")!=n or not 0<=n<=300
            or report.get("previously_compiled_system_owner_exclusions")!=1165
            or not report.get("source_control_signature_verified")
            or not report.get("all_authored_page_words_preserved")
            or report.get("raw_ROM_pointer_writes")!=0
            or report.get("runtime_variables_admitted")
            or report.get("unapproved_glyphs_admitted")):
        raise ValueError("new system paged LF stage contract failed")
    if rows:
        independent=validate_stages(workspace,{"system-text":report})
        if independent["checked_unique_source_labels"]!=n:
            raise ValueError("new source labels cannot be independently verified")
    rom=rom_file.read_bytes()
    symbols={}
    for addr,name in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_file.read_text(encoding="utf-8")
    ):
        symbols.setdefault(name,[]).append(int(addr,16))
    new_owners=set()
    for row in rows:
        file=row.get("source_file")
        label=row.get("label")
        owner=(file,label)
        if (not file or not label or not file.startswith("data/text/")
                or owner in new_owners or owner in system_owners
                or owner in map_owners):
            raise ValueError(f"duplicate or unsafe new owner {owner}")
        new_owners.add(owner)
        english=row["english"]
        authored=row["authored_vietnamese"]
        norm=row["normalized_vietnamese"]
        linked=row["vietnamese"]
        if (authored.count("\n")<1
                or row.get("raw_LF_count")!=authored.count("\n")
                or r"\p" not in english
                or norm!=normalize_authored_linefeeds(english,authored)
                or row.get("source_page_count")!=english.count(r"\p")+1
                or row.get("authored_page_count")!=len(page_words(english,norm))
                or page_words(english,linked)!=page_words(english,norm)
                or row.get("page_word_counts")!=[
                    len(chunk) for chunk in page_words(english,norm)]):
            raise ValueError(f"authored page content/control drift: {owner}")
        path=(workspace/file).resolve()
        if not path.is_relative_to(workspace.resolve()):
            raise ValueError("path outside authorized workspace")
        payload=extract_asm_payload(path.read_text(encoding="utf-8"),label)
        validate_byte_string(payload,label)
        addresses=symbols.get(label,[])
        if len(addresses)!=1:
            raise ValueError(f"ambiguous ELF label {label}")
        offset=addresses[0]-0x08000000
        if offset<0 or rom[offset:offset+len(payload)]!=payload:
            raise ValueError(f"linked GBA byte mismatch {owner}")
    return {
        "previously_compiled_source_labels":5974,
        "new_page_local_literal_LF_system_labels":n,
        "total_compiled_source_labels":5974+n,
        "previous_system_source_labels_revalidated":1165,
        "previous_map_source_labels_revalidated":2867,
        "new_source_labels_individually_linked":n,
        "all_original_system_and_map_payloads_revalidated":True,
        "native_page_controls_and_authored_words_preserved":True,
        "source_ROM_sha256":prior["source_ROM_sha256"],
        "tail_free_bytes":prior["rom_contiguous_tail_bytes"],
        "approved_v04_font_grafted":False,
        "emulator_gameplay_tested":False,
        "release_ready":False,
    }


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--artifact",type=Path,required=True)
    p.add_argument("--rom",type=Path,required=True)
    p.add_argument("--sym",type=Path,required=True)
    p.add_argument("--font-audit",type=Path,required=True)
    p.add_argument("--headroom",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    data=attest(a.workspace,a.artifact,a.rom,a.sym,a.font_audit,a.headroom)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(data,indent=2))


if __name__=="__main__":
    main()
