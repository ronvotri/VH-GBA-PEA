# Emerald Arena: v0.4 stable-source recovery TEST — 2026-10-12

## Why this build

The user's No$GBA runtime evidence showed first-battle freeze on v5-family and +341 experimental ROMs. Historical v0.3/v0.4 were the only user-confirmed battle-to-overworld baselines. **Do not use v5 (including its rollback test) or the +341 relocation experiment as the next game's binary base.**

The new local candidate starts from exact user-submitted **v0.4 Text Cluster Pass** ROM SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`. The v5-1823 base, SHA256 `ae1e00595ba3d1f193bcdbd8fcff44394b37e582c0a202e7c0c0df97f645d4d0`, was READ ONLY for comparison. The 12 targeted string bytes were identical in these two input ROMs before editing, so no v5 game code or menu pointers were imported.

## New private candidate — exact audit

`Emerald-Arena-v04-StableIntro12-TruckBoxFix-TEST.gba`:
SHA256 `2fef97006bb35293aa43764c74d1f7e0df5c8c8674a3fd42a559af6bc5a994f5`.

IPS delta from exact v0.4:
`Emerald-Arena-v04-StableIntro12-TruckBoxFix-TEST.ips`:
SHA256 `abb761143b45083b79a9ba5e3e725cefe20b2294bc19d3cd2028200c8a1aebb7`.

- 12 source-owned verified-shipping-offset in-place early dialogues: Littleroot mother, house clock setup and stopped clock, living room, mover explanation, May's mother's greeting, other rival/early map lines.
- 1 explicitly validated moving-truck box message pointer at ROM offset `0x251192`, original `0x0823BF75` (into unrelated Sootopolis text) -> `0x08251199` (original truck-box text).
- 1,213 actual differing bytes in total; new ROM stays 33,554,432 bytes, all five previously approved v0.4 font+width blocks unchanged; startup/title region below `0x1F0000` and header unchanged.
- Original byte-control and variable **sequence/order preserved**, including correction of an earlier flawed mother-dialogue draft that moved `{PLAYER}` to the wrong side of the final newline. Fixed sentence now places player-name variable BEFORE that newline, as in original game.
- No modification of original scene/script regions at `0x1FD2A3`, `0x1FDF07`, `0x201136`; no raw-pointer relocation beyond that single truck-box repair.
- Three proposed Birch lab labels with pointer-to-interior evidence were **rejected rather than forced**. Max modeled line width <=190px across all five original font width tables. Independently replayed IPS reproduced exact resulting ROM SHA256.

## Limitations / mandatory next check

**NOT emulator-certified.** Static QA cannot prove first-battle freeze is fixed; test with a fresh emulator launch (not +341 savestate): moving-truck box, mother, clock, exit house, Birch's first battle, return to overworld, save/load and May's house. If the original v0.4 still crashes in the user's emulator, compare emulator configuration, save type and original first-battle path before changing scripts.

v0.4's older `f/w/z` donor font-byte collisions with Vietnamese glyphs are NOT resolved globally, so still-English lines may have rendering issues. The v5 Votri Valley title credit was **not ported yet** to avoid touching the only historically user-tested boot region before a gameplay pass. This remains a TEST candidate, not complete localization. Source compiler integrated-label metric remains separately 7,134 / 17,512 authored manifest rows; do not add this private ROM's 12 strings to it.

Private ROM and font bytes have **not** been uploaded to public GitHub. Full per-label local audit was generated as `Emerald-Arena-v04-StableIntro12-TruckBoxFix-REPORT.json`.
