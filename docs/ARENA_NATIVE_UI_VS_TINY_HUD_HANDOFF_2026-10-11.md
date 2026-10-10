# Pokémon Emerald Arena — GUI localization: 17 native-font menus, tiny HUD is a different renderer

## Source provenance / exact scope

Source Arena v0.13.0 defines 46 `arena-only` source catalog entries. Its `src/realtime_arena.c` **native Pokémon `PrintPopup`** widgets draw ordinary in-game letter glyphs, but `src/arena_hud.inc` implements a **3×5 monochrome mini-font** with `HudTinyWindow`. It supports only the built-in GBA codepoint ranges `CHAR_A..CHAR_Z`, `CHAR_0..CHAR_9`, colon, plus, dash, punctuation. Lowercase/accented v0.4 glyph codes will be ignored / draw blanks in the mini renderer. This is an independent UI bug category, NOT solved by importing the five ordinary v0.4 font banks.

Commit [86db2a6](https://github.com/ronvotri/VH-GBA-PEA/commit/86db2a6dc4a6d24024400774bb42c7382116eea2) adds `tools/stage_arena_native_popup.py`, unit tests, integration into `.github/workflows/arena-map.yml`, and revises **17 actual player-facing PrintPopup menu labels** to byte-encodable, context-correct Vietnamese. This includes directional labels, 6 move styles, status label, pause menu title and four menu choices. The original C source line / name / English initializer and fixed row capacity are checked individually; unknown codepoints, changed source and label ambiguity fail closed. The source-built GBA is intended to be verified against *each* original local/C-array linker symbol and offset (including 7/8/18-byte fixed rows), **not inferred from a random ROM string search**.

GitHub Actions [#38082880980](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38082880980) was pending completion when this document was written. A CI PASS is required before increasing the source-compiled label count from 5,282 to 5,299. The `SOURCE_ARENA_NATIVE_POPUP_ATTESTATION.json` artifact is the exact output to inspect.

## Non-overwritable UI boundaries

- **Tiny capture/status HUD (still blocked):** `sCaptureHint`, `sCaptureAim`, `sCaptureMiss`, `sCaptureBreak`, `sCaptureParty`, `sCapturePC`, `sCaptureEmpty`, `sCaptureFull`, `sCaptureCount`, `sQualityTabs`, tiny menu help strings, etc. Do not directly substitute accented C source byte arrays here before implementing and testing the 3×5 glyph renderer's accent handling, or switching specific UI text to a fully measured supported native font path. It is not appropriate to fake support by merely translating the source manifest.
- **Arena lab-only C texts:** `sTrainerFixtureDefeat` is under `#if ARENA_LAB` (disabled in the normal retail arena build). A translated source initializer there does not necessarily create a ROM-visible label. Keep the Arena-only build configurations distinct.
- **Identity values:** `PP`, `POKéMON`, `GERMAN`, `ARENA` may be intentionally unchanged / names, not missing English translations.

## Next actions

1. Check the exact CI #38082880980 conclusion, and verify all 17 native-menu bytes in the compiled GBA at linker-owned positions before claiming completion.
2. Address the tiny HUD separately with source-level font/rendering tests and actual readable in-game screenshots; prefer the user-approved v0.4 glyph forms in any normal native-font panel.
3. Continue integrating system-UI/battle/dynamic variable messages from the 17,512-user-facing source translation catalog. New CLI staging steps must be additive on the last verified translated source tree and their source labels counted once only.
4. Do not publish a ROM before private user-accepted v0.4 donor-font graft, title-credit visibility, intro, overworld, battle, post-battle and save/load QA. Never commit commercial ROMs to GitHub.
