# Pokémon Emerald Arena v5 — private 69/341 additive ROM experiments (2026-10-12)

## Correct donor baseline (not old v0.4)

All work uses the **user supplied private v5 Votri Valley** merged with the previous +34 patch:

- Input `Emerald-Arena-v5-Votri-Valley-Plus34Cau-TEST.gba`
- Exact SHA-256: `4bba79d597a3e2bd8d09486b03d7faabe60e97e3057b6eab6c2897de1f0ab798`
- ROM size 33,554,432 bytes (32 MiB)
- The 390 earlier authored text spans (356 v5 originals +34 added) remain intact.

Authoritative source catalog: `user-facing-integration-plan.json`, 17,512 authored entries from FULL PASS GitHub Actions #38162619581 artifact `arena-0.13.0-symbol-map`. **7,134 source-compiled labels is a separate, earlier stock-font experimental build metric** and must never be added directly to numbers below.

## Actual private build outputs (do NOT commit ROM files)

### No-pointer conservative version

- File: `Emerald-Arena-v5-Votri-Valley-Plus69-NoPointer-TEST.gba`
- SHA-256: `9591c96ad5ad278eea081842d7e7887260319b840ae77af1d9ece902c4e7d873`
- IPS: `Emerald-Arena-v5-Votri-Valley-Plus69-NoPointer-TEST.ips`, SHA-256 `8a92f53ac4e5a6478767c3f314581a48258380b9963cf7079bfee8563ed60bc0`
- Exactly **69 additional source-owned user-facing texts**, no pointers modified; **6,165 actual changed bytes**.

### Controlled relocation experiment (higher runtime risk)

- File: `Emerald-Arena-v5-Votri-Valley-Plus341-VerifiedRepoint-EXPERIMENTAL.gba`
- SHA-256: `0bf451fda75f1e32c5b2fc865386009f02b6339d191c721d1346bacd8807e11b`
- BPS: `Emerald-Arena-v5-Votri-Valley-Plus341-VerifiedRepoint-EXPERIMENTAL.bps`, SHA-256 `bc501813f67bb5d924023eb2d05759db594c18246e7f4e1b00eb6ba63cfbf3bd`
- Exactly **341 additional entries** beyond v5+34: the same 69 in-place, plus **272 map/story labels relocated one by one**, each with **one declared source reference, one exact 0x08-based ROM pointer match, and other same-source-file script pointers within 512 bytes**.
- 272 pointer writes, 15,000 bytes of translated payload in separately allocated blocks in preexisting all-0xFF ROM tail (origin `0x1FF2219`), at least 7 bytes away from every apparent 4-byte GBA pointer target seen at any of four possible byte alignments; source English strings are not overwritten.
- **21,979 actual changed bytes**. Classic IPS cannot encode changes beyond 16 MiB, so this version uses CRC-validated **BPS** instead.
- Both IPS and BPS independently reapplied and produced exact matching ROM SHA-256 output.

## Invariant checks passed

- Full 32 MiB size, header Nintendo complement checksum, startup/title byte prefix below 0x1F0000, and all five user-approved v0.4 glyph/width banks unchanged.
- Earlier 390 text spans identical byte-for-byte.
- Original source-owned shipping English bytes verified at each target; all compiled Vietnamese chars supported by the actual private v0.4 glyph codebook (including donor-specific accent slots).
- Original native GBA newline/scroll/page control **sequence unchanged**; same source-page Vietnamese word order, except permitted line positioning within a page.
- Max rendered text line width checked against **the maximum of all five donor font width tables** with conservative 190-pixel ceiling; this is static width QA, **not** screenshot visual QA.
- No overlapping changed ranges with any existing catalog owner, any old-string interior pointer target, prior 390 strings, font banks or title.
- Both patch replayers and CRC/SHA verification passed against exact user-donor base.

## Critical unresolved status

**Actual mGBA/RetroArch boot, interaction, graphical rendering, dialogue visibility, battles, saving, Easy Chat and Battle Frontier cannot be certified** in the current environment: there is no installed GBA emulator, and this session has no emulator runtime test result. These are **TEST** ROMs, especially +341 with its 272 controlled pointer edits.

17,512 authored strings are NOT fully present as playable UTF-8 Vietnamese in either private ROM. Many owners lack verified shipping offsets, exceed original allocation, require dynamic token handling, or contain glyphs unsupported by original v0.4 font. Never claim full completion or merge counts from different binary baselines.

Next highest-value work:
1. Run actual mGBA on user-side private ROM, using +69 as stable fallback if +341 fails; test title/intro/map/battle/post-battle/save-load/Pokédex/Battle Frontier/Easy Chat and accents.
2. Pursue source-built 7,134+ localization with **authentic** v0.4 visual font bank pairing, and safe support for unsupported glyphs + dynamic placeholders; do not rely on unverified codepoint remaps or mass source-pointer rewriting.
3. Only when real runtime QA passes, promote a test version to a release candidate. Never upload copyrighted ROMs or donor font bitmaps to the public repository.

Detailed per-label records and private build inputs are in the conversation report `Emerald-Arena-v5-Votri-Valley-Expanded-StaticQA-report.json`; no proprietary binary stored here.
