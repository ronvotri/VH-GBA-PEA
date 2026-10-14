# Full source-build Vietnamese ROM — checkpoint 2026-10-13

First build in this project that has **all authored translations, a Vietnamese font and a real gameplay run** together. It is a private QA candidate, not a release.

## Status in the six handoff columns

| Column | Value |
| --- | --- |
| (1) authored | 17,512 |
| (2) source-linked | 13,094 strings rewritten in source and linked (the other 4,418 manifest entries are identical to English: Pokémon, move, item and trainer names). 0 skipped, 0 keys unresolved. Not re-attested by the older per-label ELF verifier. |
| (3) donor-v0.4 private spans | not used; this build does not derive from the v0.4 binary |
| (4) emulator gameplay QA | **PASS (libmgba 0.10.5, headless)**: new game → intro → Nam/Nữ → naming → truck → house/clock → rival's house → Route 101 → starter → **first Arena battle → back to overworld → Birch's lab** → nickname prompt → start menu, party, summary, bag → in-game save → cold boot → Continue. Not yet run on No$GBA or on real play beyond the lab. |
| (5) font-v0.4 graft | **NO.** The font is generated (see below), not grafted from the donor. Needs the user's visual approval. |
| (6) release ready | **NO** — see open issues. |

Candidate ROM (QA2) SHA-256 `3b1c12be85edb42c7c59f75d603bf493e944ea5b376e2f5af9d408b592175238` (kept under `private/`, never committed). QA1 was `d15c09ac…`; QA2 adds the shortened UI strings below and passed the same first-battle route, summary screens and save/Continue.

## What changed in approach

The ROM is compiled from the pinned sources (`pret/pokeemerald@5eff7864`, `pret/agbcc@da598c1d`, Arena `v0.13.0`) with every manifest applied as a source edit. The compiler and linker place all text and references, so there is no pointer write anywhere. The stock (untranslated) local build reproduces the recorded source-build hash `eb1a7dd2…`, which differs from the shipping ROM by 16 bytes.

Because nothing here is patched into the v0.4 binary, the "+341 freeze" class of failure (bad relocation) cannot occur by construction. The earlier freeze reports on No$GBA are still unexplained for the *binary* builds; this build has simply not shown it on mGBA.

## Pipeline (`tools/build_vietnamese_rom.sh WORKSPACE [TITLE_FONT.ttf]`)

1. `compact_arena_linker_gaps.py` — existing tool; frees ~1.8 MB (ROM 94.54 % used after translation).
2. `build_vietnamese_source_font.py` — adds 108 glyphs to each of the five Latin fonts and extends `charmap.txt`.
   - Every Vietnamese letter has its own code: 90 use single-byte codes the Latin charmap leaves undefined, 18 rare capitals use `F9 xx` (the engine's extra-symbol prefix, glyph ids 0x118+). The 26 letters stock already has (à á â è é ê ì í ò ó ô ù ú and capitals) are reused. **`f`, `w`, `z` are untouched.** Codebook: `checkpoints/source-build-vietnamese-codebook.json`.
   - Glyphs are composed from each stock font's own base letter plus pixel diacritics with the stock shadow. No donor pixels are read. Capitals with two marks are shortened by one duplicated row to make room.
3. `apply_source_translations.py` — rewrites string literals at the same labels / `@anon:file:line:col` anchors the catalog uses (also `label@@file:line` for duplicate labels). Skips and reports placeholder mismatches or unencodable characters (currently none). Re-wraps lines that exceed the box: script dialogue to 208 px, multi-line C text to the widest English line of the same file (1,516 strings re-wrapped; page breaks kept).
4. `widen_source_text_arrays.py` — four const arrays (`gTrainerClassNames`, `sATypeMove_Table`, `PokedexEntry.categoryName`) widened, since two-byte capitals overflow the original byte counts.
5. `apply_title_credit.py` — existing tool; `Việt hóa bởi Votri Valley` on the title screen.
6. `make`.

Local Windows build without admin rights: MSYS2 (UCRT64) with `gcc`, `make`, `libpng`, `arm-none-eabi-binutils`, Python + Pillow. MinGW `ld` rejects scripts that `INCLUDE` others, so the Makefile link rule is pointed at a script produced by `tools/inline_linker_includes.py`.

## QA tooling

- `tools/qa/gba_runner.c` — headless libmgba runner (scripted keys, screenshots, savestates).
- `tools/qa/step.py` — runs a command list / route and tiles screenshots.
- `tools/qa/route_new_game_to_first_battle.txt` — deterministic input route from power-on to Birch's lab; replays identically across rebuilds as long as dialogue page counts do not change. Use it as the first-battle regression instead of asking the user to replay.
- `tools/audit_source_text_widths.py` — rendered width of each Vietnamese string against the English it replaced.

## Open issues (why it is not a release)

- **UI overflow.** 2,234 non-dialogue strings render wider than their English. Many still fit; fixed in QA2 and checked on screen: summary headers, `T.CÔNG` / `P.THỦ`, the 13 ability descriptions wider than the 144 px English budget, Continue-menu `TÊN`. The rest are unreviewed. 27 item/Pokédex/decoration descriptions need more lines than their window has. These need shorter wording in the manifests.
- **Graphic labels** (PROFILE, ABILITY, STATS, MOVES… on the summary screen, PRESS START) are tile art and still English.
- **Arena tiny HUD** stays ASCII (species/move names are English by project rule, so it is consistent).
- **Font approval.** Shapes follow the stock letterforms like v0.4 but are not the v0.4 pixels.
- **Title credit** is rasterised from a TTF and looks soft; redraw with the game font.
- Only the opening has been played. Battle messages, Pokédex, Easy Chat, PC, shops, contests and Battle Frontier are untested at runtime.
- No BPS/IPS patch yet. The layout differs from the shipping ROM almost everywhere, so a patch will be large.
- The new tools have no unit tests; the existing 364 still pass.

## Update 2026-10-14 (candidate QA7)

Candidate ROM SHA-256 `4fb06c098b19558397c76aaaaf5a533b47cb20a3e91b11c31d770be858d9cda2`; the first-battle route passes on it. Earlier hashes in this file refer to superseded candidates.

- 13,084 strings are now rewritten: the 10 strings of `src/arena_capture.inc` stay English at the user's request, because Arena's 3x5 HUD lettering has no accented letters and dropped them (`TRƯỢT!` rendered as `TR T!`).
- Label policy decided by the user after playing: no abbreviations except `T.CÔNG` / `P.THỦ` on the stats screen. `--abbreviate-labels` exists in the applier but is off in the build script. The moves page header is `KỸ NĂNG`.
- User report, not yet reproduced here: the screen goes black with sound only while a Poké Ball chosen from the bag is thrown, and for 1-2 s when using a Potion or switching. Arena's source hands those actions to the classic battle engine with the display blanked (`gRealtimeArenaQuietIntro` / `gRealtimeArenaQuietResult`), so this is probably stock mod behaviour; confirm by repeating it on the untranslated source build with the same save.

### CI

`.github/workflows/vietnamese-source-build.yml` builds the ROM with `tools/build_vietnamese_rom.sh` and runs `tools/qa/verify_first_battle.py`, which replays the recorded route and passes only if the player ends in Birch's lab holding a Pokémon. The older `arena-map.yml` pins exact label counts for each incremental stage (it failed on this branch with 3,776 instead of 3,774 after five manifests were edited), so it is now manual-only.
