# Emerald Arena: stop repetitive first-battle replay — 2026-10-13

The user repeatedly reported that several privately patched ROMs **freeze after the first Birch battle** and that repeating the entire opening wastes time. Never assert a ROM passes gameplay based on binary SHA, IPS/BPS replay, text pointer checks or static width tests alone.

## Evidence rechecked, no private ROM bytes in public GitHub

The user's exact local ROM uploads were independently hashed and compared read-only (32 MiB each). The original v0.4 donor was reported to pass intro -> Birch first battle -> overworld in historical testing, but later derived builds and a recent v0.4 Recovery TEST also froze in the user's **No$GBA**. An emulator-level issue is a plausible explanation, not proven yet.

- v0.4 Text Cluster Pass: `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`
- v5 1823: `ae1e00595ba3d1f193bcdbd8fcff44394b37e582c0a202e7c0c0df97f645d4d0`
- v5 +341 EXPERIMENTAL (REJECTED): `0bf451fda75f1e32c5b2fc865386009f02b6339d191c721d1346bacd8807e11b`
- v0.4 Intro12/Truck recovery (user says still freezes): `2fef97006bb35293aa43764c74d1f7e0df5c8c8674a3fd42a559af6bc5a994f5`

v5 differs from v0.4 at 135,368 byte positions (including 20 before `0x1F0000`); rejected +341 differs from v0.4 at 158,616 byte positions; recovery differs by 1,213 byte positions. All four passed the original GBA header complement checksum. This establishes neither runtime stability nor crash root cause.

## External emulator-specific freeze workaround to test FIRST

Older No$GBA/Pokémon support sources explicitly report a freeze after defeating a Pokémon when audio processing is disabled. Before another patch, **enable Sound Output** in the user's No$GBA emulator settings (e.g., Digital Mono instead of disabled), then try the existing ROM without further edits:
- https://www.nogba.com/no%24gba-pokemon.htm
- https://www.nogba.com/no%24gba-setup-options.htm

This is **not** a proven Emerald Arena bugfix until the user confirms their No$GBA setting and successfully resumes overworld after the first battle.

## Reusable before-Birch gameplay checkpoint kit

A Windows PowerShell 5.1 kit has been generated in the conversation as `Emerald-Arena-Battle-QA-Kit.zip` (SHA-256 `f13ba34743fc323c5eca6d0e6d3f3c5e9edb7f12d4df34717d1918f9b0ca8fbd`). No copyrighted ROM is included.

- `01_Run_ROM.cmd`: asks for a local GBA ROM and `mGBA.exe`, stages it as `Documents/EmeraldArena-BattleQA/RUN/EMERALD_BATTLE_QA.gba`. Original input never overwritten. Exact SHA recorded; known +341 rejected.
- `02_Store_Before_Battle_Save.cmd`: user confirms a normal **in-game** `.sav` taken just before entering the grass where Birch battle triggers; stores immutable-style backup to `CHECKPOINT/BEFORE_BIRCH_BATTLE.sav`. Can import manually.
- On subsequent launches, copies the saved `.sav` to the staged ROM's matching name, enabling short test runs without replaying intro.
- `03_Record_Battle_Result.cmd`: reports PASS / FREEZE / UNSURE with ROM and checkpoint SHA to `REPORTS/battle-tests.tsv`.
- Kit uses mGBA (not No$GBA) because No$GBA battery save and save states differ and user needs independent emulator comparison.
- Includes read-only `Baseline-Static-Differences.json` auditing SHA and critical text pointers.

**Critical limits**: this kit is not yet exercised on the user's Windows setup; no mGBA executable could be installed or run inside this tool container, so no gameplay result is claimed. If user's save is not a mGBA-readable normal battery `.sav`, it may require format conversion. Save states (`.ss0`, `.sgm`) are not interchangeable with battery saves. Only a real in-emulator first-battle return to overworld establishes PASS. Do not silently promote a private test ROM to stable.

## Workflow gate

Do not add new ROM patches, alter the accepted v0.4 font, drop the Votri Valley title credit or regress Nam/Nữ and gender-appropriate May-mother wording while first-battle gameplay is unverified. First resolve Sound Output vs binary freeze ambiguity, establish one reusable prebattle save, then reproduce gameplay with an emulator under automated test if possible. Existing 7,134 source-linked compiler labels and the 17,512 authored-manifest entries remain distinct.
