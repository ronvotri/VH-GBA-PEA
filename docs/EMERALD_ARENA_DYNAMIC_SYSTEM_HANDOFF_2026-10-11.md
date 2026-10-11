# Pokémon Emerald Arena — dynamic system text source integration (11 October 2026)

## Last confirmed build

GitHub Actions [#38143908686](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38143908686) **FULL PASS** on 2026-10-11. The new page-locked literal-LF system pilot admitted **zero** new labels (native English page controls did not match the candidates) and fully revalidated all **1,165 prior system** and **2,867 map/story** ELF/GBA source labels. Consequently the total **remains exactly 5,974** distinct source-compiled Vietnamese strings. This zero-count result is not a regression: no unsupported page semantics were silently rewritten. SHA256 of experimental stock-font ROM is still `fc8d275a141ce6fff5e09564f0426f49f3b1bf78e6ed78a7fd128425ab4d8b47`.

Manifest translations remain **17,512/17,512**; this number is not the number installed in ROM.

## New attempt: dynamic system strings, no worse runtime text footprint

New experimental isolated stage `tools/stage_safe_system_dynamic_variables.py` and `tools/tests/test_stage_safe_system_dynamic_variables.py` tackle translated source-owned `data/text/*.inc` strings containing runtime variables while **refusing any increased static text footprint per native line**.

- Verify the original English assembly symbol and source text exactly before replacing with byte-encoded Vietnamese.
- Only `PLAYER=FD 01`, `STR_VAR_1=FD 02`, `STR_VAR_2=FD 03`, `STR_VAR_3=FD 04`, `KUN=FD 05` and `RIVAL=FD 06`, all cross-checked with that exact pokeemerald source workspace's `charmap.txt`. No inferred runtime placeholders.
- Within each unchanged GBA `\\n / \\l / \\p` segment, demand the **same variable names in the same order** and **Vietnamese static glyph-cell count <= original English glyph-cell count**. Never silently remove or reorder words, rename variables, move a variable between pages, normalize a different control code or guess a pointer.
- Skip strings containing unsupported diacritics, dynamic tokens, newlines, oversized static segments or source differences.
- Exclude **all nine prior system integration reports** (1,165 source labels) and never mutate source-font pixel banks or raw GBA pointers.

`tools/verify_safe_system_dynamic_variables.py` independently verifies that every accepted source has a real unique compiler/ELF owner, its exact encoded payload is present at the actual GBA ROM location and all earlier 5,974 source-owned labels still match there. It also verifies unchanged stock-font banks, linker headroom and native variables.

Workflow `.github/workflows/arena-map.yml` compiles an isolated `safe-dynamic-system-additive-source-trial` and writes `SOURCE_SAFE_DYNAMIC_SYSTEM_ADDITIVE_ATTESTATION.json`. Run [#38144514920](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38144514920) **was pending** when authored. **Do not increase 5,974 before FULL PASS and a positive, independently verified new label count**. Zero additions must remain zero.

## Font and shipment lock

The user's prior approved Vietnamese font **v0.4** (SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`) is the visual reference and rollback; do not redraw/synthesize it. This compiler test uses unmodified **English stock font pixel art**, and source text may use a separate glyph codebook requiring eventual vetted donor-compatible migration. Never claim the accepted font has already been grafted by these source CI runs.

Visible credit remains **“Việt hóa bởi Votri Valley”**. Before public v1.0, actual private ROM must pass title → intro → story/maps → battle → return → save/load → Arena-specific HUD/menu and glyph QA; no copyrighted ROM is committed to GitHub.
