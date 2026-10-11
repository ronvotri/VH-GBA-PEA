# Emerald Arena — private v0.4 120-line in-place TEST (2026-10-12)

## Outcome: real donor ROM bytes changed; not a source-built label promotion

The user supplied exact private stable `Emerald-Arena-0.13.0-VietHoa-v0.4-TextCluster-Pass(1).gba`, **33,554,432 bytes**, SHA-256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`, confirmed against the user's `Emerald-Arena-v0.4-audit.txt`.

Read the FULL SUCCESS Actions #38162619581 artifact `arena-0.13.0-symbol-map` (`user-facing-integration-plan.json` and `POKEBLOCK_SAFE_SOURCE_CODEBOOK.json`). Compared exact actual v0.4 bytes at 6,680 shipping-verified source offsets. An intentionally strict one-line, no-control, no-repoint batch has been privately applied **directly to the user-uploaded v0.4 ROM**, not to the 7,134-label stock-font source build.

### Private output identities (not uploaded to GitHub)

- ROM test: `Emerald-Arena-v0.4-120Cau-TEST.gba` SHA-256 `cb82cdcde73a51a61d3bd2b56ec638dee2f3406233417fde71a14a3ce95fd5e5`
- IPS delta: `Emerald-Arena-v0.4-120Cau-TEST.ips` SHA-256 `5ef01cf9f4eb1d9681fadb0b1ec3f529ca4c72703abf5ee6b7f244fa1e081077`
- **120** strict verified exact single-line replacements: **72 map/story, 48 system text**.
- **2,324 text bytes** written (2,129 actual byte differences); 0 pointer writes; unchanged full 32 MiB size.
- Original intro/title region below 0x1F0000 and all five font/width banks compared byte-for-byte unchanged.
- IPS patch was independently replayed onto the v0.4 source and the full ROM SHA-256 matched.
- No emulator/visual/gameplay QA done. **TEST ONLY**.

### Selection invariants

1. Source owner has `ready:verified-shipping-offset` and exact source original English encoded bytes match the **actual uploaded v0.4** at that shipping offset.
2. Both English and authored Vietnamese are **single-line, single-terminator**, with no control tags, page breaks, runtime variables, or special escapes.
3. Author's Vietnamese wording is preserved exactly, no forced accent removal. Encoder uses the same v0.4 donor assignments for `ấ=DA`, `ằ=EB`, `ắ=EE`, `đ=56`, `ì=59`; rejects ambiguous ASCII `f/w/z` in new text, missing glyphs, source owner overlaps and unsupported characters.
4. Replacement fits the exact original byte span and source owner's validated original allocation, with no new pointer. Conservative single-line window <=26 Vietnamese characters.
5. No catalog source owner address lies inside original span. Scanned **all four byte alignments** for potential GBA absolute pointers; rejected every replacement with a pointer to any interior text offset.
6. Binary test compared all changed ROM bytes against the exact intended replacement ranges and forbids non-text changes.

### Resume requirement

- Source build attestation remains **7,134 / 17,512 authored manifest entries**, not 7,254: the extra 120 were applied only to an independent PRIVATE v0.4 donor test ROM, and may overlap existing source compilation.
- Do **not** claim this private ROM is stable, emulator-certified, or a finished localization. Do NOT upload original/test full ROM or proprietary donor glyph art to GitHub.
- Next: user runtime QA on private candidate, resume the source-built integration of remaining 10,378 distinct authored entries, and graft the exact privately approved v0.4 font into a SHA/ELF-paired current source build (requires clean original ROM plus source-built ROM and symbols). Keep old stable v0.4 as rollback.
- Required smoke route: boot/title credit → intro → map → battle → post-battle → save/load → Pokédex → Battle Frontier → Easy Chat, checking diacritics and existing native symbol controls.
