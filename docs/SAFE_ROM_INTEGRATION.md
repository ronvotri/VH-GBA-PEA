# Pokémon Emerald Arena — Safe ROM integration and runtime QA

**Status (2026-10-09):** The complete *source translation manifest* is accounted for and source-QA/CI passed: **17,512 / 17,512 player-facing strings**. This is **not** a statement that the corresponding bytes have been patched into v0.4. The sole excluded entry is an internal test signpost.

## Verified identity and binary safety

| Input | SHA-256 |
| --- | --- |
| Clean Arena v0.13.0 shipping ROM | `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b` |
| Vietnamese v0.4 Text Cluster Pass | `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9` |
| Vietnamese v0.3 stable (optional guard verification) | `8234d3945fc6d3a87a9669887a114114904b85c00fd9b3ddd026aaea40d636ec` |

No ROM files belong in this public GitHub repository.

**Safe preflight (local only):**

```bash
python3 tools/verify_local_rom_baselines.py \
  --clean-rom "/local/path/Emerald-Arena-0.13.0.gba" \
  --v04-rom "/local/path/Emerald-Arena-v0.4.gba" \
  --summary "/local/private/rom-baseline-audit.json"
```

With an exact v0.3 stable ROM also available, optionally pass `--v03-rom "/local/path/Emerald-Arena-v0.3.gba"`. This checks that v0.4 retained identical startup/title bytes below `0x1F0000` relative to v0.3. A mismatched SHA-256 or failed optional title guard **must stop the operation**.

### Audit v0.4 bytes at already verified shipping offsets (local, read-only)

After downloading the `arena-0.13.0-symbol-map` workflow artifact and obtaining the exact pinned pret source `charmap.txt`, run:

```bash
python3 tools/audit_v04_verified_offsets.py \
  --plan "/local/artifact/user-facing-integration-plan.json" \
  --clean-rom "/local/path/Emerald-Arena-0.13.0.gba" \
  --v04-rom "/local/path/Emerald-Arena-v0.4.gba" \
  --charmap "/local/pinned-pokeemerald/charmap.txt" \
  --out "/local/private/v04-verified-offset-audit.json" \
  --summary "/local/private/v04-verified-offset-summary.json"
```

This compares only attested original source spans against the actual v0.4 ROM, after checking both ROM hashes and re-encoding the English source. Unsupported source-encoding cases are reported as **unresolved**, never guessed. The report **does not** validate v0.4 pointers or authorize any write/skip. Rows with unverified shipping offsets stay blocked.

## Source/manifest versus binary readiness

The GitHub workflow `.github/workflows/arena-map.yml` regenerates the catalog from pinned source, rechecks the shipping verification checkpoint, validates every manifest, and creates:

- `translation-coverage.json` — all catalog rows represented in manifests.
- `user-facing-integration-plan.json` and `user-facing-integration-summary.json` — explicit read-only per-row integration status.
- `shipping-verified-text-catalog.csv` — only individually attested shipping offsets, never guessed.
- `map-story-integration-plan.json` — source-backed map/story subset.

Current source catalog: **17,513** entries total; **17,512** player-facing, **1** debug-only. Of the player-facing entries, **6,680** (4,361 map/story + 2,319 system-text) have existing *shipping-ROM* offset attestations. **10,832** (46 Arena-only + 8,563 system-ui + 2,223 battle) still require shipping-layout verification before any write at those addresses.

The integration planner now also reports `source_text_comparison_counts`, including `source-identical` and `source-changed`. **Important:** A manifest translation identical to English source does **not** prove that v0.4 has identical bytes. v0.4 may already contain an older translation at that address. Therefore **zero** entries are automatically considered safe to skip writing until v0.4 is independently compared; such rows may need restoration of canonical English. Never treat this comparison as a substitute for the v0.4 ROM and a verified encoder.

## Integration gate — never bypass

1. Check both exact input ROM SHA-256 values with the local preflight tool. Preserve originals.
2. Verify source and shipping mapping for every **changed** string against the actual clean ROM bytes. Known source-build symbols alone are insufficient for scopes with unresolved shipping layout.
3. Recover and verify the existing v0.4 Vietnamese glyph/byte encoding. Do not assume UTF-8 or the English pret charmap represents the v0.4 encoding. Include placeholder/control byte order checks.
4. Compare **actual v0.4 baseline bytes** to desired encoded target bytes. A source-identical entry is skippable only if this comparison proves the v0.4 bytes already correct.
5. For in-place changes, validate allocated span and adjacent resources, including overlapping/shared strings. If the target is too long, defer until *each exact source-level reference* and a safe destination have been verified. Never scan-and-repoint arbitrary pointer-like ROM values.
6. Emit an explicit dry-run report of each planned write, before/after byte hashes, overlapping regions, and count of verified reference edits. Do not produce a patched ROM if any write is unverified or overlaps protected startup/logo/title/graphics.
7. Run emulator checks before promoting a new version; keep **v0.4** as the rollback baseline until the new build passes.

### Minimum runtime QA matrix

| Area | Required check |
| --- | --- |
| Startup/title | Nintendo/GAME FREAK logo, title sprites, intro, new-game, continue, no freeze |
| Overworld/story | new game through earliest quests, transitions, NPC dialogues, scripted events, no broken text |
| Battle | initial wild battle, trainer battle, status changes, catching, fainting, post-battle overworld return |
| Menus/UI | inventory, party, summary, Pokédex, PokéNav, options, PC, save/load |
| Events | Contest, Safari Zone, Berry Blender, Match Call, Secret Base, Day Care, Mystery Gift (when testable) |
| Technical | accented glyphs, control codes, dynamic Pokémon/MOVE/ITEM names, placeholders, wrap/overflow, line breaks |
| Regression | replay v0.4 crash-free startup/title and post-battle milestones, compare saved-game compatibility |

## What is blocked vs complete

- **Completed:** source-level translation, source-provenance manifest inventory, token QA, automated coverage, initial 6,680 shipping-layout attestations, hash-locked local baseline verifier and CI safety regression tests.
- **Blocked by unavailable binary inputs:** actual v0.4 byte comparison, complete shipping-offset mapping for 10,832 remaining rows, exact Vietnamese encoding/fit, final integrated ROM build and game/runtime QA.

Next engineering step once exact private ROMs are accessible: run preflight, perform a **read-only encoding and layout audit**, then prepare a bounded dry-run patch plan. Do **not** ship a claimed "fully translated ROM" before the integration and gameplay tests succeed.
