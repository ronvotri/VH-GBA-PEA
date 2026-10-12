# Emerald Arena v5 +34 private ROM patch — 2026-10-12

User's newly supplied private ROM: `Emerald-Arena-v0.4-Votri-Valley-Credit-v5-1823-strings-TEST(1).gba`, SHA-256 `ae1e00595ba3d1f193bcdbd8fcff44394b37e582c0a202e7c0c0df97f645d4d0`, 33,554,432 bytes.

Compared all 390 exact approved in-place source-owner records from prior `v0.4-390Cau-TEST` report against this **actual v5 binary**: **356 byte-for-byte already translated** on v5, **34 still identical to old English source**, **0 conflicts**. Applied **only 34** differences from the previously vetted translation bytes (never blindly applying an IPS built for v0.4).

## Private output, not committed publicly
- `Emerald-Arena-v5-Votri-Valley-Plus34Cau-TEST.gba`: SHA-256 `4bba79d597a3e2bd8d09486b03d7faabe60e97e3057b6eab6c2897de1f0ab798`
- `Emerald-Arena-v5-Votri-Valley-Plus34Cau-TEST.ips`: SHA-256 `1f2f4e692dfa5073199bec63c71097c62455eec87ad32ff40d6c1472d2701b17`
- Exactly **1,269 byte changes** across **34 original text ranges**. All 390 original target spans are byte-for-byte Vietnamese after merging.
- Original v5 GBA header checksum, startup/title prefix below 0x1F0000 and all five stock-reference font/width blocks remain unchanged. **0 pointer writes**, **0 non-text writes**.
- IPS replay was independently verified byte-for-byte against resulting ROM, which remains exactly 32 MiB.
- Full private report created locally. **Do not upload copyrighted full ROMs to public GitHub.**
- **NOT emulator tested or production-ready.** Distinct `7,134` source-compiled count is separate and must NOT be incremented by 34 or 390.
- Choice of boy/girl at game opening was NOT altered; do not conflate the existence of gender selection with old vs new ROM version.

Follow-up: runtime emulator QA for v5+34, then exact safe integration for remaining untranslated entries; preserve approved v0.4 font and Votri credit.
