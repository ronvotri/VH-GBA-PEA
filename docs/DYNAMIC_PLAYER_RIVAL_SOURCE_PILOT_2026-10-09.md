# Source-first PLAYER/RIVAL dynamic text — 2026-10-09

## What is confirmed

- Source-first 200 map/story + 30 C UI strings compiled together in [Actions #37884608217](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37884608217), not the user's live v0.4 ROM.
- Latest existing stock-source font compatibility gate passed in [Actions #37884850714](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37884850714). Vietnamese v0.4 glyphs have NOT yet been imported into this source-built binary; emulator text rendering is NOT verified.

## Dynamic source staging

- Added `tools/stage_dynamic_map_translations.py` and `tools/tests/test_stage_dynamic_map_translations.py` to integrate lines containing `{PLAYER}` or `{RIVAL}` from exact source script labels.
- The pinned upstream `charmap.txt` defines `{PLAYER}` = `FD 01`, `{RIVAL}` = `FD 06`; both values are now enforced inside the encoder, not just by the command-line setup. `PLAYER_NAME_LENGTH` is 7 in the pinned source constants, so maximum 7 glyph cells are reserved for dynamic names.
- Source placeholder sequence/order must equal original English; original page-break (`\p`) count must match. Unknown glyphs, unsupported dynamic variable types such as `{STR_VAR_1}`, changed source text, long lines and wrong charmap bytes are rejected.
- Source `.string` blocks are replaced by equivalent `.byte` directives under exactly the same assembler labels; the compiler/linker owns all pointer relocation. No blind binary writes.
- Workflow now attempts 200 static map/story + 30 C UI + up to 30 dynamic PLAYER/RIVAL map messages in isolated build workspace; reports are saved as metadata without publishing ROM bytes.

## Regression and CI

- Early unit test rejected a dangerous implementation that merely checked that dynamic tokens began `FD`, because a corrupt `FD 44` also would have passed; this bug was fixed at commit `69e6269`.
- The corrected workflow is [Actions #37886373221](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37886373221). Verify full-run conclusion and `SOURCE_LEVEL_DYNAMIC_PILOT.json` in artifact before asserting a compiled count.

## Still pending

- Genuine v0.4 font integration and display glyph validation, variable-width `{STR_VAR_*}` and complex battle placeholders, dynamic dialogue wrapping, full story translation integration, emulator intro/menu/save/battle and post-battle QA.
- Keep safe v0.4 Text Cluster Pass as rollback; source-first smoke test ROM is not a complete or visually validated Vietnamese release.
- The existing title credit requirement remains exactly: **Việt hóa bởi Votri Valley**.
- No copyrighted ROM bytes or private font arrays are stored in the public repository.

## Verified compiled checkpoint and next expanded run

- **Verified overall PASS:** [Actions #37886532765](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37886532765), artifact confirms **200 map (24 files, 87 reflowed) + 30 C UI (3 reflowed) + 30 PLAYER/RIVAL lines (22 source script files)**, totaling **260 distinct source labels**. It separately contains the source-built Votri title credit and a passing source-font compatibility audit. SHA of the compiled source pilot: `e7900c6fa34881ebafe0143fff24bb371e41b77c4a0cc337e1eefd10e44138b9`. This is **not** the v0.4 game ROM and the Vietnamese donor font is not installed yet.
- New optional `tools/wrap_dynamic_map_text.py` reflows long PLAYER/RIVAL lines at word boundaries, counts each maximum 7-character name, retains page breaks and word order, and uses `\n`/`\l` safely when needed. A dedicated regression suite `tools/tests/test_wrap_dynamic_map_text.py` is included. The map staging CLI has `--auto-wrap`; controls are re-encoded and page counts checked after reflow.
- The source workflow was raised to **up to 50** dynamic map labels, with the same 200 map + 30 UI group and title credit, at commit `5b03f479`. Track its latest run and read `SOURCE_LEVEL_DYNAMIC_PILOT.json` for the actual accepted count, not the configured limit.
- The early-game Mom source translation manifest `translations/map-story/early-game-littleroot-route101-oldale.vi.json` now uses **Mẹ:** instead of uppercase **MẸ:** across 21 entries because the v0.4 codebook has `ẹ` but not yet a verified uppercase `Ẹ` glyph. The intro also naturally reads `Đây là thị trấn Littleroot.` instead of uppercase special `THỊ TRẤN` that requires unverified glyphs. This is translation-source editing, not a shipped GBA patch.
- Current final workflow candidate after translation update is [Actions #37886877864](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37886877864); it was in progress when documented. Do not claim it PASS until checked.
- The source-first build still uses stock English font assets until the SHA-locked font-importer is applied in a private runtime with source-built ROM and exact donor binaries; **no emulator QA and no stable ROM release**.
