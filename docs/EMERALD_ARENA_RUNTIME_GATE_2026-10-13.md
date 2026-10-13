# Runtime gate update — 13/10/2026

## Confirmed project position

- 17,512/17,512 user-facing translation records are authored.
- 7,134 source-owned Vietnamese labels have source/ELF/GBA byte attestation; no newer verified label count is claimed here.
- Approved Vietnamese glyph pixels remain in the private donor ROM v0.4; the source-built ROM continues to have stock English raster fonts.
- First Birch battle and post-battle return **are not yet validated** for the recent user-tested candidates. The +341 pointer relocation variant is **REJECTED**.
- No new ROM, binary patch or donor artwork was generated or committed.

## Added this session

- `tools/verify_first_battle_runtime_report.py` validates an explicitly recorded, human-observed A/B/C run (clean / known-approved v0.4 / candidate), each with ROM SHA, actual emulator/version, sound setting, before-Birch battery save digest and observed battle-completion, overworld return, movement, save/load check.
- Requires exactly the clean and approved-v0.4 SHA checksums, identical emulator/version/sound/save evidence, and refuses the known-bad +341 SHA. Save states are not silently accepted as battery `.sav` checkpoints.
- `tools/tests/test_verify_first_battle_runtime_report.py` exercises positive evidence, reported freeze, missing game observations, mismatched A/B settings, wrong baseline, rejected pointer variant and malformed report.
- A valid first-battle **PASS is not enough to mark full-game release ready**. The tool never asserts that it played the game. It requires real observations; it does not synthesize test data.
- Run from repository root: `python -m unittest discover -s tools/tests -p "test_*.py"`. Once an actual observational JSON is available: `python tools/verify_first_battle_runtime_report.py --report <private-observations.json> --out <private-check-result.json>`. Keep private observations and saves outside public GitHub.

## Remaining blocker

No private ROMs or actual emulator gameplay evidence were provided in this turn. No$GBA Sound Output disabled remains only a plausible cause, not a proven fix. First compare sound enabled and cross-check with mGBA on a matching pre-battle battery save before adding ROM relocations or claiming freeze resolved.

This is a safety/QA tooling checkpoint, **not** an increase in localized label count or a game release.
