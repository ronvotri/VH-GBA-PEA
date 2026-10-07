#!/usr/bin/env python3
"""Plan safe map/story integration. This never modifies a ROM."""
import argparse,csv,json
from collections import Counter
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--catalog",type=Path,required=True)
    ap.add_argument("--translations",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--summary",type=Path,required=True)
    a=ap.parse_args()
    vi={}; owner={}
    for p in sorted(a.translations.glob("*.vi.json")):
        d=json.loads(p.read_text(encoding="utf-8"))
        if d.get("scope")!="map-story": continue
        for label,text in (d.get("translations") or {}).items():
            if label in vi: raise SystemExit(f"duplicate translation: {label}")
            vi[label]=text; owner[label]=p.name
    with a.catalog.open(encoding="utf-8",newline="") as f:
        rows=[r for r in csv.DictReader(f) if r.get("category")=="map-story"]
    labels=[r["source_label"] for r in rows]
    dup=[k for k,v in Counter(labels).items() if v>1]
    missing=sorted(set(labels)-set(vi)); extra=sorted(set(vi)-set(labels))
    if len(rows)!=4361 or dup or missing or extra:
        raise SystemExit(f"coverage mismatch rows={len(rows)} dup={len(dup)} missing={len(missing)} extra={len(extra)}")
    plan=[]; status=Counter()
    for r in rows:
        off=r.get("shipping_rom_offset",""); match=r.get("shipping_match_status","")
        state="ready:verified-shipping-offset" if off and match.startswith("verified:") else "blocked:needs-shipping-resolution"
        status[state]+=1
        plan.append({"source_label":r["source_label"],"manifest":owner[r["source_label"]],"source_file":r.get("source_file",""),"english":r.get("english",""),"vietnamese":vi[r["source_label"]],"shipping_rom_offset":off,"shipping_match_status":match,"original_allocation_upper_bound":r.get("original_allocation_upper_bound",""),"reference_count":r.get("reference_count",""),"reference_sites":r.get("reference_sites",""),"catalog_patch_strategy":r.get("patch_strategy",""),"integration_status":state,"encoded_fit_status":"unresolved:needs-v0.4-vietnamese-byte-encoding","planned_binary_action":"defer-until-v0.4-encoder-and-verified-reference"})
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary={"catalog_map_story_rows":len(rows),"translation_labels":len(vi),"integration_status_counts":dict(status),"safety":{"rom_modified":False,"pointer_writes":0,"mass_repoint":False}}
    a.summary.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
