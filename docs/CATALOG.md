# Source-provenance text catalog

This project does **not** treat pointer-like values found by a whole-ROM scan as safe text references.

The catalog produced by `tools/build_source_text_catalog.py` is built from the pinned Pokémon Emerald source tree after the Emerald Arena 0.13.0 patch/overlay is applied, then joined to the generated `pokeemerald.sym`.

## Output

The `Build Arena symbol map` workflow uploads:

- `pokeemerald.map`
- `pokeemerald.sym`
- `ROM_SHA1.txt`
- `ROM_SHA256.txt`
- `text-catalog.csv`
- `text-catalog.json`
- `text-catalog-summary.json`

Each catalog row records, where available:

- source label;
- source file and line;
- category (`map-story`, `battle`, `system-text`, `system-ui`, `arena-only`, etc.);
- whether the source line is vanilla, Arena-changed, or Arena-added;
- build address / build ROM offset;
- source-level reference sites;
- English source text and control tokens;
- an upper-bound allocation estimate from the next symbol;
- translation and patch strategy fields;
- a separate shipping-ROM offset field.

## Important safety rule

The reproducible source build currently does **not** hash-identically to the released Arena 0.13.0 ROM. Therefore:

- build addresses are provenance hints, not shipping offsets;
- `shipping_rom_offset` remains blank until an exact byte/source alignment proves the location in the released ROM;
- no pointer writes are performed by the catalog builder;
- no mass-repoint operation is allowed;
- long translations may only be repointed through a verified source/reference path.

This keeps v0.4 as the binary baseline while the remaining user-facing English is cataloged systematically instead of being patched screenshot-by-screenshot.

## Known validation example

The previously observed line:

`There could be treasures just waiting to be discovered down there.`

belongs to:

- label: `SootopolisCity_House4_Text_AncientTreasuresWaitingInSea`
- source: `data/maps/SootopolisCity_House4/scripts.inc`
- reference: `SootopolisCity_House4_EventScript_Man`
- build symbol: `0x0823BF5F` in the current source build

The released-ROM offset is intentionally not inferred from that build address until shipping-ROM alignment is proven.


## Shipping resolver

`tools/resolve_shipping_catalog.py` verifies the catalog against a user-supplied clean Arena 0.13.0 ROM. It refuses a ROM whose SHA-256 does not match the known shipping hash and records a shipping offset only when the encoded source string matches byte-for-byte at the build offset.

Current verified coverage on the clean shipping ROM:

- map/story: **4,361 / 4,361 exact**
- system-text: **2,319 / 2,319 exact**

This is stronger evidence than the earlier whole-ROM pointer-candidate scan and is now the preferred provenance path for localization work.
