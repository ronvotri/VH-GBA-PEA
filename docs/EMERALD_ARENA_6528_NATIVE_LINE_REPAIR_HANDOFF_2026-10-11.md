# Pokémon Emerald Arena — source owner page-line repair checkpoint (11/10/2026)

## Kết quả đã xác minh sau khi CI hoàn thành

- **[Actions #38150623105](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38150623105) FULL PASS**, source count **6.528 → 6.648 (+120)**, thêm thoại NPC trong **21 file nguồn**, xác minh mỗi nhãn với ELF symbol và byte trong GBA.
- Sau liên kết lại, **1.552 system + 3.034 map owner cũ** được đối chiếu, tất cả đều PASS. **120** map owner mới cũng PASS; tổng **3.154** map/dialogue nhãn đã có bằng chứng source-owned chính xác.
- Build source ROM SHA256 `19b1edd0168a9005dd8a6d5b08a15259ea6106646316e04f0bf5d1f29d86858a`; vùng trống liền ở cuối ROM **1.812.148 byte**; 5 ngân hàng hình font vẫn là stock tiếng Anh.
- Phần còn lại tại vòng này vẫn chủ yếu bị khóa bởi codebook thiếu glyph (ví dụ `Ồ` 42, `À` 31, `Ô` 11), nhiều biến động trong cùng trang (30) và dynamic core vượt ô chữ tĩnh gốc (41). Không xóa dấu, dời biến bừa hoặc dựng font giả để tăng chỉ số.
- Chưa ghép font v0.4 / chưa chơi thử mGBA, **chưa phát hành**.

## Verified baseline and counting rules

- Last confirmed binary-attested source build is **6,528** distinct Vietnamese source-owned labels ([FULL PASS Actions #38149462164](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38149462164)). This is not the fraction of user-visible screens fully localized.
- The manuscript/translation catalog contains **17,512 of 17,512 authored translated rows**; an authored row is not automatically a unique playable binary label. Do **not** call the game 37% or release-ready based on naïvely dividing these two counts.
- The verified old source has at least 1,552 system plus 3,034 map/dialogue labels byte-matched to compiled GBA addresses.
- **Original v0.4 Vietnamese font** (private user-approved donor SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83f9c8d13480be83f9`) is still the canonical font. Current source-built ROM is **stock English five raster banks**, not a combined playable font+text release.

## New focused work

The previous dynamic-map run admitted **167** new NPC text labels, but its report contained **164** candidates rejected solely at the first validation phase for “native line control signature changed.” Rather than retranslate those sentences, the new file `tools/stage_map_dynamic_page_line_repair.py` and regression tests `tools/tests/test_stage_map_dynamic_page_line_repair.py` examine them page by page.

- Requires identical number/order of `\\p` source page boundaries; fully preserves the authored words and runtime variable sequence within **each** page.
- Allows only **one variable-bearing native source line per page**, so its exact original English static character-cell footprint is a meaningful upper bound. Rewraps other text onto native `\\n/\\l` scroll lines, maximum 12 per page.
- **Does not assume unknown `STR_VAR_1..3` runtime widths**; keeps exact existing `PLAYER/RIVAL/KUN/STR_VAR` engine variable bytes. All variable identity/order changes, unexpected controls, unknown glyphs, long words, ambiguous whitespace and source mismatches must be refused.
- The tool never edits a ROM pointer, never redraws fonts and never changes the Vietnamese content.
- `tools/verify_map_dynamic_page_line_repair.py` re-attests all 6,528 previous source labels plus every accepted new map owner **at its real ELF/GBA address**, verifying all five stock raster banks and minimum 1 MiB ROM contiguous headroom.
- The isolated `map-native-line-repair-source-trial` stage was added to `.github/workflows/arena-map.yml` **after** the verified 6,528-source map stage. Report: `artifact/SOURCE_MAP_DYNAMIC_PAGE_LINE_REPAIR_ATTESTATION.json`.

## Current CI and follow-up

[Actions #38150623105](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38150623105) was **in progress** when this checkpoint was written; **new unit tests passed**, but compiler/ROM byte verification had not yet completed. Read the field `new_page_local_map_dynamic_labels`. Only if it is **positive and FULL PASS** may the verified 6,528 source count be increased; zero remains zero.

### Font/blocker audit

CI #38149462164 also **FULL PASS** after fixing the diagnostic to distinguish non-terminated C/UI strings from `.inc` GBA text strings. The read-only diagnostic found **4,726 source-plan rows affected by an unsupported character or special text-format condition**, across **141 distinct currently unsupported Unicode characters** in the experimental 137-entry codebook. This **does not** mean 4,726 playable ROM strings are unusable, nor that the approved v0.4 font is bad; it reveals where direct source integration requires separately proven codebook/glyph compatibility. High-impact missing characters include `Ồ`, `Ô`, `À`, `Ư`. Never substitute no-accent text or synthetic font bitmaps to inflate coverage.

Future tasks: finish source/ROM checks; investigate all category-appropriate encoding/renderer paths (dialogue vs C/UI/Battle/Arena miniature HUD), and import original approved v0.4 glyph art only via verified private geometry+code mapping. No copyrighted ROMs in public GitHub. Preserve intro credit `Việt hóa bởi Votri Valley`, then exercise actual gameplay title → map → battle → save/load → Arena menus before shipping.
