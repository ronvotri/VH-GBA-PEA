# Pokémon Emerald Arena — 6,361 Vietnamese source labels verified (2026-10-11)

## Verified final checkpoint for this turn

- **GitHub Actions [#38146099792](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38146099792) FULL PASS** (all tests, compile, byte-verified source integration, original font banks and 1MiB ROM headroom).
- Source labels progressed **5,974 → 6,005 → 6,090 → 6,361** this turn: exactly **+387** newly source-compiled labels. Earlier 5,967 is an older checkpoint, not this turn's starting baseline.
- Latest source stage **+271 STR_VAR/PLAYER/RIVAL/KUN dialogues** across **10 source files**. Every new payload was independently checked at the ELF symbol address and matched the GBA ROM.
- Original baseline **1,281 system** and **2,867 map/story** source labels were revalidated against the new final ROM; 271 new system source labels added, so currently at least **1,552 unique system** and **2,867 unique map/story** source labels have explicit byte-verification proofs.
- Full source-built experimental ROM SHA256: `b819066376a48100d80b05c3cbdcc11e5c4bd557399b8e915c98fa5039ab4f03`. Contiguous tail ROM headroom: **1,810,020 bytes**.
- The 17,512/17,512 user-facing translation manifest is *authored*, not fully integrated. The newly built ROM **still uses the unchanged five English stock pixel font banks** and has not passed emulator or gameplay QA. This is **NOT a user-facing release**.

## New verified workflow logic

`tools/stage_safe_system_dynamic_variables.py`: +31 original-line footprint-safe runtime variables, verify `FD 01` / `FD 02..04` / `FD 05` / `FD 06` and native English controls.

`tools/stage_page_bounded_system_dynamic.py`: +85 reflowed static text with bounded PLAYER/RIVAL=7 and KUN=0, page-local word identity proof and original source owner proof. Unknown STR_VAR lengths are excluded.

`tools/stage_system_dynamic_static_budget_reflow.py`: +271 longer string substitutions involving `STR_VAR`, **without guessing the STR_VAR-expanded width**. Each new variable-bearing native line has static text length no greater than the original English line's static cells, and no more than 26 static cells; surrounding longer words are moved to native scroll lines while every original Vietnamese word remains within its original page, each original line's variable list remains in the original sequence, and the `\\p` page count remains unchanged. Per-page maximum 12 scroll lines. No font pixel or ROM pointer writing.

`tools/verify_system_dynamic_static_budget_reflow.py` does independent source-to-GBA compiled-bytes attestation, and the workflow uses a separate source workspace. All these experimental stages are **source-level only** and preserve user-visible words; renderer QA is still pending.

## Remaining safely rejected cases (examples from final stage)

The latest STR_VAR source stage refused candidate strings for reasons such as missing glyphs in the **experimental v0.6 source codebook**, including `Ồ` (88), `õ` (24), `Ừ` (18), `Ô` (17), `ỳ` (13), `Ố` (13); also unsupported source control sequences (73), unknown variable kinds (26), malformed native text (21), unprovable original static-cell budget (13), altered source scroll signature (11), and moved dynamic variables within native lines (11).

These are **counts of rejection reasons in this stage**, not a count of untranslated source labels; each candidate is counted by its first blocking reason. Do **not** fix by silently deleting diacritics, replacing authored words, guessing STR_VAR widths or adding artificial/synthetic font bitmaps.

## Hard requirement: approved font v0.4 is not replaced

The user approved the existing Vietnamese font **v0.4** (donor ROM SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`). This image/ROM is private and cannot be committed to the repository. The new source-compiled builds use English stock font banks and a separate collision-safe v0.6 codebook; the codebook **requires vetted donor-art/glyph remapping**. Never draw new fonts or claim that the current source compiler automatically merged v0.4 art.

Next priority: investigate glyph/codebook-compatible import of *the original approved art* and only then real emulator visual/gameplay smoke tests. Preserve original title and `Việt hóa bởi Votri Valley` text; verify title → intro → map → battle → postbattle → save/load → Arena menus before promising a public 1.0. Do not distribute copyrighted ROM binaries in the repository.
