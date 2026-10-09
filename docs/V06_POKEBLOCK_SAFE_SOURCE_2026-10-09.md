# v0.6 Pokémon Emerald Arena — native Pokéblock font safety (2026-10-09)

**Status:** new v0.6 source-codebook and private font-raster experiment. **Not a release-ready or emulator-verified Vietnamese GBA.**

## Why v0.6 is necessary

The old v0.5 inferred byte plan still assigned Vietnamese `đ` to `0x56` and `ì` to `0x59`. The original pinned Hoenn `charmap.txt` reserves `PKMN = 53 54`, `POKEBLOCK = 55 56 57 58 59`, and, importantly, the ASCII `=` character **already uses `0x35`**. An earlier handoff incorrectly proposed using `0x35` for `ì`. This is explicitly invalidated and corrected here.

The root cause of the false free-slot detection was `tools/plan_collision_free_vietnamese_font.py` using `line.split("=",1)` on the charmap line `'=' = 35`, which split at the first **quoted literal equals sign** instead of the assignment operator. We changed it to `rsplit("=",1)` with a permanent regression test.

The **actual safe planned Latin mapping** is:

| Vietnamese glyph | Old v0.5 byte | New v0.6 byte | Native glyph preserved |
| --- | --- | --- | --- |
| `ấ` | `30` | `30` | ASCII f at DA |
| `ằ` | `31` | `31` | ASCII w at EB |
| `ắ` | `32` | `32` | ASCII z at EE |
| `đ` | `56` | **`33`** | Pokéblock segment at 56 |
| `ì` | `59` | **`37`** | Pokéblock segment at 59 |

Slots `34` (`LV`), `35` (`=`) and `36` (`;`) are intentionally protected, as are **all `53..59`** native PKMN/Pokéblock segments. v0.6 keeps the same **137 supported unique Unicode characters**, and still quarantines unsupported uppercase `Ừ`.

## Source code, tests and compiler gate

- `tools/plan_v06_pokeblock_safe_font.py` validates the original English-mode charmap, special five-byte Pokéblock sequence, ASCII d/i, glyph-occupancy conflicts, and all previous v0.5 f/w/z repairs.
- Durable new byte plan: `checkpoints/v06-pokeblock-safe-codebook.json`. It may **never** be used with unmodified v0.4 donor graphics.
- `tools/graft_v06_pokeblock_safe_fonts.py` is the private, SHA-locked experimental importer. It relocates the five accent glyphs, restores the 13 protected Latin glyph positions in each font (ASCII f/w/z, PKMN+Pokéblock 53..59, LV/= /; 34..36), and forbids writes outside font and width ranges. Original target exact SHA256 and original/donor ROM SHA hashes are required.
- Regression suites `tools/tests/test_plan_v06_pokeblock_safe_font.py`, `test_graft_v06_pokeblock_safe_fonts.py`, and earlier v0.5 scanner tests cover slot-35 regression, no duplicate codepoints, real/native glyph ownership and no non-font writes.
- `tools/stage_pokeblock_item_descriptions.py` separately handles the **16** previously skipped berry/Pokéblock Case texts by keeping exactly one `{POKEBLOCK}` native source token, encoding it as the **exact five bytes `55 56 57 58 59`**, matching the source's three-line description box. This stage NEVER guesses or deletes runtime placeholders.
- `tools/verify_compiled_source_strings.py` and tests now independently attest exact native token bytes, three lines, unique C source labels and terminal `FF` for this eighth integration group.
- CI now generates/checks v0.6 from pinned v0.5, compiles static map/UI/battle/description groups using v0.6 bytes, then stages the 16 special Pokéblock descriptions; compiler/integrity report must finish PASS before those 16 are counted as installed. **Run [37960836736](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37960836736) was pending at initial checkpoint.**

## Real font-only donor test (private; verified)

Inputs were actual local 32MiB ROMs locked by SHA-256:

- Clean Arena 0.13.0 SHA256 `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`
- v0.4 Vietnamese donor SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`

Using original five shipping font offsets and original Latin GBA 16×16 glyph packing, a **private clean-ROM font-only diagnostic**, **not a v0.6 source ROM**, verified:

- **25** nonblank relocated/synthesized accent glyph pictures (5 characters × 5 fonts).
- Exactly **9** raster pictures require Narrow-derived synthetic small fonts: 5 in SmallNarrow, 4 in Small (all except `đ`).
- **6,053 changed bytes**, **all** confined to five Latin font graphic blocks and their width tables.
- Every original ASCII `f/w/z` glyph, PKMN bytes `53–54`, Pokéblock bytes `55–59`, plus `LV` `34`, `=` `35` and `;` `36`, preserved bit-for-bit from the clean ROM in **all five styles**.
- The **clean-ROM font-only diagnostic** SHA256 is `a06de5b32aa569dc83439b61dd86c61f546946a6f82008c407fe1086d5569006`. No private ROM or glyph image binaries have been pushed to public GitHub. Only source tooling and textual test facts are committed.

**Important nuance:** v0.4 also changed the unassigned target slots `0x33` and `0x37` in Normal and Narrow font graphics. They are *unassigned in the pinned Latin charmap*, not empty raster art. The v0.6 graft explicitly overwrites those slots with the correct new accented glyph. No inference is made that arbitrary other raw engine bytes are safe.

## Current limits / next work

The last **confirmed** full source-build checkpoint before v0.6 is **2,077** translated source labels (1,000 map, 41 UI, 134 dynamic names, 196 battle script, 59 C battle, all 354 move descriptions and 293 static item descriptions), confirmed in [Actions 37953125938](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37953125938). **Do not claim 2,093 until latest v0.6 CI confirms 16 additional distinct native-token labels.**

Even with full source-build CI PASS, the new GBA will still use **stock font raster**, not the private v0.6 remapped Vietnamese font. The user-facing release still requires reproducing the exact source-build ROM locally, applying the SHA+symbol-locked private graft, visual QA of the 9 synthetic fonts, and emulator tests of Pokéblock Case, berries, text, battle, title credit **“Việt hóa bởi Votri Valley”**, and save/load. The original playable v0.4 rollback remains untouched.

Do not upload any commercial ROM or donor font graphics to the public repository.
