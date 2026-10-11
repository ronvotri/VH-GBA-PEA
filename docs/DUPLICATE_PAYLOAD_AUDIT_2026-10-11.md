# Emerald Arena — duplicate source dialogue audit (2026-10-11)

## Verified reproducible result

GitHub Actions [#38125295698](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38125295698), commit `4eb42548614b280eb4be3fcb376d1dffafea49ee`, **FULL PASS**.

- 6 existing source-application reports, **2,698 independently source-labeled map dialogue strings** from the already-built 5,777-label tree.
- **34 same-source-file exact-byte duplicate groups**, containing **128 duplicate labels beyond their first representative**.
- Their **theoretical** payload-only duplication cost is **5,047 bytes** if safe sharing were ever proven. This is *not* the same as linker savings: changes to alignment, scripts, symbol ownership and pointer identity could reduce or invalidate the estimate.
- 17 cross-file matching-payload groups also identified; deliberately **not considered safe** for linkage or pooling.
- **Actual byte savings: 0**. Zero pointers changed, zero source labels aliased, no text/ROM/font data modified.
- Generated report: `artifact/SOURCE_5777_DUPLICATE_MAP_PAYLOAD_AUDIT.json`, uploaded by the successful run.
- Script: `tools/audit_duplicate_source_payloads.py`; regressions: `tools/tests/test_audit_duplicate_source_payloads.py`; both run in CI.
- 221 most recent dialogue additions retained full compiler/linker verification; source count remains **5,777**, not a new translation batch.

## Decision

**Do not auto-alias duplicate dialogue symbols to reclaim 5,047 theoretical bytes.** Direct pointer identity, location-sensitive references and parser semantics have not been proven safe. The small potential gain cannot solve the much larger remaining localization coverage problem and does not justify risking emulator crashes or dialogue ownership.

## Next useful technical work

1. Inspect actual ELF `PT_LOAD` segment ranges and address gaps (not only the highest ROM load address). The prior 99.8094% is the **linker high-water mark as a fraction of the 32 MiB address limit**, which is not proof that every address below that mark contains unique occupied payload bytes. Quantify internal gaps before declaring the ROM entirely unoptimizable.
2. Source-catalogue large Arena asset groups and any user-unseen resources with true ownership evidence. Never delete assets just because the game does not show them in a short test.
3. Separately audit complex runtime tokens (`{STR_VAR_1}`, `{B_*}`) for exact engine semantics/maximum display width before attempting new translations.
4. Privately pair the **actual user-approved v0.4 artwork** with a SHA-attested source ROM and run mGBA gameplay/visual QA. Do not silently synthesize small-font Vietnamese raster or ship the current stock-font experimental source build.
5. Preserve `Việt hóa bởi Votri Valley`, existing titles/UI/native token bytes and the stable v0.4 rollback; do not upload copyrighted ROMs to GitHub.
