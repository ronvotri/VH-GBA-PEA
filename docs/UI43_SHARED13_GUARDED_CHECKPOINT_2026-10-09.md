# UI + shared-suffix follow-up, exact private test — 2026-10-09

**STATUS:** Internal ROM candidate, STATIC QA ONLY. Do not distribute as final v0.5 or ask the user to test yet. The translation manifest is 17,512/17,512 on GitHub, not 17,512 installed in runtime ROM.

## Exact SHA-locked inputs and output

| ROM / patch | SHA-256 |
|---|---|
| Clean Arena 0.13.0 (32 MiB) | `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b` |
| Original safe v0.4 rollback | `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9` |
| Previous internally guarded recovery ROM | `5ec43ea41192e473939002d3ed809cd84d650e51e583124bd175f7f503dda6b3` |
| Intermediate guarded + 43 new UI lines | `8eed7374d4313f99ad24cfd6205a7597ad4ba4a178e44a88cd24a952ee644f91` |
| New guarded + 43 UI + 13 multi-owner shared-suffix translations | `187993098e11317873043a70751cd9009fc1556a8a46a550f017be233a2ec05e` |
| Previous guarded → new private **BPS**, **3,741 bytes** | `363151649dd389f4aa2217e7b49257da2325860c3cc03be6f8de593ed35e8d02` |

No full copyrighted ROM nor BPS binary committed to the public GitHub repository.

## New actual binary integrations

**43 new `system-ui` lines**, from **59** source-exact candidate strings in `src/strings.c`, after rejecting **16** with an encoded line exceeding conservative 26-byte limit. Candidate requirements before writing:
- Source-build offset `build_rom_offset` read from the pinned `text-catalog.csv` artifact; the exact original English bytes must match **clean shipping, original v0.4, and guarded ROM** at the candidate offset. No global substring/pointer guess.
- Source `gText_*` in `src/strings.c`, nonempty distinct authored Vietnamese in `user-facing-integration-plan.json`; source reference metadata present.
- One or more exact 32-bit original pointer literals pointing to that source string in the *clean* ROM, every occurrence unchanged in guarded ROM; no clean/guarded pointer into the overwritten string interior, no other catalog source symbol start inside and no special or unsupported control.
- Vietnamese single-byte encoding uses prior inferred donor glyph codebook, with exact newline/page/scroll signature; translation **fits existing source string allocation and each line <= 26 encoded bytes**.
- **In-place only: zero new pointer edits for the 43 UI strings.**

Samples: save-file corruption/recovery notices, battery warnings, Pokédex/Pokémon storage warnings, Mystery Gift/News, Wireless/Berry Crush/Link, confirm/cancel and save notifications. These 43 are **additional** to previous experimental integrations; **they were not part of the older 6,680 shipping-checkpoint-attested offsets** and require emulator QA for final approval.

**13 new multi-owner shared-suffix passages** recovered out of previously **58 blocked cases**. Every one has **2–8** original pointer references (total **31** pointer literals), all physically **preceding their text owner within 0x4000 bytes**, source reference metadata and exact unchanged clean/current pointer bytes, and title protected boundary excluded. The original shared English/v0.4 data is preserved for suffix users; Vietnamese text is copied to a **4-byte-aligned FF-only, preexisting-pointer-free** private tail range. Reflowed string length remains below 26 encoded bytes per segment and includes final FF. **1,803** relocated payload bytes used. 45 blocked cases remain: 37 need distant/nonpreceding source-reference ownership research, 6 have pointer sites outside the strict local condition, **2 would have repointed previously restored damaged pointer sites**, so they were explicitly rejected.

### Crucial QA catch

Independent verification of a preliminary 15-case proposed owner relocation **FAILED**, because **two of the planned pointer sites coincided with historical source-reference repairs**. Those two proposals (`VerdanturfTown_BattleTentLobby_Text_AttractionMutual` and `MauvilleCity_Text_WattsonWontBeChallenge`) were **removed and the candidate rebuilt**. On the final output **all 64 historically restored clean-ROM pointer sites remain exactly restored**. This is a safety regression caught before release, not concealed as a PASS.

## Independent static verification of final output

- Five exact input/intermediate/output SHA-256 gates: **PASS**.
- Independently replayed 43 UI text spans and 13 relocation payloads plus 31 owned pointer words to regenerate **all 32 MiB** of final output: **PASS**.
- **3,376 changed bytes** versus previous guarded baseline, all inside the exact allowlist: **PASS**.
- Old startup/title, `Việt hóa bởi Votri Valley` credit, font, v4 menu assets and 212 previous single-owner relocations preserved: **PASS**.
- Original shared text preserved at all new relocation owners: **PASS**.
- No preexisting clean/guarded 32-bit pointer points into the new relocated payloads: **PASS**.
- All **64/64** preexisting historical reference repairs remain correct: **PASS**.
- SourceRead/TargetRead BPS independent round-trip reconstructs exact new ROM; three CRC32 checks: **PASS**.
- **Actual GBA emulator gameplay/font/rendering/line-break/save/battle QA: NOT RUN**, so this is **not release-ready**. Unicode-to-glyph codebook inferred earlier still not visually certified.

## Temporary reproducibility / next steps

Current conversation filesystem contains: `/mnt/data/arena_safe_repair/triage_ui_candidates.py`, `integrate_verified_ui_v7.py`, `relocate_verified_multi_owner_v8.py`, `verify_ui_multi_stage_v8.py`, `ui43-allowlist.json`, `multi-owner-new-allowlist.json`, `ui43-multi15-independent-verify.json`, binary private ROM candidate `Emerald-Arena-v5-GuardedRecovery-UI43-MultiOwner-TEST.gba`, and private BPS `Emerald-Arena-Guarded-to-UI43-Multi15-TEST.bps`. The BPS filename contains the original preliminary `Multi15` label but its **final contents are the verified Multi13 build** (SHA above); do not rely on filename over checksum.

Priority next: (a) verify existing Vietnamese font's actual glyph mapping and GBA text pixel-width/scroll behavior (not just byte count), (b) audit 45 deferred shared-suffix cases and 16 longer UI strings by *source-level* owner and allocation rather than guessing, (c) systematic additional English/battle/Arena label recovery only with provenance; do not call it 17,512 installed strings or send a user-facing ROM until runtime QA is plausible. Keep exact safe v0.4 for rollback.
