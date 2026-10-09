# Font release blocker: POKéBLOCK native glyph collision (2026-10-09)

> **Correction, verified against the pinned charmap:** the original proposed `0x35` for `ì` was **UNSAFE**. `0x35` is already the ASCII `=` glyph. The safe *planned* relocations are `đ → 0x33` and `ì → 0x37` in the separate v0.6 source codebook. No source ROM with verified transplanted font has been released.

This is a **source+original ROM verified** compatibility issue beyond the earlier English f/w/z collision. It is **not** merely a missing translation. Keep the 16 source texts with this token blocked until the actual glyph art is relocated and the GBA renderer is tested.

## Pinned charmap and user-facing impact

The original `pret/pokeemerald` charmap at pinned commit `5eff78649e7170a877b961ef0b3da13b81a16038` defines:

```
PKMN        = 53 54
POKEBLOCK   = 55 56 57 58 59
```

These are **fixed native Latin glyph sequences**, not arbitrary-length battle variables. `{POKEBLOCK}` is used in 16 authored item descriptions, including berries and the Pokéblock Case. The experimental `checkpoints/v05-collision-free-codebook.json` currently has `đ = 0x56` and `ì = 0x59`, both within native `POKEBLOCK` glyph indices.

**So a source build with v0.5 text bytes and an unmodified imported v0.4 Vietnamese font would risk displaying broken Pokéblock symbols**, even if all ASCII f/w/z glyphs were restored. The existing `tools/graft_collision_safe_v04_fonts.py` only protects those earlier 3 ASCII slots and is **not sufficient as a release candidate**.

## Exact original-vs-v0.4 ROM glyph comparison

Private local hash-verified inputs:

- Clean Arena 0.13.0 SHA-256 `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`
- Original Vietnamese donor v0.4 SHA-256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`

The table gives the number of changed **bytes per 64-byte glyph** in each Latin font array, with direct comparison at the five pinned source-shipping offsets.

| Font | 0x53/0x54 PKMN | 0x55 | 0x56 | 0x57 | 0x58 | 0x59 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| SmallNarrow | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| Small | 0 / 0 | 0 | 18 | 0 | 0 | 0 |
| Narrow | 0 / 0 | 0 | 25 | 0 | 19 | 10 |
| Short | 0 / 0 | 0 | 26 | 0 | 0 | 10 |
| Normal | 0 / 0 | 28 | 25 | 21 | 20 | 10 |

**Important:** the donor even modifies native Pokéblock glyph indices `0x55`, `0x57` and `0x58` in some styles, although the inferred v0.5 codebook names only `đ` and `ì` in the range. A correct transplant must restore **all five original 0x55–0x59 graphics** in all affected styles, not merely the two translated letters.

## Proposed guarded solution (NOT YET APPLIED)

1. Independently reserve unused Latin codepoints **0x33 for `đ`** and **0x37 for `ì`**. Both are free in the pinned Latin charmap and v0.5 codebook. **Do not use 0x35: it is the built-in `=` glyph**; also protect 0x34 (`LV`) and 0x36 (`;`). The initial 0x35 proposal was incorrect because the old charmap scanner split the literal `'='` definition at the wrong equals sign. Treat this as a new v0.6 font/codebook format — never rewrite the v0.5 checkpoint without changing both source byte encoding and source font images.
2. In the SHA-locked *private* font graft, copy actual accented glyph pictures for `đ` and `ì` out of donor v0.4 codepoints 0x56 and 0x59 into the new slots. Synthesize missing font styles from the verified Narrow art, with explicit display QA flags, as done for ấ/ằ/ắ.
3. Restore the *original clean font's* **all five glyph images 0x55..0x59**, including special fixed-character Pokéblock symbols. Preserve original 0x53/0x54 PKMN glyph images as well.
4. Reject any source build unless the v0.6 codebook, original charmap, glyph-offset symbols and exact source-built ROM SHA-256 all match. Test all five font styles by decoding their glyph bitmaps and running emulator title, item/berry, Pokéblock Case and battle scenes before distributing.
5. Only after the font collision is eliminated may `{POKEBLOCK}` item descriptions be translated using the **literal pinned five-byte sequence `55 56 57 58 59`**, while preserving token count, relative placement and fixed three-line box width. Do not treat it as a `{PLAYER}` token or blindly delete braces.

## What is safe right now

- Source-only `v0.5` builds for 2,069+ text labels compile and pass reference/terminator QA, but **still use stock English font** and are not user-facing releases.
- Static item descriptions can be edited and included without touching this special token; seven missing-glyph static item descriptions were revised separately in `translations/system-ui/item-descriptions-*.vi.json`.
- The 16 token-bearing item descriptions are still deliberately excluded by `tools/stage_source_descriptions.py`; `tools/tests/test_static_item_descriptions.py` now keeps a regression guard on their unresolved status.
- Original playable v0.4 remains a rollback. No source ROM, copyrighted font assets, or private ROM donor have been uploaded to the public GitHub repository.
