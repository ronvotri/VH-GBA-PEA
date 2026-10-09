# 2026-10-09 — Source-first Vietnamese integration pilot

**Status:** A limited source-level smoke build is being tested in GitHub Actions. It is **not** a complete localized ROM, does **not** validate Vietnamese font glyphs, and does **not** replace the guarded v0.4/v5 binary repair work.

## Why this route

The binary repair track exposed corrupt pointers, shared-suffix text that could not be edited in-place, English/accents sharing glyph bytes, and many strings too long for their original allocation. Source-level insertion allows the assembler/linker to resize text and update source-owned symbols by themselves instead of guessing ROM free-space addresses or mass repointing.

## Commit and toolchain

- `tools/stage_source_map_translations.py` (commit `0e396d8`) stages limited `map-story` English-to-Vietnamese translations by exact source file and symbol label. It uses existing 17,512-row `user-facing-integration-plan.json` and the experimental v0.4 glyph codebook.
- `tools/tests/test_stage_source_map_translations.py` (commit `8c79c0e`) contains **11 regression tests** of exact English source matching, label preservation, Vietnamese encoding, control bytes, unsupported dynamic placeholders, NFC validation, encoded line length, rejected glyph/control collisions and limited map selection; the local test run passed.
- `.github/workflows/arena-map.yml` (commit `bab0dca`) now adds a **separate source-localization-smoke workspace after catalog/manifest construction**. It stages at most ONE conservative `data/maps/LittlerootTown/` entry and compiles that workspace independently, preserving the original normal Arena build plus separate Votri Valley title credit smoke stage. Artifacts include `SOURCE_LEVEL_VIETNAMESE_PILOT.json` and SHA-256 **only**, never a distributable ROM.
- Exact pinned upstream `pret/pokeemerald` and `GBurgardt/pokemon-emerald-arena` sources and existing workflow dependencies are reused, not silently changed.

### Safeguards and current limits

The source patcher only replaces contiguous `.string` directives under **one exact existing label**, using byte directives `.byte 0xXX` to avoid incorrectly assuming an English charmap understands Vietnamese Unicode. It rejects source mismatch, multiple/missing labels, unknown glyphs, dynamic tokens such as `{PLAYER}`, unsupported controls, missing terminal `$`, early terminator, non-NFC accents and any line exceeding the conservative threshold. By default it is dry-run, with explicit `--apply` needed to change workspace sources. Source reference pointers remain owned by the assembler/linker.

**This only proves an alternate compilation method, not correct rendering.** The experimentally inferred v0.4 font codebook is not a bijective Unicode map and is not visually validated for the source-built ROM. The newly generated source-built ROM may not include the v0.4 Vietnamese font modifications. Larger story pages, dynamic placeholders, UI/battle C strings and title logo integration need separate supported transformations and testing.

## Historic pointer evidence progress

The same checkpoint also added:
- `tools/triage_actual_script_ownership.py` and `tools/tests/test_triage_actual_script_ownership.py` (9 local unit tests PASS).
- `checkpoints/shared-owner-opcode-evidence-2026-10-09.csv`, **44 matching source words** in 43 strings: **13** loadword-0F, **16** trainerbattle-5C, **11** aligned text-table entries, **2** graphics coincidences, **2** code coincidences.
- Those 40 plausible script/table occurrences are NOT permission to patch; the exact latest guarded ROM was unavailable, so no additional GBA binary changes were made.

## Required next

1. Check source smoke CI. If it fails, fix source matching/build without touching the guarded binary.
2. Extend to controlled pages, dynamic `{PLAYER}` placeholders and C source UI/battle localization, with per-file source-ownership verification; add appropriate glyph/font compilation rather than reusing raw English assets.
3. Rebuild all source translations in a fresh workspace, validate encoding/font and battle/save runtime; only then consider a stable v0.5 alternative.
4. Keep the original v0.4 rollback and do not represent 17,512 source manifest entries as installed ROM entries.

User does not need technical ZIPs or repeated manual test requests.
