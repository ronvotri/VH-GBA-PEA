# Pokémon Emerald Arena — source-localized paginated NPC text / 2026-10-11

## Verified upstream baseline before this new stage

- Full CI [#38134165229](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38134165229) **PASS**.
- **5,791 distinct source-compiled Vietnamese strings** (earlier 5,777 + **14** source-owned static zero-page map dialogues). This is source integration, **NOT** a playable v0.4-font-paired release.
- **2,712 ELF-verified source-owned map/dialogue labels** (earlier 2,698 + 14).
- Previous compiled source ROM SHA256: `f5828d767a07b62856922cda4a23a18fa33fb1450e362fd24bcbad5e30e2edb5`, linker tail headroom **1,803,812 bytes**, stock source font; no approved v0.4 donor font.
- The previous experimental graphics linker compaction recovered 1,739,728 contiguous tail bytes in its isolated branch. Do not merge into stable user-tested v0.4 without full gameplay/visual QA.

## Newly implemented page-preserving map source stage

- `tools/stage_static_paged_map_dialogues.py` stages only original `data/maps/` source-owner dialogue with an exact matching count of English and Vietnamese literal `\\p` page breaks.
- `tools/tests/test_stage_static_paged_map_dialogues.py` verifies page-local authored Vietnamese word order, exact page-count preservation, absent dynamic tokens, absence of unsupported escapes, no source-label drift and no accidental mutation of neighboring labels.
- Uses source-checked `patch_labeled_block` and existing pinned charmap/codebook; each page reflows independently with native GBA `\\n` and `\\l` rather than moving words across a `\\p` boundary.
- Pipeline stage introduced in [commit d906d76](https://github.com/ronvotri/VH-GBA-PEA/commit/d906d7604ef469815d36c1a48a77e08c6f638eb1), after the 5,791 packed zero-page branch.
- Excludes all seven previously source-integrated map/dynamic batches by exact source owner, **2,712 prior owners**; target: bounded up to 750 more.
- Independently checks applied stage report, exact page count and word order, original source ownership, final ELF-linked ROM byte arrays for **all old and new map symbols**, five source font banks, and at least 1 MiB remaining ROM headroom.
- Crucially, **do not count any new paginated strings before this pipeline stage passes and publishes `SOURCE_PAGED_MAP_ADDITIVE_ATTESTATION.json`**.
- Current workflow run for new paginated stage: [#38134862518](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38134862518) — verify its final conclusion and new label count at continuation.

## Blockers remain

The source ROM uses stock font glyph pixels, not the user's accepted v0.4 art. Runtime variables (`{PLAYER}`, `{STR_VAR_*}`, `{B_*}`) and missing uppercase/lowercase Vietnamese glyphs are rejected by this conservative mode. No emulator visual review, gameplay QA or user-ready binary/patch yet. Preserve original v0.4 as the only accepted tested-font rollback; do not ship distorted synthetic glyphs or copyrighted ROM binaries.
