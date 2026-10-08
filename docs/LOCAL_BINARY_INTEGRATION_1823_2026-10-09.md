# Experimental in-place Vietnamese batch — 2026-10-09 (1,823 rows)

## Status

**Source manifest completion remains 17,512/17,512; this is NOT equivalent to installed runtime localization.** A new private/local test ROM has now been produced by making **1,823 bounded manifest-based text replacements** on the previously shared v4-menu/title-credit donor, without adding any pointer writes or source-build-dependent mass-repoint.

**This is an experimental test build, not a stable or emulator-tested release.** Some Vietnamese accent glyph mappings were inferred statistically from existing v0.4 donor text, not yet checked visually in a running emulator.

| ROM | SHA-256 |
| --- | --- |
| Clean Arena 0.13.0 reference | `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b` |
| v0.4 safe rollback | `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9` |
| Input title-credit-v4-menu ROM | `ee82c588a960bcb59466ea950fb6a6a1ce1ab94ada62c6b9f8fceaa8dd0d47c3` |
| Result: v5-1823-strings-TEST ROM (32 MiB) | `ae1e00595ba3d1f193bcdbd8fcff44394b37e582c0a202e7c0c0df97f645d4d0` |
| BPS patch v4 menu → v5-1823-TEST | `14896804c7295189cb26183d9b5fcf7fce86aa67160105bcf25482eff810eee3` |

BPS size: **142,034 bytes**. SourceRead/TargetRead full ROM reconstruction and BPS source, target, patch CRC32 checks all **PASS**. Header/startup and previously installed v4 credit/menu pointer tables are unchanged. No full ROM/BPS binaries are committed to this public repository.

## String integration work performed

- **1,288 map/story** source-catalog manifest strings: source-bytes clean/v4 equality at **shipping-checkpoint-attested exact offset**, bounded to original text `0xFF` span, verified reference metadata, no documented overlapping string start, and no repoint.
- **456 system-text** strings under the same restrictions.
- **1 additional map/story**: `SootopolisCity_House4_Text_AncientTreasuresWaitingInSea`, replaces previous v2 prototype *without diacritics* with the actual UTF-8 Vietnamese manifest text compiled to the v0.4 codebook. Original 175-byte English allocation; target encoded to 150 bytes.
- **78 system-ui** strings under the *additional* requirements: source kind `c-named-string` from `src/strings.c`; exact clean shipping English bytes matched at source-build offset; still equal in current ROM; the literal target address exists in both clean and current donor; reference metadata is present; rewritten string fits original span; no pointer edits. These **78 new local exact matches were not included among the previously shipping-checkpoint-attested 6,680**, and should be treated separately for formal runtime-reference attestation.
- **One extra gender-label correction**: the previous v4 interim `Gái` was replaced with `Nữ` in `gText_BirchGirl` at `0x006DA94F`. The already localized `Nam` remains. This label correction is tracked separately from the 1,823 manifest-row count.

Total content rows: **1,289 map/story + 456 system-text + 78 system-ui = 1,823**.
Explicit ROM offsets were never guessed from random pointer scans. Every write was a SHA-locked bounded in-place string replacement. No binary pointer updates in this batch. The previous v4 menu patch's existing reference edits remain present, but were not modified by this batch.

## Recovered candidate Vietnamese glyph mapping

The project's v0.4 Vietnamese text encoding is *not* ordinary UTF-8. A separate read-only pass inspected **1,005** prior v0.4 text spans whose bytes differ from clean. Matching anchored groups of known ASCII/Latin glyphs against the newer manifest texts yielded **50 previously unknown accent mappings** with repeated independent source-label support (examples: `ấ → 0xDA`, `ế → 0x1D`, `ố → 0x05`, `ớ → 0x0E`, `ữ → 0x0C`, `â → 0x68`). The resulting candidate codebook is recorded in `checkpoints/v04-inferred-vietnamese-codebook.json`.

**This mapping is inferred, not validated by visually reading every accent in mGBA.** Preserve the codebook as an experimental input with explicit hash locking. Unknown glyphs, unsupported dynamic placeholders, all translated strings that do not fit and any binary locations already changed in v4 were excluded from the 1,744 main rows. The 78 UI additions are also bounded; see above.

## QA and remaining work

- Exact source/target ROM SHA locks: PASS.
- BPS source, target, patch CRC and byte-accurate reconstruction: PASS.
- 1,744 main in-place spans + repaired Sootopolis + repaired gender + 78 UI spans, separately bounded: PASS.
- Changes to original startup/title and v4 menu reference regions in this batch: **none**.
- Intended new pointer writes/repoint: **0**.
- mGBA visual/runtime QA: **NOT RUN**.
- Translated lines involving overlong text, dynamic controls `{PLAYER}`/`{STR_VAR_1}`, unmatched encoding, previously localized spans, shared pointer environments, other system-ui/battle/Arena-only groups: **still pending**.

**Important:** This binary is not ready to call a stable translation. Test against title, intro, dialogue, gender, saving/loading, party and battles (especially post-battle return); validate the previously reported accent typography and UI width. Preserve safe v0.4 rollback. Future work must integrate remaining rows using verified source-level references and a **visually validated glyph encoder** before broader writes.

In the user's chat, the local package `Emerald-Arena-1823-Strings-Patchkit.zip` contains scripts, the SHA-locked v4→v5 BPS, manifest-based write plan, all audits and read-only glyph inference. It includes **no commercial ROM**.
