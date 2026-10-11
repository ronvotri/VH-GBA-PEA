# Emerald Arena — source-owned system-text literal LF gate (11 October 2026)

## Current verified baseline

- CI [#38139503164](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38139503164): **FULL PASS**, 5,969 distinct source-compiled strings, 1,160 system and 2,867 map/story exact ROM/ELF owned-byte checks.
- 17,512/17,512 manifest translations are authored, **not** all installed in a playable GBA.
- The user's playable/visually approved **v0.4** is the retained baseline/rollback (SHA256: `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`). Never redesign/synthesize fonts as if the user's approved artwork were wrong. Source trials still have **stock** glyph pixels; the v0.6 codebook requires a genuine donor-art-compatible migration, not blindly copying donor banks.

## Second additive stage (after 5,969)

Work committed in tools and CI to investigate source-manifest strings with an actual UTF-8 newline character instead of the native textual `\\n` directive:

- `tools/stage_static_literal_lf_system_text.py`: static `data/text/*.inc` symbols only; no runtime placeholders, pages, other escapes or raw ROM writes. Converts a literal line feed **only** if `normalize_authored_linefeeds()` establishes exact original English `\\n/\\l/\\p` control sequence. Relayout keeps every original Vietnamese word.
- It excludes **all seven prior source-owned system reports**, 1,160 identities, by exact `(source_file, source_label)`, and checks original unmodified English assembly source before rewriting.
- `tools/tests/test_stage_static_literal_lf_system_text.py`: unit tests for valid conversion, wrong original bytes, unknown glyph, inserted controls, dynamic variables, extra pages and duplicate owners.
- `tools/verify_literal_lf_system_additive.py`: re-verifies all prior 1,160 system plus 2,867 map ROM/ELF-linked payloads **in the new ROM**, verifies any new labels and words, confirms five unchanged stock font banks and >=1 MiB ROM headroom.
- `.github/workflows/arena-map.yml`: separate `literal-lf-system-additive-source-trial` workspace after the 5,969 stage, never replacing the passed baseline.

## CI result tracking

[New CI #38142750497](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38142750497) was **in progress when this checkpoint was authored**. Unit tests passed; compilation/ROM attestation had not yet finished. Artifact expected: `SOURCE_LITERAL_LF_SYSTEM_ADDITIVE_ATTESTATION.json`.

**IMPORTANT:** The new stage may legitimately add **zero** new labels if the original English control signature or approved codebook excludes every candidate. The report must show `new_native_LF_normalized_system_labels` and `total_source_compiled_labels`. Do not count candidates before FULL PASS.

## Remaining blockers

1. Source-map count and translation manifest count must not be conflated. Remaining dynamic variables (especially `STR_VAR_*`, `PLAYER`, `RIVAL`), glyphs absent from the current verified codebook and renderer-specific Arena mini-font need dedicated context-aware support.
2. Do not infer/edit arbitrary ROM pointers or corrupt logo/title. Preserve **“Việt hóa bởi Votri Valley”** credit.
3. Private approved v0.4 donor image is **not** stored in this GitHub repository; font-art graft cannot be marked done from stock-font CI. Do not synthesize new unapproved glyphs, even if an old experimental tool supports that.
4. Test intro → overworld → battle → postbattle → save/load → Arena UI in mGBA before calling a build a real Vietnamese release.
