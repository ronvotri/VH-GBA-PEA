# Pokémon Emerald Arena — Ability / Match Call source integration checkpoint

**Date:** 2026-10-12. Repo: `ronvotri/VH-GBA-PEA`, branch `main`.

## Final CI result: **7,091 source labels verified**

[Actions **#38159804341**](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38159804341) **FULL PASS**. The new source C stage compiled **137 additional Vietnamese strings**: **39 Ability** descriptions in `src/data/text/abilities.h`, and **98 Match Call** profile fragments in `src/data/text/match_call_messages.h`. **All 6,954 prior integrated source labels** were also re-attested against the newly linked ROM; all new 137 source C payloads matched independently encoded Vietnamese bytes at their unique ELF/GBA addresses.

- New total: **7,091** verified source-compiled Vietnamese labels; **not** a proven percentage of total playable user-interface coverage.
- Latest source ROM SHA256: `50c51fdcb73a9361fbf771fb9556adbf4de1569ebe9979036e34ee7171febd4d`; contiguous ROM tail space: **1,816,092 bytes**.
- New source stage refused **230** candidate items because Vietnamese text would exceed the original English line's static-cell budget; additional missing glyphs included uppercase Vietnamese such as `Ư`, `Ọ`, `Ệ`, `Ồ`. These were **not** rewritten or counted as compiled.
- All five stock English pixel-font banks still unchanged. **Approved v0.4 Vietnamese art not imported, no emulator visual QA, not release-ready.**
- The earlier estimated ~139 compatible candidates was a preliminary screen; the independently verified count is **137**.

## Most recently independently verified source ROM

- [GitHub Actions **#38157439511**](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38157439511) FULL PASS: **6,954** independent source-owned Vietnamese strings in the experimental rebuilt GBA ROM, including 306 newly proven Pokédex descriptions.
- The **17,512/17,512 translated manifest** describes authored Vietnamese entries, *not* how many playable surfaces have been visually validated.
- Current source-built ROM still uses **5 stock English font raster banks**. The user's previously approved **v0.4** Vietnamese font donor (SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`) has **not been imported**. Never redraw, synthesize, or silently substitute it. No final gameplay/emulator QA or playable distribution.

## Newly developed source-only trial

This round targets the already-translated `src/data/text/abilities.h` and `src/data/text/match_call_messages.h` declarations. They are **single-line C-owned UI descriptions**, distinct from the already compiled Pokédex. These two source owners had not been part of previous source integration stages.

- `tools/stage_ability_matchcall_source_text.py` handles precisely `s...Description` and `gText_MatchCall...` symbols from the two expected files, with **exact original English initializer identity**. Declines duplicates, dynamic tokens, escaped controls, unsupported Unicode and text that exceeds either the English source's static display-cell length or a conservative 32-cell UI line.
- The tool **never rewrites authored words or capitalization**, strips accents or changes punctuation. It substitutes only byte arrays for exactly sourced C symbols and leaves every unrelated symbol unchanged.
- `tools/tests/test_stage_ability_matchcall_source_text.py` covers accepted original symbols, exact decoded words, unknown glyphs, long text, token/whitespace errors, unexpected sources, multiple matching C symbols and original-English drift.
- `tools/verify_ability_matchcall_source_text.py` re-attests **all 6,954** previously accepted strings against the newly linked ELF/GBA and independently recomputes every new accepted ability / Match Call string's exact C payload and ELF symbol-to-ROM address. Five stock font banks, at least 1MiB contiguous ROM headroom, no raw pointer writes and no v0.4 donor import are required.
- `.github/workflows/arena-map.yml` creates a separate source checkout `ability-matchcall-one-line-source-trial` AFTER the verified 6,954 Pokédex stage, builds it, audits fonts/headroom and produces `SOURCE_ABILITY_MATCHCALL_ONE_LINE_ATTESTATION.json`.
- Authored categories: **77 Ability descriptions + 308 Match Call profile fragments = 385 translated rows**. A read-only preliminary codebook/width filter suggested **~139** may satisfy the strict criteria; this is **not** the new verified label count.

## CI status

The latest scheduled runner is [**#38159804341**](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38159804341), **in progress at this checkpoint**. The new unit tests have **PASS**. An earlier runner failed because the test-only fake codebook omitted sample accented letters `à`, `ĩ`, `đ`, `ậ`; fixed without modifying any shipping font or translated string.

**Count gate:** keep **6,954** until Actions FULL PASS and the new attestation reports an actual positive `new_ability_matchcall_source_labels`. Do not count skipped rows. If CI fails, inspect the named job and fix tests/verification rather than weakening the source-control gates.

## Still required for a real release

Use the *original approved* v0.4 font artwork and verify byte-to-glyph compatibility with source text before merging. Test title credit **“Việt hóa bởi Votri Valley”**, title/intro, NPC conversation, Ability screens, Match Call profiles, Pokédex, battle, save/load and Arena-specific menus in the emulator. Do not publish commercial GBA ROM content to GitHub.
