#!/usr/bin/env python3
"""Attest linker ownership and bounded dynamic-text placement in GBA ROM."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_safe_system_dynamic_variables import (
    VARIABLE_BYTES,encode,lines_with_matching_dynamic_slots,
)
from verify_compiled_source_strings import (
    extract_asm_payload,validate_byte_string,validate_stages,
)
from verify_paged_literal_lf_system_additive import attest as attest_previous
from verify_zero_page_system_additive import read_reports,SYSTEM_REPORTS,MAP_REPORTS

PRIOR_SYSTEM=SYSTEM_REPORTS+(
    "SOURCE_LITERAL_LF_SYSTEM_ADDITIVE_STAGE.json",
    "SOURCE_PAGED_LITERAL_LF_SYSTEM_ADDITIVE_STAGE.json",
)
NEW_REPORT="SOURCE_SAFE_DYNAMIC_SYSTEM_ADDITIVE_STAGE.json"


def verify(workspace:Path,artifact:Path,rom_file:Path,sym_file:Path,
           font_report:Path,headroom_report:Path,codebook:Path)->dict:
    prev=attest_previous(
        workspace,artifact,rom_file,sym_file,font_report,headroom_report)
    if (prev["total_compiled_source_labels"]!=5974
            or prev["new_page_local_literal_LF_system_labels"]!=0
            or prev["previous_system_source_labels_revalidated"]!=1165):
        raise ValueError("5974 prior source baseline changed")
    system_reports=read_reports(artifact,PRIOR_SYSTEM,"data/text/")
    map_reports=read_reports(artifact,MAP_REPORTS,"data/maps/")
    system_owners={(r["source_file"],r["label"])
                   for report in system_reports for r in report["translated"]}
    map_owners={(r.get("source_file") or r.get("file"),r["label"])
                for report in map_reports
                for r in report.get("translated",report.get("accepted"))}
    if len(system_owners)!=1165 or len(map_owners)!=2867:
        raise ValueError("baseline source owner set drift")
    stage=json.loads((artifact/NEW_REPORT).read_text(encoding="utf-8"))
    rows=stage.get("translated")
    n=len(rows) if isinstance(rows,list) else -1
    if (stage.get("mode")!="apply" or not 0<=n<=750
            or stage.get("labels_staged")!=n
            or stage.get("previously_compiled_system_owner_exclusions")!=1165
            or not stage.get("variable_bytes_pinned_to_source_charmap")
            or not stage.get("variable_names_and_native_lines_preserved")
            or stage.get("static_line_expansion_admitted")
            or stage.get("raw_rom_pointer_writes")!=0
            or stage.get("font_art_modified")):
        raise ValueError("unsafe dynamic variable report")
    if n:
        source_check=validate_stages(workspace,{"system-text":stage})
        if source_check["checked_unique_source_labels"]!=n:
            raise ValueError("new dynamic label source verification failed")
    glyphs={
        char:int(code,16) for char,code
        in json.loads(codebook.read_text(encoding="utf-8"))["glyph_bytes"].items()
    }
    _,tokens=parse_charmap(workspace/"charmap.txt")
    for key,value in VARIABLE_BYTES.items():
        if tokens.get(key)!=value:
            raise ValueError("unverified engine charmap runtime token")
    rom=rom_file.read_bytes()
    addresses={}
    for addr,label in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_file.read_text(encoding="utf-8")
    ):
        addresses.setdefault(label,[]).append(int(addr,16))
    seen=set()
    for row in rows:
        file,label=row.get("source_file"),row.get("label")
        owner=(file,label)
        if (not file or not label or not file.startswith("data/text/")
                or owner in seen or owner in system_owners or owner in map_owners):
            raise ValueError(f"unexpected or duplicate dynamic source owner {owner}")
        seen.add(owner)
        en,vi=row["english"],row["vietnamese"]
        if row.get("segments")!=lines_with_matching_dynamic_slots(en,vi):
            raise ValueError(f"dynamic footprint/controls changed {owner}")
        expected=encode(vi,glyphs,tokens)
        file_path=(workspace/file).resolve()
        if not file_path.is_relative_to(workspace.resolve()):
            raise ValueError("source outside workspace")
        actual=extract_asm_payload(file_path.read_text(encoding="utf-8"),label)
        validate_byte_string(actual,label)
        if expected!=actual:
            raise ValueError(f"source encoded dynamic bytes mismatch {owner}")
        matching=addresses.get(label,[])
        if len(matching)!=1:
            raise ValueError(f"ambiguous/missing symbol {label}")
        off=matching[0]-0x08000000
        if off<0 or rom[off:off+len(expected)]!=expected:
            raise ValueError(f"ROM linked dynamic bytes mismatched {owner}")
    return {
        "previously_compiled_source_labels":5974,
        "new_pinned_dynamic_system_source_labels":n,
        "total_compiled_source_labels":5974+n,
        "system_source_owners_previously_attested":1165,
        "map_source_owners_previously_attested":2867,
        "new_dynamic_source_owners_linked_byte_verified":n,
        "all_runtime_variable_bytes_pinned":True,
        "native_line_and_page_layout_preserved":True,
        "every_new_static_line_nonexpanding":True,
        "source_rom_sha256":prev["source_ROM_sha256"],
        "source_rom_tail_free_bytes":prev["tail_free_bytes"],
        "approved_v04_visual_font_imported":False,
        "emulator_QA":False,"release_ready":False,
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
    result=verify(a.workspace,a.artifact,a.rom,a.sym,
                  a.font_audit,a.headroom,a.codebook)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
