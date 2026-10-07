#!/usr/bin/env python3
"""Validate catalog-driven Vietnamese translation manifests."""
from __future__ import annotations
import argparse, csv, gzip, json, re
from collections import Counter
from pathlib import Path

BRACE_RE = re.compile(r"\{[^{}]+\}")

def load_json(path: Path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--translations", type=Path, required=True)
    args=ap.parse_args()

    rows=list(csv.DictReader(args.catalog.open(encoding="utf-8")))
    by_label={r["source_label"]:r for r in rows}
    errors=[]
    seen={}
    total=0
    manifests=0

    # Canonical manifests are plain JSON. Compressed *.json.gz files are\n    # convenience copies (for example sootopolis.vi.json.gz) and must not be\n    # counted/validated a second time as independent manifests.\n    paths=sorted(args.translations.rglob("*.json"))\n    for path in paths:
        doc=load_json(path)
        trans=doc.get("translations")
        if not isinstance(trans, dict):
            errors.append(f"{path}: missing object 'translations'")
            continue
        manifests += 1
        declared_scope=doc.get("scope")
        for label, vi in trans.items():
            total += 1
            if label in seen:
                errors.append(f"{path}: duplicate label {label}; already in {seen[label]}")
                continue
            seen[label]=path
            src=by_label.get(label)
            if src is None:
                errors.append(f"{path}: unknown catalog label {label}")
                continue
            if declared_scope and src.get("category") != declared_scope:
                errors.append(f"{path}: {label} category={src.get('category')} but manifest scope={declared_scope}")
            if not isinstance(vi, str) or not vi:
                errors.append(f"{path}: {label} has empty/non-string translation")
                continue

            en=src.get("english","")
            en_controls=Counter(BRACE_RE.findall(en))
            vi_controls=Counter(BRACE_RE.findall(vi))
            if en_controls != vi_controls:
                errors.append(
                    f"{path}: {label} placeholder/control mismatch "
                    f"EN={dict(en_controls)} VI={dict(vi_controls)}"
                )
            if en.endswith("$") and not vi.endswith("$"):
                errors.append(f"{path}: {label} lost terminal $")
            if not en.endswith("$") and vi.endswith("$"):
                errors.append(f"{path}: {label} gained unexpected terminal $")

    summary={
        "manifests":manifests,
        "translated_labels":total,
        "unique_labels":len(seen),
        "errors":len(errors),
    }
    print(json.dumps(summary, ensure_ascii=False))
    if errors:
        for e in errors[:200]:
            print("ERROR:",e)
        if len(errors)>200:
            print(f"... {len(errors)-200} more")
        return 1
    return 0

if __name__=="__main__":
    raise SystemExit(main())
