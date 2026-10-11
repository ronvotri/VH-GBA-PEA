# AGENTS.md — Pokémon Emerald Arena localization

## Always resume from latest verified state

1. Read the latest `main` commit FIRST, then its newest dated docs/checkpoints and completed GitHub Actions runs. The append-only `CONTINUE_WITH_MODEL.md` may end on an obsolete checkpoint. Never take an old number from memory/handoff as current.
2. Compare counts using the same metric: **authored translation manifest (17,512 entries)** vs **distinct compiler-integrated, ELF/GBA attested source labels** vs **emulator-verified visual/runtime labels** vs **release-ready patch**. These are different.
3. Baseline at authoring of this instruction: **7,134 source-integrated labels** verified by Actions #38161452509; HEAD was `de597634`. Newer counts require actual newer successful CI and attested source/ROM evidence. A pending run is NOT a pass.
4. Any apparent regression in count requires an investigation: stale docs, wrong branch, different metric, actual rollback, or failed CI. Do not silently decrement or redo previously completed translations.
5. On each work session: inspect latest commits, select focused untranslated / unintegrated work, test, and write a new dated checkpoint with before/after numbers, commit, workflow run/status and unresolved blockers. Do not claim a gain until full verification.

## Critical safety and style

- Respect the previously user-approved Vietnamese font v0.4. Current experimental source-compiled ROM still contains STOCK English raster font banks, and an approved v0.4 donor graft and emulator QA are outstanding. Never substitute distorted synthesized fonts.
- Preserve original placeholder/control tokens and text pagination semantics, original Vietnamese word order per page, source owners, UI widths and provenance. No guessed pointers or mass repointing.
- Keep `Việt hóa bởi Votri Valley` on the game title screen.
- Never publish full copyrighted game ROMs or claim the stock-font compiled experiment is playable/completed.
- Test title, intro, map, battle, post-battle, save/load, Pokédex, Easy Chat and Arena before release.

## Reliable resume sources

- Latest known 7,134 FULL PASS: https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38161452509
- Latest audit checkpoint at this writing: `docs/EMERALD_ARENA_EASY_CHAT_UI_AUDIT_HANDOFF_2026-10-12.md`; its newer run #38162619581 was pending when documented, do not automatically promote it.
- Always use newest HEAD and newer FULL PASS attestations if available.
