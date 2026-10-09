# 741 source-level Vietnamese strings + font safety audit — 2026-10-09

## Verified milestone: actual source-built ROM compilation

[GitHub Actions #37895308303](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37895308303), commit `cf1c46fde97533160e61dfa3c5916f70218694b3`, **PASS** in the full build + compilation smoke. Verified artifact reports (not guessed from CLI limits):

| Compiled text category | Labels | Auto-reflowed | Source files |
| --- | ---: | ---: | ---: |
| map-story `data/maps/` | 500 | 205 | 57 |
| general C UI `src/strings.c` | 41 | 4 | 1 |
| map-story `{PLAYER}`/`{RIVAL}` | 100 | 75 | 36 |
| battle `data/text/*.inc` | 100 | 42 | 3 |
| **TOTAL** | **741** | **326** | n/a |

Compiled experimental source ROM **SHA256 `e63d4799b06c634d92b3dc003e07e27c933629e480c8c01047457b0029ef6cc7`** (32MiB). It is a *fresh stock-font source build* of pinned Emerald Arena 0.13.0 with translations; **NOT** a modification of the original existing v0.4 gameplay binary. The compiled source build also contains the user-required visible title line **`Việt hóa bởi Votri Valley`**, built by the title-credit source patch. Five compiled Latin font glyph blocks match stock clean reference according to `SOURCE_LEVEL_FONT_AUDIT.json`.

The source build retains three mandatory early-game text sources from prior screenshot bugs: `InsideOfTruck_Text_BoxPrintedWithMonLogo`, `LittlerootTown_Text_OurNewHomeLetsGoInside`, `LittlerootTown_Text_WaitPlayer`. All source pointers are managed by assembler/linker, no global binary pointer rewrite.

Full original translation manifest is **17,512 source translation entries**, but only **741 labels** are integrated in this source-first smoke build. **Do not present 741 as a finished Vietnamese ROM.**

## New actual tools and safety checks

- `tools/stage_source_map_translations.py` now has an explicitly gated `--category battle --source-prefix data/text/` mode. A record must match its source label and exact English bytes, have a supported glyph/control sequence and fit the conservative length bound; source-only `.byte` replacing `.string` under the *same assembler label*. Two battle-specific unit tests added. No source-script pointers are edited manually.
- `tools/audit_v04_font_code_collisions.py` with regression tests: read-only SHA-locked private donor check of original Latin font codepoints and the inferred Vietnamese codebook.
- **Verified font incompatibility remains:** original Hoenn Latin text assigns `f=DA`, `w=EB`, `z=EE`. Existing v0.4 codebook also maps accented `ấ=DA`, `ằ=EB`, `ắ=EE`. In Vietnamese v0.4 donor ROM, those Latin glyph blocks are actually changed in normal/narrow/short fonts; the small/small-narrow glyph blocks still use the original English shapes. **Blind donor font transplant would mix Vietnamese accents with yet untranslated English**, exactly the user's earlier symptom. There is also ambiguous `Ừ`/`ừ` sharing `0x50`. This is not proof that other inferred glyphs are wrong.
- Existing graft helper `tools/import_v04_glyphs_into_source_build.py` has stringent SHA gates and target symbol-offset checks and was improved to require exact *target source-built SHA256* to output. It **has NOT grafted donor font to this new source ROM**, because GitHub artifact deliberately contains metadata/hash only; no full copyrighted game ROM or donor glyph binary stored on the public repo.
- New independent source attestation `tools/verify_compiled_source_strings.py` and tests verify each source-owned assembly/C label and exact final FF byte across map/UI/dynamic/battle groups, with no duplicated labels and no fake totals. A CI gate has been added; check the latest [Actions #37895525872](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37895525872) result before claiming independent attestation PASS. It was still in progress when this document was first authored.

## Why this is not release ready

1. Actual rendered Vietnamese glyphs (especially f/w/z aliases and case distinctions) still need a collision-free strategy and testing with the engine font renderer before importing donor font. Literal indices with `0xF7` or above are text controls, **NOT** safe free glyph slots. Do not choose supposedly unused font slots without source charmap and layout proof.
2. Pixel-accurate line widths and game window behavior, plus proper battle text placeholders, need review. Static word/cell length reflow is conservative but not a visual guarantee.
3. Still thousands of source/user-facing strings outside this prototype. Future expansion: full battle C templates and variable names, long messages / unknown upper-case accents, NPC and catalogs.
4. Emulator boot/title/truck/Mom/menu/battle/save-load QA not performed. Original stable v0.4 should remain a rollback option.

## Next actions

Check independent attestation CI and repair failures only from evidence; produce deterministic, collision-aware font/codebook migration from private clean/v0.4 + exact source ROM (never upload proprietary full ROM to public GitHub). Extend source build categories after each good compiler + QA gate. Preserve `docs/EARLY_STORY_SOURCE_FONT_GATE_2026-10-09.md` and this checkpoint for handoff.
