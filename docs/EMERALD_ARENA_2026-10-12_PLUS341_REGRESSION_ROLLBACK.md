# 2026-10-12 — +341 EXPERIMENTAL REGRESSION: DO NOT USE AS BASELINE

## User's runtime bug report (confirmed, prioritized over static attestation)

User tested `Emerald-Arena-v5-Votri-Valley-Plus341-VerifiedRepoint-EXPERIMENTAL.gba` and reported:
- Beginning mom dialogue still partly English, `MOM: A, ... we're here, honey!`, with visually corrupted English `w`;
- Upstairs clock dialogue unaccented (`Dong ho dung...`);
- **Freeze following the very first battle**, a regression from a previously stable v0.4 path.

**REJECT / DEPRECATE THE +341 EXPERIMENTAL ROM.** Binary pointer-validation and SHA/CRC tests did NOT establish runtime safety. Never promote +341 or its +272 pointer relocations into a stable baseline without reproducible in-emulator gameplay evidence. The original introductory mom dialogue `LittlerootTown_Text_OurNewHomeLetsGoInside` at shipping offset `0x001FD8E0` and clock string `PlayersHouse_2F_Text_ClockIsStopped` at `0x0020D88C` were **identical in the v0.4, original v5 and +341 experiment**, so the language omissions PREDATE +341. Importantly, +341 DOES change an early-game map script pointer for `LittlerootTown_Text_YouSavedBirch` at `0x001FD2A3` from original target `0x001FDF07` to `0x01FF63C0`; this and other untested script references are suspects, NOT a proven exact crash mechanism.

The donor v0.4 character scheme reuses the stock English `f/w/z` slots for diacritics `ấ/ằ/ắ`. Until every English UI/dialogue is translated or the font mapping is safely migrated, untranslated English containing those letters can display corrupted. The user's screenshot `we're` is consistent with this collision. The separately compiled 7,134-label stock-font build is not a v0.4-donor graft and is not a playable/visual-QA release.

## Actual corrective private build: v5 original + 3 safe early dialogues

Input EXACT original, user-supplied v5 `Emerald-Arena-v0.4-Votri-Valley-Credit-v5-1823-strings-TEST(1).gba`, 33,554,432 bytes, SHA-256 `ae1e00595ba3d1f193bcdbd8fcff44394b37e582c0a202e7c0c0df97f645d4d0`.

Output (private conversation attachment ONLY): `Emerald-Arena-v5-Intro3Fix-NoPointer-ROLLBACK-TEST.gba` SHA-256 `aaa14c9c9d2bb6ba017221e7089665b6baf0ad06978caea8781537acd98723ed`. IPS `Emerald-Arena-v5-Intro3Fix-NoPointer-ROLLBACK-TEST.ips`, SHA-256 `cfea53012f1487aa9e8933cc0315aff95135aff99a02cbb630bf134ccbdaecab`.

Only three source-owned map texts were replaced IN PLACE, with verified shipping offsets:
- `LittlerootTown_Text_OurNewHomeLetsGoInside` (`0x1FD8E0`), exact source English 293 bytes -> authored Vietnamese reflowed to 273 bytes, keeping all five `\\p`, four `\\n`, two `{PLAYER}` tokens;
- `PlayersHouse_1F_Text_GoSetTheClock` (`0x20CD8B`), original unaccented v5 40 bytes -> 37-byte Vietnamese with accents and preserved `{PLAYER}`;
- `PlayersHouse_2F_Text_ClockIsStopped` (`0x20D88C`), original unaccented v5 38 bytes -> 34-byte Vietnamese with accents.

The original spelling, source-owner offsets and native code controls were checked against Actions #38162619581 artifact. All lines bounded by <=190 **worst of all five donor font width tables**, with a 7-character upper-case placeholder stress-test. All four byte alignments searched for ROM references INTO modified text interiors; zero found. Another catalog owner never begins in any changed span.

QA: 298 actual bytes changed, **ZERO POINTER WRITES**, original ROM header/title prefix below 0x1F0000/5 donor font and width banks identical. IPS replay exactly matched candidate SHA. **No mGBA/real gameplay run performed in this environment**, so this is a rollback TEST, NOT a certified fix. User must test it fresh through first battle and afterward, ideally with a separate save state. If crash remains on original v5+3, investigate baseline/emulator rather than reinstating +341.

The private local script was created at `emerald_v5_early_dialogue_hotfix.py` in the conversation workspace and requires the exact v5 donor and full Actions artifact; do not commit ROM or extracted font pixels into this public repo.

**SOURCE BUILD COUNT UNCHANGED: 7,134 / 17,512 authored labels.** This private v5 3-text rollback must not be numerically added to stock-font source compiler coverage.

## Optional no-pointer continuation (NOT a substitute for rollback test)

To preserve the 34+69 earlier no-pointer-only additions, exactly the same three early-text bytes were also applied to SHA-pinned `Emerald-Arena-v5-Votri-Valley-Plus69-NoPointer-TEST.gba` (SHA `9591c96ad5ad278eea081842d7e7887260319b840ae77af1d9ece902c4e7d873`). Output private `Emerald-Arena-v5-Plus69-Intro3Fix-NoPointer-TEST.gba` SHA-256 `c722e75471394d0281f95751036c92a9d90e90ceae45567df1f2d5a553a51423`. Diff is identical to the three-dialogue v5 rollback IPS (SHA `cfea53012f1487aa9e8933cc0315aff95135aff99a02cbb630bf134ccbdaecab`), writing 298 changed bytes and zero pointers. This variant is **not emulator certified**; user should first boot the original-v5+3 diagnostic rollback through the first battle, then optionally test this +69+3 only if the first passes. Never reuse +341.

## Next: actual remediation

1. Obtain emulator gameplay evidence and reproduce the first post-battle freeze. Never infer runtime QA from byte checks.
2. Source-driven early-game sweep for unlocalized English and unaccented texts, prioritizing mom/clock → Birch rescue/post-battle → routes, then full catalog.
3. Fix donor `f/w/z` collisions using authentic approved glyphs and suitable separate codepoints; do not reintroduce synthesized ugly glyph shapes.
4. Increment source-built integration counts only after new successful, separately attested CI; keep ROM test counts separate.
