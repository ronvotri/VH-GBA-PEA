# 2026-10-09 — text ownership script opcode evidence checkpoint

This stage addresses the user's request to continue localization safely **without** chasing each screenshot. **No new ROM was produced or patched**: the newest guarded+UI43+shared13 ROM has a documented SHA-256 but its binary and private builders are not mounted. The older 2,084-row test ROM is NOT an acceptable basis for a purported next release; that would undo shared-suffix repairs.

## Actual work

New checked-in read-only tool `tools/triage_actual_script_ownership.py`, with nine fail-closed tests in `tools/tests/test_triage_actual_script_ownership.py`. It takes SHA-locked clean `0.13.0` and earlier test2084 ROMs, the prior static-QA ZIP, and the pinned `pokeemerald.sym` source artifact. It checks exact matching clean/current 32-bit words against script opcodes / source symbol provenance. The output may **NEVER authorize rewriting a pointer** and never alters any ROM.

To avoid loss when temporary chat files disappear, the result has been stored as [checkpoints/shared-owner-opcode-evidence-2026-10-09.csv](../checkpoints/shared-owner-opcode-evidence-2026-10-09.csv), containing 44 source-word occurrences with source label, text owner, literal-site address, nearest symbol and byte-level classification:

| Evidence type | Occurrences |
| --- | ---: |
| `0F 00` loadword-style command immediately before pointer | **13** |
| `5C` trainerbattle-style command at script start | **16** |
| Aligned known text pointer table entry | **11** |
| Byte coincidences inside sprite graphics / tilemaps | **2** |
| Byte coincidences inside executable code | **2** |
| **Total examined** | **44** |

These involve **43 distinct source labels**. The three script/table categories together yield **40 plausible source references**, not 40 newly patched strings: a single string may have two references. Three named source strings are represented only by four **incidental code/graphics word matches**; the two old historical pointer conflicts still require separate ownership review.

The source build is NOT the exact released ROM layout for all symbols. This is byte-level evidence against shipping and older test2084, not runtime certification for the unavailable latest guarded ROM. **Never mass-repoint the 40 candidates.**

## Specific checks that improve the project

- Literal `DewfordTown_EventScript_LandedSlateport` at `0x001FE9BF`: the original bytes preceding the text pointer are `0F 00`, indicative of text loadword.
- `Route114_EventScript_Nolan` starts with `5C`, and its intro and defeat pointers sit at relative offsets 6 and 10.
- The `gMonFrontPic_Numel` and `gRaySceneTakesFlight_Bg_Tilemap` hits are graphics, **not** text references.
- `MoveWordSelectCursor` and `LoopedTask_CloseMonMarkingsWindow` hits are within instructions, **not** text references.
- The prior reference triage counts remain: **212 + 13 already integrated in the inaccessible guarded output**, 45 deferred then investigated; do not conflate raw reference evidence with those net pending rows.

## Reproduce

```sh
python3 tools/triage_actual_script_ownership.py \
  --clean /private/Emerald-Arena-0.13.0.gba \
  --test2084 /private/Emerald-Arena-v5-TEST-dynamic-pointer-fixes.gba \
  --qa-zip /private/Emerald-Arena-2084-Static-QA-2026-10-09.zip \
  --symbol-zip /private/arena-0.13.0-symbol-map.zip \
  --output /private/shared-owner-opcode-evidence.json
python3 -m unittest discover -s tools/tests -p 'test_triage_actual_script_ownership.py' -v
```

Local test results: **9/9 PASS**. CI full build is tracked separately; passing unit tests do not certify the shipped game ROM.

## Required next tasks

1. Recover/rebuild the **newest guarded ROM** from a deterministic script and all its mutation allowlists; do not restart from old v5 and quietly lose the 64 source pointer repairs, 225 shared-suffix translations, 43 UI strings or credit.
2. Compare the 40 candidate pointers against **that exact latest SHA** and verify script owner/consumer from source opcodes and data tables, especially cross-map labels.
3. For confirmed owners, preserve original shared text, move the accented translation to pointer-safe ROM space, update only allowed individual references and verify terminators/width/overlaps.
4. Systematically integrate remaining UI/battle and English-colliding f/w/z strings, then validate glyphs and dialogue scroll in a GBA emulator. Keep the original v0.4 baseline for rollback.

Do not ask the user to download technical reports; this is internal repository material.
