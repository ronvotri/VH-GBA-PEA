# Pokémon Emerald Arena — 5,946 source-compiled localized strings (11 October 2026)

## Actual source integration verified

GitHub Actions [#38134862518](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38134862518) **FULL SUCCESS** with the paginated NPC integration pipeline from commit `d906d7604ef469815d36c1a48a77e08c6f638eb1`.

- **5,791 → 5,946** unique source-compiled Vietnamese string labels, **155 NEW** page-preserving NPC/map dialogue labels.
- **2,712 → 2,867** independent map/NPC source labels verified **at actual ELF-linked GBA ROM byte locations**, including all previously installed map translations.
- The 155 authored dialogues span **486 GBA pages**, from **80 distinct map script files**; every `\\p` page-break count and the Vietnamese word sequence **within each authored page** was verified unchanged.
- Source owner identity and English `.string` bytes were matched exactly before staging; out-of-scope dynamics and unsupported controls were rejected. No raw ROM repointing or guessed offset writes.
- The compiler/linker-produced experimental packed **STOCK-font** source ROM's SHA256 is `75bf824f8eb7ab5e3932de728c3af7e50bd87c5712386a62a1954d43d61db609`.
- ROM linker high-water after integration: **31,747,076 bytes**, with **1,807,356 bytes of contiguous tail headroom**. A minimum **1 MiB** headroom guard passed.
- All 5 stock glyph-bank content hashes match the clean English font source. **This is NOT the approved Vietnamese v0.4 font artwork**.
- Exact 5946-ROM SHA and font offsets are now paired in `tools/graft_v06_pokeblock_safe_fonts.py` and regression tests:
  - SmallNarrow `0x717448`
  - Small `0x71F648`
  - Narrow `0x727848`
  - Short `0x72FA48`
  - Normal `0x737C48`
- The 5946 font bank addresses **DIFFER** from the old packed 5777 trial (0x7182AC and so on): never reuse old font offsets. A further CI stage guard uses the exact paired hash and geometry.

## Limitations and work ahead

- This is **source-level compiler and linked-byte QA only**. No playable Vietnamese-font-correct patch has been shipped. Existing user-tested **v0.4** is the rollback and approved visual quality baseline.
- Game must still be tested in mGBA across title/intro/maps/battles/return to overworld/save-load and Arena-specific effects, because source linker graphics sections were relocated to recover ROM capacity.
- Unsupported `{PLAYER}` beyond pinned handling, `{STR_VAR_*}`, `{B_*}`, other engine dynamic tokens, and missing Vietnamese glyphs (e.g. uppercase accented characters) require dedicated token semantics and genuine approved font donor work. **Do not silently alter authored Vietnamese words to fit glyphs**.
- The user-facing translation manifest's **17,512** authored entries are a separate source coverage figure, not the number present in the current test ROM. Remaining manifest entries have not all been integrated.
- This project repo publishes tools/reports only, not copyrighted base/modified GBA ROM binaries. Do not upload user's private v0.4 donor ROM or distribute unsafe synthetic fonts.

## How to resume

Read `CONTINUE_WITH_MODEL.md`, `docs/EMERALD_ARENA_PAGED_DIALOGUE_HANDOFF_2026-10-11.md`, this checkpoint, and the newest `PROGRESS.md`. Latest successful **5946 source-integrated** CI was #38134862518; later commits add strict SHA/font-pair regression checks to the same stage, and those must obtain their own CI PASS before treating the *strengthened gate* as proven. Continue with a new source-owner batch or genuine v0.4 donor integration, not another ROM-padding experiment.
