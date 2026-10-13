# CLAUDE.md — Pokémon Emerald Arena Vietnamese localization

**Read `docs/CLAUDE_HANDOFF_2026-10-13.md` first.** It is the canonical handoff to continue this repository, including the user-approved v0.4 font, the 17,512 source translations, the independently verified source-build milestone (7,134), the rejected +341 ROM pointer experiment and the open first-battle freeze test gate. Also read `AGENTS.md`, `docs/EMERALD_ARENA_FIRST_BATTLE_TEST_GATE_2026-10-13.md`, `PROGRESS.md` and current main HEAD / latest successful Actions.

## Required way of working

- The user wants **a finished playable Vietnamese patch**, not more small translation demos. All **17,512 catalog user-facing entries are already authored**. Focus on **integration, font mapping, runtime stability and QA**; do not retranslate finished manifests without evidence of editorial mistakes.
- **Never claim that 7,134 source-linked/ELF/GBA-attested strings are 7,134 strings rendered correctly in a completed playable ROM.** All source builds so far retain **stock English glyph raster**. The accepted visual font is in the private **v0.4 Text Cluster Pass donor**, SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`.
- **The first-battle freeze is unresolved.** Before patching more game content, test No$GBA Sound Output enabled and cross-check with mGBA using a real pre-Birch battery save. The +341 relocation experiment is REJECTED, despite passing static audits. No runtime PASS without a real emulator gameplay run.
- Keep `Việt hóa bởi Votri Valley`, naturally translated mother/May dialogue and the **Nam/Nữ** gender picker. Avoid glyph collisions (`f/w/z`), broken accents, undersized HUD fonts, bad line breaks, altered dynamic tokens and English leftovers.
- Do NOT commit or publish any copyrighted full GBA ROM, ROM donor glyph pixels, private save or test candidate to public GitHub. Version only translation manifests, utilities, checksums, safe patch tooling and reports.
- Each batch: read HEAD → understand source owner / correct renderer → modify narrowly → `python -m unittest discover -s tools/tests -p "test_*.py"` → build linked ROM / attestation in Actions → test real gameplay when relevant → checkpoint with actual source count, donor status, test status and CI URL.
- Produce **BPS/IPS patch against user-provided original ROM** with exact source/target SHA and reproducible instructions only after runtime QA. Do not relabel in-progress or failed experimental builds as releases.

## Fast access

- [Canonical transfer brief](docs/CLAUDE_HANDOFF_2026-10-13.md)
- [Current GitHub Actions](https://github.com/ronvotri/VH-GBA-PEA/actions)
- [No$GBA / mGBA first-battle isolation](docs/EMERALD_ARENA_FIRST_BATTLE_TEST_GATE_2026-10-13.md)
- [REJECT +341 rollback](docs/EMERALD_ARENA_2026-10-12_PLUS341_REGRESSION_ROLLBACK.md)
- [Approved v0.4 font/private in-place QA](docs/V04_PRIVATE_128_INPLACE_QA_HANDOFF_2026-10-12.md)

**If the user supplies fresh files or proves a new stable baseline, update the handoff with the exact SHA and emulator results rather than guessing.**
