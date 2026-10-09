# Collision-safe Vietnamese font prototype — 2026-10-09

**Status: experimental source-first/font-only verification. Not a downloadable or release-ready Việt hóa ROM.**

This checkpoint follows the independently audited **741/741 source-localized labels** in [Actions 37896025115](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37896025115). The earlier 741 labels were compiled with the inferred v0.4 codebook and stock fonts; glyph rendering had not been validated. The newer v0.5 codebook and font tooling are a separate experimental pipeline.

## Verified source font defect — exact original ROM comparison

The SHA-locked private clean Arena 0.13.0 (`a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`) and Vietnamese v0.4 (`c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`) establish:

| Original ASCII letter | English byte | v0.4 Vietnamese glyph at SAME byte | v0.5 reserved Latin slot |
| --- | --- | --- | --- |
| f | `0xDA` | ấ | `0x30` |
| w | `0xEB` | ằ | `0x31` |
| z | `0xEE` | ắ | `0x32` |

Direct comparison of all original 52 ASCII letter glyphs, for each of five font data arrays, shows **only f/w/z differ in Normal/Narrow/Short**; Small and SmallNarrow ASCII letter slots are unchanged. Five source width tables are unchanged by v0.4. This explains broken leftover English like `How` → mixed-encoding text, and it is not a mere missing-translation issue.

The pinned source `charmap.txt` does not assign Latin slots `0x30..0x32` before its Japanese mode. Japanese glyphs reuse these bytes **in Japanese mode**; the v0.5 plan is for Latin text only. A byte collision remains in inferred v0.4 codebook for `Ừ` versus `ừ` at `0x50`: uppercase `Ừ` is **quarantined** rather than silently accepting wrong-case rendering.

## New source-controlled implementation

1. `tools/plan_collision_free_vietnamese_font.py` produces a v2 byte-injective source codebook, requires the pinned original collision pairings and refuses any target slot occupied by the source Latin charmap, a previous codebook letter or GBA control byte.
2. `checkpoints/v05-collision-free-codebook.json` is the durable checked-in plan: **137 individually addressed glyph letters**; f/w/z remain `DA/EB/EE`, ấ/ằ/ắ move to `30/31/32`, `Ừ` is withheld until a separate accurate uppercase glyph exists. Never use this codebook against unmodified v0.4 font graphics.
3. The GitHub Actions source-first staging smoke now checks the generated v2 codebook against the pinned checkpoint and uses it to compile the existing map/UI/dynamic/battle groups. **Check the latest CI conclusion before claiming v2 source compilation PASS.**
4. `tools/pokemon_gba_font_glyphs.py` decodes/encodes the original four-tile, 3-color 16×16 Pokémon Latin glyph format used in `src/text.c:DecompressGlyphTile` and provides a deterministic 13px-high small-font fallback from real donor Narrow glyph data.
5. `tools/graft_collision_safe_v04_fonts.py`: a SHA-locked **private** graft tool that copies real v0.4 glyph arrays by verified source and target symbols, restores English f/w/z into their original slots, moves ấ/ằ/ắ to their reserved Latin slots and patches only the corresponding width values. In the two Small font styles, it **synthesizes** glyph pictures from the genuine donor Narrow bitmap and flags them as unverified artwork. Never writes source ROMs, scripts, menus or pointers; refuses output if exact private source-built SHA and v2 codebook do not match.
6. Dedicated tests cover codebook collisions/Latin mode, re-encoding of 16×16 color rasters, image compression, small height constraints, English glyph preservation, unchanged non-font ranges, shifted compiled-font symbols and private SHA safety.

## Direct binary font-only smoke (real data; not a translated game)

A private diagnostic applied the same glyph/width relocation to a **copy of the clean released ROM** and compared the complete 32 MiB against original shipping bytes:

- **6,095 byte differences**, ALL restricted to five font glyph arrays and their width table slots.
- All **15 accent glyphs** (3 letters × 5 font styles) have nonempty raster data at v0.5 reserved positions.
- English f/w/z glyph pictures remain **bit-for-bit the clean ROM** in all five fonts.
- Normal, Narrow, Short glyphs directly copied from Vietnamese v0.4 donor; Small and SmallNarrow glyphs synthesized from its Narrow donor picture.
- Font-only diagnostic output SHA-256 `19ba06b191c403d7ad32f1eed52d0059d189d508d2e55c7899b814d480e069c8`. **This is NOT a user-ready or source-localized ROM; no download is offered.** Do not call this font experiment a v0.5 release.
- **No emulator, on-screen pixel-width, save/load, title or battle gameplay tests** were conducted.

The actual source-built translated ROM SHA for the *earlier old-codebook* 741-label build is `e63d4799b06c634d92b3dc003e07e27c933629e480c8c01047457b0029ef6cc7`. Its font remains stock English; it cannot be retrofitted with new glyphs unless its 741 text payloads are recompiled from **the v0.5 byte-injective codebook**. A new CI source compile is running for this purpose, with reports/hashes in the symbol-map artifact; compiled copyrighted ROM and donor font graphics are intentionally not stored on the public repository.

## Next blockers before actual final ROM

- Obtain/rebuild the exact new v2-codebook compiled source ROM in a private workspace; verify its SHA and full byte-symbol map, run the private font graft with the v0.4 donor, and independently validate all moved glyphs + full ROM integrity.
- Visually QA all five font types in game; especially the two synthesized small styles, glyph widths, menus and battle text wrapping. Read-only bitmap/prototype QA is insufficient.
- Resolve unsupported uppercase `Ừ` and remaining Vietnamese glyph coverage, dynamic placeholders beyond PLAYER/RIVAL, and remaining thousands of unintegrated source entries.
- Do not upload commercial ROM/font graphic bytes to GitHub; do not ask the user to test small incremental builds. Keep safe v0.4 rollback and exact title credit `Việt hóa bởi Votri Valley`.

**Status: real font-collision root cause isolated and an experimentally verified non-destructive relocation prototype exists; user-facing source ROM with donor font has NOT yet been produced.**


## CI result confirmed after initial write — v0.5 source codebook PASS

**GitHub Actions [37900453143](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37900453143) completed SUCCESS** on commit `8bed73ac58eb98623c928e99daf631c275d13238`, independently verified against artifact `arena-0.13.0-symbol-map`:

- Durable `checkpoints/v05-collision-free-codebook.json` matches freshly generated v2 codebook exactly. **137 codepoints with unique bytes**, f/w/z at DA/EB/EE, ấ/ằ/ắ at 30/31/32; unsupported uppercase Ừ omitted.
- All **741 source-owned Vietnamese text labels PASS** compile: 500 map, 41 C UI, 100 named-variable, 100 battle. The independent file scanner reports exactly 741 unique owners, **0 duplicates, 0 early/missing FF**.
- New v0.5-codebook compiled source ROM SHA-256: **`419c7578193dc08cd4af04965690fa65a30c89a0e5c11ef6af320409e67b43e1`**. **This is a stock-font compiled experiment**, not a user release.
- Font symbols in the new target are `SmallNarrow 0x71CC64`, `Small 0x724E64`, `Narrow 0x72D064`, `Short 0x735264`, `Normal 0x73D464`. The symbol-aware graft should use these actual addresses, not original shipping offsets. The five source font glyph blocks continue to pass stock clean SHA audits. **The actual new target GBA bytes are not available in this session**; CI uploaded only SHA, symbols, catalog and reports. No full copyrighted ROM is present in public GitHub artifacts.
- The private real-donor font-only test verified all 15 relocated glyph rasters, with Small/SmallNarrow **synthetically produced and not visually certified**. The future target graft must be applied only to a ROM with the exact source SHA above; opening/boot/font/gameplay/emulator QA remains pending.

Do not label this pipeline as a finished playable v0.5 ROM. The user should not need to download technical CI reports or manually test until a coherent build is ready.
