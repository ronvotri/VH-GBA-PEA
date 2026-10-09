# Early-game source localization + donor-font preflight — 2026-10-09

## Verified source-build milestone

- **Full PASS**: [GitHub Actions run 37888719823](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37888719823), commit `6dd568803`.
- Pinned source-build artifact `arena-0.13.0-symbol-map`, `SOURCE_LEVEL_VIETNAMESE_PILOT.json`: **200 map-story labels**, **91 auto-wrapped**, **29 source files**. New deterministic priority stage puts moving truck, Littleroot, Route101, Oldale, Route102, Petalburg, Rustboro before late-game scenes.
- `SOURCE_LEVEL_DYNAMIC_PILOT.json`: **50 PLAYER/RIVAL-bearing labels**, **39 auto-wrapped**, **22 files**.
- `SOURCE_LEVEL_UI_PILOT.json`: **30 source-level UI labels**, **3 auto-wrapped**.
- Combined **280** source-owned labels in a source-built test (not the user's existing v0.4 or full 17,512 integrated ROM); derived pilot SHA-256 `961859be16b07bd3c286002880d052c3d7689179f41a7e660dbd64c7bbdf34ff`.
- The source-built pilot includes the Votri Valley credit by `tools/apply_title_credit.py`, and the five unchanged stock font glyph blocks passed the font-layout audit. Donor Vietnamese glyph blocks are **NOT yet imported**; no emulator/rendering test.

### Previously user-visible failures are now compiled in this experiment

- `InsideOfTruck_Text_BoxPrintedWithMonLogo` — truck-box description, no cross-map pointer override needed because the linker owns the script symbol.
- `LittlerootTown_Text_OurNewHomeLetsGoInside` — Mom's first greeting with proper `{PLAYER}` token and page controls.
- `LittlerootTown_Text_WaitPlayer` — Mom's follow-up line.
- The workflow has **explicit assertions** that all three labels are present in the compile reports. Missing any one fails CI rather than silently claiming coverage.

Translation editorial fix: `translations/map-story/map-story-final-misc.vi.json` truck text has short, natural, 25/18/26-character lines: `Thùng có in logo POKéMON.\\pDịch vụ chuyển nhà\\nvà giao hàng của POKéMON.$`. The context and original page/newline structure are retained; static width count is not equivalent to pixel-perfect runtime confirmation.

## Font integration state / safety

- The exact private clean Arena ROM SHA-256 `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b` and Vietnamese donor v0.4 SHA-256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9` passed local hash gates.
- Original five Latin glyph blocks differ by **5,917 bytes** total: small-narrow 16, small 550, narrow 2078, short 906, normal 2367. Font offset provenance and widths match source build's five stock-glyph SHA-256 checks.
- New source-built target font symbols are relocated relative to shipping; **NEVER paste shipping offsets into source-built binary**. `tools/import_v04_glyphs_into_source_build.py` uses the two symbol files and explicitly requires the target source-built ROM's SHA-256 when outputting the private localized ROM (`--expected-source-sha256`).
- Added shifted-offset regression test so a font graft must change only the new symbol ranges. Source built GBA file itself is **not available in the current local environment**: Actions uploads metadata and SHA only, not copyrighted ROM. As a result, **no source-built ROM had font grafted this turn**.

## Important distinctions and next gates

1. Do not treat 280 compiled smoke-test labels as a fully translated shipping game; `17,512/17,512` is *source manifest coverage*, not integrated runtime coverage.
2. Never overwrite the source-built stock fonts at old shipping offsets. Fetch/build the **exact source ROM corresponding to the pilot SHA**, import donor glyphs under SHA/pinned symbols, and verify all 5 copied glyph blocks and unchanged non-font bytes.
3. Audit the Unicode-to-byte map and line width visually; current guessed Vietnamese codebook contains byte collisions with untranslated English.
4. Then expand source integration to additional map/story, UI and battle placeholders; use source-owned symbol labels and fail-closed semantics; keep original v0.4 rollback and do not upload private ROM or font asset binaries to public GitHub.
5. Emulator QA still needed: title credit font/position, truck/Mom dialog, menus, battle/post-battle, save/reload.
