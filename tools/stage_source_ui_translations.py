#!/usr/bin/env python3
"""Stage only long, static, named src/strings.c UI messages for source rebuild.

Preserves C symbol identities and source-owned references. Does not patch ROM.
Uses the experimental v0.4 glyph byte codebook; font validation still pending.
"""
from __future__ import annotations
import argparse, json, re
from collections import Counter
from pathlib import Path

from stage_source_map_translations import encode_text
from wrap_vietnamese_map_text import auto_wrap_script_text


def replace_c_string(src: str, label: str, english: str, payload: bytes) -> str:
    if not re.fullmatch(r"gText_[A-Za-z0-9_]+",label):
        raise ValueError("unsupported C label")
    pattern = re.compile(
        r'(?m)^(?P<pre>[ \t]*const u8 '+re.escape(label)
        +r'\[\] = )_\("(?P<en>(?:\\.|[^"\\])*)"\);(?P<tail>[^\r\n]*)$')
    matches = list(pattern.finditer(src))
    if len(matches) != 1:
        raise ValueError("source label not unique")
    match = matches[0]
    if match.group("en") != english:
        raise ValueError("source text drift")
    if not payload or payload[-1] != 0xFF or 0xFF in payload[:-1]:
        raise ValueError("invalid string terminator")
    replacement = (
        match.group("pre")+"{"+", ".join("0x%02X" % x for x in payload)
        +"};"+match.group("tail"))
    return src[:match.start()]+replacement+src[match.end():]


def stage(rows:list, source:str, codes:dict[str,int],
          limit:int=30, max_segment:int=26, auto_wrap:bool=False):
    accepted=[]; skipped=Counter()
    for row in rows:
        if len(accepted)>=limit:
            break
        english=row.get("english","")
        translation=row.get("vietnamese","")
        label=row.get("source_label","")
        if (row.get("category")!="system-ui" or
            row.get("source_file")!="src/strings.c" or
            not label.startswith("gText_") or not translation or
            english==translation or len(english)<32 or
            not (r"\n" in english or r"\p" in english)):
            continue
        try:
            # C's _("...") source automatically adds the FF terminator.
            # Map .string manifests normally include $, C UI manifests do not.
            authored_with_end = translation if translation.endswith("$") else translation+"$"
            try:
                encoded=encode_text(authored_with_end,codes,max_segment)
                proposed=authored_with_end
            except ValueError as exc:
                if not auto_wrap or not str(exc).startswith("line exceeds "):
                    raise
                proposed=auto_wrap_script_text(authored_with_end,max_segment)
                encoded=encode_text(proposed,codes,max_segment)
            new_source=replace_c_string(source,label,english,encoded)
        except ValueError as exc:
            skipped[str(exc)]+=1
            continue
        source=new_source
        accepted.append({"label":label,"english":english,
                         "authored_vietnamese":translation,
                         "compiled_vietnamese":proposed,
                         "auto_wrapped":proposed!=authored_with_end,
                         "encoded_bytes":len(encoded)})
    return source,accepted,dict(skipped)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace",type=Path,required=True)
    ap.add_argument("--plan",type=Path,required=True)
    ap.add_argument("--codebook",type=Path,required=True)
    ap.add_argument("--limit",type=int,default=30)
    ap.add_argument("--max-segment",type=int,default=26)
    ap.add_argument("--auto-wrap",action="store_true")
    ap.add_argument("--apply",action="store_true")
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args()
    if not 1<=a.limit<=300 or not 10<=a.max_segment<=30:
        ap.error("limit 1..300 and max-segment 10..30")
    plan=json.loads(a.plan.read_text(encoding="utf-8"))
    raw=json.loads(a.codebook.read_text(encoding="utf-8"))
    codes={ch:int(value,16) for ch,value in raw["glyph_bytes"].items()}
    root=a.workspace.resolve()
    source_file=(root/"src/strings.c").resolve()
    if not source_file.is_relative_to(root) or not source_file.is_file():
        raise SystemExit("REFUSED: missing or unsafe source C file")
    source=source_file.read_text(encoding="utf-8")
    new_source,accepted,skipped=stage(
        plan,source,codes,a.limit,a.max_segment,a.auto_wrap)
    if a.apply:
        source_file.write_text(new_source,encoding="utf-8")
    report={"mode":"apply" if a.apply else "dry-run",
            "source_file":"src/strings.c","labels_staged":len(accepted),
            "auto_wrapped_labels":sum(v["auto_wrapped"] for v in accepted),
            "skipped_reasons":skipped,"translated":accepted,
            "font_emulator_validated":False,
            "rom_modified_by_tool":False}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="translated"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
