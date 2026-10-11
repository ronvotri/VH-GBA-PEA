# Emerald Arena — Easy Chat UI blockers, 12/10/2026

Last FULL PASS source-built baseline: **7,134** source labels ([Actions #38161452509](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38161452509)). The manifest has 17,512 authored translations, **not** 17,512 verified in the ROM. The source build still contains five stock English raster font banks, and the visually approved private v0.4 Vietnamese font donor has NOT been safely grafted; no emulator gameplay certification.

## This session

Added `tools/audit_easy_chat_ui_blockers.py` and `tools/tests/test_audit_easy_chat_ui_blockers.py`. This read-only classifier reports, per original C Easy Chat group and exact source-owned label, whether an authored Vietnamese word (a) is longer in Unicode character count than the English original, (b) exceeds the prior 15-cell trial cap, (c) uses unsupported glyphs in the experimental v0.6 codebook, (d) has other incompatible formatting, or (e) is eligible. Counts are **not proven pixel widths**, and do not authorize widening UI boxes. Original spelling/case/diacritics are never changed.

Wired diagnostic into `.github/workflows/arena-map.yml`, producing `artifact/SOURCE_EASY_CHAT_UI_BLOCKERS.json` before the previously verified Easy Chat source-recompile stage. [Current CI #38162619581](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38162619581): tests PASSED as of this checkpoint, full build still running. Until it finishes, **7,134 remains the verified total** and diagnostic counts are not published as confirmed.

Avoid editing or regenerating the approved v0.4 visual font (private donor SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`). Future Easy Chat integration must validate actual UI renderer/pixel widths and match correct font bank, not weaken English-length checks to inflate integrated labels. Preserve `Việt hóa bởi Votri Valley` credit, and run title/intro/maps/battle/Pokédex/Easy Chat/Arena/play-save QA before a public patch.
