# Pokémon Emerald Arena — Keep the good v0.4 font; finish the game text

## User-approved target
The user personally inspected the **3,894-string debug synthesized-font mGBA screenshots** and rejected the font as distorted/uneven. The earlier Vietnamese **v0.4** font was visually acceptable; the remaining priority is finishing **ALL player-facing texts**, not redesigning that font.

**Do not promote `tools/synthesize_vietnamese_source_fonts.py` outputs to release.** Automatic push builds now skip both 3,774 and 3,894 synthetic-font experiments; they are available only via the explicit manual `experimental_synthetic_font_smoke` workflow_dispatch input for debugging. Historical synthetic-font mGBA smoke runs demonstrate boot mechanics, not typography acceptance.

Use the **local/private v0.4 font donor** with verified SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`. Existing `tools/graft_v06_pokeblock_safe_fonts.py` copies known donor accent glyphs and preserves native Pokémon/Pokéblock/F/W/Z slots; it now accepts the separately source/ELF-attested 3,894 build pair:

- Clean shipping Arena SHA256: `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`
- Compiled 3,894 source (stock-font) SHA256: `7bf9b814a415f814c51c2e900638fda8ee9c87b533688d828f4134336e316bd9`
- Font offsets SmallNarrow `0x71A588`, Small `0x722788`, Narrow `0x72A988`, Short `0x732B88`, Normal `0x73AD88`

Note: **donor-grafting is not identical to blindly copying every old bitmap**: a few locations are intentionally relocated for native code collisions, and missing donor small-font accent slots may need targeted safe synthesis. Inspect real screenshots to confirm artwork. The exact original ROM donors are **not available in this connected GitHub working environment**. Do not publish them, bypass pinned SHA checks, or claim a donor-grafted release ROM was produced.

## Localization scope
Source translation manifests cover **17,512 / 17,512 user-facing catalog entries**, but the latest source-and-linker-verified assembled milestone is **3,894 unique source labels**. These numbers are not interchangeable. A 100% source manifest does **not** mean 100% playable Vietnamese game. No claims about endgame/battles/save-load completeness.

New integration checkpoint:
- Workflow [`b6b40b8`](https://github.com/ronvotri/VH-GBA-PEA/commit/b6b40b83215269dd78312ae7015bfc351fe74f35) adds opt-in **native GBA page-scroll reflow for static system-text**, only after exact source-English page/newline/scroll control verification. It never touches dynamic placeholders, preserves all ordered words and `\\p` page-break count, and rejects unsupported glyphs. This should recover a substantial part of the **555** previously flagged long static system dialogues in a **separate stock-font source compilation** with independent linker byte verification.
- Bugfix [`9ce4f6e`](https://github.com/ronvotri/VH-GBA-PEA/commit/9ce4f6ee5b89b0f7ffd7148c79fa1a3e702f4a6d) corrects only new unit-test raw-string escaping. Do not count added strings until its fresh CI reaches FULL SUCCESS and its `SOURCE_SYSTEM_SCROLL_REFLOW_ATTESTATION.json` is read.

## Remaining scope and rules
After that safe scrolling batch, handle literal LF source normalization, other `data/text/` dynamic placeholders via dedicated engines, special C/battle/status UI fragments, unnamed text/anonymous source owners and Arena-only text; maintain strict pronouns, Pokémon proper names, language context and nonchanging dynamic tokens. Every new stage needs a **cross-batch unique source label audit**, source byte validation, actual GBA ELF-linked payload inspection and corresponding font profile before game testing.

Reject third-party ROM-pointer heuristics; never run a mass pointer rewrite. Protect the known stable v0.4 logo/intro/battle/post-battle baseline. **No complete playable ROM is available yet.**
