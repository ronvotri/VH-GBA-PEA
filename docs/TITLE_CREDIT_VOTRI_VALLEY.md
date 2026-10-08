# Title-screen Việt hóa credit — Votri Valley (2026-10-09)

**Requested text (exact, with Vietnamese accents):** `Việt hóa bởi Votri Valley`.

## Output

A **separate local v0.4 title-credit test ROM** has been created from the exact already-playable Vietnamese v0.4 Text Cluster Pass. This does **not** mean the 17,512 user-facing source manifests have been integrated, nor is it a v0.5 full localization. Keep original v0.4 untouched as rollback.

| Item | SHA-256 |
| --- | --- |
| Input v0.4 Text Cluster Pass (32 MiB) | `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9` |
| Local v0.4 with credit (32 MiB) | `d101b87d6236e286d5e79e99c76b7df9dae629fa5855a5a8af1b318f2d50f7c0` |
| Locally generated BPS patch, apply **only to input v0.4** | `2046a05405b7822f2c91a511da2b8b815d6860b7d55475918bee28adfc78b859` |

The local patch is **6,468 bytes**; an independent BPS SourceRead/TargetRead round-trip recovered the exact target ROM with all source, target and patch CRC32 checks passing. Neither commercial ROM nor full BPS patch is stored in this public repo. The private test ROM and BPS patch were shared in the chat as downloadable artifacts.

## Presentation and isolated engineering change

The credit is embedded into title **BG2** (the original Pokémon-logo display layer) as small white text with a dark-blue pixel outline. The credit bitmap is 127 x 15 pixels starting at BG2 coordinate (29,124), below the Press Start banner at screen y108 and above the original copyright sprites at y148. **The original logo, copyright and intro are not replaced**. Font was rasterized once into a tiny 1-bit bitmap mask (not distributed as a font file).

Exact pinned source symbol: `gTitleScreenPokemonLogoGfx`. Source file: `src/title_screen.c`. Function: `CB2_InitTitleScreen`. The pre-patch 8bpp 16KiB graphics stream is at ROM offset `0x00EDE690`, has compressed size **5,889** and allocation **5,892**. New graphics need **6,103** compressed bytes, so **in-place overwrite was rejected**.

Safe bounded change on the *exact v0.4 SHA only*:

1. **One explicitly audited literal/reference edit**: change the single source-level title graphics literal at ROM `0x000BF900` from `0x08EDE690` to `0x09FF0700`. Its original target pointer was found at **exactly one ROM location** and was identical in clean and v0.4.
2. Put new LZ77(0x10)-compressed 16KiB 8bpp BG2 graphics (6,103 bytes) in reserved trailing `0xFF` at ROM offset `0x01FF0700`. Source build symbols end earlier near `0x01FF0604`.
3. Replace the compressed BG2 affine 1024-byte tilemap at the original `0x00EE0644` with a verified LZ77 stream of **315 bytes**, within its original 388-byte allocation. Retain the rest of the original tilemap allocation untouched.
4. Reuse **48 formerly transparent graphic tiles**; reset their original tilemap references to transparent tile 0 before using those tile IDs for the added credit. Original Pokémon-logo pixels are checked to remain unchanged.

### Static validation

- Source and output ROM size both **33,554,432 bytes**.
- Output SHA-256 as above.
- Both changed LZ77 streams independently re-decompress to expected graphics and tilemap.
- Original Pokémon logo graphics compressed stream untouched at its old offset.
- Exactly three authorized ranges of ROM differences, totaling **6,329 modified bytes**: four bytes at `0x000BF900`, 302 bytes in the original map compressed stream and 6,023 bytes in trailing reserved graphics space. (Ranges contain unchanged bytes.)
- In the formerly protected startup/title area `[0,0x1F0000)`, **the sole exception is the four-byte title literal at `0x000BF900`**. Prior general title guard no longer reports byte identity; this controlled exception is necessary for added graphics.
- Unrelated pointers touched: **0**. General ROM pointer scanning/repointing: **none**.
- **Not yet emulator-tested** in this environment (no mGBA installed).

### QA needed before making this the official v0.5 build

Run the new test ROM in mGBA: Nintendo/GAME FREAK -> title Pokémon logo -> white credit appears after title settles, accented glyphs legible, original PRESS START / copyright visible, Start -> intro/menu -> save/load -> wild battle -> post-battle overworld. Compare visual placement at native 240x160; check timing/scroll and title fade. Only once the one-line credit passes emulator QA may it be carried into the final full-integration v0.5 build, preserving the custom BG2 resource and the exact pointer correction.

**Do not paste this 4-byte pointer into another ROM revision or use this as permission for mass-repoint.** It applies only to SHA-locked v0.4 and its exact verified title symbol.
