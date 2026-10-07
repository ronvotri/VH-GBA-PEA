#!/usr/bin/env python3
"""Restore shipping offsets from an exact historical verification checkpoint.

This does not inspect or modify a ROM. It is only valid when BOTH the current
catalog bytes and source-build ROM hash exactly match the checkpoint that was
previously verified against the clean shipping ROM.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--catalog",type=Path,required=True)
    ap.add_argument("--build-sha256-file",type=Path,required=True)
    ap.add_argument("--checkpoint",type=Path,required=True)
    ap.add_argument("--out-csv",type=Path,required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    ap.add_argument("--summary",type=Path,required=True)
    a=ap.parse_args()

    cp=json.loads(a.checkpoint.read_text(encoding="utf-8"))
    catalog_sha=sha256_file(a.catalog)
    if catalog_sha.lower()!=cp["source_catalog_sha256"].lower():
        raise SystemExit(f"Catalog hash mismatch: {catalog_sha}")

    build_hash=a.build_sha256_file.read_text(encoding="utf-8").strip().split()[0]
    if build_hash.lower()!=cp["source_build_rom_sha256"].lower():
        raise SystemExit(f"Build ROM hash mismatch: {build_hash}")

    with a.catalog.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    verified=cp["verified_categories"]
    counts=Counter(r.get("category","") for r in rows)
    for cat,expected in verified.items():
        if counts.get(cat,0)!=expected:
            raise SystemExit(f"{cat} count mismatch: {counts.get(cat,0)} != {expected}")

    restored=Counter()
    for r in rows:
        cat=r.get("category","")
        if cat not in verified:
            continue
        off=r.get("build_rom_offset","")
        if not off:
            raise SystemExit(f"Missing build offset for verified row {r.get('source_label')}")
        r["shipping_rom_offset"]=off
        r["shipping_match_status"]="verified:restored-from-exact-layout-checkpoint"
        restored[cat]+=1

    fields=list(rows[0].keys())
    a.out_csv.parent.mkdir(parents=True,exist_ok=True)
    with a.out_csv.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    a.out_json.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary={
        "schema_version":1,
        "catalog_sha256":catalog_sha,
        "source_build_rom_sha256":build_hash,
        "shipping_rom_sha256_attested":cp["shipping_rom_sha256"],
        "restored_verified_offsets":dict(restored),
        "safety":{"rom_modified":False,"pointer_scan":False,"pointer_writes":0,"mass_repoint":False}
    }
    a.summary.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
