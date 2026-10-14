#!/usr/bin/env python3
"""Pixel widths of source-form game text, and page-preserving line reflow.

Widths come from the workspace's own charmap.txt and src/fonts.c, so they match
what the game renders. Text is in pokeemerald source form (\\n, \\l, \\p,
{PLACEHOLDER}, trailing $).
"""
from __future__ import annotations

import re
from pathlib import Path

FONT_TABLES = {
    "normal": "gFontNormalLatinGlyphWidths",
    "short": "gFontShortLatinGlyphWidths",
    "narrow": "gFontNarrowLatinGlyphWidths",
    "small": "gFontSmallLatinGlyphWidths",
    "small_narrow": "gFontSmallNarrowLatinGlyphWidths",
}
TOKEN_RE = re.compile(r"\{[^{}]+\}|\\.|.", re.S)
# Runtime-expanded placeholders, measured as their longest ordinary value in
# stock capital letters (6 px per cell in the normal font).
PLACEHOLDER_CELLS = {
    "PLAYER": 7, "RIVAL": 7, "KUN": 0, "STR_VAR_1": 10, "STR_VAR_2": 10, "STR_VAR_3": 10,
    "B_BUFF1": 10, "B_BUFF2": 10, "B_BUFF3": 10,
}


class Metrics:
    def __init__(self, workspace: Path, font: str = "normal"):
        self.codes: dict[str, tuple[int, ...]] = {}
        self.constants: dict[str, tuple[int, ...]] = {}
        for line in (workspace / "charmap.txt").read_text(encoding="utf-8").splitlines():
            line = line.split("@")[0].rstrip()
            m = re.match(r"^'(\\?.)'\s*=\s*((?:[0-9A-F]{2}\s*)+)$", line)
            if m:
                self.codes.setdefault(m.group(1)[-1], tuple(int(b, 16) for b in m.group(2).split()))
                continue
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*((?:[0-9A-F]{2}\s*)+)$", line)
            if m:
                self.constants.setdefault(m.group(1), tuple(int(b, 16) for b in m.group(2).split()))
        text = (workspace / "src" / "fonts.c").read_text(encoding="utf-8")
        m = re.search(re.escape(FONT_TABLES[font]) + r"\[\]\s*=\s*\{(.*?)\};", text, re.S)
        self.widths = [int(n) for n in re.findall(r"\d+", m.group(1))]
        self.cell = self.widths[0xBB]  # 'A'

    def _glyphs(self, code: tuple[int, ...]) -> int:
        if code and code[0] == 0xF9 and len(code) > 1:
            return self.widths[0x100 + code[1]]
        if code and code[0] in (0xFC, 0xFD):  # control / placeholder escape
            return 0
        return sum(self.widths[b] for b in code)

    def token_width(self, tok: str) -> int:
        if tok.startswith("{"):
            name = tok[1:-1].split()[0]
            if name in PLACEHOLDER_CELLS:
                return PLACEHOLDER_CELLS[name] * self.cell
            if " " in tok:  # {PAUSE 8}, {COLOR RED}, ...
                return 0
            return self._glyphs(self.constants.get(name, ()))
        if tok.startswith("\\") or tok == "$":
            return 0
        return self._glyphs(self.codes.get(tok, ()))

    def width(self, text: str) -> int:
        return sum(self.token_width(t) for t in TOKEN_RE.findall(text))

    def lines(self, text: str) -> list[str]:
        return re.split(r"\\[npl]", text.rstrip("$"))

    def widest(self, text: str) -> int:
        return max((self.width(line) for line in self.lines(text)), default=0)

    def reflow(self, text: str, limit: int, scroll: bool = True) -> str:
        """Re-wrap every page so no line exceeds `limit`; page breaks are kept.

        The first break in a page is \\n and later ones \\l (scroll), which is
        the convention the stock scripts use for pages of three or more lines.
        With scroll=False every break is \\n (fixed multi-line windows).
        """
        end = "$" if text.endswith("$") else ""
        pages = text[:-1].split("\\p") if end else text.split("\\p")
        out_pages = []
        for page in pages:
            words = re.sub(r"\\[nl]", " ", page).split(" ")
            lines, cur = [], ""
            for word in words:
                trial = word if not cur else cur + " " + word
                if cur and self.width(trial) > limit:
                    lines.append(cur)
                    cur = word
                else:
                    cur = trial
            lines.append(cur)
            page_out = lines[0]
            for i, line in enumerate(lines[1:]):
                page_out += ("\\n" if i == 0 or not scroll else "\\l") + line
            out_pages.append(page_out)
        return "\\p".join(out_pages) + end

    def max_page_lines(self, text: str) -> int:
        return max(len(re.split(r"\\[nl]", page)) for page in text.rstrip("$").split("\\p"))
