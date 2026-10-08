# Votri Valley title credit — v3 center correction

Date: 2026-10-09

## User-reported regression

User screenshot of the v2 test ROM shows `Việt hóa bởi Votri Valley` shifted right, approximately screen-center **149.5 px** rather than **120 px** on 240x160 GBA display. The logo's BG2 layer is translated approximately **+29 px in screen X**; v2 erroneously laid out text around BG2 coordinate 121 rather than 92. The actual credit was not centered.

## New v3 corrected test ROM

- **Base:** exact Vietnamese v0.4 Text Cluster Pass ROM, SHA-256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`.
- The separately generated v2 test ROM SHA-256: `77715e8acbbe99b1ba6a074a0560361e86e2c1704d649328af66c344d890a579`.
- **v3-centered test ROM SHA-256:** `82a028ea469b758fb4acf228b1642c773bfa47241f2d51e6cf98541326380c03`.
- **BPS patch v2 → v3 SHA-256:** `42b97d2cf2a4d016cded34e6f7aa916e70f5e887d927ea5c70b5940f55cb714f`, size **6,929 bytes**; independent BPS SourceRead/TargetRead round-trip plus all three CRC32 tests **PASS**.
- Center now laid out at x=92 in BG2 for approximately +29px onscreen offset; actual changed-pixel bounding box in BG2 x=17–166, y=126–137 (midpoint x=91.5), giving **estimated displayed midpoint x=120.5px**.
- Graphics and map LZ77 re-decompress correctly to **16,384** graphic bytes and **1,024** tilemap bytes, respectively; packed length **6,042 gfx bytes**, **305 map bytes**. Only title BG2 tilemap compressed allocation and new title graphics stream differ **between v2 and v3**. The version pointer is unchanged.
- User-visible preview from running emulator **not yet verified**; static-only validation. Test title immediately after game begins and press START/menu/battle after; keep v0.4 as safe rollback.

## Critical localization caveat

This v3 is a *geometry-only correction of the previously shared v2 test build*. It **intentionally preserves all other bytes in v2**, including two imperfect stopgap edits already disclosed: `gText_BirchGirl` currently appears as `Gái` rather than final requested `Nữ`, and one Sootopolis ancient-ruin sentence was temporarily written as Vietnamese without diacritics. **Do not claim v3 is the finished translation or that font is a perfect copy of in-game glyphs.** Restoring approved manifest translations with proper Vietnamese encoding and validating actual runtime references is pending. The full source translation catalog (17,512/17,512) is NOT installed into this gameplay ROM.

## Checkpoint

Local reproducible scripts `patch_votri_title_and_text_v3.py`, `qa_votri_credit_v3.py`, `make_credit_v3_from_v2_bps.py` exist in the temporary chat filesystem and are not copied into public repo. Never commit full ROMs. This document records exact SHA-256 and safety facts so future sessions can reconstruct from the exact uploaded v0.4 and v2, if needed. Pending next engineering work: validated Vietnamese text encoder/graphics, verified runtime references, bounded manifest patch plan, and full gameplay QA.

The title credit should remain `Việt hóa bởi Votri Valley`, centered in 240px screen width, not on the BG2 256px canvas without accounting for affine shift.
