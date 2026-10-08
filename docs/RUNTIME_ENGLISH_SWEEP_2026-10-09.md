# Source-driven English leftovers sweep — 2026-10-09

**Objective:** audit all untranslated *in-ROM* English source byte spans systematically; **do not** patch per screenshot, mass-repoint or assume manifest coverage = runtime coverage.

## Provenance and exact inputs

- Authoritative GitHub Actions artifact: `arena-0.13.0-symbol-map` from successful workflow run `37829747129`, containing `user-facing-integration-plan.json` with **17,512** user-facing source rows.
- Earlier read-only audit: `docs/LOCAL_ROM_AUDIT_2026-10-09.md` and its locally generated `candidate-layout-by-source.csv` (attested and byte-exact candidate offsets).
- Clean Arena 0.13.0 SHA-256: `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`.
- **Input** Vietnamese v0.4 SHA-256: `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`.
- **Optional comparison** isolated local title/partial-text v2 SHA-256: `77715e8acbbe99b1ba6a074a0560361e86e2c1704d649328af66c344d890a579`.
- The accompanying private audit ZIP in the chat is `Emerald-Arena-Missing-English-Sweep-2026-10-09.zip`; it contains a runnable Python read-only scanner, all 17,512 source-row classifications in CSV, 4,651 high-priority prose rows in CSV/JSON, summary.json, and extensive samples in README. **No full ROM stored in GitHub.**

## Exact audit results

All 17,512 user-facing catalog rows were cross-referenced with their translation manifest and original/candidate byte state in **v0.4**:

| Bucket | Interpretation | Rows |
| --- | --- | ---: |
| **A** | English source bytes still at previously **shipping-checkpoint-attested** offset; manifest contains Vietnamese different from source; **8+ source words and >=50 source chars** | **3,555** |
| **B** | Same English byte match but only **candidate exact at source-build offset** (requires shipping/runtime reference verification); long text | **1,096** |
| **C** | Remaining shorter English-at-attested-offset source-changed entries | **1,217** |
| **D** | Remaining shorter English-at-candidate-offset source-changed entries | **1,685** |
| **E** | English retained by manifest convention, bytes different at original offset, or source layout unresolved; **not necessarily already translated** | **9,959** |
| **Total** | | **17,512** |

Thus **7,553 source-changed entries retain exact source English bytes at original/candidate offsets** (A+B+C+D); **4,772** are already shipping-offset-attested (A+C) and **2,781** are source-build candidates only (B+D). **4,651** of the 7,553 are longer English prose (A+B). This does **NOT** certify a live reference still points to every offset in the v0.4 build, nor authorize any write.

Source category highlights for long prose:

- `map-story`: A **2,393**.
- `system-text`: A **1,162**.
- `system-ui`: B **747**.
- `battle`: B **349**.
- No counted Arena-only longer strings in A/B; Arena-only still has short/source-canonical/unresolved rows.

Top source files by A+B prose volume (across references and source blocks, not unique dialogues):

- `data/text/trainers.inc`: **573** (A 363, B 210).
- `src/data/pokemon/pokedex_text.h`: **386** (all B).
- `data/text/tv.inc`: **293** (A 249, B 44).
- `data/text/apprentice.inc`: **273** (all A).
- `src/data/union_room.h`: **65** (B).
- `src/strings.c`: **61** (B).

### Important early-story uncovered examples

- `LittlerootTown_Text_OurNewHomeLetsGoInside` at shipping-verified original offset `0x001FD8E0`.
- `OldaleTown_House1_Text_LeftPokemonGoesOutFirst` at `0x002110B3`.
- `PetalburgCity_Text_AreYouRookieTrainer` at `0x001F1AA5`.
- `RustboroCity_Text_WeShortenItToDevon` at `0x001F6463`.
- `SootopolisCity_House4_Text_AncientTreasuresWaitingInSea` at `0x0023BF5F` (user screenshot English; translated source manifest already exists).

Source file audit shows **36** long English-at-offset rows under `data/maps/LittlerootTown`, **10** under `data/maps/OldaleTown`, **66** under `data/maps/PetalburgCity`, **127** under `data/maps/RustboroCity`, when using A/B. These are evidence of remaining English source bytes at documented ROM locations, not proof of runtime source usage for every row.

### User-reported issues remain tracked

- `gText_BirchBoy` and `gText_BirchGirl` come from `src/strings.c:58-59`, read by `src/main_menu.c:457-458`. The source manifest explicitly wants **NAM / NỮ**. `gText_BirchGirl` original source English `GIRL` at unverified build offset `0x006DA94F`. A previous local v2 test replaced that one string with `Gái`, **not the specified NỮ**, and cannot be called complete.
- For `SootopolisCity_House4_Text_AncientTreasuresWaitingInSea`, v0.4 still has full English source at the verified original offset. The previous isolated v2 test replaced it **without accents** via ASCII; this is not the final approved Vietnamese manifest wording. Its full authored translation is present in `translations/map-story` already.
- Title credit requirement remains exact `Việt hóa bởi Votri Valley`; user has requested that its font match the in-game UI style. An earlier v2 changed the title bitmap style, but it has **not** been pixel-matched/validated as the same glyph set, and runtime QA is still pending.

## Safety and next build phase

1. Use per-source file audit rather than chasing individual screenshot strings. Start with A `map-story` and `system-text` in the intro/early story; then A `trainers`, `tv`, `apprentice`.
2. Verify each **actual v0.4 runtime reference** and any shared/overlapped strings; original source byte equality is never sufficient to authorize a write/skip.
3. Recover and verify the **real** Vietnamese v0.4 text encoder, including glyph assets, all tone marks, placeholders, `\\n/\\p/\\l`, terminators, length/word wrap; do not strip accents just to fit allocation.
4. Move on to source-build candidates B/D only after shipping-offset confirmation; unresolved E requires review, and intentionally canonical species/MOVE/ITEM names must remain English per policy.
5. Prepare an explicit bounded in-place/relocation dry-run and regression tests; preserve v0.4 title/battle behavior and the Votri Valley credit when proven safe.
6. Require emulator QA before publishing a new build. **No new ROM writes were made by this sweep; no v0.5 produced.**

**Important:** Manifest coverage **17,512/17,512** is source translation completeness, **not** confirmation the running ROM has no English. This scan is intentionally read-only.
