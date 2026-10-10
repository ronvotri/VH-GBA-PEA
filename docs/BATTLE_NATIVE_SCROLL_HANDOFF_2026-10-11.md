# Pokémon Emerald Arena — next native-scroll battle source trial (2026-10-11)

Current fully CI-passed **stock-font source integration** is **5,299 distinct translation identities**, verified by [Actions #38082880980](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38082880980). The 17,512 entries in translation manifests are *authored translations*, NOT fully integrated runtime coverage.

## New experiment

Commits `709c0b1`, `4a7b8f6`, `8caa453` and [`29f17d4`](https://github.com/ronvotri/VH-GBA-PEA/commit/29f17d4852fe1d25ed6b54ecdbfe3fdf7c403689) enable native GBA `\\l` scrolling for **source-owned, static battle texts** under `data/text/` when the original English control signature exactly matches the original Vietnamese text. Runtime variables, unsupported accented glyphs, changed page breaks and ambiguous text are rejected.

The new CI step forks the 5299-built `arena-native-popup-source-trial` into `battle-scroll-source-trial`, excludes all **196** already installed assembly battle texts with `SOURCE_LEVEL_BATTLE_PILOT.json`, stages at most 1000 additional battle strings, and checks:

- exact source-English token/control signature, original Vietnamese word order and unchanged pagination
- no duplicate compiled battle, system, Birch, or map source label
- compiler-produced GBA and all 5 stock-font bank layout checks
- every translated battle payload byte at its one unambiguous ARM ELF linked ROM address

CI report names: `SOURCE_BATTLE_SCROLL_REFLOW_STAGE.json`, `SOURCE_BATTLE_SCROLL_REFLOW_ATTESTATION.json`, `SOURCE_BATTLE_SCROLL_REFLOW_SHA256.txt`, `SOURCE_BATTLE_SCROLL_REFLOW_FONT.sym`, and `SOURCE_BATTLE_SCROLL_REFLOW_FONT_AUDIT.json`.

**Verified: [Actions #38083932879](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38083932879) FULL SUCCESS.** The report verified exactly **257 NEW static battle messages**, all individually checked at their true compiled ELF/GBA source addresses, bringing the source-built total from **5,299 to 5,556** unique labels. A new dedicated verifier checks prior 196 battle labels, source-owner uniqueness, unchanged pagination/control order and Vietnamese word order. Source-only ROM (stock-font) SHA256 `b3d79575d7fcd27031c9b01dfbc4994493eea499d8f63ee61866ed9a31c980c7`; attested clean font positions SmallNarrow `0x718ADC`, Small `0x720CDC`, Narrow `0x728EDC`, Short `0x7310DC`, Normal `0x7392DC`. No playable ROM, private font graft or in-battle mGBA validation is claimed.

**Font policy:** User rejected the distorted synthesized Vietnamese source glyphs. The earlier v0.4 font is the accepted rendering baseline. New source builds use stock font *for content/linker QA only*, and require a separate exact SHA-locked **private v0.4 donor glyph graft and genuine mGBA battle/menus/save-load QA** before any playable release. No proprietary ROM is uploaded to GitHub. Also leave Arena's tiny ASCII-only 3×5 HUD unchanged until its renderer has independent accented-font support.

Remaining localization scope includes dynamic `{PLAYER}`, `{STR_VAR_1}` and `{B_*}` engine variables, long C messages, Arena tiny HUD and original title credit visibility. The latest verified readable intro/naming mGBA images preceded user's font rejection; those screenshots do **not** certify new typography.
