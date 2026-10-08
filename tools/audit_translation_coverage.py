#!/usr/bin/env python3
"""Report exact catalog coverage represented by translation manifests."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter, defaultdict
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--translations", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    with a.catalog.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    by_identity = {
        f'{r.get("source_label","")}@@{r.get("source_file","")}:{r.get("source_line","")}': r
        for r in rows
    }
    by_label = defaultdict(list)
    for r in rows:
        by_label[r.get("source_label","")].append(r)

    covered = set()
    unresolved = []
    duplicate_rows = []
    row_owner = {}

    for path in sorted(a.translations.rglob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        trans = doc.get("translations")
        if not isinstance(trans, dict):
            continue
        for key in trans:
            row = by_identity.get(key)
            if row is None:
                candidates = by_label.get(key, [])
                if len(candidates) == 1:
                    row = candidates[0]
                else:
                    unresolved.append({"manifest": str(path), "key": key, "candidate_count": len(candidates)})
                    continue
            identity = f'{row.get("source_label","")}@@{row.get("source_file","")}:{row.get("source_line","")}'
            if identity in covered:
                duplicate_rows.append({
                    "identity": identity,
                    "first_manifest": row_owner[identity],
                    "duplicate_manifest": str(path),
                })
                continue
            covered.add(identity)
            row_owner[identity] = str(path)

    total = Counter(r.get("category","") for r in rows)
    represented = Counter()
    missing_by_category = defaultdict(list)
    missing_by_source = defaultdict(Counter)

    for r in rows:
        identity = f'{r.get("source_label","")}@@{r.get("source_file","")}:{r.get("source_line","")}'
        category = r.get("category","")
        if identity in covered:
            represented[category] += 1
        else:
            missing_by_category[category].append({
                "source_label": r.get("source_label",""),
                "source_file": r.get("source_file",""),
                "source_line": r.get("source_line",""),
                "english": r.get("english",""),
            })
            missing_by_source[category][r.get("source_file","")] += 1

    categories = sorted(total)
    report = {
        "schema_version": 1,
        "catalog_entries": len(rows),
        "represented_rows": len(covered),
        "unresolved_manifest_keys": unresolved,
        "duplicate_catalog_rows_represented": duplicate_rows,
        "categories": {
            cat: {
                "total": total[cat],
                "represented": represented[cat],
                "missing": total[cat] - represented[cat],
                "missing_by_source_file": dict(missing_by_source[cat].most_common()),
            }
            for cat in categories
        },
        "missing_rows": dict(missing_by_category),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"catalog_entries={len(rows)}",
        f"represented_rows={len(covered)}",
        f"unresolved_manifest_keys={len(unresolved)}",
        f"duplicate_catalog_rows_represented={len(duplicate_rows)}",
    ]
    for cat in categories:
        lines.append(
            f"{cat}: {represented[cat]}/{total[cat]} represented; "
            f"{total[cat] - represented[cat]} missing"
        )
        if missing_by_source[cat]:
            top = ", ".join(f"{p}={n}" for p,n in missing_by_source[cat].most_common(20))
            lines.append(f"  missing sources: {top}")
    a.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
