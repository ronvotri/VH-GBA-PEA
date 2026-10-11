# Pokémon Emerald Arena — Experimental source linker packing, 5,777 labels (2026-10-11)

## Important breakthrough: source-owned linker gaps, no ROM pointer guessing

Two initial ELF-uncovered spans from the exact stock-font 5,777-text-source ROM were audited by **FULL PASS** CI [#38131394297](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38131394297):

| Offset start | Offset end (exclusive) | Original gap |
| --- | --- | ---: |
| `0xABE90C` | `0xC00000` | 1,316,596 bytes |
| `0xC98B28` | `0xD00000` | 423,128 bytes |
| | **Total original zero-filled gaps** | **1,739,724 bytes** |

These exact endpoint addresses correspond to the two fixed linker anchors changed by Arena v0.13.0 in `game/native-engine.patch`: `__anim_mon_load_address = 0x8c00000` and `__gfx_load_address = 0x8d00000`. The upstream pinned `pret/pokeemerald` `ld_script.ld` explicitly instructs that the declarations **and their references** may be deleted to get rid of the gaps. No unrelated game source or unknown ROM offsets were modified.

Read-only forensic tool: `tools/audit_rom_internal_gaps.py`. Reject all automatic gap writes; an ELF-uncovered area is not proven free for arbitrary patch insertion.

## Compiler-produced packed trial — FULL PASS

Actions [#38131970183](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38131970183), successful from exact source commit `4c049b7a147c852ee2a80e7de9bacc6a4bc3f99e`.

Experimental tool `tools/compact_arena_linker_gaps.py` removes exactly **two fixed definitions and their matching section references** in `ld_script.ld`, **only in a copy** of the earlier fully attested source build. The project is recompiled/relinked; the linker resolves every source symbol. All labels, GBA text bytes, game assets, native title-credit source and source codebook remain unchanged.

| Metric | Original source linker | Experimental compacted linker |
| --- | ---: | ---: |
| Linker ROM high-water / used span | 33,490,484 B | **31,750,756 B** |
| Contiguous ROM tail headroom | 63,948 B | **1,803,676 B** |
| ELF internal gap count | 2 | **0** |
| Newly available contiguous ROM space | — | **1,739,728 B** |
| Unique source-compiled translation labels | 5,777 | **5,777 (unchanged)** |

Four-byte accounting difference from original gap sum is normal linker alignment/re-layout. Experimental packed **STOCK-font** ROM SHA256: `5f80f5b8f8f18eebb158d500684283fe3cf5ccaf3c09b3bd1e05a4c40524cf1d`. Original source ROM SHA256: `a812ad75ba3729076c274c3ddca643e1c1eff9ddcedca409e86ebb049ca8fa14`.

**Verified by CI**:
- Real GBA .elf/.gba compiled and linked successfully.
- All **2,698** independently source-owned map/NPC/dynamic dialogues byte-for-byte matched unique ELF label addresses in the new compacted GBA ROM.
- All **five** clean stock-font glyph banks retained their original exact graphic hashes and linker addresses:
  SmallNarrow `0x7182AC`, Small `0x7204AC`, Narrow `0x7286AC`, Short `0x7308AC`, Normal `0x738AAC`.
- ELF gap / headroom report byte accounting matched a full 32 MiB GBA capacity; empty internal gaps; at least 1 MiB tail space proved, actually 1,803,676 B.
- New unit tests for exact linker anchor identities and source-owner preservation passed. Whole workflow succeeded.
- The hash/symbol pair is pinned in `tools/graft_v06_pokeblock_safe_fonts.py`, with regression tests refusing other layouts; no font pixels have yet been grafted into the packed source ROM.

CI report names: `SOURCE_5777_ELF_INTERNAL_GAPS.json`, `SOURCE_5777_EXPERIMENTAL_LINKER_PACK_STAGE.json`, `SOURCE_5777_EXPERIMENTAL_PACK_HEADROOM.json`, `SOURCE_5777_EXPERIMENTAL_PACK_GAPS.json`, `SOURCE_5777_EXPERIMENTAL_PACK_FONT_AUDIT.json`, `SOURCE_5777_EXPERIMENTAL_PACK_ATTESTATION.json`.

## Strict release blockers / next work

1. **No playable patch issued.** The packed ROM has not been tested in mGBA, the actual approved v0.4 Vietnamese font has not been imported, and core gameplay/trainer names/battle/HUD/save-load/title-credit appearance are not validated.
2. Source linker compression is **EXPERIMENTAL** until game runtime QA verifies all relocated graphics are displayed correctly, including species animations, sprites, Arena effects and title graphics. The upstream linker instructions are helpful but do not prove Arena custom overlays do not assume fixed positions.
3. **Next translation priority:** now that there is 1.8 MiB room, compile *additional distinct* user-facing strings only through exact source-owner and safe glyph/control-token analysis, with the 5,777 existing labels preserved. Do not inflate the 5,777 metric with the unrelated 17,512 already-authored translation rows.
4. Complex `{STR_VAR_*}`, battle `{B_*}` and unsupported accented uppercase glyphs still require dedicated engine/font analysis. Do not bypass existing source checks or use the distorted synthetic font.
5. Never upload a commercial `.gba` file or private user-owned v0.4 donor ROM to GitHub. Keep accepted stable v0.4 as rollback.

Current canonical handoff: this file; code and reports are sufficient to rerun the experimental source build.
