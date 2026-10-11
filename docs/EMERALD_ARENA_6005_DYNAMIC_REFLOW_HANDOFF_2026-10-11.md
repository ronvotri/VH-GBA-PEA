# Pokémon Emerald Arena — 6,005 compiled source labels; safe name reflow gate (2026-10-11)

## Confirmed source integration

[GitHub Actions #38144514920](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38144514920) **FULL PASS**: new **31 system texts** with verified `PLAYER`, `RIVAL`, `KUN` or `STR_VAR_1..3` engine variable bytes, bringing the source-compiled proof from **5,974 to 6,005 unique labels**. Source changed across **9 source files**. The compiler-linked source ROM hash is `39ddc62cb5e9df1db02011df04bf1e054942bae03a0c6b4c72b2b1657612c09a`, with **1,807,820 bytes** contiguous tail free.

The CI scanner reported **523 translated candidates rejected for longer static line text** and **176 rejected for a translated static segment beyond its conservative width bound**, plus variable/glyph/control exclusions. Those are **skips, not integrated strings**, and cannot be counted as done in ROM. The broader translation manifest **17,512/17,512** remains authored and translated, not all integrated.

This ROM is still a source-compiled **stock English pixel-font trial**, not the user's accepted Vietnamese font v0.4 and not gameplay/emulator certified.

## Next isolated source stage

The following changes were committed to `main`:

- `tools/stage_page_bounded_system_dynamic.py`: uses only **verified runtime display widths** `PLAYER=7`, `RIVAL=7`, `KUN=0`. The Birch engine's actual KUN empty-value placeholders are checked for both genders; unknown runtime variable lengths such as `STR_VAR_1..3` are excluded rather than guessed.
- Dynamically rewraps translated text to **26 display cells per line** using native `\\n` and `\\l` scroll controls, **without changing the original `\\p` page boundaries**, each page's original Vietnamese word order, or variable order/identity. A maximum of 12 lines per page prevents uncontrolled scrolling. Unrecognized escapes, glyphs, malformed control syntax, source owner mismatches and long unbreakable words are rejected.
- New unit tests `tools/tests/test_stage_page_bounded_system_dynamic.py` cover long original-authored Vietnamese lines, pagination, mixed variables, wrong engine state, original source drift, font-codebook exclusions and unbreakable words.
- `tools/verify_page_bounded_system_dynamic.py`: re-attests earlier **1,196 source-owned system labels and 2,867 source-owned map labels**, then independently recomputes every new payload and checks bytes at its real ELF linker symbol offset in the generated GBA, matching source and report.
- `.github/workflows/arena-map.yml`: separate `page-bounded-system-dynamic-source-trial` branch of the source build, with five stock-font glyph-bank audit and >=1MiB headroom checks.

**Current CI run:** [#38145240337](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38145240337). At checkpoint creation this run **was still compiling**; unit tests already passed. The authoritative new count, if any, is the artifact `SOURCE_PAGE_BOUNDED_SYSTEM_DYNAMIC_ATTESTATION.json` field `new_bounded_name_system_labels`; do not claim a new source-count milestone without a FULL PASS.

## User-approved visual font lock

**Do not change, redraw, synthesize or replace the already approved v0.4 Vietnamese font**, SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`. Its donor bytes are not hosted in this repository, so the latest compiled source trials cannot be declared a visually working release. The safe v0.6 glyph codebook is a separate experimental layout and must never be applied blindly to the v0.4 graphics.

Preserve `Việt hóa bởi Votri Valley` title credit, protect original title/logo, and test intro → map → battle → postbattle → save/load → Arena UI with a private verified font+text build before any final distribution. Never commit copyrighted GBA ROMs.
