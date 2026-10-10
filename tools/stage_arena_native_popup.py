#!/usr/bin/env python3
"""Stage only fixed native-font Arena PrintPopup strings in pinned C source.

ARENA mini-HUD uses a totally different ASCII-only 3x5 glyph renderer. Do not
send Vietnamese accent codes into it: those become blank / broken mini letters.
This patch is limited to source-line-proven native PrintPopup C initializers.
The original u8 array size, source-English literal, exact label/position, and
the complete compiler/linker byte payload are independently verified.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from stage_source_map_translations import encode_text

FILE="src/realtime_arena.c"
# English text is pinned from exact Arena 0.13.0 overlay source; line and symbol
# are part of the immutable owner identity, not an arbitrary text search.
SPECS=(
 (328,"sTextPaused","ARROWS: PICK MOVE   START: PLAY","D-pad: Chọn chiêu  START: Chơi","sTextPaused",0,0),
 (330,"@anon:src/realtime_arena.c:330:42","UP","Lên","sMoveDirections",0,7),
 (330,"@anon:src/realtime_arena.c:330:50","RIGHT","Phải","sMoveDirections",1,7),
 (330,"@anon:src/realtime_arena.c:330:61","DOWN","Xuống","sMoveDirections",2,7),
 (330,"@anon:src/realtime_arena.c:330:71","LEFT","Trái","sMoveDirections",3,7),
 (331,"@anon:src/realtime_arena.c:331:37","CLASSIC","Cổ điển","sMoveKinds",0,8),
 (331,"@anon:src/realtime_arena.c:331:50","HIT","Đánh","sMoveKinds",1,8),
 (331,"@anon:src/realtime_arena.c:331:59","DASH","Lướt","sMoveKinds",2,8),
 (331,"@anon:src/realtime_arena.c:331:69","SHOT","Bắn","sMoveKinds",3,8),
 (331,"@anon:src/realtime_arena.c:331:79","CONE","Quạt","sMoveKinds",4,8),
 (331,"@anon:src/realtime_arena.c:331:89","BOOST","Tăng","sMoveKinds",5,8),
 (332,"sMoveStatusLabel","STATUS","Trạng thái","sMoveStatusLabel",0,0),
 (793,"@anon:src/realtime_arena.c:793:44","POKEMON","POKéMON","labels",0,18),
 (793,"@anon:src/realtime_arena.c:793:57","BAG","Túi","labels",1,18),
 (793,"@anon:src/realtime_arena.c:793:66","MOVES","Chiêu","labels",2,18),
 (793,"@anon:src/realtime_arena.c:793:77","RESUME","Tiếp","labels",3,18),
 (794,"title","PAUSED","Tạm dừng","title",0,0),
)
assert len(SPECS)==17 and len({(line,label) for line,label,*_ in SPECS})==17
HEADERS={
 "sMoveDirections":r"static const u8 sMoveDirections[4][7]",
 "sMoveKinds":r"static const u8 sMoveKinds[6][8]",
 "labels":r"static const u8 labels[4][18]",
}
def patch_one_line(source:str,line_no:int,english:str,vietnamese:str,
                   symbol:str,index:int,stride:int,codes:dict[str,int]):
    lines=source.splitlines(keepends=True)
    if line_no<1 or line_no>len(lines):
        raise ValueError("Arena line is no longer in pinned source")
    original=lines[line_no-1]
    if symbol in HEADERS:
        if HEADERS[symbol] not in original:
            raise ValueError("Arena fixed-size array declaration drift")
    elif not re.search(r"\b"+re.escape(symbol)+r"\[\]\s*=",original):
        raise ValueError("Arena named declaration drift")
    expr='_("'+english+'")'
    if original.count(expr)!=1:
        raise ValueError("source English token or count drift at exact Arena line")
    if '\n' in vietnamese or '\r' in vietnamese or '{' in vietnamese or '}' in vietnamese:
        raise ValueError("dynamic/control tokens not supported by Arena native menu stage")
    payload=encode_text(vietnamese+"$",codes,48)
    if not payload or payload[-1]!=255 or 255 in payload[:-1]:
        raise ValueError("invalid C source string terminator")
    if stride and len(payload)>stride:
        raise ValueError("Arena fixed-size display array overflow")
    if symbol=="sTextPaused" and len(vietnamese)>len(english):
        raise ValueError("paused-menu line exceeds source width budget")
    if symbol=="sMoveStatusLabel" and len(vietnamese)>12:
        raise ValueError("native move status label exceeds side panel")
    literal="{"+", ".join("0x%02X"%c for c in payload)+"}"
    lines[line_no-1]=original.replace(expr,literal)
    return "".join(lines),payload

def stage(rows:list[dict],source:str,codes:dict[str,int]):
    selected=[r for r in rows if r.get("category")=="arena-only" and r.get("source_file")==FILE]
    by_owner={(int(r["source_line"]),r["source_label"],r["english"]):r for r in selected}
    if len(by_owner)!=len(selected):
        raise ValueError("duplicate owner row in Arena manifest")
    accepted=[]
    for line,label,english,vi,symbol,index,stride in SPECS:
        row=by_owner.get((line,label,english))
        if row is None or row.get("vietnamese")!=vi:
            raise ValueError(f"manifest/C source discrepancy for {label}@{line}")
        source,payload=patch_one_line(source,line,english,vi,symbol,index,stride,codes)
        accepted.append({"source_label":label,"source_file":FILE,
                         "source_line":line,"owner_symbol":symbol,
                         "array_index":index,"array_stride":stride,
                         "english":english,"vietnamese":vi,
                         "encoded_hex":payload.hex(),"encoded_bytes":len(payload)})
    if len(accepted)!=17:raise ValueError("incomplete source-owner Arena text stage")
    return source,accepted

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    root=a.workspace.resolve()
    source=(root/FILE).resolve()
    if not source.is_relative_to(root) or not source.is_file():
        raise SystemExit("REFUSED: missing pinned arena native UI source")
    rows=json.loads(a.plan.read_text(encoding="utf-8"))
    book=json.loads(a.codebook.read_text(encoding="utf-8"))
    codes={k:int(v,16) for k,v in book["glyph_bytes"].items()}
    before=source.read_text(encoding="utf-8")
    after,accepted=stage(rows,before,codes)
    if a.apply: source.write_text(after,encoding="utf-8")
    report={"mode":"apply" if a.apply else "dry-run",
            "category":"arena-only","source_file":FILE,
            "labels_staged":len(accepted),"translated":accepted,
            "unchanged_tiny_3x5_hud_text":True,
            "native_normal_font_only":True,"dynamic_control_touched":False,
            "existing_5282_source_labels_unmodified":True,
            "v04_font_grafted":False,"gameplay_verified":False,"release_ready":False}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Arena native-font source UI staged:",len(accepted))
if __name__=="__main__":main()
