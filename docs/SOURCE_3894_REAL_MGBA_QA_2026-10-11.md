# 3,894-source Vietnamese font + real mGBA inspection — 2026-10-11

## Provenance
- Full-success [GitHub Actions #38078444743](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38078444743) from source/font workflow commit `31ae2af20142a964014bc13f6a9a311760ed53f0`.
- Source ROM (stock fonts) SHA-256 `7bf9b814a415f814c51c2e900638fda8ee9c87b533688d828f4134336e316bd9`; **120 new** individually linked system-text labels, **3,894** total source labels under prior counting convention.
- Experimental source ROM with synthesized 5-bank Vietnamese font SHA-256 `a50742ec495b5c58315660bc6ef31f38bb929297df26ba664f328b1c6f967cd3`.
- 63 accented glyphs × 5 native GBA font styles = 315 glyphs. Audit confirms 8,380 font-only byte changes, stock ASCII and protected Pokémon/Pokéblock slots unchanged.
- CI artifact ID `11680001018`; screenshot evidence in files `SOURCE_3894_MGBA_*.png`, report `SOURCE_3894_MGBA_BOOT_QA.json`. This artifact contains **metadata/screenshots only**, not a ROM.

## Independently inspected CI screenshots
Screenshot files from the exact CI ZIP were viewed, not only trusted as numerical logs:
- `AFTER_16A.png`: first Birch introduction shown in Vietnamese, including `Chào mừng đến với thế giới`.
- `AFTER_24A_SETTLED.png`: `Mọi người gọi ta là giáo sư POKéMON.` clearly visible as Vietnamese game-window text.
- `AFTER_32A.png` and `AFTER_40A.png`: Birch and POKéMON sprite/text progression shown without screen corruption.
- `AFTER_68A.png`, `AFTER_80A.png`, `NAME_START.png`, `NAME_OK.png`: naming UI shows `Tên bạn?`, `Di chuyển / OK / Quay lại`, preserved button icons; test name `AAAAAAA` fits the original seven-character field.
- `AFTER_NAME_2A.png`: rendered `Có/Không` dialog for expanded `Vậy cháu là AAAAAAA?`; `AFTER_NAME_8A.png` shows `Ra là vậy!`.
- `AFTER_NAME_12A.png` shows named character insertion in the Littleroot explanation.
- CI smoke records 46 captured frames/40 distinct visual phases and no early emulator exit. This confirms the tested intro/naming progression, **not** battle, save/load or full story.

## Remaining high-priority runtime evidence
The original `54S` screenshot shows the Pokémon logo against a black background **without the full title UI**; it cannot confirm visibility of `Việt hóa bởi Votri Valley`. Do not claim visible credit from source-level compilation alone. New CI commit [381445ac](https://github.com/ronvotri/VH-GBA-PEA/commit/381445acce5cec6cf2ad2e6706fafa6d25bfe43d) captures settled title frames at 66, 78 and 90 seconds and extends inputs after Birch confirmation through 46 A presses. [Actions #38079805325](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38079805325) was IN PROGRESS when this note was created. Inspect those frames individually before certifying title credit, truck/overworld, or announcing gameplay QA.

Safety: The verified 3,774-source mGBA build and user-tested v0.4 rollback remain untouched. No full commercial ROM is uploaded or released. Source catalog 17,512/17,512 translated/manifested **does not mean all have been compiled into the game**.

## Next batch constraints
Independent stage `SOURCE_SYSTEM_TEXT_SECOND_STAGE.json` applies 120 new source-owned labels in 17 data/text files with 43 safe reflows; many remaining source rows cannot be silently integrated under current codebook because explicit third-line layout (~555 system-text rejections), missing uppercase accented glyphs, or dynamic/control placeholders require dedicated handling. Do not reinterpret a rejected control code as plain text, silently lowercase names, or force raw ROM-pointer scans.
