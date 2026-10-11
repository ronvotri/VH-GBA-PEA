# Easy Chat overlapping blocker audit — 2026-10-12

## Baseline and scope
- Last previously completed fully attested source integration: **7,134 / 17,512 authored manifest labels**, Actions [#38161452509](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38161452509).
- The existing audit Actions [#38162619581](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38162619581) has now finished **successfully** (all build-map steps succeeded), but it did not establish additional unique source-integrated labels. Do not count diagnostic candidates as compiled translations.
- Commit `5ecb56d` augments `tools/audit_easy_chat_ui_blockers.py` with **independent, read-only overlapping flags**: a candidate can be both wider in Unicode character count and missing glyphs from the experimental codebook. Reports now include `overlapping_blockers` and capped examples; original exclusive primary classification and acceptance gate are unchanged.
- Commit `6b1dba9` adds a unit regression case for simultaneously longer-than-original and unsupported-accent text.
- Both commits are repository source/test changes. **No new compiled label total, full CI attestation, ROM bytes, font graft or emulator QA is claimed for these two new commits.** Verify in a new workflow run.

## Next localization work
1. Inspect the new `SOURCE_EASY_CHAT_UI_BLOCKERS.json` and independent overlap counters from a completed workflow to prioritize legitimate UI+font work.
2. Confirm renderer's actual pixel width and bank selection for Easy Chat rather than presuming codepoint count equals pixel width.
3. Keep approved visual v0.4 font donor unchanged; exact donor graft and mGBA visual proof are pending.
4. Once exact source-owner, font encoding and actual display constraints are satisfied, stage additional unique labels with original-source and ELF/GBA byte attestations and update the 7,134 baseline **only after a full successful run**.

All original placeholders, control codes, approved user-facing wording and title credit `Việt hóa bởi Votri Valley` remain untouched.
