#!/usr/bin/env python3
"""Report map/story catalog rows not yet represented by translation manifests."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--translations", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    translated: set[str] = set()
    manifest_counts: dict[str, int] = {}
    for path in sorted(args.translations.glob("*.vi.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        keys = set((data.get("translations") or {}).keys())
        translated.update(keys)
        manifest_counts[path.name] = len(keys)

    with args.catalog.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("category") == "map-story"]

    remaining = [r for r in rows if r.get("source_label") not in translated]
    dup_labels = Counter(r.get("source_label", "") for r in rows)
    duplicate_labels = sorted(k for k, v in dup_labels.items() if k and v > 1)

    by_file = Counter(r.get("source_file", "") for r in remaining)
    by_map = Counter(
        (r.get("source_file", "").split("/")[2]
         if r.get("source_file", "").startswith("data/maps/")
         and len(r.get("source_file", "").split("/")) > 2
         else r.get("source_file", ""))
        for r in remaining
    )

    payload = {
        "catalog_map_story_rows": len(rows),
        "translated_unique_labels": len(translated),
        "remaining_rows": len(remaining),
        "duplicate_catalog_labels": duplicate_labels,
        "remaining_by_map": [
            {"map": k, "count": v}
            for k, v in sorted(by_map.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
        "remaining_by_source_file": [
            {"source_file": k, "count": v}
            for k, v in sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
        "remaining": remaining,
        "manifest_counts": manifest_counts,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"catalog_map_story_rows={len(rows)}",
        f"translated_unique_labels={len(translated)}",
        f"remaining_rows={len(remaining)}",
        f"duplicate_catalog_labels={len(duplicate_labels)}",
        "",
        "remaining_by_map:",
    ]
    lines.extend(f"{v:4d}  {k}" for k, v in sorted(by_map.items(), key=lambda kv: (-kv[1], kv[0])))
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
