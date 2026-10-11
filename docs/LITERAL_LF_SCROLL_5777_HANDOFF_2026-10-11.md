# Pokémon Emerald Arena — 5,777 compiled source labels (2026-10-11)

## Verified results

GitHub Actions [#38115481548](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38115481548) **FULL SUCCESS** from commit `cc4d0bf74592199bb960de71f414fcd5d276ed7d`.

- Verified prior distinct source labels: **5,556**.
- Additive map/NPC source-owned literal-LF text: **221 NEW** labels, in **32** `data/maps/` source files.
- New total: **5,777 source-compiled translations**.
- Exactly 221/221 source-authored newline normalizations and 221/221 native GBA `\\l` scroll reflows.
- English source-control sequence, original Vietnamese word order and `\\p` pagination independently checked.
- Four earlier map stages excluded **2,343** exact source owners; the prior 134 named-player dynamic labels were separately checked and excluded by ownership.
- All 221 additions verified as byte-exact at their own compiled ELF symbol addresses in `pokeemerald.gba`. No guessed pointer writes.
- CI build, strict glyph/source-bank audit, title-credit smoke and workflow PASS.
- The parallel additional PLAYER/RIVAL-only stage accepted **0** new strings after the initial 134, for documented control/encoding reasons; it did not change the compiled 5,556 baseline. Do not count any new dynamic labels.
- A separate earlier isolated literal-LF smoke compiled 175 strings; **these are NOT an additional 175 in the 5,777 total**. They were part of earlier source stages and the new additive build excludes their labels.

## Exact immutable source/font pair (STOCK-font build only)

SHA256 `a812ad75ba3729076c274c3ddca643e1c1eff9ddcedca409e86ebb049ca8fa14`.

| Source font bank | Exact ROM offset |
| --- | --- |
| SmallNarrow | `0x7182AC` |
| Small | `0x7204AC` |
| Narrow | `0x7286AC` |
| Short | `0x7308AC` |
| Normal | `0x738AAC` |

All five source font raster-block SHAs match the clean Arena source font, **not the user's accepted v0.4 Vietnamese appearance**. The SHA and offsets are now added to `tools/graft_v06_pokeblock_safe_fonts.py`, with tests refusing the earlier 5,556 font offsets when the 5,777 SHA is requested. These are only future private-graft *identity guards*, not proof that the final donor visual font works. The graft utility still contains historical generated-small-glyph fallback; **do not treat its output as the user-approved release font**.

ROM source-build linker memory usage: **33,490,484 / 33,554,432 ROM bytes** (~99.81% full; only **63,948 bytes** headroom). Any large additional staging risks linker-space exhaustion. Do not blindly append another thousands of strings without a safe size/layout plan.

## Deferred blockers

The 17,512 source translation manifest entries are authored, but most are not yet integrated into a playable font-correct release. Residual LF candidates include page/control-signature drift, missing native Vietnamese glyphs (notably uppercase accented letters), and ambiguous dynamic controls; they were **rejected**, not silently altered.

The stable user-tested **v0.4** remains the only accepted font appearance and rollback. No private v0.4 donor was loaded into this GitHub source CI build; no user-facing final patch, font/visual QA, title-credit screenshot approval, in-battle, post-battle or save/load validation can be claimed.

Next priorities:
1. Establish explicit safe ROM headroom/integration policy before attempting more bulk source rows.
2. Handle `{STR_VAR_*}`/`{B_*}`/complex C tokens with dedicated engine-backed semantics and visible text-width QA (not generic string substitution).
3. Restore **only approved v0.4 font artwork** via independently SHA-locked *private* font import; reject synthetic raster artifacts or visibly deformed glyphs.
4. Test title → intro → truck → overworld → battle → post-battle → save/load → Arena menus in real mGBA before release.
5. Never publish any full copyrighted ROM in this public repo.
