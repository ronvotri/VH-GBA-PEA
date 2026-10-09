# 1.430 verified Vietnamese source labels — static battle C checkpoint (2026-10-09)

**Status:** SOURCE-COMPILED, independently attested, **NOT** a releasable GBA ROM. No Vietnamese donor font was grafted into this source build, and no gameplay/emulator rendering test has been run. The user does not need to download technical ZIPs or repeatedly test partial ROMs.

## Exact full CI result

**[GitHub Actions run #37914622483](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37914622483) — SUCCESS**, source commit `c564a97c6a33f8427c8dd1063d13236bdf90eccc`.

Downloaded CI artifact `arena-0.13.0-symbol-map`, whose source compilation SHA file reports **`3abc84cd46c2ea283eedd1218c091d5e97b9c724bb03854a35e809f6450230cd`** for the built experimental (stock-font) 32 MiB GBA. Reports verify:

| Source group | Installed labels | Auto-wrapped |
| --- | ---: | ---: |
| Map/story `data/maps/` | 1,000 | 543 |
| C general UI `src/strings.c` | 41 | 4 |
| Dynamic-name map/story `{PLAYER}/{RIVAL}` | 134 | 102 |
| Battle `.inc` scripts `data/text/` | 196 | 96 |
| **New static battle C** `src/battle_message.c` | **59** | **4** |
| **Total** | **1,430** | **749** |

`SOURCE_TEXT_INDEPENDENT_QA.json` reports **1,430 unique source labels, 0 duplicates, 1,430 exact FF terminators**, all five source categories attested. No game ROM was uploaded into the public GitHub artifact; it contains only reports, symbols and hashes.

## What was actually added this session

- New `tools/stage_source_battle_c_messages.py` preserves the exact `sText_*` or `gText_*` named `src/battle_message.c` C-array references, matches authored English literally and writes byte-encoded Vietnamese initializer under the same symbol, letting GCC and the linker manage all source-owner pointers. It does **not** globally repoint binary ROM addresses.
- C battle staged examples (present in final build artifact): `sText_UseNextPkmn`, `sText_CantEscape2`, `sText_CriticalHit`, `sText_SuperEffective`, `sText_SpikesScattered`, weather/terrain and capture/status messages.
- Restrictive eligibility: skip dynamic `{B_*}`, `{WAIT_SE}` and other variable/engine tokens, unknown Vietnamese glyphs, any concat fragment with leading/trailing spaces, short battle fragments, page-control signature drift, unsafe three-line cases and any C symbol that does not match the pinned upstream source exactly.
- New `tools/tests/test_stage_source_battle_c_messages.py` regression tests cover exact C source ownership, changed/duplicate source detection, early terminators, dynamic template exclusions and required page controls.
- `tools/verify_compiled_source_strings.py` now verifies the new `battle-c` category independently, supporting `static const u8` arrays and rejecting ghost labels, duplicate symbol names and data/code drift; new regression tests added.
- `.github/workflows/arena-map.yml` stages up to 80 candidate static battle C entries, and now includes the separate source byte-proof audit before the GBA compiler runs. The actual qualifying total was **59**, not the configured 80.

## What still remains and why

This build is only **1,430 installed** out of **17,512 source-manifest translation entries**. CI's detailed candidate review shows:

- Within `src/battle_message.c`, **363** translated source candidates contain battle engine control tokens/dynamic buffers and cannot use the static message stage. A further **71** are fragments or short concatenation strings and require different context-safe handling; **15** were blocked by missing glyphs or complex line/page formatting. **Do not force the missing items into byte arrays with guessed values.**
- Map/story/source UI backlog still contains many character glyphs absent from the v0.5 inferred codebook, including uppercase accented letters, and hundreds of entries with third-line/complex page controls. Do not mask errors by stripping accents or changing page counts.
- The v0.5 source byte mapping is **collision-safe in the planned Latin codebook**, but the **experimental compiled ROM's fonts are still stock English**. The private SHA-locked donor glyph transplant and actual rendering verification must be applied to the exact latest build SHA **before user testing/release**.
- Original v0.4 and the guarded experimental pointer-repair trail remain intact as rollback. Do not replace them with an unverified source-build ROM.
- Must still do real runtime QA: boot/title credit “Việt hóa bởi Votri Valley”, intro truck/Mom, Pokédex, item descriptions, battle/post-battle, save/load, text width, scrolling, all five font styles.

## Sensible next work order

1. Extend source-first catalog integration to `src/data/text/move_descriptions.h` (355 entries; many static 2-line C description arrays) and `src/data/text/item_descriptions.h` (310 entries, with 3-line layout safeguards); check source ownership, original English, control signatures and page limits.
2. Create explicit token-width/reference logic for battle templates with `{B_*}` / dynamic buffers, separate from static C tool. Evaluate max displayed lengths and battle-specific UI boxes. Keep uncertain cases blocked.
3. Advance the v0.5 font graft to a SHA-locked private source-built ROM; check correct fresh font offsets via matching `.sym`, preserve English `f/w/z` and 15 accent glyphs, validate source text codebook consistency, and verify emulator rendering before a user-facing ROM.
4. Update `PROGRESS.md` and `CONTINUE_WITH_MODEL.md` with actual CI counts and new exact SHA. Never call 17,512 manifest translations equal to game binary integration.
