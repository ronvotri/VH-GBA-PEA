#!/usr/bin/env python3
"""Widen the fixed-size const text arrays that Vietnamese strings overflow.

Vietnamese capitals outside the stock charmap take two bytes (0xF9 + id), so a
name that fits the original cell count can exceed the original byte count.
Each edit is an exact, single-occurrence source replacement on const data;
nothing here touches RAM/save structures.
"""
from __future__ import annotations

import argparse
from pathlib import Path

EDITS = [
    ("include/data.h", "extern const u8 gTrainerClassNames[][13];",
     "extern const u8 gTrainerClassNames[][26];"),
    ("src/data/text/trainer_class_names.h", "const u8 gTrainerClassNames[][13] =",
     "const u8 gTrainerClassNames[][26] ="),
    ("src/battle_message.c", "static const u8 sATypeMove_Table[NUMBER_OF_MON_TYPES][17] =",
     "static const u8 sATypeMove_Table[NUMBER_OF_MON_TYPES][34] ="),
    ("include/pokedex.h", "/*0x00*/ u8 categoryName[12];", "/*0x00*/ u8 categoryName[24];"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    args = ap.parse_args()
    for rel, old, new in EDITS:
        path = args.workspace / rel
        text = path.read_text(encoding="utf-8")
        if text.count(old) != 1:
            raise SystemExit(f"{rel}: expected exactly one occurrence of {old!r}")
        path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
        print(f"{rel}: widened")


if __name__ == "__main__":
    main()
