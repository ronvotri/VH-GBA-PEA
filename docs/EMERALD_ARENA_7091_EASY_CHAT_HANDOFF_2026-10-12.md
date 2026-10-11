# Pokémon Emerald Arena — Easy Chat source-build handoff (12/10/2026)

## Final CI result — 7,134 source labels verified

[GitHub Actions #38161452509](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38161452509) **FULL PASS**. Easy Chat staging added **43 C-owned translated words from 15 source group files** on top of the confirmed 7,091 baseline. The independent ELF symbol and GBA ROM byte audit verifies each new owner and rechecks all 7,091 prior source labels.

- Total: **7,134** distinct source-compiled, verified Vietnamese labels.
- New source-ROM SHA256: `df7e47319aa9c054bd952d39ccb6cef8b2c36eedbc0ae1e7d1422cc558acf5fc`; contiguous ROM tail headroom: **1,816,164 bytes**.
- **373 Easy Chat word candidates** failed the strict rule that Vietnamese must not have more static character cells than the source English word. Many other words require missing uppercase accented glyphs (e.g., `Ư`, `Ó`, `À`, `Ấ`, `Ắ`, `Ọ`). Every rejection remained unchanged; no accents were removed or new art generated.
- Five unchanged English stock-font banks are still present in this experimental ROM. **No v0.4 approved Vietnamese font graft or emulator gameplay QA yet**. Not a playable patch/release.
- The `17,512/17,512` catalog count is authored translation, not a binary installation or visible-release percentage.

## Starting checkpoint

- [GitHub Actions #38159804341](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38159804341) **FULL PASS**: exactly **7,091 source-owned Vietnamese labels** in the experimental source-built ROM, including 137 verified Ability + Match Call C labels added after the previous 6,954. SHA256 `50c51fdcb73a9361fbf771fb9556adbf4de1569ebe9979036e34ee7171febd4d`.
- Source-built ROM still uses the **five original English stock font pixel banks**. The private **v0.4** Vietnamese font was already approved by the user (donor SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`) and is **not** available in the source-built ROM; never synthesize or replace it.
- **17,512 / 17,512** manifest entries have authored Vietnamese but **are not** all integrated/playable. Do not divide 7,091 by 17,512 and call that release coverage or assert a release.

## Work completed in this session

The next source-built branch handles **Easy Chat vocabulary**, not new translation writing.

- `tools/stage_easy_chat_word_groups.py`: only `gEasyChatWord_*` exact C symbols from `src/data/easy_chat/easy_chat_group_*.h` with **original-English source initializer equal byte-for-byte**. Preserves the user's exact original Vietnamese wording and capitalization. Requires NFC, no dynamic/control syntax, max 15 display cells and no more cells than source English. Unknown glyphs are not dropped, replaced or manufactured. No guessing ROM offsets or pointer rewrites.
- `tools/tests/test_stage_easy_chat_word_groups.py`: validates accepted source owner payloads, detects duplicate symbols, missing glyphs, longer UI strings, control characters, wrong C source and original English drift.
- `tools/verify_easy_chat_word_groups.py`: independently re-attests previous **7,091 labels**, recompiles each new word from authored Vietnamese to GBA bytes and verifies unique C ELF symbol address and physical ROM bytes. Requires 5 unchanged stock-font banks and at least 1MiB ROM tail.
- `.github/workflows/arena-map.yml`: isolated `easy-chat-source-trial` copied from verified Ability/Match Call source branch, emits `artifact/SOURCE_EASY_CHAT_WORD_GROUPS_STAGE.json` and `artifact/SOURCE_EASY_CHAT_WORD_GROUPS_ATTESTATION.json`.

**CI gate:** [#38161452509](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38161452509) was in progress when this checkpoint was authored. Python unit tests already **PASS**. **Do not raise 7,091 until this CI FULL PASS and the attestation reports a positive `new_easy_chat_source_labels` count.** If zero, publish zero.

## Safety and next tasks

- A 15-character word cap is conservative for original Easy Chat UI. Long existing Vietnamese phrases are left untouched for future UI-specific review, not shortened automatically.
- The experimental source codebook still lacks many uppercase Vietnamese glyphs. These must be investigated against the *approved* v0.4 visual font and renderer/codebook compatibility, not replaced by arbitrary font art or accent removal.
- Final patch requires source/visual font integration and emulator smoke gameplay: title/credit → intro → NPC → battle → save/load → Pokédex → Ability/Match Call/Easy Chat → Arena HUD.
- Preserve exact title credit **“Việt hóa bởi Votri Valley”** and never commit/share a commercial complete Pokémon GBA ROM to public GitHub.
