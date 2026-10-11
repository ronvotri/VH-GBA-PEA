# Pokémon Emerald Arena — zero-page system-text integration (11/10/2026)

## State when this source work was committed

- Last independently **FULL PASS** source milestone: **5,967 unique source-compiled labels** in Actions [#38137406551](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38137406551).
- New additive system-text stage added on \`main\` in commit \`b43005a\`. Its first CI run is [#38139355341](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38139355341). **Do not increase the 5,967 count unless this run finishes FULL PASS and its attestation confirms an exact value.**
- This experiment is **not** a downloadable Vietnamese ROM. Source-built fonts are still stock English glyph art, not the user's visually accepted v0.4 Vietnamese font. No source-level addition can replace actual emulator gameplay/visual validation.

## Work performed

1. New \`tools/stage_static_zero_page_system_text.py\` is restricted to authenticated \`data/text/*.inc\` assembly owners from the user-facing source plan; it excludes **all six earlier system-text batches** (including the 21 recently staged paginated strings).
2. New staging admits *only* static system text without \`\\p\` page breaks or runtime placeholders. The original English \`.string\` bytes and global symbol must be exact. Vietnamese words may be reflowed using standard \`\\n\`/\`\\l\` within their single original page, but words are not replaced, reordered, moved across pages or silently stripped of diacritics. Unknown controls, actual literal newlines, absent codebook glyphs and ambiguous owners are not added.
3. Source staging never writes raw ROM offsets or guesses pointer locations. It does not edit any of the five font banks.
4. New unit tests cover correct source owner, no-page invariants, unknown/missing-glyph text, duplicate owners and bad English source.
5. Workflow \`.github/workflows/arena-map.yml\` builds the additive source in a **separate workspace** after the verified 5,967 milestone and generates explicit GBA/ELF symbol, font and ROM headroom audits.
6. \`tools/verify_zero_page_system_additive.py\` rechecks every original **1,158 system** and **2,867 map/story** source-owner payload in the **new** linked ROM, plus new system labels, byte-for-byte at their unique ELF symbol addresses. The gate requires five untouched stock font banks and at least 1 MiB free linker tail. No assertion of final-game readiness is made.

## Where to inspect the result

Workflow run: https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38139355341

Expected artifact files, if this pipeline reaches the new stage:
- \`SOURCE_ZERO_PAGE_SYSTEM_ADDITIVE_STAGE.json\`
- \`SOURCE_ZERO_PAGE_SYSTEM_ADDITIVE.sym\`
- \`SOURCE_ZERO_PAGE_SYSTEM_ADDITIVE_FONT_AUDIT.json\`
- \`SOURCE_ZERO_PAGE_SYSTEM_ADDITIVE_HEADROOM.json\`
- \`SOURCE_ZERO_PAGE_SYSTEM_ADDITIVE_ATTESTATION.json\`

The final report defines \`new_static_zero_page_system_labels\`, \`combined_source_compiled_labels\` and the exact map/system ELF checks. When CI is pending, cancelled or failed, **do not describe the proposed additions as verified or finished**.

## Unchanged hard requirements

- User-approved stable **v0.4** (SHA-256 \`c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9\`) remains the visual and rollback reference.
- **Do not ship** the synthesized/stock-font build as localized, and do not reuse relocated font offsets without pairing them with an exact source ROM hash.
- The source translation manifest already has **17,512/17,512 user-facing entries**; this is not equivalent to 17,512 installed game strings. Continue linker-safe installation and runtime tests rather than retranslating completed text.
- Title-screen credit remains **“Việt hóa bởi Votri Valley”**. Avoid corrupting title/startup graphics, intro, overworld, combat, return, or save/load. No commercial ROM is committed to GitHub.
