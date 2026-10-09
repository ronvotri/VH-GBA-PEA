#!/usr/bin/env python3
"""Conservative word-boundary reflow for source-built Emerald text.

Preserves every existing page/newline/scroll control and the ordered words.
Newline is added only for a second visible line; \\l scrolls thereafter.
Does not interpret dynamic placeholders, unknown escapes, complex whitespace
or quote-internal spaces. Byte length is rechecked by the caller.
"""
from __future__ import annotations

import re

CONTROLS = (r"\n",r"\p",r"\l")


def auto_wrap_script_text(text: str, width: int = 26) -> str:
    if not text.endswith("$") or text.count("$") != 1:
        raise ValueError("missing or extra terminator")
    if "{" in text or "}" in text:
        raise ValueError("dynamic placeholder requires dedicated layout")
    if not 10 <= width <= 30:
        raise ValueError("invalid width")
    chunks = re.split(r"(\\[npl])",text[:-1])
    parts: list[str] = []
    line = 0
    column = 0
    for chunk in chunks:
        if not chunk:
            continue
        if chunk in CONTROLS:
            if chunk == r"\p":
                line = 0
            elif chunk == r"\n":
                if line == 1:
                    raise ValueError("explicit third line requires review")
                line = 1
            else:
                line = 1
            parts.append(chunk)
            column = 0
            continue
        if any(ch in chunk for ch in "\\\r\n\t"):
            raise ValueError("unrecognized escape/control")
        if chunk.startswith(" ") or chunk.endswith(" ") or "  " in chunk:
            raise ValueError("ambiguous original whitespace")
        # Treat an entire double-curly-quoted phrase as one non-splittable word.
        for index,word in enumerate(re.findall(r"“[^”]*”[.,!?]?|[^ ]+",chunk)):
            if not word or len(word)>width:
                raise ValueError("word longer than line width")
            spacing = 1 if index else 0
            if column+spacing+len(word)<=width:
                if spacing:
                    parts.append(" ")
                    column += 1
                parts.append(word)
                column += len(word)
            elif column:
                parts.extend((r"\n" if line == 0 else r"\l",word))
                line = 1
                column = len(word)
            else:
                raise ValueError("cannot place word")
    result = "".join(parts)+"$"
    words = lambda s: re.sub(r"\\[npl]"," ",s[:-1]).split()
    if words(result) != words(text):
        raise ValueError("word order changed")
    return result
