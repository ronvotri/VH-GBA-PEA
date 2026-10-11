# Pokémon Emerald Arena — 6,090 source labels and STR_VAR static-width budget reflow

**Checkpoint date:** 2026-10-11. Source of truth: `main` branch, `README.md`, `.github/workflows/arena-map.yml`.

## Last confirmed source-built ROM

- [Actions #38145240337](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38145240337) **FULL SUCCESS**.
- **6,090 distinct source-owned Vietnamese labels** linked into experimental GBA, +85 page-local PLAYER/RIVAL/KUN strings above the former 6,005. Existing **1,196 system** and **2,867 map/story** owner labels reverified against ELF/GBA bytes; the new 85 were individually verified.
- Exact source-built ROM SHA256 `94206a5d4ac4143e561a64aad151d87e3194b3a17d8a84b530c7d99c8932da04`, contiguous tail space **1,808,676 bytes**. This remains **stock English raster font**, no accepted v0.4 art graft, no emulator gameplay QA.
- Authored manifest **17,512/17,512 translated** but NOT all integrated. Do not call 1.0 done.

## Work continued this session

New `tools/stage_system_dynamic_static_budget_reflow.py` tackles source-owned `data/text/*.inc` with `STR_VAR_1..3`, `PLAYER`, `RIVAL`, `KUN` placeholder expansions without ever guessing `STR_VAR` runtime size. Within each original native line, **every compiled variable-bearing line must contain exactly the English source's original ordered variable list and its static Unicode-cell count must not exceed the original English line's static-cell count**, capped by 26. Extra authored Vietnamese words are moved into new native scroll lines, with no cross-page word moves, page insertions, variable moves between original source lines, altered words, guessed pointer addresses, or bitmap writes.

- `tools/tests/test_stage_system_dynamic_static_budget_reflow.py` contains regression checks. An initial test failed because the **test-only fake codebook omitted uppercase `C`**; fixed in commit `a09bcf834490dcbf4f720b1e92b5fe3f4902dc4e`. The latest GitHub Actions run's 320 unit tests pass.
- `tools/verify_system_dynamic_static_budget_reflow.py` revalidates all earlier **1,281 source-owned system** and **2,867 map/story** texts at actual ELF/GBA offsets, recomputes every newly staged payload, compares source/linker bytes and checks unchanged stock font, >=1MiB linker tail.
- `.github/workflows/arena-map.yml`: additional isolated `static-budget-system-dynamic-source-trial` compiling after the 6,090 name reflow, producing `SOURCE_STATIC_BUDGET_DYNAMIC_REFLOW_ATTESTATION.json`.

[**Active new CI #38146099792**](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38146099792) was **in progress** at checkpoint creation; **do not add new labels to 6,090** before the new job is FULL PASS and `new_original_budget_dynamic_system_labels` in its attestation is positive.

## Font, credit, release safeguards

Accepted Vietnamese font is the user's old **v0.4** ROM (SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`). Do not regenerate or synthesize its glyphs. The source-compiled trials use **stock English raster glyphs** and are **NOT** visual/gameplay certification. The private v0.4 donor ROM is not in the repo and must not be committed. Safely merge donor-art glyphs only once source/codebook and five-glyph-bank geometry are mutually verified, without corrupting PKMN/Pokéblock/control slots.

Preserve **“Việt hóa bởi Votri Valley”** credit at title, avoid editing title bitmap without a matched asset, and test main menu → intro → overworld → battle → return → save/load → Arena UI before a playable release.
