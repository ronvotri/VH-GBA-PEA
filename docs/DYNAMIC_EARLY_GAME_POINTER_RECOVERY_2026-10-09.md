# Gameplay English/mixed-glyph and cross-map pointer fix — 2026-10-09

## Evidence: user screenshots and root cause

The user reported at the truck/Littleroot opening:

- `MOM: O, ắ’re here, honey!` instead of Vietnamese, with the same character substitution in `How do you like it?` and `This is our new home!`.
- Inside the moving truck a message appeared as `ột chuyện hay` instead of the box's correct text.

**Two root causes**, not isolated spelling mistakes:

1. `LittlerootTown_Text_OurNewHomeLetsGoInside` (shipping verified `0x001FD8E0`) was not installed from the 17,512-row translation manifest because it includes `{PLAYER}`. Its clean English source bytes remained in experimental v5-1823. A remapped Vietnamese glyph byte collides with the old English `w`, visually producing `ắ/ẳ` in words like `we're` or `How`. Fix: encode the full manifest-based Vietnamese using the exact `{PLAYER}` control bytes `FD 01`, not manual replacements of isolated screen text. Also correct `LittlerootTown_Text_WearTheseRunningShoes` (offset `0x001FDA14`).
2. **Confirmed pointer corruption in the user's truck scene.** `InsideOfTruck_Text_BoxPrintedWithMonLogo` is a shipping-verified localized v0.4 text at `0x00251199`; source reference `data/maps/InsideOfTruck/scripts.inc:51` has literal word at `0x00251192`. Exact clean-shipping ROM has expected little-endian word `0x08251199`, while v0.4 and experimental v5-1823 had **`0x0823BF75`**. The wrong address is **one byte inside** the word `một` in `SootopolisCity_House4_Text_AncientTreasuresWaitingInSea`; thus the truck displayed `ột chuyện hay`. This is repaired by restoring the one source-attested literal to `0x08251199`, not by inserting digit `1` into an unrelated sentence.

## Experimental output

| Binary | SHA-256 |
| --- | --- |
| Clean Arena v0.13.0 | `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b` |
| Safe rollback v0.4 | `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9` |
| Input experimental v5 1,823-strings ROM | `ae1e00595ba3d1f193bcdbd8fcff44394b37e582c0a202e7c0c0df97f645d4d0` |
| Output experimental v5 2,084-strings **TEST** ROM | `575515ff66f640e22b77a38d06395ce3e53a9c459c1e34ab6ebd125f12d34859` |
| Exact input → output BPS (30,302 bytes) | `952072c62cfceed81ccb854ae41224444459b864261aa41fdebfd072acba7518` |

261 new strings: **259 manifest-driven dynamic-placeholder strings + 2 reviewed Littleroot/mother dialogues**, all exact-source-verified, in-place, safe-length, original dynamic tokens retained, and no reference into edited interiors. 123 map/story + 138 system-text. This brings the count of uniquely integrated manifest rows in the experimental binary from 1,823 to **2,084** (not 17,512).

58 other candidate dynamic strings were **blocked** after scanning four byte alignments in the exact clean and current ROMs for pointers into their interior. These are not safe to replace without individually recovering references and shared suffix semantics.

Eight specifically verified corrupt source-script pointers restored to their **exact clean-shipping source addresses**, all belonging to unrelated-map misreferences:

| Literal offset | Source label | Wrong -> restored |
| --- | --- | --- |
| `0x00251192` | `InsideOfTruck_Text_BoxPrintedWithMonLogo` | `0x0823BF75` -> `0x08251199` |
| `0x00251D05` | `SSTidalRooms_Text_NaomiIntro` | `0x0823CF97` -> `0x082521BB` |
| `0x00251D09` | `SSTidalRooms_Text_NaomiDefeat` | `0x0823CFF4` -> `0x08252218` |
| `0x00251D0F` | `SSTidalRooms_Text_NaomiPostBattle` | `0x0823D013` -> `0x08252237` |
| `0x00221FE1` | `SlateportCity_Harbor_Text_TradeForDeepSeaScale` | `0x0820D8F1` -> `0x08222B15` |
| `0x00222010` | `SlateportCity_Harbor_Text_HandedScannerToStern` | `0x0820D94A` -> `0x08222B6E` |
| `0x0022202A` | `SlateportCity_Harbor_Text_WhichOneDoYouWant` | `0x0820D926` -> `0x08222B4A` |
| `0x0022203C` | `SlateportCity_Harbor_Text_ThisWillHelpResearch` | `0x0820D970` -> `0x08222B94` |

## Read-only source-wide pointer audit

From the **6,680 shipping-attested original source offsets**, scan exact 32-bit values in all four alignments of clean Arena, and compare their values in v5 at the same original pointer sites.

- **64 source-pointer occurrences differ** in the experimental v5 donor.
- Exactly **8** individually attested cross-map corruptions were repaired in this specific build.
- **56 others are NOT automatically restored.** They include apparent pre-existing relocations into 0x09FFxxxx ROM tail, some legitimate text relocation candidates, and other suspect cross-map references; each needs separate source-level proof.
- Do **not** treat 64 as all errors or perform global pointer rewrite.

## BPS and static QA

- Full ROM size unchanged, 32 MiB.
- BPS independent reconstruction + source/target/patch CRC32: **PASS**.
- 27,797 byte differences, across 1,544 short changed runs; BPS compresses to 30,302 bytes.
- Title startup, existing centered `Việt hóa bởi Votri Valley` credit and previously patched menu reference bytes unchanged.
- No unplanned source span writes; source and output SHA locks PASS.
- **mGBA gameplay/font/line-wrap QA NOT PERFORMED**. This is **test only**; keep exact v0.4 rollback and try title -> truck box -> MOM/Littleroot -> menu -> battle -> return to world, and save/load.

## Available private deliverables

In the conversation artifacts, `Emerald-Arena-v5-TEST-dynamic-pointer-fixes.gba`, `Emerald-Arena-v5-1823-to-2084-dynamic-pointer-repair.bps`, and `Emerald-Arena-2026-10-09-DynamicFix-Patchkit.zip` (scripts, a complete 261-write plan, 64-pointer read-only audit, exact 8-write allowlist, CRC QA) are available. **Do not upload commercial full ROM to public GitHub.** The patchkit itself lives as a chat artifact.

Next engineering priority: validate exact inferred Vietnamese glyphs against emulator and read-only audit the remaining 56 changed source references. Continue translated rows with placeholders, page controls, unknown glyphs, or expanded allocation using source-provenance-aware integration rather than screenshot-by-screenshot binary hacks.
