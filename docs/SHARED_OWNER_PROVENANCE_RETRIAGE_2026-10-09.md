# Shared text owner-reference provenance re-triage — 2026-10-09

## Scope and warning

**READ-ONLY** follow-up to [the prior 43-UI/13-shared checkpoint](UI43_SHARED13_GUARDED_CHECKPOINT_2026-10-09.md). This does **not** rebuild that guarded candidate and does **not** add ROM translations yet. The previous private guarded + UI43 + shared13 GBA has SHA-256 `187993098e11317873043a70751cd9009fc1556a8a46a550f017be233a2ec05e` but its *bytes were not present in this resumed runtime*. Available inputs were the previously shared clean ROM, the 2,084-string test ROM, the source/symbol artifact and the static-QA ZIP. **Do not create an output from the older 2,084 ROM and label it a successor**: that would silently discard newer guarded/relocation/UI repairs.

New reproducible, read-only auditor: `tools/triage_shared_owner_provenance.py` with unit tests `tools/tests/test_triage_shared_owner_provenance.py`. It SHA-locks both GBA inputs, reads all 270 flagged shared-suffix candidates and 64 historical source pointer sites, then uses pinned build symbols to distinguish plausible text owner sites from incidental 32-bit matches in binary graphics and instructions. **The symbol nearest a word is supporting provenance, not a runtime reference certificate; its address belongs to a source build whose overall SHA differs from the shipping ROM.** The auditor never marks a pointer safe to rewrite.

## Reproduced exact classification of all 270 shared-source candidates

| Finding from clean + v5-2084 | Rows |
| --- | ---: |
| One nearby unmodified reference | 212 |
| Multiple nearby unmodified references | 13 |
| Distant/nonpreceding unmodified reference(s) | 41 |
| Extra matching word in protected code area | 2 |
| Modified/repointed source-reference cases | 2 |
| **Total** | **270** |

The previously documented **212 + 13 = 225** were subsequently rescued into a guarded internal build; **45 cases remained blocked**. Those 45 are now explained more precisely, without assuming all pointer-like matches are real:

- **39** of the 41 distant/nonpreceding cases have one or more exact source-address matches at a **named EventScript or data/text pointer table** in the pinned build symbol map, including Route109/114/115/117/121/123/124/125, Trainer Hill, apprentice and TV-news tables. The 39 rows correspond to 40 observed symbol-provenance occurrences. These are strong *candidates for individual owner verification*, not automatic write approval.
- **2** of the 41 are spurious matches in **graphics data**, not authored text pointers: `MauvilleCity_Gym_Text_KirkIntro` matched a word in `gMonFrontPic_Numel`; `BattleFrontier_BattlePikeLobby_Text_LookForwardToSeeingYou` matched one in `gRaySceneTakesFlight_Bg_Tilemap`. **DO NOT REPPOINT THOSE WORDS**.
- **2** additional cases each have a plausible nearby text owner *plus* an incidental four-byte match in executable code: `Route114_LanettesHouse_Text_ResearchNotesPage3` (inside `MoveWordSelectCursor`) and `Route110_TrickHouseEnd_Text_AllNightToPlantTrees` (inside `LoopedTask_CloseMonMarkingsWindow`). Those code bytes are **not safe to treat as data pointers**. The nearby script sites can be separately verified later.
- **2** remaining cases `VerdanturfTown_BattleTentLobby_Text_AttractionMutual` and `MauvilleCity_Text_WattsonWontBeChallenge` have already-changed source reference values that overlap historical damage/repair work. **DO NOT override the protected restorations** without a full ownership model.

The source-build symbol map offers additional candidates but **does not itself prove byte-for-byte shipping symbol layout for unverified categories**. Before authorizing a new relocation, inspect source script opcode/table ownership at the exact reference site, the present guarded ROM's pointer bytes, current allocation, suffix-sharing, and all protections.

## Codebook collision impact

The private `Emerald-Arena-1823-Strings-Patchkit.zip` contains `inferred_v04_codes_v2.json`. Its **141 candidate codepoints have seven collisions**, notably `f` vs `ấ` (0xDA), `w` vs `ằ` (0xEB), `z` vs `ắ` (0xEE); also space vs `þ`, `Ừ` vs `ừ`, `Ơ` vs `Ồ`, and `ì` vs `ỳ`. This is **not a bijective Unicode encoder**. Certain collisions may be unavoidable due to how v0.4 repurposes original font glyph slots.

In the prior static QA's **5,469** source-changed translated entries that retain English bytes at source/candidate addresses, **3,482** English strings contain `f`, `w` and/or `z` (2,141 shipping-attested, 1,341 candidates). They risk broken mixed-script rendering under the repurposed glyphs; the number is **risk exposure, not 3,482 confirmed visually broken live dialogue strings**.

## Next gate

1. Reproduce the latest guarded candidate from a **durable, source-controlled deterministic recipe** (or recover its SHA-locked original bytes) before writing another binary; the previous temporary-only scripts and candidate are not mounted in the current runtime. Merely restoring the old 2,084 ROM would lose already-completed work.
2. Individually validate script opcodes and actual guarded-owner pointers for the **39 candidate distant/table-owned rows plus 2 code-collision rows with nearby owners**. Do not change the two graphic coincidences or two historical-reference conflicts.
3. Preserve original shared source strings so suffix users still work; only relocate authenticated owner calls to pointer-safe FF regions with all four offset alignments checked against existing pointer destinations.
4. Prioritize replacing English source spans containing colliding f/w/z glyph bytes with approved Vietnamese manifest strings; do not attempt to globally remap English letters back without destroying accents.
5. Verify page/line controls and glyph output in an emulator before a user-facing release. Neither a new GBA ROM nor a BPS patch was produced in this resumed turn.

Source manifest coverage remains 17,512/17,512, not installed ROM completeness. Original v0.4 remains rollback.
