#!/usr/bin/env python3
"""Compare rendered pixel widths of applied Vietnamese text with the English it replaced.

Reads the applier's --sites-out dump and the workspace font tables. English is
the layout budget: a Vietnamese line wider than the widest English line of the
same string is a candidate overflow in whatever window prints it.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from vietnamese_text_metrics import Metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--sites", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dialogue-limit", type=int, default=208)
    args = ap.parse_args()

    m = Metrics(args.workspace)
    sites = json.loads(args.sites.read_text(encoding="utf-8"))
    en_dialogue_widths: list[int] = []
    dialogue_over, ui_over = [], []
    for s in sites:
        en_w, vi_w = m.widest(s["english"]), m.widest(s["vi"])
        dialogue = s["kind"] == "asm" and s["site"].startswith("data/")
        if dialogue:
            en_dialogue_widths.append(en_w)
            if vi_w > max(args.dialogue_limit, en_w):
                dialogue_over.append({"site": s["site"], "vi_px": vi_w, "en_px": en_w})
        elif vi_w > en_w:
            ui_over.append({"site": s["site"], "en_px": en_w, "vi_px": vi_w, "over_px": vi_w - en_w,
                            "english": s["english"], "vi": s["vi"]})
    en_dialogue_widths.sort()
    pct = lambda p: en_dialogue_widths[min(len(en_dialogue_widths) - 1, int(len(en_dialogue_widths) * p))]
    ui_over.sort(key=lambda r: -r["over_px"])
    summary = {
        "sites": len(sites),
        "english_dialogue_widest_line_px": {"p50": pct(0.5), "p99": pct(0.99), "p999": pct(0.999),
                                            "max": en_dialogue_widths[-1]},
        "dialogue_lines_over_limit": len(dialogue_over),
        "ui_strings_wider_than_english": len(ui_over),
        "ui_over_by_file": dict(Counter(r["site"].split("::")[0] for r in ui_over).most_common(40)),
    }
    args.out.write_text(json.dumps({"summary": summary, "dialogue_over": dialogue_over,
                                    "ui_over": ui_over}, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
