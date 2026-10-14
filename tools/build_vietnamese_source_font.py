#!/usr/bin/env python3
"""Add collision-free Vietnamese glyphs to a pokeemerald source tree.

Works on the SOURCE build only (graphics/fonts/latin_*.png, src/fonts.c,
charmap.txt). Every Vietnamese letter gets its own code, so no stock Latin
letter (f/w/z included) is overwritten. Glyphs are composed from each stock
font's own base letter plus pixel diacritics, keeping the stock letterforms.
No donor ROM pixels are read or written.

usage: build_vietnamese_source_font.py --workspace WS [--sheet-dir DIR]
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

from PIL import Image

FONTS = {
    "small_narrow": "gFontSmallNarrowLatinGlyphWidths",
    "small": "gFontSmallLatinGlyphWidths",
    "narrow": "gFontNarrowLatinGlyphWidths",
    "short": "gFontShortLatinGlyphWidths",
    "normal": "gFontNormalLatinGlyphWidths",
}
OUT, FG, SH, BG = 0, 1, 2, 3  # palette indices used by the stock font PNGs

# Stock charmap codes of the plain base letters.
BASE_CODE = {c: 0xBB + i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
BASE_CODE.update({c: 0xD5 + i for i, c in enumerate("abcdefghijklmnopqrstuvwxyz")})

# Latin single-byte codes that stock charmap.txt leaves undefined.
FREE_SINGLE = ([0x0A, 0x18, 0x1F] + list(range(0x2F, 0x34)) + list(range(0x37, 0x51))
               + list(range(0x5E, 0x68)) + list(range(0x69, 0x6F)) + list(range(0x70, 0x77))
               + [0x78] + list(range(0x7D, 0x84)) + list(range(0x87, 0xA0)))
FREE_EXTRA = list(range(0x18, 0xD0))  # second byte after 0xF9 (CHAR_EXTRA_SYMBOL)

# Letters stock charmap.txt already defines; reused as-is.
STOCK_ACCENTED = dict(zip("ÀÁÂÈÉÊÌÒÓÔÙÚàáèéêìòóôùú",
                          [0x01, 0x02, 0x03, 0x05, 0x06, 0x07, 0x09, 0x0D, 0x0E, 0x0F, 0x11, 0x12,
                           0x16, 0x17, 0x1A, 0x1B, 0x1C, 0x1E, 0x22, 0x23, 0x24, 0x26, 0x27]))
STOCK_ACCENTED.update({"Í": 0x5A, "â": 0x68, "í": 0x6F})

TONES = {"́": "acute", "̀": "grave", "̉": "hook", "̃": "tilde", "̣": "dot"}
MODS = {"̂": "circ", "̆": "breve", "̛": "horn"}
MARK = {
    "acute": ["..#", ".#."],
    "grave": ["#..", ".#."],
    "hook": ["##.", "..#", ".#."],
    "hook2": ["##", ".#"],
    "tilde": [".##.#", "#..#."],
    "tilde4": [".#.#", "#.#."],
    "circ": [".#.", "#.#"],
    "breve": ["#.#", ".#."],
    "side_acute": [".#", "#."],
    "side_grave": ["#.", ".#"],
}
# Uppercase letters ordered by how often the authored translations use them,
# so the common ones get single-byte codes.
UPPER_PRIORITY = "ĐỒƯẤỐẾẢẠỜỦỞỘẬỌƠẮỪỨỊẦỆỚỔỂỎỀĂÃỢẸỬÝỰẶẺỤỮỈẨỄĨẼŨẪỶỖỲỠỸẰÕẲẴỴ"


def vietnamese_letters() -> tuple[list[str], list[str]]:
    lower = []
    for base in ["a", "ă", "â", "e", "ê", "i", "o", "ô", "ơ", "u", "ư", "y"]:
        for tone in ["", "̀", "́", "̉", "̃", "̣"]:
            ch = unicodedata.normalize("NFC", base + tone)
            if ch not in "aeiouy":
                lower.append(ch)
    lower.append("đ")
    return lower, [c.upper() for c in lower]


def allocate_codes() -> dict[str, tuple[int, ...]]:
    lower, upper = vietnamese_letters()
    need = [c for c in lower if c not in STOCK_ACCENTED]
    ranked = [c for c in UPPER_PRIORITY if c in upper and c not in STOCK_ACCENTED]
    need += ranked + [c for c in upper if c not in STOCK_ACCENTED and c not in ranked]
    assert len(set(need)) == len(need)
    codes: dict[str, tuple[int, ...]] = {}
    singles, extras = list(FREE_SINGLE), list(FREE_EXTRA)
    for ch in need:
        codes[ch] = (singles.pop(0),) if singles else (0xF9, extras.pop(0))
    return codes


def glyph_id(code: tuple[int, ...]) -> int:
    return code[0] if len(code) == 1 else 0x100 + code[1]


class Cell:
    def __init__(self, px: list[list[int]], width: int, rows: range):
        self.px, self.width, self.rows = px, width, rows

    def ink_rows(self) -> list[int]:
        return [y for y in range(16) if FG in self.px[y]]

    def ink_cols(self, ys) -> list[int]:
        return [x for x in range(16) if any(self.px[y][x] == FG for y in ys)]


def read_cell(im: Image.Image, gid: int) -> list[list[int]]:
    ox, oy = (gid % 16) * 16, (gid // 16) * 16
    return [[im.getpixel((ox + x, oy + y)) for x in range(16)] for y in range(16)]


def write_cell(im: Image.Image, gid: int, px: list[list[int]]) -> None:
    ox, oy = (gid % 16) * 16, (gid // 16) * 16
    for y in range(16):
        for x in range(16):
            im.putpixel((ox + x, oy + y), px[y][x])


def finish(fg: set[tuple[int, int]], width: int, rows: range) -> tuple[list[list[int]], int]:
    """Rebuild a cell from foreground pixels: stock-style right/down shadow."""
    min_x = min(x for x, _ in fg)
    if min_x < 0:
        fg = {(x - min_x, y) for x, y in fg}
        width -= min_x
    width = min(16, max(width, max(x for x, _ in fg) + 2))
    px = [[BG if (y in rows and x < width) else OUT for x in range(16)] for y in range(16)]
    for x, y in fg:
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            sx, sy = x + dx, y + dy
            if sx < width and sy in rows and (sx, sy) not in fg:
                px[sy][sx] = SH
    for x, y in fg:
        if 0 <= x < 16 and y in rows:
            px[y][x] = FG
    return px, width


def stamp(fg: set, pattern: list[str], left: int, top: int) -> None:
    for dy, row in enumerate(pattern):
        for dx, c in enumerate(row):
            if c == "#":
                fg.add((left + dx, top + dy))


def shorten(fg: set[tuple[int, int]], count: int) -> set[tuple[int, int]]:
    """Drop `count` duplicated rows from a letter, keeping its bottom fixed."""
    for _ in range(count):
        ys = sorted({y for _, y in fg})
        rows = {y: frozenset(x for x, yy in fg if yy == y) for y in ys}
        dup = [y for y in ys[1:-1] if rows[y] == rows.get(y + 1) or rows[y] == rows.get(y - 1)]
        if not dup:
            break
        cut = dup[len(dup) // 2]
        fg = {(x, y + 1) if y < cut else (x, y) for x, y in fg if y != cut}
    return fg


def compose(ch: str, font: dict) -> tuple[list[list[int]], int]:
    rows: range = font["rows"]
    if ch in "đĐ":
        base = font["cells"]["d" if ch == "đ" else "D"]
        fg = {(x, y) for y in range(16) for x in range(16) if base.px[y][x] == FG}
        ys = sorted({y for _, y in fg})
        if ch == "đ":
            stem = max(x for x, y in fg if y == ys[0])
            fg |= {(stem - 2, ys[1]), (stem - 1, ys[1]), (stem + 1, ys[1])}
            return finish(fg, base.width + 1, rows)
        fg = {(x + 1, y) for x, y in fg}
        mid = ys[len(ys) // 2 - 1]
        fg |= {(0, mid), (2, mid), (3, mid)}
        return finish(fg, base.width + 1, rows)

    nfd = unicodedata.normalize("NFD", ch)
    letter, marks = nfd[0], nfd[1:]
    mod = next((MODS[m] for m in marks if m in MODS), None)
    tone = next((TONES[m] for m in marks if m in TONES), None)
    base = font["cells"][letter]
    fg = {(x, y) for y in range(16) for x in range(16) if base.px[y][x] == FG}
    width = base.width
    if letter == "i":  # dotless i under any mark above
        xtop = font["xheight"]
        if mod or tone not in (None, "dot"):
            fg = {(x, y) for x, y in fg if y >= xtop}

    if mod == "horn":
        top = min(y for _, y in fg)
        right = max(x for x, y in fg if y <= top + 1)
        fg |= {(right + 1, top - 1), (right + 1, top)}
        width += 1
        mod = None

    if tone == "dot":
        bottom = max(y for _, y in fg)
        cols = sorted({x for x, _ in fg})
        cx = (cols[0] + cols[-1]) // 2
        y = min(bottom + 2, rows[-1])
        if y <= bottom:  # descender in the way: sit beside it
            cx = cols[-1] + 2
        fg.add((cx, y))
        tone = None

    if mod or tone:
        stack_h = {(None, "acute"): 2, (None, "grave"): 2, (None, "hook"): 3, (None, "tilde"): 2,
                   ("m", None): 2, ("m", "acute"): 3, ("m", "grave"): 3, ("m", "hook"): 3,
                   ("m", "tilde"): 4}[("m" if mod else None, tone)]
        top = min(y for _, y in fg)
        room = top - rows[0]
        # Lowercase has room to stack the tone above the circumflex/breve; capitals
        # do not, so there the tone sits beside it.
        stacked = bool(mod) and tone in ("acute", "grave", "hook") and room >= 4
        if stacked:
            stack_h = 4
        if room < stack_h:
            fg = shorten(fg, stack_h - room)
            top = min(y for _, y in fg)
            room = top - rows[0]
        gap = 1 if room > stack_h else 0
        bottom_row = top - 1 - gap  # last row the stack may use
        cols = sorted({x for x, y in fg if y <= top + 1})
        centre2 = cols[0] + cols[-1]  # twice the centre x

        def left_for(pattern):
            return (centre2 - len(pattern[0]) + 2) // 2

        if mod:
            pat = MARK[mod]
            mleft = left_for(pat)
            mtop = bottom_row - 1
            stamp(fg, pat, mleft, mtop)
            if stacked:
                tp = MARK["hook2"] if tone == "hook" else MARK[tone]
                stamp(fg, tp, left_for(tp), mtop - 2)
            elif tone in ("acute", "grave"):
                stamp(fg, MARK["side_" + tone], mleft + 3, mtop - 1)
            elif tone == "hook":
                stamp(fg, MARK["hook2"], mleft + 3, mtop - 1)
            elif tone == "tilde":
                tp = MARK["tilde"] if cols[-1] - cols[0] >= 3 else MARK["tilde4"]
                stamp(fg, tp, left_for(tp), mtop - 2)
        else:
            if tone == "hook":
                pat = MARK["hook"] if room >= 3 else MARK["hook2"]
            elif tone == "tilde":
                pat = MARK["tilde"] if cols[-1] - cols[0] >= 3 else MARK["tilde4"]
            else:
                pat = MARK[tone]
            stamp(fg, pat, left_for(pat), bottom_row - len(pat) + 1)
        fg = {(x, y) for x, y in fg if y >= rows[0]}
    return finish(fg, width, rows)


def parse_widths(text: str, symbol: str) -> tuple[int, int, list[int]]:
    m = re.search(re.escape(symbol) + r"\[\]\s*=\s*\{(.*?)\};", text, re.S)
    if not m:
        raise ValueError(f"missing width table {symbol}")
    nums = [int(n) for n in re.findall(r"\d+", m.group(1))]
    if len(nums) != 0x200:
        raise ValueError(f"{symbol}: expected 512 widths, got {len(nums)}")
    return m.start(1), m.end(1), nums


def format_widths(nums: list[int]) -> str:
    lines = ["    " + ", ".join(f"{n:2d}" for n in nums[i:i + 16]) + "," for i in range(0, 0x200, 16)]
    return "\n" + "\n".join(lines) + "\n"


def charmap_token(ch: str) -> str:
    return f"'{ch}'"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True, type=Path)
    ap.add_argument("--sheet-dir", type=Path)
    ap.add_argument("--codebook-out", type=Path)
    args = ap.parse_args()
    ws: Path = args.workspace

    codes = allocate_codes()
    fonts_c = ws / "src" / "fonts.c"
    text = fonts_c.read_text(encoding="utf-8")

    for name, symbol in FONTS.items():
        png = ws / "graphics" / "fonts" / f"latin_{name}.png"
        im = Image.open(png)
        start, end, widths = parse_widths(text, symbol)
        ref = read_cell(im, BASE_CODE["A"])
        in_rows = [y for y in range(16) if any(v != OUT for v in ref[y])]
        rows = range(in_rows[0], in_rows[-1] + 1)
        cells = {c: Cell(read_cell(im, code), widths[code], rows) for c, code in BASE_CODE.items()}
        font = {"rows": rows, "cells": cells, "xheight": min(cells["x"].ink_rows())}
        for ch, code in codes.items():
            gid = glyph_id(code)
            px, width = compose(ch, font)
            write_cell(im, gid, px)
            widths[gid] = width
        im.save(png)
        text = text[:start] + format_widths(widths) + text[end:]
        if args.sheet_dir:
            args.sheet_dir.mkdir(parents=True, exist_ok=True)
            order = sorted(codes, key=lambda c: glyph_id(codes[c]))
            sheet = Image.new("RGB", (16 * 17 * 4, ((len(order) + 15) // 16) * 17 * 4), (200, 220, 255))
            pal = {OUT: (235, 240, 250), FG: (40, 40, 40), SH: (170, 170, 170), BG: (255, 255, 255)}
            for i, ch in enumerate(order):
                cell = read_cell(im, glyph_id(codes[ch]))
                for y in range(16):
                    for x in range(16):
                        colour = pal[cell[y][x]]
                        for dy in range(4):
                            for dx in range(4):
                                sheet.putpixel(((i % 16) * 68 + x * 4 + dx, (i // 16) * 68 + y * 4 + dy), colour)
            sheet.save(args.sheet_dir / f"vi_{name}.png")
    fonts_c.write_text(text, encoding="utf-8", newline="\n")

    charmap = ws / "charmap.txt"
    cm = charmap.read_text(encoding="utf-8")
    marker = "@ Vietnamese letters (collision-free; added by build_vietnamese_source_font.py)"
    if marker in cm:
        raise SystemExit("charmap.txt already has the Vietnamese block")
    block = [marker]
    for ch, code in codes.items():
        block.append(f"{charmap_token(ch)} = " + " ".join(f"{b:02X}" for b in code))
    charmap.write_text(cm.rstrip("\n") + "\n\n" + "\n".join(block) + "\n", encoding="utf-8", newline="\n")

    if args.codebook_out:
        book = {ch: " ".join(f"0x{b:02X}" for b in code) for ch, code in codes.items()}
        book.update({ch: f"0x{code:02X}" for ch, code in STOCK_ACCENTED.items()})
        args.codebook_out.write_text(json.dumps(
            {"schema_version": 1, "kind": "source-build collision-free Vietnamese codebook",
             "single_byte": sum(len(c) == 1 for c in codes.values()),
             "extra_symbol_prefixed": sum(len(c) == 2 for c in codes.values()),
             "codes": book}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"glyphs added per font: {len(codes)} "
          f"({sum(len(c) == 1 for c in codes.values())} single-byte, "
          f"{sum(len(c) == 2 for c in codes.values())} F9-prefixed)")


if __name__ == "__main__":
    main()
