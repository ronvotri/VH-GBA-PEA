# 1,961 verified source-compiled Vietnamese strings — move/item descriptions (2026-10-09)

**Status: compiler + independent source QA PASS. NOT a downloadable release or emulator-verified ROM.**

## Actual successful build

[GitHub Actions #37943838702](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37943838702) **SUCCESS** after repairing a duplicated Python source snippet in `tools/stage_source_descriptions.py`. The full independent QA report from the workflow artifact states **1,961 unique integrated text labels**, **0 duplicate labels**, all properly FF-terminated, and no direct ROM pointer writes.

| Source group | Accepted compiled labels | Independent report |
| --- | ---: | --- |
| NPC and map/story | 1,000 | `SOURCE_LEVEL_VIETNAMESE_PILOT.json` |
| Common UI | 41 | `SOURCE_LEVEL_UI_PILOT.json` |
| Map text with `{PLAYER}` / `{RIVAL}` | 134 | `SOURCE_LEVEL_DYNAMIC_PILOT.json` |
| Script battle texts | 196 | `SOURCE_LEVEL_BATTLE_PILOT.json` |
| Static C battle texts | 59 | `SOURCE_LEVEL_BATTLE_C_PILOT.json` |
| **New 2-line move descriptions** | **246** | `SOURCE_LEVEL_MOVE_DESC_PILOT.json` |
| **New 2–3-line item descriptions** | **285** | `SOURCE_LEVEL_ITEM_DESC_PILOT.json` |
| **TOTAL** | **1,961** | `SOURCE_TEXT_INDEPENDENT_QA.json` |

Compiled source-only GBA SHA256 **`c108adbca891bb6164ad99a08e54c0733f81456ea18d30c3c99c1e8ce415ac67`**. All **five** font blocks matched *stock* source assets in `SOURCE_LEVEL_FONT_AUDIT.json`; **Vietnamese font graft is NOT installed in this compiled ROM yet**.

## Tooling

- `tools/stage_source_descriptions.py` parses the exact pinned multiline C source `static const u8 sXYZDescription[] = _("\n" "...");` and `sXYZDesc[]`, preserves the symbol label and rewrites it as byte-encoded Vietnamese C initializer. `src/data/text/move_descriptions.h` requires **two visible lines**, `src/data/text/item_descriptions.h` requires exactly the source **two or three visible lines**.
- Unchanged English source content, exact label identity, known glyph codebook, number of newline tokens, no page/scroll tokens, supported byte width and dynamic token checks are all required. Unsafe rows are *skipped*, not silently patched.
- `tools/tests/test_stage_source_descriptions.py` covers original/translated multiline C string block ownership, 2/3-line preservation, source drift and rejected unknown glyphs/variables/oversize text.
- `tools/verify_compiled_source_strings.py` now attests the `move-desc` and `item-desc` groups independently; exact FF and no duplicate source labels are verified before the assembler/linker build.
- All 17,512 manifest translation entries are **not** yet integrated into a playable ROM.

## Remaining description cases

Original source manifest: 355 move description rows (354 changed), 310 item description rows (309 changed).

Initial conservative stage rejected **98 move descriptions** because their authored Vietnamese exceeded 26 encoded text cells on an existing line. It also rejected **5 missing `ỳ`**, **2 missing `è`**, among other glyphs.

Item stage accepted **285**, while **16** variable/control-token rows, **2** line-count mismatches and a small number of missing glyphs (e.g. `&`, `ỷ`, `%`) remain blocked. Do not delete dynamic fields or remove accents to claim 100% coverage.

## New two-line move rebalance experiment (CI pending)

A newer tool pass adds an opt-in `--rebalance` for **move only**. It moves the newline to a different word boundary without deleting, rearranging or paraphrasing words; both lines must fit `<=26` glyph cells. A read-only corpus check found **42 potentially eligible** of the 98 overlong authored move rows, before unknown-glyph checks. No third line is introduced. GitHub Actions [latest workflow](https://github.com/ronvotri/VH-GBA-PEA/actions) attempts this; verify its actual accepted count and independent QA before reporting additional integrated rows.

## Important unresolved blocker

Even though source compilation and pointer ownership QA PASS, **the source GBA still uses stock English font raster**. The `v0.5` collision-free Latin codebook reserves `0x30/31/32` for `ấ/ằ/ắ` and restores ordinary English `f/w/z`, but the glyph artwork must be imported into the *exact matching source-built ROM* using SHA-locked font import tools, then five-font visual/emulator tests and gameplay save/load tests must PASS. Original playable v0.4 remains a rollback; no new playable ROM was delivered.

Next source groups include long battle templates and remaining story/catalog descriptions; keep explicit `Việt hóa bởi Votri Valley` title credit.
