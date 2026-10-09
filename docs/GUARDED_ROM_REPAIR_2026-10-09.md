# Guarded ROM repair + shared-suffix relocation — 2026-10-09

**Status: RESEARCH / INTERNAL TEST. NOT A STABLE RELEASE; NO EMULATOR QA.** The user explicitly requested that we repair discovered defects, continue Vietnamese-accented integration, and check carefully before sharing a new playable ROM. **Do not ask the user to test this yet.**

## Exact private ROM inputs and outputs

| Binary | SHA-256 |
| --- | --- |
| Clean released Arena 0.13.0 | `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b` |
| Safe original Vietnamese v0.4 baseline | `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9` |
| **Input** experimental v5-2084 TEST | `575515ff66f640e22b77a38d06395ce3e53a9c459c1e34ab6ebd125f12d34859` |
| **Output** guarded/reflowed/relocated internal candidate (32 MiB) | `5ec43ea41192e473939002d3ed809cd84d650e51e583124bd175f7f503dda6b3` |
| BPS from input v5-2084 to guarded candidate (61,489 bytes) | `f2801efb97b8282f7b5050d84625d434586b8bf080f1033dc5045ff9a0d131ed` |

All commercial ROM bytes remain private and are **not** in this public GitHub repo. The chat execution filesystem contains the candidate at `/mnt/data/arena_safe_repair/Emerald-Arena-v5-GuardedRecovery-Relocated-TEST.gba` and BPS at `/mnt/data/arena_safe_repair/Emerald-Arena-v5-2084-to-GuardedRelocation-TEST.bps`; these are runtime-local paths, not permanent GitHub downloads. This document preserves SHA/provenance if conversation files are lost.

## What has actually changed

1. **Historical bad source pointers: all 64 attested sites now point to their original verified clean-ROM owner addresses.** Eight were already restored in the preceding 2,084-row test; **56 additional** were restored in this pass, each requiring exact clean source literal, current corrupted value, catalog label, shipping-attested owner offset and named source reference sites. This includes **15 references into all-FF filler, one into an FF terminator**, numerous pointers into unrelated maps, and two pointers into non-text bytes in the trailing region. No general ROM pointer search/repoint used to choose replacement values: target = exact clean shipping source owner for each site.
2. The **270 previously in-place-patched spans with detected 4-alignment pointer-like values into their interiors** were restored to exact v0.4 bytes first. This prevents damaging any old suffix references (some rows have many such references). It also means these translations were temporarily removed from their original slots.
3. Of those 270, **212 were recovered as Vietnamese with accents through narrowly attested owner-pointer relocation**: only rows with **one exact original owner pointer in clean ROM, unchanged in input, at an unprotected source-script site preceding the text by no more than 0x4000 bytes**, source-file ownership consistent with manifest. The original shared text stays byte-for-byte v0.4 so suffix users are unharmed; one owned pointer per row is redirected to the new translation. The remaining **58** rows were *not* force-repointed: 21 have multiple original reference sites, 37 do not satisfy local/unprotected-site criteria.
4. **29 additional source-verified manifest translations** were integrated in place: 22 map/story + 7 system-text. They must fit source allocation, preserve dynamic tokens exactly and control counts, have active exact source reference, no interior alias, no overlapping source symbol, and meet conservative line-width limits. All unsupported glyph/control/overlong/ambiguous candidates were skipped.
5. **916 already translated fixed-text spans** had long lines made safer by replacing **1,548 existing space bytes** with standard Emerald FE-newline or FA-scroll controls **without changing string sizes, terminators or pointers**. Max encoded glyph segment now 28 for those spans. These inserts are *not yet runtime/visual validated*; they may still need editing if engine page behavior differs.
6. Exact original startup/title graphic and existing `Việt hóa bởi Votri Valley` title credit plus menu pointer/assets remain unchanged in this pass.

### Important critical allocator correction

Being filled with `0xFF` is **NOT evidence of safe unused ROM**: the old v5 ROM had **hundreds of pre-existing damaged reference values pointed into empty tail filler**. An initial contiguous tail allocation was rejected by a new independent reference scan. The final allocator treats **all preexisting pointer destinations in the post-repair input ROM** (all four possible alignments) as exclusions. Only 4-byte-aligned, fully FF, pointer-free spans within reserved range `0x01FF4000..0x01FFFF00` were selected. 212 localized copies use **22,591 bytes**; **221 unique destination bytes** in that zone were blacklisted due to existing literal references. Final independent QA confirmed **no pre-existing pointer into any newly installed translation span**, its old shared-suffix owner text is preserved, and every new owned pointer resolves to a terminated string.

## QA results (strict static only)

- All three ROM baselines and final output locked by SHA-256.
- Exactly **64/64** source-attested historical pointer sites now match their original released-ROM owner pointer literals.
- **270/270** old shared source spans equal v0.4 byte-for-byte; **212/212** relocated copies have valid terminators, controlled width and one verified source-owned literal.
- **29** new in-place strings checked against source and exact ROM bytes.
- Old logo, startup and menus protected.
- BPS source, target, patch CRC32 and full 32 MiB independent reconstructed output **PASS**.
- Total differences from prior v5-2084: **52,998 bytes** distributed in 3,686 runs; BPS size **61,489 bytes**.
- New pointer writes: **56 source-owner restorations + 212 explicitly allowlisted single-reference relocations**. This is *not* a blind all-pointer rewrite.
- **No runtime/emulator rendering, battle, scene transition, or save/load tests performed. The inferred Vietnamese codebook still needs visual verification.**
- Partial English/codepage collisions remain. Net installed manifest count is not the 17,512 translated source rows. Earlier 5,469 still-English-at-source number cannot be directly compared to post-relocation because original English is intentionally retained for old suffix users.

## Reproducibility and future work

Local private sources/scripts and JSON allowlists live under `/mnt/data/arena_safe_repair/`:
- `build_guarded_v6.py` — source-owner pointer recovery + 270 safe source restores + 29 new bounded manifest rows, exact write ledger.
- `reflow_guarded_text.py` — reflow controls without changing original string lengths.
- `relocate_shared_suffix_safe.py` — individual owner-pointer relocations with pointer-target-excluding allocator.
- `verify_and_package.py` and `final_qa_relocations.py` — independent byte replay, SHA, reference, text/allocation and BPS CRC/round-trip QA.
- `write-ledger.json`, `relocation-allowlist.json`, `relocation-report.json`, `FINAL_VERIFY.json` — complete mutation evidence.

Before producing a user-facing version: (a) validate **real GBA emulator rendering/scroll/page** and diacritics, (b) verify 58 unresolved alias cases with complete source pointer provenance, (c) fix missing original English/runtime labels and long dynamic lines, (d) verify battle/post-battle, intro/truck, title, menu and save/load. **Do not call this a fully integrated v0.5 or ask the user to inspect technical ZIPs.**

Keep stable v0.4 unchanged for rollback.
