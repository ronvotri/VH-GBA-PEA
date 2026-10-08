# Read-only local ROM audit — 2026-10-09

This checkpoint follows completed **17,512 / 17,512** user-facing source translation manifests. It is **not** a built or playable v0.5. Full ROMs remain private and are not committed to GitHub.

## Exact local inputs obtained in this session

| Input | Size | SHA-256 |
| --- | ---: | --- |
| Clean Arena 0.13.0 | 33,554,432 | `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b` |
| Vietnamese v0.4 Text Cluster Pass | 33,554,432 | `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9` |
| AowVN donor/reference | 16,777,216 | `d95c778a653ff408e2e5ac388ab77feb1f3a519600713bf4d1ddf109d6e6be2e` |

The local input files are **not** checked into this repository. Downloaded GitHub Actions artifact `arena-0.13.0-symbol-map` from successful run **37829747129**, containing the source catalog, its checkpoint-attested shipping subset, and the 17,512-row integration plan.

## Local exploratory binary findings

All comparisons below are **read-only**:

- Clean vs v0.4 differs at **255,639 bytes**, in **20,805 contiguous change runs**. First changed offset `0x001F286E`, last `0x00A296F7`. Protected first `0x001F0000` bytes are identical even to the clean ROM.
- Previously attested source rows: **6,680**, comprising 4,361 map/story and 2,319 system-text.
  - At these exact original source spans: **4,893** are byte-identical to clean in v0.4, and **1,787** differ from clean.
  - Among the 1,787 differing spans, 1,695 v0.4 terminated byte strings (12+ bytes) are found verbatim in AowVN. This is **byte-level donor evidence**, not a localization/rendering/semantic certification.
- Of the formerly unresolved **10,832** rows, a *restricted English/controls encoder* (self-checked on 6,679 of the 6,680 prior attested source spans; one special `PLUS` macro unsupported) located **7,024 additional source-byte-exact matches at their source-build offset** in the actual clean shipping ROM:
  - 26 Arena-only; 5,545 system-ui; 1,453 battle.
  - **6,824** of these candidate target addresses have at least one equal 32-bit pointer-like value in the clean ROM; this alone **does not identify the real source-level reference**.
  - **3,764** match the clean English byte span in v0.4; **3,260** have different v0.4 bytes.
  - **7,024 are NEW CANDIDATES ONLY**, not new verified safe patch/write addresses.
- **3,808** rows remain unresolved by this exact-at-build-offset subset audit. Of them, 3,686 have no build symbol offset; most are short strings/names, for which unscoped search would be highly ambiguous.
- Matching 32-bit values to checkpoint targets in the clean ROM produces 7,140 pointer-like occurrences; **64 four-byte words differ in v0.4**. They may be changed text, true pointer references, or other data. This does **not** prove 64 pointer writes by the v0.4 patch, nor authorize changing them.
- New ROM/pointer writes from this audit: **ZERO**.

## Reproducible audit tool

New source-controlled script: `tools/audit_local_rom_source_byte_candidates.py`. It uses the **full pinned pret `charmap.txt`** via `resolve_shipping_catalog.py` and hash locks from `verify_local_rom_baselines.py`; it may resolve more rows than the exploratory restricted-encoder counts above. It distinguishes `checkpoint-attested`, `candidate:byte-exact-at-build-offset`, and blocked rows; no result is considered a safe binary write/skip.

```bash
python3 tools/audit_local_rom_source_byte_candidates.py \
  --catalog "/private/artifact/shipping-verified-text-catalog.csv" \
  --clean-rom "/private/Emerald-Arena-0.13.0.gba" \
  --v04-rom "/private/Emerald-Arena-0.13.0-v0.4.gba" \
  --charmap "/private/pinned-pokeemerald/charmap.txt" \
  --out "/private/candidate-layout-by-source.json" \
  --summary "/private/local-rom-audit-summary.json"
```

Safety unit tests: `tools/tests/test_audit_local_rom_source_byte_candidates.py`.

## Next engineering gates

1. Use the full pinned charmap and inspect any additional candidates and the 3,808 unresolved rows. Source-build hash differs from shipping hash; do **not** infer runtime references from build offsets, nor issue bulk replacements for repeated short strings.
2. Verify **actual shipping and v0.4 references** for each patch candidate using source provenance/reference sites and bounded byte checks; analyze shared/overlapping strings separately.
3. Recover/validate the actual **Vietnamese v0.4 encoder, accented glyph layout, placeholders, and terminators**. The English pret charmap is not proof of v0.4 Vietnamese byte encoding.
4. Produce a dry-run patch plan with exact before/after spans and ownership. Reject any unverified address, overlap, protected graphics/title modification or uncontrolled pointer rewrite.
5. Build the next candidate only after the above gates, then emulator QA title/intro, early quests, battle/post-battle, save/load, menus and later story. Retain v0.4 as rollback.

**No playable v0.5 exists as a result of this audit. Do not place either GBA ROM or donor ROM in public GitHub.**
