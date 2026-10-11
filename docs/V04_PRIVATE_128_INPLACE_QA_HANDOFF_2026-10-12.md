# Private v0.4 donor in-place translation experiment — 2026-10-12

This checkpoint records actual edits to the user's verified, privately uploaded v0.4 ROM, separate from the source-compiled branch. **Do not add 128 to the 7,134 compiled-source labels.**

## Verified inputs

- User-uploaded `Emerald-Arena-0.13.0-VietHoa-v0.4-TextCluster-Pass(1).gba` is precisely 33,554,432 bytes.
- SHA-256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`: matches historical v0.4 checkpoint.
- GitHub Actions #38162619581 source-translation artifact supplies 17,512 user-facing plan rows with shipping-verified offsets and an independently compiled **7,134** source-label attestation.
- Its latest 7,134-layout ROM/font information is *metadata only*: 5 stock source font-bank offsets `0x7151E0 / 0x71D3E0 / 0x7255E0 / 0x72D7E0 / 0x7359E0`. The actual newly compiled 7,134 source ROM is not in that public artifact. Do not claim that donor font was grafted onto the source-compiled binary.

## Actual private ROM work performed

Produced a separate, conservative **v0.4-based private QA TEST build** by patching **128 distinct previously-English source strings** at shipping-verified offsets: **72 map-story**, **56 system-text**. Input strings were exact byte matches to shipping-source English. Only simple static single-byte text was admitted: original `\\p/\\n/\\l` control counts preserved, no dynamic tokens, no missing codebook glyph, no line over 26 characters, replacement byte length never exceeded original allocation; every known overlapping source offset and potential ROM pointer into the interior of a candidate source string excluded. Known f/w/z-accent slot collisions excluded; no synthetic font pixels. No string relocation, pointer writes or unverified target guesses.

Independent byte audit:
- **3,237** ROM bytes differ; all are inside the 128 approved original text spans.
- SmallNarrow/Small/Narrow/Short/Normal donor Latin font ranges, title/startup region below `0x1F0000` are **byte-for-byte unchanged**.
- User ROM candidate SHA-256: `d1e9d17670a2e9fe29c6ca8a158172182b9bad47d1177ea28b58014c5750c957`
- Private exact-input BPS1 patch: **4,019 bytes**, SHA-256 `f3cf710706cc0289393c8a2719e16409ee1d30d86effe6cd12e08e43d202c2aa`. BPS round-trip was verified against the input v0.4 ROM with source/target/patch CRC32.
- Generated ROM and BPS were **never committed to GitHub**; remain private conversation artifacts.
- This is an **unverified gameplay QA candidate**, not a public release, not an emulator-tested full Vietnamese ROM, and not a 7,262-source-label compilation.

## Next

1. Real game testing on title/intro/map/NPC/battle/post-battle/save, plus major facilities, prior to any distribution. Check text overflow; rollback is unchanged input v0.4.
2. Continue source-integrated 7,134 track separately; do not conflate it with this private v0.4 in-place pass.
3. For donor glyph graft into a 7,134 source rebuild, require the actual exact compiled ROM, shipping-clean Arena binary, pinned source SHA and symbol map, and no synthesized/distorted font fallback.
4. Build further v0.4 in-place translations only if exact-source byte equality and all controls/pointer-overlap safety gates pass. Preserve Vietnamese content and `Việt hóa bởi Votri Valley` title credit.

