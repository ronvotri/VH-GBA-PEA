# Move-description editorial sweep — all 354 source texts (2026-10-09)

## Purpose

Close the **59 move descriptions** previously excluded from the source build for overlong text (and the related unsupported-accent cases) without deleting semantic gameplay information, losing Vietnamese diacritics or altering the fixed GBA two-line description layout. Work is committed to the public source/translation repository; no proprietary ROM assets were uploaded.

## Completed changes in source

- Edited **62 long translated move descriptions** directly across **all nine** `translations/system-ui/move-descriptions-01..09.vi.json` source manifest files. Each is now two lines with **1–26 visible glyph cells per line**; all characters exist in the experimental **v0.5 collision-free codebook**. Hand-edited lines preserve relevant battle mechanics, such as 2–3-turn lock-in and confusion, poison/paralysis, PP/HP, recoil, target immunity, recharge turns, and multi-hit effects.
- Edited **7 further move descriptions** with unsupported v0.5 glyph characters (the missing `è`, `ỳ`, `õ` and uppercase `Ư`): Body Slam, Supersonic, Psybeam, Submission, Splash, Wish and Magical Leaf. Used contextual Vietnamese synonyms rather than stripping accents or inserting guessed glyph bytes.
- No .gba binaries, script labels, pointer bytes, header templates, compiled font blocks or game-executable assets were changed. These are **authored translation source edits**.
- Added `tools/tests/test_condensed_move_descriptions.py` to lock the **62** revised moves, two-line/26-cell widths, supported accents and important numeric/status mechanics.
- Added `tools/tests/test_complete_move_descriptions.py` to validate **all 354** authored move descriptions with actual v0.5 glyph-byte encoding. It requires **315 directly fitting lines, 39 deterministic word-boundary rebalances**, and rejects unsupported glyph bytes, missing final FF, or extra GBA dialogue line controls.
- Updated `.github/workflows/arena-map.yml` to stage `--kind move --limit 355 --rebalance` and require **exactly 354** integrated move labels, with **39** auto-rebalances. All source-ownership and compiler QA gates remain enabled.

## Static editorial/codebook preflight

The last read-only direct review of the nine GitHub translation manifests, after editing, found:

| Check | Result |
| --- | ---: |
| Authored move descriptions | **354** |
| Directly within two 26-cell lines | **315** |
| Fit safely after moving the newline, with no removed words | **39** |
| Require deletion/abbreviation beyond word-boundary rebalance | **0** |
| Missing characters in v0.5 source codebook | **0** |

This is **source-text / encoding readiness**, not proof of pixel-perfect font rendering or ROM boot.

## Build status / acceptance gate

Last previously confirmed source-build total: **2,000 unique compiled Vietnamese labels** from [Actions #37944716925](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37944716925), including 285 move descriptions. If all new candidates compile without other changes, the expected next total is **2,069** (285 → 354 moves, +69). **Do not report 2,069 as verified until the fresh CI finishes and the independent source QA report is checked.**

Fresh run: [GitHub Actions #37950847854](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37950847854), **PENDING/BUILDING when checkpoint was written**. It must pass:
1. Unit tests for all 354 move texts and 62 specific edits.
2. Compilation into pinned Emerald Arena source via exact C symbol names and English source bytes.
3. Independent audit of every integrated byte-array source label, uniqueness and terminator byte `FF`.
4. Source font-layout checks and title-credit `Việt hóa bởi Votri Valley`.

If new CI fails, inspect the exact failed step/logs, fix the source/test tool and rerun instead of increasing the reported integrated count.

## Remaining milestones (not optional)

- The experimental source ROM still uses **stock English font shapes**. The verified private donor v0.4 bitmap has yet to be imported using the source ROM SHA and v0.5 remapped glyph slots; correct small-font glyphs, glyph widths and rendered Vietnamese require actual emulator QA.
- Remaining variable-bearing item descriptions, complex battle message placeholders, rare case-sensitive Vietnamese characters, map/story/catalog strings and battle/item user-facing text need dedicated integration.
- Preserve stable original v0.4 as rollback and do not treat the **17,512 source translation manifest entries** as installed playable game strings.
