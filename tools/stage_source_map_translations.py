#!/usr/bin/env python3
"""Stage a bounded SOURCE-LEVEL map text smoke build, not a GBA ROM patch.

Labels stay unchanged so assembler/linker reallocate text and pointers. Strictly
check the pinned English .string bytes, codebook and line-length threshold.
The font/glyph table is still experimental; no runtime certification.
"""
from __future__ import annotations
import argparse, json, re, unicodedata
from collections import Counter
from pathlib import Path
from wrap_vietnamese_map_text import auto_wrap_script_text

LINE = re.compile(r'^(?P<indent>\s*)\.string\s+"(?P<value>.*)"\s*$')
CONTROLS = {"\\n":0xFE,"\\p":0xFB,"\\l":0xFA}


def encode_text(s: str, codes: dict[str,int], max_segment: int) -> bytes:
    if unicodedata.normalize("NFC",s) != s:
        raise ValueError("non-NFC text; review combining accents")
    encoded=bytearray(); i=0; segment=0
    while i<len(s):
        if s[i:i+2] in CONTROLS:
            encoded.append(CONTROLS[s[i:i+2]]); i+=2; segment=0
            continue
        if s[i]=="$":
            if i!=len(s)-1: raise ValueError("early terminator")
            encoded.append(0xFF); i+=1; continue
        if s[i] in "{}\\":
            raise ValueError(f"unsupported dynamic/escape token at {i}")
        ch=s[i]
        if ch not in codes: raise ValueError(f"missing Vietnamese glyph {ch!r}")
        value=codes[ch]
        if value in (0xFA,0xFB,0xFC,0xFD,0xFE,0xFF):
            raise ValueError(f"glyph {ch!r} collides with control byte")
        encoded.append(value);segment+=1;i+=1
        if segment>max_segment: raise ValueError(f"line exceeds {max_segment} encoded cells")
    if not encoded or encoded[-1]!=0xFF:
        raise ValueError("missing terminal $")
    return bytes(encoded)


def patch_labeled_block(source: str,label: str,expected_en: str,encoded: bytes)->str:
    lines=source.splitlines(keepends=True)
    indices=[i for i,line in enumerate(lines) if re.match(
        r"^"+re.escape(label)+r":{1,2}\s*(?:@[^\r\n]*)?$",line.strip())]
    if len(indices)!=1: raise ValueError(f"{label}: {len(indices)} source labels")
    start=indices[0]+1; pos=start; fragments=[]
    while pos<len(lines):
        match=LINE.match(lines[pos].rstrip("\r\n"))
        if not match:break
        fragments.append(match.group("value"));pos+=1
    if not fragments:raise ValueError(f"{label}: no contiguous .string directives")
    if "".join(fragments)!=expected_en:
        raise ValueError(f"{label}: English source is not exact pinned match")
    replacement=["\t.byte "+", ".join(f"0x{v:02X}" for v in encoded[j:j+16])+"\n"
                 for j in range(0,len(encoded),16)]
    lines[start:pos]=replacement
    return "".join(lines)


def prioritized_rows(rows: list[dict], prefixes: list[str]) -> list[dict]:
    """Stable ordering: earliest gameplay areas first, original order otherwise."""
    def rank(row):
        file = row.get("source_file", "")
        return next((i for i, prefix in enumerate(prefixes)
                     if file.startswith(prefix)), len(prefixes))
    return sorted(rows, key=rank)


def exclude_previously_staged(rows:list[dict],reports:list[dict])->tuple[list[dict],int]:
    """Skip only verified *apply* reports with a complete label/source identity.

    Used for incremental source-only experiments, NEVER as a proof that text
    reached a release ROM. A mismatched or incomplete report fails closed.
    """
    used=set()
    for report in reports:
        translated=report.get("translated")
        if (report.get("mode")!="apply" or not isinstance(translated,list)
                or report.get("labels_staged")!=len(translated)):
            raise ValueError("invalid previously staged source report")
        for row in translated:
            label=row.get("label")
            path=row.get("source_file")
            if not label or not path:
                raise ValueError("source report is missing source label identity")
            identity=(path,label)
            if identity in used:
                raise ValueError("duplicate label across exclusion reports")
            used.add(identity)
    return [r for r in rows if (r.get("source_file"),r.get("source_label")) not in used],len(used)


def exclude_explicit_source_labels(rows:list[dict],names:list[str],
                                   category:str,source_prefix:str)->list[dict]:
    """Protect a previously SHA-pinned source batch from new candidate priorities.

    Every requested exclusion must have exactly one full source owner; rejects
    missing/ambiguous labels instead of silently changing the selection.
    """
    if len(names)!=len(set(names)):
        raise ValueError("duplicate explicit source exclusion label")
    selected=set()
    for label in names:
        owned=[(row.get("source_file"),row.get("source_label"))
               for row in rows if row.get("source_label")==label
               and row.get("category")==category
               and row.get("source_file","").startswith(source_prefix)]
        if len(owned)!=1:
            raise ValueError(f"missing or ambiguous explicit source exclusion: {label}")
        selected.add(owned[0])
    return [row for row in rows
            if (row.get("source_file"),row.get("source_label")) not in selected]


def normalize_authored_linefeeds(english:str,vietnamese:str)->str:
    """Repair literal LF as GBA \\n ONLY if the ordered source controls agree.

    JSON authoring can accidentally store an actual newline in place of the
    two-character \\n script directive. No other control substitution is safe.
    This deliberately does not attempt to unwrap or rewrite dynamic tokens.
    """
    if "\n" not in vietnamese:
        return vietnamese
    normalized=vietnamese.replace("\n",r"\n")
    signature=lambda s:re.findall(r"\\[npl]",s)
    if signature(english)!=signature(normalized):
        raise ValueError("literal LF: source control sequence differs")
    return normalized


def plan_rows(rows:list,codes:dict[str,int],src_prefix:str,max_segment:int,limit:int,
              auto_wrap:bool=False, priority_prefixes:list[str]|None=None,
              category:str="map-story",normalize_literal_newlines:bool=False,
              only_literal_newlines:bool=False,page_scroll_reflow:bool=False):
    chosen=[]; rejected=Counter()
    for row in prioritized_rows(rows, priority_prefixes or []):
        if len(chosen)>=limit:break
        if row.get("category")!=category or not row.get("source_file","").startswith(src_prefix):
            continue
        english,vietnamese=row.get("english",""),row.get("vietnamese","")
        if only_literal_newlines and "\n" not in vietnamese:
            continue
        if not vietnamese or english==vietnamese or not row.get("source_label"):continue
        if normalize_literal_newlines and "\n" in vietnamese:
            try:
                normalized=normalize_authored_linefeeds(english,vietnamese)
            except ValueError as exc:
                rejected[str(exc)]+=1
                continue
            row=dict(row)
            row["authored_vietnamese"]=vietnamese
            row["vietnamese"]=vietnamese=normalized
            row["literal_newlines_normalized"]=True
        if page_scroll_reflow:
            # Fail closed: the authored GBA page/newline/scroll order must
            # already match the pinned English owner before layout adaptation.
            # Never let this mode process dynamic placeholders or raw LF.
            signature=lambda s:re.findall(r"\\[npl]",s)
            if (signature(english)!=signature(vietnamese) or
                    "{" in english or "}" in english or
                    "\n" in vietnamese):
                rejected["page-scroll: source controls/placeholder drift"]+=1
                continue
        try:payload=encode_text(vietnamese,codes,max_segment)
        except ValueError as exc:
            if auto_wrap and str(exc).startswith("line exceeds "):
                try:
                    wrapped=auto_wrap_script_text(
                        vietnamese,max_segment,
                        page_scroll_reflow=page_scroll_reflow)
                    payload=encode_text(wrapped,codes,max_segment)
                except ValueError as wrap_exc:
                    rejected["auto-wrap: "+str(wrap_exc)]+=1
                    continue
                row=dict(row)
                row["authored_vietnamese"]=row.get("authored_vietnamese",vietnamese)
                row["vietnamese"]=wrapped
                row["auto_wrapped"]=True
                if page_scroll_reflow:
                    # This is a source-verified layout adaptation, not a new
                    # translation or permission to change control/page order.
                    assert wrapped.count(r"\p")==vietnamese.count(r"\p")
                    row["page_scroll_reflowed"]=True
            else:
                rejected[str(exc)]+=1
                continue
        chosen.append((row,payload))
    return chosen,dict(rejected)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--source-prefix",default="data/maps/LittlerootTown/")
    p.add_argument("--category",choices=["map-story","battle","system-text"],default="map-story",help="Source text category, never infer from filenames")
    p.add_argument("--limit",type=int,default=20)
    p.add_argument("--max-segment",type=int,default=26)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--auto-wrap",action="store_true",help="Only word-boundary newline/scroll conversion for overlong non-dynamic text")
    p.add_argument("--page-scroll-reflow",action="store_true",
                   help="Opt-in: repair third visible line as native GBA scroll for source-pinned static system text; page breaks remain unchanged")
    p.add_argument("--normalize-literal-newlines",action="store_true",
                   help="Opt-in: change literal JSON LF to \\n only when ordered source controls match")
    p.add_argument("--only-literal-newlines",action="store_true",
                   help="Restrict selection to authored literal LF; requires --normalize-literal-newlines")
    p.add_argument("--exclude-report",type=Path,action="append",default=[],
                   help="Exclude exact label/source identities from a previously applied stage report")
    p.add_argument("--exclude-label",action="append",default=[],
                   help="Reserve exact owned source label for a later independent compilation stage")
    p.add_argument("--priority-source-prefix",action="append",default=[],help="Stable source-map priority for early-game QA; repeatable")
    a=p.parse_args()
    if a.limit<1 or a.limit>1000 or not 10<=a.max_segment<=30:
        p.error("limit 1..1000 and max-segment 10..30")
    if a.category in ("battle","system-text") and not a.source_prefix.startswith("data/text/"):
        p.error("battle/system-text source staging restricted to data/text/ assembly files")
    if a.only_literal_newlines and not a.normalize_literal_newlines:
        p.error("--only-literal-newlines requires --normalize-literal-newlines")
    if a.page_scroll_reflow and (a.category!="system-text" or
                                  not a.source_prefix.startswith("data/text/") or
                                  not a.auto_wrap or a.normalize_literal_newlines):
        p.error("--page-scroll-reflow requires static system-text, --auto-wrap, and no literal-LF normalization")

    plan=json.loads(a.plan.read_text(encoding="utf-8"))
    if a.exclude_label:
        try:
            plan=exclude_explicit_source_labels(
                plan,a.exclude_label,a.category,a.source_prefix)
        except ValueError as exc:
            p.error(str(exc))
    excluded_count=0
    if a.exclude_report:
        try:
            plan,excluded_count=exclude_previously_staged(
                plan,[json.loads(path.read_text(encoding="utf-8"))
                      for path in a.exclude_report])
        except ValueError as exc:
            p.error(str(exc))
    raw=json.loads(a.codebook.read_text(encoding="utf-8"))
    codes={c:int(v,16) for c,v in raw["glyph_bytes"].items()}
    selected, skipped=plan_rows(plan,codes,a.source_prefix,a.max_segment,a.limit,a.auto_wrap,a.priority_source_prefix,a.category,a.normalize_literal_newlines,a.only_literal_newlines,
                                  a.page_scroll_reflow)
    skipped=Counter(skipped); changes={}; accepted=[]
    for row, encoded in selected:
        relative=row["source_file"]
        filepath=(a.workspace/relative).resolve()
        if not filepath.is_relative_to(a.workspace.resolve()) or not filepath.is_file():
            skipped["missing/unsafe source file"]+=1;continue
        if filepath not in changes:
            changes[filepath]=filepath.read_text(encoding="utf-8")
        try:changed=patch_labeled_block(changes[filepath],row["source_label"],row["english"],encoded)
        except ValueError as exc:
            skipped[str(exc)]+=1;continue
        changes[filepath]=changed
        accepted.append({"label":row["source_label"],"source_file":relative,
                         "encoded_bytes":len(encoded),
                         "english":row["english"],"vietnamese":row["vietnamese"],
                         "authored_vietnamese":row.get("authored_vietnamese",row["vietnamese"]),
                         "auto_wrapped":bool(row.get("auto_wrapped")),
                         "page_scroll_reflowed":bool(row.get("page_scroll_reflowed")),
                         "literal_newlines_normalized":bool(row.get("literal_newlines_normalized"))})
    if a.apply:
        for filepath,updated in changes.items():
            filepath.write_text(updated,encoding="utf-8")
    report={"category":a.category,
            "mode":"apply" if a.apply else "dry-run",
            "source_prefix":a.source_prefix,"labels_staged":len(accepted),
            "previously_staged_label_exclusions":excluded_count,
            "explicit_owned_label_exclusions":len(a.exclude_label),
            "files_staged":len(changes),
            "auto_wrapped_labels":sum(1 for row in accepted if row["auto_wrapped"]),
            "page_scroll_reflowed_labels":sum(1 for row in accepted if row["page_scroll_reflowed"]),
            "literal_newlines_normalized":sum(1 for row in accepted if row["literal_newlines_normalized"]),
            "skipped_reasons":dict(skipped),
            "translated":accepted,"font_rendering_emulator_certified":False,
            "shipping_ROM_changed":False,
            "source_build_is_not_verified_shipping_layout":True}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="translated"},ensure_ascii=False,indent=2))


if __name__=="__main__":main()
