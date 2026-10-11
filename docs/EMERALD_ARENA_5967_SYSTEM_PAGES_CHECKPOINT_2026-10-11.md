# Pokémon Emerald Arena — 5,967 compiled source strings: paginated system text

## Verified result (2026-10-11)

GitHub Actions [#38137406551](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38137406551) **FULL PASS**, from commit `127faa1996bd07d88e122374a48e38662cd93b7e`.

Starting from the prior 5,946 distinct source-compiled labels, the new `tools/stage_static_paged_system_text.py` integrated **21 further unique system-text strings** (seven `data/text/*.inc` files) in an isolated, linker-compacted **stock-font** source build:

| Metric | Passed source-build value |
| --- | ---: |
| Distinct compiled Vietnamese source labels | **5,967** |
| New paginated system-text labels | **21** |
| Source-owned system text ELF/GBA payloads verified | **1,158** (1,137 earlier + 21 new) |
| Map/story dialogue ELF/GBA payloads attested in previous 5,946 build | **2,867** |
| Contiguous ROM linker tail headroom | **1,807,588 bytes** |
| Five stock Latin font glyph banks | Unchanged byte hashes |
| Runtime gameplay / visual approval | **NO** |
| User-approved v0.4 Vietnamese font grafted | **NO** |

The script reuses the page-locked, word-preserving compiler from `tools/stage_static_paged_map_dialogues.py`. It admits only exact source-owned static `data/text/` labels where the English source and authored Vietnamese text have **identical original GBA `\\p` page counts**; every Vietnamese word stays in its own authored page. Dynamic placeholders, unsupported escapes, unencodable glyphs, source English mismatches, or malformed page layouts are excluded. Standard native GBA newline and scroll controls (`\\n`, `\\l`) may be reflowed **within**, not across, original pages. All source glyphs still use the restrictive approved-codebook bytes, but the actual glyph pixels remain stock/English.

The CI compilation re-checks each of **1,158 source-owned system labels** byte-for-byte at its newly linked ELF/GBA ROM address; the 2,867 earlier verified map source labels remain unchanged by this new system-only patch and were verified in the previous stage. Source ROM SHA256 of this 5,967 stock-font experiment: `4e54dcdf20ce4fa6899400069c99feb17723147227cd3693ac4ca78feec2838a`.

Exact five clean stock-font source offsets, now pinned to this SHA in `tools/graft_v06_pokeblock_safe_fonts.py` and regression-tested:

- gFontSmallNarrowLatinGlyphs: `0x717360`
- gFontSmallLatinGlyphs: `0x71F560`
- gFontNarrowLatinGlyphs: `0x727760`
- gFontShortLatinGlyphs: `0x72F960`
- gFontNormalLatinGlyphs: `0x737B60`

Generated CI reports: `artifact/SOURCE_PAGED_SYSTEM_ADDITIVE_STAGE.json`, `artifact/SOURCE_PAGED_SYSTEM_ADDITIVE_FONT_AUDIT.json`, `artifact/SOURCE_PAGED_SYSTEM_ADDITIVE_HEADROOM.json`, and `artifact/SOURCE_PAGED_SYSTEM_ADDITIVE_ATTESTATION.json`.

## Important unresolved blockers

1. **Not a playable release.** Source build still uses original stock English glyph *images*, not accepted v0.4 Vietnamese font art. Previous synthesized glyph variants visibly distorted characters. Do NOT automatically synthesize or ship them again.
2. **Arena linker graphics move still experimental** until mGBA visual/gameplay QA confirms sprite/animation/title integrity, title credit, intro, overworld → battle → return, menus and save/load. User-approved stable v0.4 remains available as rollback.
3. **17,512 translated manifest rows are NOT 17,512 compiled strings**. This checkpoint proves 5,967 distinct source-owned strings only.
4. Remaining map, system and UI translations include dynamic `{PLAYER}`, `{STR_VAR_*}`, `{B_*}`, altered page semantics and unsupported Vietnamese glyphs, all needing context-aware dedicated source logic instead of blind padding/repointing.
5. Copyrighted full ROMs and private v0.4 donor remain outside the GitHub repository.

Next technically meaningful work: identify and validate genuine v0.4 glyph donor source locally, improve unsupported glyph coverage only with approved artwork, source-integrate dynamic placeholders with strict semantic and layout QA, and run the packed-source ROM through mGBA on a private artifact. Preserve title credit `Việt hóa bởi Votri Valley`.
