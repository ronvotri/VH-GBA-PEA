#!/usr/bin/env python3
"""Conservative word reflow for named PLAYER/RIVAL variables in GBA dialogue.

Keeps existing page break count, preserves text word order and name-variable
sequence, converts a third explicit line to standard scroll when necessary.
This tool does not encode glyphs; the caller must revalidate byte widths.
"""
from __future__ import annotations
import re

TOKEN_WIDTH = {"PLAYER": 7, "RIVAL": 7}


def display_cells(word: str) -> int:
    found=list(re.finditer(r"\{([^{}]+)\}",word))
    remainder=re.sub(r"\{[^{}]+\}","",word)
    if "{" in remainder or "}" in remainder:
        raise ValueError("unbalanced named token")
    length=len(word)
    for match in found:
        if match.group(1) not in TOKEN_WIDTH:
            raise ValueError("unknown variable width")
        length+=TOKEN_WIDTH[match.group(1)]-len(match.group(0))
    return length


def wrap_dynamic_text(text: str, width: int=26) -> str:
    if not text.endswith("$") or text.count("$")!=1:
        raise ValueError("invalid terminator")
    if not 12<=width<=30:
        raise ValueError("invalid line width")
    output=[]
    line=0
    cells=0
    for chunk in re.split(r"(\\[npl])",text[:-1]):
        if not chunk:
            continue
        if chunk in (r"\n",r"\l",r"\p"):
            if chunk==r"\p":
                line=0
            else:
                if chunk==r"\n" and line==1:
                    chunk=r"\l"
                line=1
            output.append(chunk)
            cells=0
            continue
        if ("\\" in chunk or "\n" in chunk or "\r" in chunk
            or "\t" in chunk or chunk.startswith(" ") or chunk.endswith(" ")
            or "  " in chunk):
            raise ValueError("ambiguous embedded control or whitespace")
        # A quoted phrase containing spaces cannot safely be broken blindly.
        words=re.findall(r'“[^”]*”[.,!?]?|[^ ]+',chunk)
        for n,word in enumerate(words):
            length=display_cells(word)
            if length>width:
                raise ValueError("word or quoted phrase wider than line")
            gap=1 if n else 0
            if cells+gap+length<=width:
                if gap:
                    output.append(" ")
                    cells+=1
                output.append(word)
                cells+=length
            elif cells:
                output.extend((r"\n" if line==0 else r"\l",word))
                cells=length
                line=1
            else:
                raise ValueError("cannot wrap word")
    result="".join(output)+"$"
    strip_controls=lambda v:re.sub(r"\\[npl]"," ",v[:-1]).split()
    if strip_controls(result)!=strip_controls(text):
        raise ValueError("text word order changed")
    if result.count(r"\p")!=text.count(r"\p"):
        raise ValueError("pagination drift")
    return result
