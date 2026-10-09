#!/usr/bin/env python3
"""Lossless three-color Pokémon GBA Latin glyph codec and small-font reducer.

Each 16x16 glyph has four 8x8 tiles, each compressed to 16 bytes. Every row
stores eight 2-bit palette selectors (3 means transparent/background).
Bit order matches the GBA text.c DecompressGlyphTile routine and its source
sFontHalfRowOffsets lookup table. Preserves 0/background, 1/foreground,
2/shadow. Used only for *internal* glyph migration, not as a released font.
"""
from __future__ import annotations

GLYPH_SIZE=64
WIDTH=HEIGHT=16


def decode_glyph(data:bytes)->list[list[int]]:
    if len(data)!=GLYPH_SIZE:
        raise ValueError("expected one 64-byte compressed glyph")
    out=[[0]*WIDTH for _ in range(HEIGHT)]
    for tile_index in range(4):
        tile_x=(tile_index % 2)*8
        tile_y=(tile_index//2)*8
        for row in range(8):
            low,high=data[tile_index*16+row*2:tile_index*16+row*2+2]
            for half,packed in enumerate((high,low)):
                for column in range(4):
                    color=(packed>>(6-2*column))&3
                    out[tile_y+row][tile_x+half*4+column]=0 if color==3 else color
    return out


def encode_glyph(pixels:list[list[int]])->bytes:
    if len(pixels)!=HEIGHT or any(len(row)!=WIDTH for row in pixels):
        raise ValueError("expected a 16x16 raster")
    if any(color not in (0,1,2) for row in pixels for color in row):
        raise ValueError("only background/foreground/shadow are supported")
    result=bytearray()
    for tile_index in range(4):
        tile_x=(tile_index%2)*8
        tile_y=(tile_index//2)*8
        for row in range(8):
            line=pixels[tile_y+row][tile_x:tile_x+8]
            def pack4(values):
                return sum(value<<(6-2*i) for i,value in enumerate(values))
            # On GBA little-endian: first visible half-row is the high byte.
            result.extend((pack4(line[4:]),pack4(line[:4])))
    if len(result)!=GLYPH_SIZE:
        raise ValueError("incorrect compressed glyph layout")
    return bytes(result)


def synthesize_small_from_narrow(data:bytes, source_width:int)->bytes:
    """Deterministic 13px-high fallback preserving narrow accent silhouette.

    Source narrow glyph 15px tall (active y=0..12 for donor vowels); small is
    13px tall. Map 13 input rows into 12 visible output rows, keeping last
    baseline pixels at row 11. This is NOT typographic or visual QA.
    """
    if not 1<=source_width<=8:
        raise ValueError("only 1..8 pixel narrow glyphs supported")
    picture=decode_glyph(data)
    output=[[0]*WIDTH for _ in range(HEIGHT)]
    for y in range(12):
        sy=round(y*12/11)
        for x in range(source_width):
            output[y][x]=picture[sy][x]
    return encode_glyph(output)
