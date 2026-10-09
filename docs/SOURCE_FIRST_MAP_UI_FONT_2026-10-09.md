# Source-first Vietnamese integration: 200 map rows, C UI staging and v0.4 font data (2026-10-09)

**Status: research/source build, NOT a user-playable v0.5. No emulator/visual QA.** Never equate translated source manifest coverage 17,512/17,512 with shipped ROM integration.

## Confirmed, completed map-only CI

[GitHub Actions run 37883943966](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37883943966) **PASS**. The source-build artifact report `SOURCE_LEVEL_VIETNAMESE_PILOT.json` independently confirmed:
- **200** map/story Vietnamese translations staged into **24** `data/maps/*/scripts.inc` source files.
- **85** source texts needed opt-in conservative newline/scroll reflow.
- **215** additional candidates were correctly blocked as `explicit third line requires review`; numerous glyph/control/dynamic-token cases were also excluded.
- Source-built output SHA-256 `47f9cdc86d063eaa2152b038945e9d33ab82dd92f131a11d68096738fe0e7a53`. The compiler and linker produced a different valid GBA from the original source baseline. This does NOT include the user v0.4 font asset modifications.

Tools:
- `tools/wrap_vietnamese_map_text.py` and `tools/tests/test_wrap_vietnamese_map_text.py` (14 tests) conservatively preserve existing `\\n/\\p/\\l` controls, wrap only at word boundaries, avoid splitting double-curly-quoted phrases, preserve token order, reject dynamic placeholders, unknown controls, overlong words, double spaces, and ambiguously formatted third lines.
- `tools/stage_source_map_translations.py` gained an opt-in `--auto-wrap` flag and reports both authored and staged text, including `auto_wrapped_labels`. It retains exact English source-label match, Unicode NFC validation and C/asm-independent byte-encoding protections.

## Separate C UI source-first staging

- `tools/stage_source_ui_translations.py` and its regression tests now handle only `gText_*` static long message strings directly under `src/strings.c`. It skips short/narrow UI fields, unsupported dynamic controls, source drift, and long unfit text; stage uses the full C symbol as owner, with no manual ROM pointer writes.
- Important implementation correction: C `_("...")` strings **implicitly terminate** in the assembler/charmap; the Vietnamese UI translation manifest often lacks a terminal `$` unlike map `.string` blocks. The tool now appends an FF terminator only for byte encoding if missing, and tests this behavior explicitly. An initial C UI smoke CI failed with zero accepted rows because of this; corrected and **unit tests PASS**. Do not report a combined GBA compile PASS until its later CI run is actually complete.
- The combined map+UI compiler smoke workflow was added in commit `fba88cb`. Follow the latest run associated with corrected commit `8523be7` / subsequent main; the older failed run `37884118717` must not be mistaken for success.

## Exact v0.4 font-glyph extraction prototype

The user-provided released Arena clean and v0.4 SHA-locked donor ROMs have identical fixed-size layout for five named Latin glyph arrays (each **32,768 bytes**):

| Source-build symbol | Clean ROM offset | Modified bytes in v0.4 |
| --- | --- | ---: |
| `gFontSmallNarrowLatinGlyphs` | `0x0071DEA0` | 16 |
| `gFontSmallLatinGlyphs` | `0x007260A0` | 550 |
| `gFontNarrowLatinGlyphs` | `0x0072E2A0` | 2,078 |
| `gFontShortLatinGlyphs` | `0x007364A0` | 906 |
| `gFontNormalLatinGlyphs` | `0x0073E6A0` | 2,367 |
| **Total** | | **5,917** |

The corresponding `gFontNormalLatinGlyphWidths` bytes observed at `0x007466A0..0x007468A0` are unchanged in v0.4. This is **binary font data equivalence**, not proof all Vietnamese glyphs render correctly.

- New tool `tools/import_v04_glyphs_into_source_build.py` with `tools/tests/test_import_v04_glyphs_into_source_build.py` has strict clean/v0.4 SHA-256 gates, exact reference font symbol offsets, target build symbol mapping, full 32-KiB pre-change byte equality of each glyph array against clean ROM, and a no-overlap/no-other-write guarantee. The user must locally supply the private clean and donor ROMs plus source-built GBA and matching .sym; donor ROMs must **never** be uploaded to this public repo.
- **Local read-only/prototype verification passed using clean as a simulated source-built ROM:** the five modified blocks exactly equal v0.4 after applying the delta; **5,917 bytes changed, all within approved fonts**, zero pointer edits. The tool must still be tested against the **actual** source-built ROM after it becomes locally available, plus emulator visual glyph/page QA.

## Engineering status and next action

1. Verify corrected combined map+UI source-build CI. Record exactly how many UI text rows were staged; initial CI zero-row failure was fixed, but do not guess the final count.
2. Bring the source-built ROM bytes and its exact source symbol map into private runtime; run the font importer with strict source equality and post-write QA. Merely finding `0xFF` space is not permitted.
3. Develop explicit dynamic placeholder rules and page-level dialogue layout; blocked `{PLAYER}` and 215 third-line candidates need separate reviews. Do not bulk-repoint.
4. The latest prior manual binary guarded+UI43+shared13 output SHA `187993098e11317873043a70751cd9009fc1556a8a46a550f017be233a2ec05e` was not mounted in this session. Do NOT replace that with an older v5-2084 ROM and claim a successor.
5. Preserve title credit `Việt hóa bởi Votri Valley` and verified center alignment. No source-first ROM release before font rendering and gameplay QA.

Original v0.4 always stays rollback. No user download or screenshot requests needed yet.


## Follow-up build and font CI gates

The `checkpoints/v04-inferred-vietnamese-codebook.json` added two inferred, independently supported glyph values: `ẹ=0x5A` (six distinct source-label observations) and `ẻ=0x08` (three distinct labels). They remain **candidate** assignments until emulator visual verification.

An initial combined map + C UI CI run `37884118717` **FAILED** because C source messages implicitly end with FF while the map-text encoder expected literal `$`. This was fixed in `tools/stage_source_ui_translations.py` by appending only the internal terminator for compilation. A later unit test had a doubled `\\n` in the test fixture; corrected. **Do not report the combined source build as passed until a later run actually succeeds.**

New `tools/audit_source_font_layout.py` with its regression tests protects the five source-compiled Latin glyph block SHA-256 values against the verified clean Arena font content. The workflow now exports `SOURCE_LEVEL_FONT.sym` and `SOURCE_LEVEL_FONT_AUDIT.json` **without publishing a ROM**. The compiled source ROM must pass this gate before any private v0.4 font import is allowed. This workflow change is commit `b6400f3`; follow its CI run for real status. Matching stock font hashes alone still does not mean the Vietnamese donor font has been imported into the compiled ROM or visually verified.

**No full user-playable GBA released in this follow-up.**


## VERIFIED combined map + C UI compiler milestone

[GitHub Actions run 37884608217](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37884608217) **COMPLETED SUCCESS** after fixing the C implicit terminator and regression fixture. The actual source build artifact `SOURCE_LEVEL_UI_PILOT.json` independently confirms **30 C UI labels** staged (3 auto-wrapped) alongside **200 map/story labels** (85 auto-wrapped) in the other source report, totaling **230 source-built Vietnamese strings** in that *one isolated compiler test ROM*. Source-built ROM SHA-256: `950f15995a78783d58ac405cf4cc72199ec725d2b2e7c80f3b6acd2759befffe` (the ROM itself is intentionally not published to GitHub). Examples: `gText_WirelessNotConnected`, `gText_SaveFileErased`, various Pokédex sort descriptions, `gText_NoRoomForItems`, `gText_CantStoreImportantItems`.

**These 230 are not yet incorporated into the user's original v0.4 binary**, and are not verified to render Vietnamese correctly under source-built stock fonts. The newer CI addition to check font block hashes is separate and needs its own final verdict. The codebook entry updates for `ẹ` and `ẻ` were made later, so this specific 230-row artifact reflects the earlier codebook snapshot.
