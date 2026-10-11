# Emerald Arena — Pokédex four-line source integration checkpoint (11 October 2026)

## CI result — completed and independently attested

- [GitHub Actions **#38157439511**](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38157439511): **FULL PASS**. The new Pokédex stage compiled and checked **306 additional C-owned source symbols**, bringing the verified source-ROM total from **6.648 → 6.954**.
- **183** Pokédex descriptions were automatically reflowed at word boundaries, preserving every original Vietnamese word in exactly four lines; the other **123** accepted descriptions retained their original line breaks.
- All **6.648 previously attested source labels** were checked again by the chained verifier. All **306** new `g...PokedexText` symbols had their C initializer bytes re-encoded independently and compared to the actual ELF/GBA address.
- The **81 skipped descriptions** were not silently modified. Rejection reasons: `ỳ` 26, `è` 11, `õ` 8, `°` 3, `Ở` 2, `Â` 2, `ỷ` 1, `ỹ` 1, `♀` 1, `♂` 1, `;` 1, plus **24** descriptions whose complete authored words could not fit within four 40-cell rows. The counts represent only the first failing gate per description.
- Experimental **stock-font** GBA SHA256: `302698c36cbe35b057025133c741da71ae75ce2cffacd9b5f8ff58702aa8fcea`; contiguous linker headroom **1.815.684 bytes**. The verified script states `approved_v04_Vietnamese_font_imported=false` and `emulator_rendering_QA=false` — these are still release blockers.
- Full source-label milestone is **6.954**, *not* a literal percentage of UI/gameplay fully localized. All **17.512** manifest items remain authored translations.

## Verified source-build baseline

- Last **FULL PASS** before Pokédex: [GitHub Actions #38156331396](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38156331396). **6,648** distinct Vietnamese source strings proven in ELF/GBA.
- The immediately preceding source-owned multiple-dynamic-line experiment `SOURCE_MAP_MULTI_DYNAMIC_LINE_SLOTS_STAGE.json` admitted **0** new map labels, correctly preserving the 6,648 checkpoint. Do not count attempted input entries as compiled strings.
- The authored localization manifest remains **17,512/17,512**, but ROM source-integration count is **not a percentage of playable game screens**.
- All source-built trials still retain five **stock English bitmap** banks. The user's private, approved v0.4 Vietnamese font is the visual reference: SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`. **Do not synthesize a replacement font** or claim a release before donor migration and emulator QA.

## New bulk Pokédex text trial

- `tools/stage_source_pokedex_text.py`: static C-owned source symbol `src/data/pokemon/pokedex_text.h`, up to **450** catalog entries; requires original exact English initializer, four native lines / 3 `\\n` separators, no runtime tokens, every Vietnamese word retained, max 40 encoded cells per line, strict v0.6-safe codebook. A rejected entry stays unchanged.
- `tools/tests/test_stage_source_pokedex_text.py`: source matching, unrelated symbol preservation, impossible box refusal, unknown glyph and token refusal, word-preserving reflow and no duplicate C label. Initial unit test used an impossible 4x40 fixture, corrected to a word-partitionable fixture; test **PASS** in the immediately prior Actions run.
- `tools/verify_source_pokedex_four_line.py`: first re-attests the entire **6,648** baseline by existing verifier, then independently re-encodes every newly accepted Pokédex symbol, checks unique ELF addresses, exact C byte initializer and matching physical GBA bytes, original four-line size, word order and unchanged font/headroom. Reports `new_exact_Pokedex_source_labels` and `total_verified_source_labels` and excludes false gameplay readiness.
- `.github/workflows/arena-map.yml`: new isolated Pokédex build after the 6,648 source-owning map trial. Artifact `SOURCE_POKEDEX_FOUR_LINE_STAGE.json` plus `SOURCE_POKEDEX_FOUR_LINE_ATTESTATION.json`.
- Active build at checkpoint: [GitHub Actions #38157439511](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38157439511). **No new label counts should be reported unless FULL PASS and the attestation gives a positive count.**

## Read-only authored Pokédex eligibility preview

An independent audit of the ten authored `translations/system-ui/pokedex-text-01..10.vi.json` files found **387** distinct translated descriptions, all retaining exactly four authored text lines. **306** were preliminarily compatible with the current glyph-codebook inventory and a possible four-line, 40-cell word-preserving partition; **81** had missing glyphs or impossible layout combinations, and **239** authored entries needed at least some line-width repair before a physical fit. These are *pre-build candidates*, **not** attested source labels or gameplay coverage. Common unsupported glyphs in the authored Pokédex subset include `ỳ` (27 source rows), `è` (12), `õ` (8), `°` (3), plus `♀/♂`. Preserve accents and special symbols; do not silently normalize them away.

## Next bottlenecks and approved artwork

Read `skipped_reasons` to understand actual missing Unicode glyphs, lines longer than 40 cells or English source-owner mismatch. The v0.6 codebook has 141 known unavailable Unicode characters in the broad catalog diagnostic; this does **not** mean the approved v0.4 donor font is visually defective. Do not erase Vietnamese diacritics or inject fabricated glyph bitmaps to increase staged numbers. Once stable, reconcile original approved glyph artwork and private donor code-to-pixel mapping, then visual/gameplay test title → intro → maps → Pokédex → battle → save/load → Arena UI. Preserve title credit **“Việt hóa bởi Votri Valley”**. Never commit full copyrighted Pokémon ROMs.
