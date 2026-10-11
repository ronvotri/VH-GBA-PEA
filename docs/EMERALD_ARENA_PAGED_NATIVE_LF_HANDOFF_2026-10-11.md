# Pokémon Emerald Arena — page-locked literal LF system additions (11 October 2026)

## Verified baseline

**FULL PASS GitHub Actions #38142750497**: exactly **5,974** distinct source-compiled Vietnamese labels (5 new zero-page native LF system labels after 5,969). Existing **1,160 system** and **2,867 map/story** ELF/GBA source-owner byte arrays matched after relinking, and the new 5 labels also matched. The source-ROM SHA256 at 5,974 is `fc8d275a141ce6fff5e09564f0426f49f3b1bf78e6ed78a7fd128425ab4d8b47`; linker contiguous tail space was **1,807,580 bytes**. **Five fonts remain original English stock raster** and no gameplay QA or original v0.4 Vietnamese-art graft has been completed.

The localization manifest of **17,512/17,512** is already translated but is not all installed into a finished ROM. Do not misreport coverage as a playable-release percentage.

## Changes in this handoff

`tools/stage_static_paged_literal_lf_system_text.py` and unit tests stage only static, source-owned `data/text/*.inc` labels whose **original English text includes GBA `\\p` page boundaries** and whose authored Vietnamese includes literal LF (`\n` byte in source JSON), rather than GBA escape text `\\n`.

- The unaltered English source owner must match exactly before rewriting.
- Repair literal LF only when the **full ordered native `\\n`, `\\l`, `\\p` control signature is exactly equal** to the original English source's signature.
- The number and boundaries of pages, and every authored Vietnamese word **inside each page**, must remain unchanged. Only line wrapping within pages may be adjusted.
- Refuse runtime placeholders, unknown escapes, missing diacritics in the current experimental glyph codebook, mismatched source symbols or duplicate owners.
- Exclude all **eight prior system source reports** (1,165 distinct system labels) by exact source_file+label identity; map/story source labels are immutable.
- No arbitrary ROM pointer edits, source-font modifications, user-approved donor ROM uploads or synthesized glyph art.

The workflow `.github/workflows/arena-map.yml` now creates an isolated `paged-literal-lf-system-additive-source-trial`, recompiles ROM, audits all five stock-font banks and >=1MiB linker headroom, then runs `tools/verify_paged_literal_lf_system_additive.py`. The verifier revalidates the 5,974-source gate, **1,165 prior system** plus **2,867 prior map/story** source labels against actual ROM/ELF bytes and checks every new page-local translated payload against its ELF symbol.

**New Actions run:** [#38143908686](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38143908686). At this checkpoint the new run is not yet FULL PASS. The artifact `SOURCE_PAGED_LITERAL_LF_SYSTEM_ADDITIVE_ATTESTATION.json` must report `new_page_local_literal_LF_system_labels` and `total_compiled_source_labels`. A zero admission count must remain zero in public progress reporting.

## Approved font and final QA requirements

The v0.4 Vietnamese font and graphics the user already approved remain the required visual baseline, SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`. **Do not redesign, regenerate or replace that approved font with synthetic raster from an experimental graft.** The source ROM currently uses stock English bitmap fonts. Exact old font visual compatibility must be confirmed with the private donor and the correct source-symbol/table geometry, rather than being claimed from this stock-font CI.

Continue with source-verified static/dynamic system, battle and UI strings after inspecting the new CI result. Preserve the title credit `Việt hóa bởi Votri Valley` and test title → intro → overworld → battle → return → save/load → Arena screens before claiming a public patch is complete. No copyrighted GBA ROM should be committed to GitHub.
