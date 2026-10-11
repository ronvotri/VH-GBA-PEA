#!/usr/bin/env python3
"""Page-local, name-width-verified reflow for source-owned dynamic system text.

Only known runtime widths: PLAYER/RIVAL <= 7, KUN = 0 (with Birch engine
verification). Unknown STR_VAR expansions are excluded, never guessed.
Preserves every authored Vietnamese word and variable sequence inside its
original GBA page; only \n/\l line layout may be regenerated.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_birch_dynamic_intro import verify_engine
from stage_safe_system_dynamic_variables import encode, VARIABLE_BYTES, TOKEN
from stage_source_map_translations import patch_labeled_block, prioritized_rows
from stage_static_paged_system_text import exclude_source_owners

KNOWN_WIDTH={"PLAYER":7,"RIVAL":7,"KUN":0}
LAYOUT=re.compile(r"\\[nl]")
ESCAPE=re.compile(r"\\[npl]")
QUOTED_WORD=re.compile(r'“[^”]*”[.,!?]?|[^ ]+')


def page_words(text:str)->list[list[str]]:
    if (not text.endswith("$") or text.count("$")!=1
            or unicodedata.normalize("NFC",text)!=text
            or any(ch in text for ch in "\n\r\t")):
        raise ValueError("malformed source/translated text")
    pages=text[:-1].split(r"\p")
    if not pages or any(not page for page in pages):
        raise ValueError("empty source/translation page")
    output=[]
    for page in pages:
        stripped=LAYOUT.sub(" ",page)
        rest=TOKEN.sub("",stripped)
        if any(x in rest for x in "{}\\"):
            raise ValueError("unknown escape or invalid dynamic markup")
        words=stripped.split()
        if not words:
            raise ValueError("empty text page")
        if page.startswith(" ") or page.endswith(" ") or "  " in page:
            raise ValueError("ambiguous whitespace in text")
        output.append(words)
    return output


def render_width(token:str)->int:
    spans=list(TOKEN.finditer(token))
    tail=TOKEN.sub("",token)
    if any(x in tail for x in "{}\\"):
        raise ValueError("unsupported token in word")
    widths=0
    for match in spans:
        key=match.group(1)
        if key not in KNOWN_WIDTH:
            raise ValueError(f"unknown expansion width: {key}")
        widths+=KNOWN_WIDTH[key]
    return len(tail)+widths


def wrap_page(words:list[str],width:int=26,max_lines:int=12)->tuple[str,int]:
    if not 10<=width<=30 or not 1<=max_lines<=12:
        raise ValueError("unsafe layout limits")
    lines=[];current="";cells=0
    for word in words:
        n=render_width(word)
        if n>width:
            raise ValueError("one quoted word exceeds maximum line")
        if not current:
            current=word;cells=n
        elif cells+1+n<=width:
            current+=" "+word
            cells+=1+n
        else:
            lines.append(current)
            current=word;cells=n
        if len(lines)>=max_lines:
            raise ValueError("too many native scroll lines")
    if current:
        lines.append(current)
    rendered=lines[0]+("".join(
        (r"\n" if i==1 else r"\l")+line
        for i,line in enumerate(lines[1:],1)))
    if LAYOUT.sub(" ",rendered).split()!=words:
        raise ValueError("page-local original words changed")
    return rendered,len(lines)


def compile_source_pair(en:str,vi:str,glyphs:dict[str,int],
                        tokens:dict[str,bytes],kun_verified:bool,
                        width:int=26)->tuple[str,bytes,list[dict]]:
    engl_pages=page_words(en)
    vi_pages=page_words(vi)
    if len(engl_pages)!=len(vi_pages):
        raise ValueError("GBA page boundaries changed")
    en_raw=en[:-1].split(r"\p")
    vi_raw=vi[:-1].split(r"\p")
    descriptions=[]
    rendered_pages=[]
    dynamic_found=False
    for en_p,vi_p,words in zip(en_raw,vi_raw,vi_pages):
        original_tokens=TOKEN.findall(en_p)
        target_tokens=TOKEN.findall(vi_p)
        if original_tokens!=target_tokens:
            raise ValueError("dynamic variable identity/order moved across page")
        if any(x not in KNOWN_WIDTH for x in original_tokens):
            raise ValueError("unverified runtime expansion width")
        if "KUN" in original_tokens and not kun_verified:
            raise ValueError("KUN blank-suffix engine state unverified")
        dynamic_found=dynamic_found or bool(original_tokens)
        compiled,lines=wrap_page(words,width)
        if TOKEN.findall(compiled)!=original_tokens:
            raise ValueError("reflow reordered a runtime placeholder")
        descriptions.append({
            "variables":original_tokens,
            "authored_words":len(words),
            "native_lines":lines,
            "page_words_preserved":True,
        })
        rendered_pages.append(compiled)
    if not dynamic_found:
        raise ValueError("no supported dynamic variables")
    compiled=r"\p".join(rendered_pages)+"$"
    if page_words(compiled)!=vi_pages or compiled.count(r"\p")!=en.count(r"\p"):
        raise ValueError("authored words or native page controls drifted")
    payload=encode(compiled,glyphs,tokens)
    return compiled,payload,descriptions


def stage(rows:list[dict],sources:dict[str,str],glyphs:dict[str,int],
          tokens:dict[str,bytes],kun_verified:bool,
          limit:int=750,width:int=26)->tuple[dict,list[dict],dict]:
    if not 1<=limit<=1000:
        raise ValueError("invalid candidate limit")
    for key,value in VARIABLE_BYTES.items():
        if tokens.get(key)!=value:
            raise ValueError(f"unverified runtime charmap: {key}")
    accepted=[];skipped=Counter();seen=set()
    priority=[
        "data/text/birch_speech.inc","data/text/pkmn_center_nurse.inc",
        "data/text/trainers.inc","data/text/match_call.inc",
    ]
    for row in prioritized_rows(rows,priority):
        if len(accepted)>=limit:break
        path=row.get("source_file","")
        label=row.get("source_label","")
        en=row.get("english","")
        vi=row.get("vietnamese","")
        if (row.get("category")!="system-text"
                or not path.startswith("data/text/")
                or not path.endswith(".inc")
                or not label or not en or not vi or en==vi
                or "{" not in en):
            continue
        owner=(path,label)
        if owner in seen:
            raise ValueError(f"duplicate source manifest owner {owner}")
        seen.add(owner)
        if path not in sources:
            skipped["source file not present in workspace"]+=1
            continue
        try:
            text,payload,pages=compile_source_pair(
                en,vi,glyphs,tokens,kun_verified,width)
            changed=patch_labeled_block(sources[path],label,en,payload)
        except ValueError as e:
            skipped[str(e)]+=1
            continue
        sources[path]=changed
        accepted.append({
            "source_file":path,"label":label,"english":en,
            "authored_vietnamese":vi,"vietnamese":text,
            "pages":pages,"page_count":len(pages),
            "source_page_count":en.count(r"\p")+1,
            "page_local_words_and_variable_order_preserved":True,
            "known_runtime_variable_max_widths":True,
            "encoded_bytes":len(payload),
        })
    return sources,accepted,dict(skipped)


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--exclude-report",type=Path,action="append",required=True)
    p.add_argument("--limit",type=int,default=750)
    p.add_argument("--width",type=int,default=26)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    root=a.workspace.resolve()
    plan=json.loads(a.plan.read_text(encoding="utf-8"))
    prev=[json.loads(x.read_text(encoding="utf-8")) for x in a.exclude_report]
    plan,excluded=exclude_source_owners(plan,prev)
    _,tokens=parse_charmap(root/"charmap.txt")
    verify_engine(
        (root/"charmap.txt").read_text(encoding="utf-8"),
        (root/"src/strings.c").read_text(encoding="utf-8"))
    book=json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs={ch:int(byte,16) for ch,byte in book.items()}
    wanted={
        r.get("source_file") for r in plan
        if r.get("category")=="system-text"
        and r.get("source_file","").startswith("data/text/")
        and r.get("source_file","").endswith(".inc")
        and "{" in r.get("english","")
    }
    sources={}
    for file in sorted(wanted):
        src=(root/file).resolve()
        if not src.is_relative_to(root):
            raise ValueError("source path outside workspace")
        if src.is_file():
            sources[file]=src.read_text(encoding="utf-8")
    original=dict(sources)
    out,rows,skipped=stage(
        plan,sources,glyphs,tokens,True,a.limit,a.width)
    if a.apply:
        for filename,content in out.items():
            if content!=original[filename]:
                (root/filename).write_text(content,encoding="utf-8")
    report={
        "mode":"apply" if a.apply else "dry-run",
        "category":"system-text",
        "selection":"source_page_locked_bounded_PLAYER_RIVAL_KUN_reflow",
        "labels_staged":len(rows),
        "previously_compiled_system_owner_exclusions":excluded,
        "source_files_staged":sum(out[k]!=original[k] for k in original),
        "engine_KUN_empty_both_genders_verified":True,
        "all_runtime_token_bytes_verified":True,
        "all_authored_page_words_and_variables_preserved":True,
        "max_runtime_PLAYER_RIVAL_cells":7,
        "raw_ROM_pointer_writes":0,
        "v04_donor_font_changed":False,
        "emulator_QA":False,
        "release_ready":False,
        "skipped_reasons":skipped,"translated":rows,
    }
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                        encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="translated"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
