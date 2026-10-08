# CONTINUE WITH MODEL — Pokémon Emerald Arena Việt hóa

Đọc file này đầu tiên khi mở phiên ChatGPT mới.

## Mục tiêu

Hoàn thiện bản **Pokémon Emerald Arena 0.13.0 Việt hóa có dấu**, giữ nguyên gameplay Arena và không còn tình trạng Anh–Việt xen kẽ ở nội dung người chơi nhìn thấy.

Repo: `ronvotri/VH-GBA-PEA`

## Baseline phải giữ

**v0.4 – Text Cluster Pass**

SHA-256:

`c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`

Nó kế thừa v0.3 đã được người dùng xác nhận:

- logo đầu game ổn;
- intro chạy;
- font Việt có dấu hiển thị;
- battle chạy;
- sau battle đi tiếp được.

v0.4 thêm 462 cluster shared/overlap, không ghi pointer mới. Người dùng đã chơi tiếp tới khu vực sâu hơn và chưa báo regression crash/freeze, nhưng vẫn gặp nhiều câu English.

**Không quay lại Test 1/2/v0.2 làm baseline.**

## Bug/thiếu sót hiện tại

Độ phủ bản dịch còn thiếu. Ví dụ mới nhất người dùng thấy:

> There could be treasures just waiting to be discovered down there.

Yêu cầu của người dùng là **dịch cho xong rồi mới test lớn**, không muốn quy trình “chụp câu nào thì vá câu đó”.

## Dữ liệu phân tích đã có

Shipping Arena:

- size: 33,554,432 bytes;
- SHA-256: `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`;
- SHA-1: `a3247882b469fecb491e2875d45ddc3b4b49e310`.

Text scan:

- 24,916 target theo bộ lọc rộng;
- 20,383 target theo bộ lọc plausible-English chặt.

Đây chỉ là candidate targets, không được mass-repoint.

## Việc phải làm ngay ở phiên mới

**Map/story translation catalog đã hoàn tất 4,361 / 4,361 (100%). Không quay lại dịch 585 câu cũ.**

1. Đọc `translations/map-story/INDEX.md`, `PROGRESS.md`, `docs/TECHNICAL_NOTES.md`.
2. Giữ **v0.4 – Text Cluster Pass** làm baseline.
3. Dùng shipping-verified catalog/source provenance để tích hợp toàn bộ manifest map/story vào ROM:
   - inplace nếu bản dịch vừa allocation;
   - chỉ relocate/repoint đúng reference đã xác minh khi không thể vừa allocation;
   - không mass-repoint.
4. Sau map/story integration, tiếp tục các nhóm user-facing còn lại theo thứ tự:
   - system-text;
   - Arena-only;
   - system/UI và battle text.
5. Build candidate ROM và QA theo tuyến: title → intro → overworld → battle → post-battle → save/load → story/post-game → UI/Arena.
6. Nếu CI đỏ, kiểm tra lỗi thật. Validator đã được sửa để **không đếm `sootopolis.vi.json.gz`** như manifest thứ hai.

## Điều tuyệt đối không làm

- Không quét rồi sửa mọi số giống ROM pointer.
- Không copy nguyên vùng ROM AowVN sang Arena.
- Không dùng Test 1/2/v0.2 làm nền.
- Không ghi vào title graphics/startup nếu không có source provenance.
- Không gọi “hoàn thiện” nếu còn English user-facing.
- Không commit ROM thương mại đầy đủ vào repo.

## Văn phong dịch

Tiếng Việt tự nhiên, dễ đọc, có dấu. Giữ tên riêng/Pokémon phù hợp. Giữ placeholder/control code. Không để câu nửa Anh nửa Việt.

## Câu người dùng có thể gửi để tiếp tục

`Tiếp tục VH-GBA-PEA. Đọc CONTINUE_WITH_MODEL.md và các checkpoint trong repo, kiểm tra workflow arena-map rồi tiếp tục dựng catalog để Việt hóa toàn bộ text còn sót. Dùng v0.4 làm baseline, không vá theo từng ảnh và không mass-repoint.`


## Translation checkpoint (late 2026-10-06)

Technical discovery is sufficiently complete for translation work. **Do not spend another session expanding pointer/font/catalog research unless an actual patch/build QA failure requires it.**

Current completed map/story manifests:
- Littleroot + Route 101 + Oldale: 146
- Route 102 + Petalburg: 112
- Route 103 + Route 104 + Petalburg Woods: 81
- Sootopolis: 155
- **Total: 494**

All were source-catalog driven and passed placeholder / paragraph-control QA. Continue next with **Rustboro City**. Preserve the project rule: v0.4 baseline, no screenshot-by-screenshot patching, no mass-repoint.


## Translation checkpoint — Rustboro to Dewford

Completed after the prior 494-string checkpoint:
- Rustboro City: **177 / 177**
- Route 116 + Rusturf Tunnel: **38 / 38**
- Dewford + Route 106 + Granite Cave: **103 / 103**

Current total complete map/story manifests: **812 strings**.

Continue next with **Route 109 + Slateport City (257 catalog strings)**. Keep translating; do not reopen technical discovery unless patch/build QA exposes an actual blocker.


## Translation checkpoint — Slateport to Verdanturf

New complete manifests after the 812-string checkpoint:
- Route 109 + Slateport: **257 / 257**
- Route 110 + Mauville: **178 / 178**
- Route 110 Trick House: **146 / 146**
- Route 117 + Verdanturf: **55 / 55**

Current total complete map/story manifests: **1,448 strings**.

All batches passed source-level placeholder / paragraph / terminator QA. Continue next with **Route 111 (40) + Route 112 (11)**, then Jagged Pass / Lavaridge. Keep translating; do not reopen technical discovery unless patch/build QA exposes an actual blocker.


## Translation checkpoint — Lavaridge

Current total complete map/story manifests: **1,658 strings**.

Latest complete batches:
- Route 111 + Route 112: **51 / 51**
- Mt. Chimney + Jagged Pass + Lavaridge: **159 / 159**

Next, fill the story segment skipped before Mt. Chimney:
- Route 113: 21
- Fallarbor: 40
- Route 114: 21
- Meteor Falls: 37
- total: **119 strings**

Continue translation directly. No font/pointer/catalog research unless an actual patch/build QA failure blocks progress.


## Translation checkpoint — Fallarbor / Meteor Falls

Latest complete manifest:
- Route 113 + Fallarbor + Route 114 + Meteor Falls: **119 / 119**

Current total complete map/story manifests: **1,777 strings**.

Continue translation directly from the post-Lavaridge / post-Petalburg route coverage. Prefer filling any remaining story gaps before Fortree. Do not reopen font/pointer/catalog research unless an actual patch/build QA failure blocks progress.


## Translation checkpoint — Fortree

Latest complete manifests:
- Route 115 + Route 118 + Route 119 + Weather Institute: **66 / 66**
- Fortree City: **78 / 78**

Current total complete map/story manifests: **1,921 strings**.

Continue next with **Route 120 → Route 121 → Lilycove / Mt. Pyre**. Keep translating directly; no font/pointer/catalog research unless an actual patch/build QA failure blocks progress.


## Translation checkpoint — Lilycove core

Latest complete manifests:
- Route 120 + Route 121 + Mt. Pyre: **92 / 92**
- Lilycove core / Harbor / Motel / houses / Move Deleter / Pokemon Center: **107 / 107**

Current map/story manifest coverage: **2,120 / 4,361 (~48.6%)**.
Remaining map/story: **2,241**.

Lilycove remainder: **163 strings** (Contest Hall/Lobby, Department Store, Museum, Trainer Fan Club).

Continue translation directly. Do not reopen font/pointer/catalog research unless patch/build QA exposes an actual blocker.


## Repository integrity checkpoint — 2026-10-07

Before continuing translation, use `translations/map-story/INDEX.md` as the canonical committed-manifest inventory.

Important repair already completed:
- `route103-route104-petalburgwoods.vi.json`: restored to **81 translations**
- `route110-mauville.vi.json`: restored to **178 translations**

These files had previously been accidentally committed as a file-reference error string. A repo-wide search after repair found no remaining occurrence of that error text.

Current committed map/story coverage remains **2,120 / 4,361 (~48.6%)** across **18 real JSON manifests**. Do not count `sootopolis.vi.json.gz` separately.

Next: Lilycove remainder **163 strings**, then Route 122/123 → Safari Zone / Aqua Hideout / Mossdeep.


## Translation checkpoint — Lilycove complete

Lilycove is now fully covered:
- core / Harbor / Motel / houses / Move Deleter / Center: **107 / 107**
- Contest Hall / Lobby: **53 / 53**
- Department Store: **29 / 29**
- Museum: **43 / 43**
- Trainer Fan Club: **38 / 38**
- total Lilycove: **270 / 270**

Current committed map/story coverage: **2,283 / 4,361 (~52.4%)**.
Remaining map/story: **2,078**.

All 163 newly added strings passed source-level label / placeholder / paragraph / terminator QA.

Continue next with **Route 122 / Route 123 → Safari Zone → Aqua Hideout → Mossdeep**. Use `translations/map-story/INDEX.md` as the canonical inventory and do not reopen technical discovery unless an actual patch/build QA failure blocks progress.


## Translation checkpoint — Mossdeep complete

New complete manifests after Lilycove:
- Route 123: **6 / 6**
- Aqua Hideout: **34 / 34**
- Mossdeep core: **52 / 52**
- Mossdeep Gym: **52 / 52**
- Mossdeep Space Center + Steven: **65 / 65**

Route 122 and Safari Zone have no map-local `.string` entries in this source scope.

Current committed map/story coverage: **2,492 / 4,361 (~57.1%)**.
Remaining map/story: **1,869**.

All 209 newly added strings passed source-level label / placeholder / paragraph / terminator QA.

Continue next with **Route 124/125 + Shoal Cave → Route 126/127/128 → Seafloor Cavern → Route 129/130/131/Sky Pillar**. Use `translations/map-story/INDEX.md` as canonical inventory.


## Translation checkpoint — Pokémon League reached

Latest complete manifests:
- Route 124-131 + Shoal / Seafloor / Sky Pillar: **63 / 63**
- Pacifidlog + Route 132-134: **34 / 34**
- Victory Road: **54 / 54**
- Ever Grande + Elite Four + Champion + Hall of Fame: **36 / 36**

Current committed map/story coverage: **2,679 / 4,361 (~61.4%)**.
Remaining map/story: **1,682**.

Main-story route is now covered by QA-clean manifests through the Pokémon League ending. Continue by auditing the remaining optional/post-game map-story gaps, starting with **New Mauville / Abandoned Ship / Magma Hideout**, then legendary/island/Battle Frontier content. Use `translations/map-story/INDEX.md` as the canonical inventory.


## Translation checkpoint — New Mauville / Abandoned Ship / Magma Hideout

Latest complete manifests:
- New Mauville + Abandoned Ship: **62 / 62**
- Magma Hideout: **56 / 56**

Current committed map/story coverage: **2,797 / 4,361 (~64.1%)**.
Remaining map/story: **1,564**.

Both manifests passed source-level label / placeholder / paragraph / terminator QA.

Continue next by auditing and translating **legendary / sealed / island / post-game gaps**, then Battle Frontier / Battle Tent. Use `translations/map-story/INDEX.md` as the canonical inventory.


## Translation checkpoint — Battle Arena

Latest complete manifests:
- Battle Frontier / Battle Arena: **66 / 66**
- Optional legendary/island local text: **1 / 1**

Current committed map/story coverage: **2,864 / 4,361 (~65.7%)**.
Remaining map/story: **1,497**.

Battle Arena passed source-level label / placeholder / paragraph / terminator QA. Legendary/sealed/island audit found only one map-local string in Faraway Island among the checked Regi/Southern/Birth/Terra/Marine/Navel group.

Continue next with **Battle Dome (113 map-local strings)**, then remaining Battle Frontier facilities. Use `translations/map-story/INDEX.md` as canonical inventory.


## Translation checkpoint — Dome / Factory / Palace

Latest complete QA-clean manifests:
- Battle Dome: **113 / 113**
- Battle Factory: **95 / 95**
- Battle Palace: **67 / 67**

Current committed map/story coverage: **3,139 / 4,361 (~72.0%)**.
Remaining map/story: **1,222**.

Next facilities already inventoried:
- Battle Pike: **97**
- Battle Pyramid: **81**
- Battle Tower: **112**

Continue directly with Pike → Pyramid → Tower. Use `translations/map-story/INDEX.md` as canonical inventory and do not reopen technical discovery unless an actual patch/build QA failure blocks progress.


## Translation checkpoint — Battle Pike

Battle Pike is complete and QA-clean: **97 / 97**.
Current map/story coverage: **3,236 / 4,361 (~74.2%)**; remaining **1,125**.

Continue next with **Battle Pyramid (81)** then **Battle Tower (112)**. Use `translations/map-story/INDEX.md` as canonical inventory.


## Translation checkpoint — Pyramid / Tower

QA-clean:
- Battle Pike: **97 / 97**
- Battle Pyramid: **81 / 81**
- Battle Tower: **112 / 112**

Current map/story coverage: **3,429 / 4,361 (~78.6%)**; remaining **932**.

Continue by auditing/translating remaining Battle Frontier shared lounges/services, Battle Tent leftovers, and optional/post-game map/story gaps. Use `translations/map-story/INDEX.md` as canonical inventory.


## Translation checkpoint — Shared Battle Frontier

QA-clean shared batches: Exchange/Lounges **87**, Outside/Mart **72**, Services/Scott **60**.
Current map/story coverage: **3,648 / 4,361 (~83.7%)**; remaining **713**.

Next: audit the remaining 713 source-map strings exactly, then translate Battle Tent and optional/post-game gaps. Use `translations/map-story/INDEX.md` as canonical inventory.


## FINAL CHAT HANDOFF — 2026-10-07

Use this section as the authoritative resume point for the next chat.

Repo: `ronvotri/VH-GBA-PEA`
Baseline: **v0.4**
Canonical manifest inventory: `translations/map-story/INDEX.md`

Current committed map/story coverage: **3,776 / 4,361 (~86.6%)**
Remaining map/story: **585 strings**

Latest fix/checkpoint:
- `battle-frontier-pyramid-dynamic.vi.json`: **128 / 128**, now `translation-complete-source-qa`.
- Corrected six bad labels from `OneItemsRemaining1..6` to `OneItemRemaining1..6`.
- Re-QA against `data/maps/BattleFrontier_BattlePyramidFloor/scripts.inc`: 0 label/placeholder/`\p`/terminator issues.
- Repo-wide search confirms 0 remaining occurrences of `The requested file reference is not currently visible`.

Already QA-clean at a high level:
- Main story through Pokémon League / Hall of Fame.
- New Mauville, Abandoned Ship, Magma Hideout.
- Battle Frontier Arena, Dome, Factory, Palace, Pike, Pyramid, Tower.
- Shared Battle Frontier exchange/lounge/outside/mart/services/Scott content.
- Optional legendary/island local-text audit represented in manifests.

**Continue next:** identify the exact remaining 585 map/story catalog strings not yet represented by `INDEX.md`, prioritize Battle Tent leftovers + optional/post-game gaps, translate in source-driven batches, QA, push, and update INDEX/PROGRESS/HANDOFF.

Rules unchanged:
- v0.4 baseline.
- No screenshot-by-screenshot patching.
- No mass-repoint.
- Preserve placeholders/control codes.
- Do not reopen font/pointer/catalog research unless a real patch/build QA failure blocks progress.
- Translation manifests are not yet the final patched/tested ROM; ROM patch/pointer-write step remains later.


## AUTHORITATIVE HANDOFF — MAP/STORY 100% — 2026-10-07

Phần này **ghi đè mọi checkpoint map/story cũ ở phía trên**.

Repo: `ronvotri/VH-GBA-PEA`  
Baseline: **v0.4 – Text Cluster Pass**  
Canonical inventory: `translations/map-story/INDEX.md`

### Trạng thái đã chốt

- Source catalog map/story: **4,361**
- Committed canonical translation coverage: **4,361 / 4,361 = 100%**
- Remaining map/story backlog: **0**
- Chưa patch/repoint toàn bộ manifest vào ROM ở bước này.

Checkpoint 585 cuối đã được xử lý toàn bộ:
- Trainer Hill **27**
- S.S. Tidal **48**
- Route 105 / Desert Underpass / Mirage Tower **8**
- Cave of Origin **6**
- Battle Frontier Exchange/Lounges **150**
- misc **5**
- Battle Tower Multi Partner Room **341**
  - regular partners **250**
  - apprentice/shared **91**

Audit:
- `tools/audit_remaining_map_story.py` xuất danh sách authoritative còn thiếu.
- Artifact ngay trước manifest cuối xác nhận **4,270 / 4,361**, còn đúng **91** label và tất cả nằm ở Multi Partner Room.
- Manifest `battle-frontier-multi-partners-apprentices.vi.json` chứa đúng **91** label đó, QA sạch về placeholder order, `\p`, và `$`.
- `battle-frontier-multi-partners-regular.vi.json` chứa **250** partner thường và có assertion source-driven trước commit.
- Không tính `sootopolis.vi.json.gz` hai lần; đây chỉ là convenience duplicate. Validator đã được sửa để bỏ qua `*.json.gz`.

### Việc tiếp theo

**Không dịch lại map/story.** Chuyển sang integration/patch planning:
1. map 4,361 label → shipping ROM offset/reference đã xác minh;
2. ghép tiếng Việt lên **v0.4**;
3. inplace khi an toàn, relocate/repoint có kiểm soát khi cần;
4. build ROM candidate;
5. QA lớn;
6. sau đó xử lý system-text / Arena-only / UI / battle user-facing còn lại.

Luật bất biến:
- v0.4 baseline;
- không screenshot-by-screenshot;
- không mass-repoint;
- không đoán pointer;
- không coi manifest translation-complete là ROM-complete cho tới khi build + QA.


## AUTHORITATIVE HANDOFF — INTEGRATION PLANNER — 2026-10-07

This section is newer than the map/story completion handoff above.

Map/story remains complete: **4,361 / 4,361 (100%)**.

New tooling on `main`:
- `tools/plan_map_story_integration.py`
- workflow step that emits `map-story-integration-plan.json` and `map-story-integration-summary.json`

Safety behavior:
- rejects any map/story coverage other than exactly 4,361 canonical catalog rows;
- rejects duplicate/missing/extra manifest labels;
- only marks a row ready when `shipping_rom_offset` is present and `shipping_match_status` is verified;
- never writes ROM bytes or pointers.

Current blocker for actually producing the next ROM candidate: the clean Arena 0.13.0 ROM and the tested v0.4 baseline binary are not accessible in the current conversation/Library workspace. Continue all source/catalog work normally, but do not fabricate binary offsets or a candidate ROM without those exact files.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT PHASE — 2026-10-07

Current translation coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **131 / 2,319 complete**
- remaining system-text: **2,188**

Shipping provenance is now restored from the exact historical checkpoint and validated in CI #116:
- catalog SHA-256: `20f9f6888b3d50458cfd53b0ac534059925c166fae2e48a6aaff49e14015f845`
- source build SHA-256: `eb1a7dd2b7eaccc4138b5d5d51f244911fc08c01c1ed7189354b033e18fba5ab`
- shipping ROM attested SHA-256: `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`
- verified shipping offsets restored: map/story 4,361; system-text 2,319
- planner result: map/story 4,361 ready at verified shipping offsets

New completed system-text manifests:
- `translations/system-text/core-services-news-events.vi.json`: 62
- `translations/system-text/core-save-pc-items-events.vi.json`: 69

Continue translation from the shipping-verified source catalog. Do not return to map/story unless QA finds a concrete defect. Binary write/repoint remains separate from translation completeness.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 295 / 2,319 — 2026-10-07

Latest completed system-text manifests:
- \`translations/system-text/cable-club.vi.json\`: **82**
- \`translations/system-text/move-tutors.vi.json\`: **41**
- \`translations/system-text/berries.vi.json\`: **41**

Authoritative coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **295 / 2,319 complete**
- remaining system-text: **2,024**

Continue system-text from the shipping-verified catalog. Recommended next bounded groups: Trick House Mechadolls (45), Secret Base Trainers (30), Frontier Brain (28), Contest Painting (27), Pokédex Rating (25), Mauville Man (18), Contest Link (11), furniture checks (7), record mix (2), then the larger contest/match-call/apprentice/TV/trainer blocks. Preserve placeholders/control tokens and do not perform ROM writes or mass-repoint during translation-only passes.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 398 / 2,319 — 2026-10-07

Latest additional completed manifests:
- \`translations/system-text/trick-house-mechadolls.vi.json\`: **45**
- \`translations/system-text/secret-base-trainers.vi.json\`: **30**
- \`translations/system-text/frontier-brain.vi.json\`: **28**

Authoritative coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **398 / 2,319 complete**
- remaining system-text: **1,921**

Recent validated system-text work in this phase:
- Cable Club / Wireless / Union Room: 82
- Move Tutors: 41
- Berries: 41
- Trick House Mechadolls: 45
- Secret Base Trainers: 30
- Frontier Brains: 28

Continue with bounded player-facing groups next: Contest Painting (27), Pokédex Rating (25), Mauville Man (18), Contest Link (11), furniture checks (7), record mix (2), then contest_strings / match_call / apprentice / TV / trainers. Preserve source control-token order and terminators. Translation-only passes must not write ROM bytes or pointers.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 488 / 2,319 — 2026-10-07

Latest completed system-text groups:
- Contest Painting: **27**
- Pokédex Rating: **25**
- Mauville Man / Giddy: **18**
- Contest Link: **11**
- shared furniture inspection: **7**
- Record Mix: **2**

Authoritative coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **488 / 2,319 complete**
- remaining system-text: **1,831**

The small bounded player-facing groups are now cleared. Continue with the larger blocks next: `contest_strings.inc` (200), `match_call.inc` (176), `apprentice.inc` (288), `tv.inc` (336), then `trainers.inc` (831). Preserve exact source label coverage plus placeholder/control-token order. Commit every completed manifest to GitHub `main` immediately; no translation file should exist only outside the repository.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 688 / 2,319 — 2026-10-07

`contest_strings.inc` is now complete: **200 / 200** translated and committed across four 50-string manifests.

Current coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **688 / 2,319 complete**
- remaining system-text: **1,631**

GitHub `main` is the authoritative source. Current system-text directory contains **18 manifests**. The 200 Contest strings have 0 missing/extra labels and 0 placeholder/control-token-order mismatches.

Next large blocks:
1. `match_call.inc`: 176
2. `apprentice.inc`: 288
3. `tv.inc`: 336
4. `trainers.inc`: 831

Commit each completed chunk/manfiest immediately, then update this handoff. Do not leave translations only outside the repository. Translation-only passes must not modify ROM bytes or pointers.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 864 / 2,319 — 2026-10-07

`match_call.inc` is now complete: **176 / 176** translated and committed across four 44-string manifests.

Current coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **864 / 2,319 complete**
- remaining system-text: **1,455**

Match Call QA is clean: 0 missing/extra labels, 0 placeholder/control-token-order mismatches, 0 missing terminators. GitHub `main` remains authoritative.

Next large blocks:
1. `apprentice.inc`: 288
2. `tv.inc`: 336
3. `trainers.inc`: 831

Continue committing each completed source slice to GitHub `main` immediately. Translation-only passes must not modify ROM bytes or pointers.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 944 / 2,319 — 2026-10-07

Latest completed work:
- `match_call.inc`: **176 / 176 complete**, CI #139 PASS.
- `apprentice.inc`: **80 / 288 translated** across `apprentice-01.vi.json` and `apprentice-02.vi.json`.

Authoritative coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **944 / 2,319 complete**
- remaining system-text: **1,375**

Continue `apprentice.inc` from source row 81; **208 Apprentice strings remain**. After Apprentice, continue `tv.inc` (336) then `trainers.inc` (831). GitHub `main` is authoritative; commit each completed source slice immediately. Translation-only passes must not modify ROM bytes or pointers.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 1,152 / 2,319 — 2026-10-08

`apprentice.inc` is now **288 / 288 complete** and committed in eight manifests.

Current coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **1,152 / 2,319 complete**
- remaining system-text: **1,167**

Only two major system-text source blocks remain:
1. `tv.inc`: **336**
2. `trainers.inc`: **831**

GitHub `main` is authoritative. Continue with `tv.inc` first, commit each source slice immediately, then finish `trainers.inc`. Translation-only passes must not modify ROM bytes or pointers.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 1,232 / 2,319 — 2026-10-08

Current translation coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **1,232 / 2,319 complete**
- remaining system-text: **1,087**

`apprentice.inc`: **288 / 288 complete**.
`tv.inc` system-text subset: **80 / 336 translated**, rows 1-80 committed as `tv-01.vi.json` and `tv-02.vi.json`.

Continue `tv.inc` from system-text row **81**. After the remaining 256 TV strings, only `trainers.inc` (831) remains. GitHub `main` is authoritative; commit each completed source slice immediately.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 1,272 / 2,319 — 2026-10-08

Current coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **1,272 / 2,319 complete**
- remaining: **1,047**

Completed major blocks:
- `contest_strings.inc`: 200/200
- `match_call.inc`: 176/176
- `apprentice.inc`: 288/288

Current block:
- `tv.inc` system-text subset: **120 / 336**, continue from row **121**.
- after TV, `trainers.inc`: **831** remains.

GitHub `main` is authoritative. Keep committing each 40-ish source slice immediately.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 1,488 / 2,319 — 2026-10-08

`tv.inc` system-text is now **336 / 336 complete** across nine manifests.

Current coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **1,488 / 2,319 complete**
- remaining system-text: **831**

The only remaining system-text source block is:
- `data/text/trainers.inc`: **831**

Continue trainers from row 1, committing bounded source slices to GitHub `main` immediately. GitHub `main` is authoritative. Preserve exact label coverage, placeholder/control-token order and terminators. No mass repointing or ROM/pointer writes in translation-only passes.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 1,608 / 2,319 — 2026-10-08

`tv.inc` is complete: **336 / 336**.
`trainers.inc` is now **120 / 831** across three 40-string manifests.

Current coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **1,608 / 2,319 complete**
- remaining system-text: **711**

Continue `data/text/trainers.inc` from row **121**. GitHub `main` is authoritative. Keep committing bounded slices immediately and preserve exact source control-token order/terminators.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT 1,928 / 2,319 — 2026-10-08

Current coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **1,928 / 2,319 complete**
- remaining system-text: **391**

`trainers.inc` is **440 / 831** across 11 manifests. Continue from trainer row **441**.

GitHub `main` is authoritative. Keep committing bounded source slices immediately. Preserve exact source labels, placeholder/control-token order and terminators. No ROM/pointer writes in translation-only passes.


## AUTHORITATIVE HANDOFF — SYSTEM-TEXT COMPLETE 2,319 / 2,319 — 2026-10-08

Major completed categories:
- map/story: **4,361 / 4,361**
- Arena-only: **46 / 46**
- system-text: **2,319 / 2,319**

`trainers.inc` is complete: **831 / 831** across 21 manifests (`trainers-01.vi.json` ... `trainers-21.vi.json`).

Do **not** continue searching for untranslated system-text unless a concrete QA defect is found. The next work phase should sweep the remaining user-facing categories:
1. `system-ui`: **8,279 source rows**
2. `battle`: **2,223 source rows**
3. later QA/exclusion review for debug/internal as appropriate

GitHub `main` is authoritative. Continue source-catalog-first, not screenshot-by-screenshot. Preserve placeholders/control codes and do not mass-repoint or write ROM pointers during translation-only passes.


## AUTHORITATIVE HANDOFF — SYSTEM-UI 66 / 8,279 — 2026-10-08

System-text is complete: **2,319 / 2,319**. Do not reopen it without a concrete QA defect.

System-ui work has begun:
- `trainer_class_names.h`: **66 / 66 complete**
- `translations/system-ui/trainer-class-names.vi.json`

System-ui total:
- **66 / 8,279 translated**
- **8,213 remaining**

Continue system-ui source-catalog-first. Good next targets include player-facing text blocks such as abilities, item descriptions, move descriptions, item names, region-map entries, and strings.c. Keep manifests bounded and commit each completed slice immediately to GitHub `main`.


## Canonical Pokémon terminology rule — 2026-10-08

Do **not** translate canonical Pokémon terms used as names/identifiers:
- Pokémon species names
- move names
- item names
- TM/HM names and identifiers

Translate surrounding UI/help/description text, but keep those canonical names exactly in English. This rule is authoritative for all remaining `system-ui` and `battle` work.


## AUTHORITATIVE HANDOFF — SYSTEM-UI 461 / 8,279 — 2026-10-08

System-text remains complete at **2,319 / 2,319**.

System-ui completed/reviewed:
- trainer classes: 66
- abilities: 155
- move descriptions: first 240 named descriptions committed in six 40-string manifests

Canonical terminology rule is mandatory:
- Pokémon names: do not translate
- MOVE names: do not translate
- ITEM names: do not translate
- TM/HM names/IDs: do not translate

Continue `src/data/text/move_descriptions.h` after RAIN DANCE, then item descriptions. Translate prose only; canonical identifiers remain English.


## AUTHORITATIVE HANDOFF — SYSTEM-UI 655 / 8,279 — 2026-10-08

System-text remains complete: **2,319 / 2,319**.

System-ui:
- trainer classes: 66 complete
- abilities: 155 complete/reviewed
- move descriptions: **354 / 354 real descriptions complete**
- item descriptions: **80 / 309 real descriptions translated** (dummy sentinel excluded)

Continue item descriptions after TINY MUSHROOM.

Mandatory canonical terminology:
- do not translate Pokémon names
- do not translate MOVE names
- do not translate ITEM names
- do not translate TM/HM names/IDs
- translate surrounding descriptions/help/UI prose only

GitHub `main` is authoritative.


### Pre-pass GitHub sync — 2026-10-08
Confirmed `main` is synchronized before continuing localization:
- system-text: **2,319 / 2,319**
- system-ui committed: **655 / 8,279**
- move descriptions: **354 / 354 real descriptions complete**
- item descriptions: **80 / 309**
- canonical Pokémon / MOVE / ITEM / TM / HM names remain English


## AUTHORITATIVE HANDOFF — SYSTEM-UI 884 / 8,279 — 2026-10-08

System-text remains complete: **2,319 / 2,319**.

System-ui completed/reviewed:
- trainer classes: 66
- abilities: 155
- move descriptions: 354 / 354 real descriptions
- item descriptions: 309 / 309 real descriptions

Mandatory canonical terminology:
- Pokémon / MOVE / ITEM / TM / HM names and IDs remain English
- translate descriptive/help/UI prose only

Continue with another bounded player-facing system-ui source group. GitHub `main` remains authoritative.


## AUTHORITATIVE HANDOFF — SYSTEM-UI 1,004 / 8,279 — 2026-10-08

Completed player-facing system-ui groups now include:
- trainer classes 66
- abilities 155
- move descriptions 354
- item descriptions 309
- decoration descriptions 120

Next system-ui work should continue source-catalog-first. Mandatory rule remains: Pokémon / MOVE / ITEM / TM / HM names and IDs stay English; translate surrounding prose only.


### Pre-pass GitHub sync — 2026-10-08
Confirmed `main` is synchronized before continuing:
- system-text: **2,319 / 2,319**
- system-ui committed: **1,004 / 8,279**
- move descriptions: **354 / 354**
- item descriptions: **309 / 309**
- decoration descriptions: **120 / 120**
- canonical Pokémon / MOVE / ITEM / TM / HM names remain English


## AUTHORITATIVE HANDOFF — SYSTEM-UI 1,124 / 8,279 — 2026-10-08

Current Pokédex descriptive text progress:
- `src/data/pokemon/pokedex_text.h`: **120 / 387**
- continue from Pokédex row **121**

Completed system-ui groups remain:
- trainer classes 66
- abilities 155
- move descriptions 354
- item descriptions 309
- decoration descriptions 120

Mandatory terminology rule remains unchanged: keep Pokémon / MOVE / ITEM / TM / HM names and IDs in English; translate surrounding prose only.


## AUTHORITATIVE HANDOFF — SYSTEM-UI 1,204 / 8,279 — 2026-10-08

Pokédex descriptive text progress:
- **200 / 387**
- continue from Pokédex row **201**

Five Pokédex manifests are on GitHub `main`; QA confirmed 200 unique labels and correct four-line structure after correcting TENTACOOL.

Completed system-ui groups remain:
- trainer classes 66
- abilities 155
- move descriptions 354
- item descriptions 309
- decoration descriptions 120

Keep canonical Pokémon / MOVE / ITEM / TM / HM names in English.


### Pre-pass GitHub sync — 2026-10-08
Confirmed `main` before continuing Pokédex work:
- system-text: **2,319 / 2,319**
- system-ui checkpoint previously: **1,124 / 8,279**
- Pokédex text now committed through row **160 / 387**
- TENTACOOL layout fix is committed
- canonical Pokémon / MOVE / ITEM / TM / HM names remain English


## AUTHORITATIVE HANDOFF — SYSTEM-UI 1,391 / 8,279 — 2026-10-08

System-text remains complete: **2,319 / 2,319**.

System-ui completed/reviewed:
- trainer classes 66
- abilities 155
- move descriptions 354
- item descriptions 309
- decoration descriptions 120
- Pokédex descriptive text **387 / 387 complete**

Continue with another player-facing system-ui source group. Mandatory rule remains unchanged: Pokémon / MOVE / ITEM / TM / HM names and IDs stay English; translate surrounding prose only.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 1,527 / 8,279 — 2026-10-08

System-text remains complete: **2,319 / 2,319**.

System-ui completed/reviewed now includes:
- trainer classes: 66
- abilities: 155
- move descriptions: 354
- item descriptions: 309
- decoration descriptions: 120
- Pokédex descriptive text: 387
- `src/strings.c` Pokédex search/sort UI block: **64**
- `src/strings.c` Hall of Fame + core Bag/menu block: **72**

Authoritative system-ui coverage:
- **1,527 / 8,279**
- remaining: **6,752**

New manifests:
- `translations/system-ui/strings-pokedex-ui.vi.json`
- `translations/system-ui/strings-hof-bag-core.vi.json`

Source QA against pinned `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`:
- new strings checked: **136**
- missing source labels: **0**
- placeholder/control-token-order mismatches: **0**

Continue `src/strings.c` from **gText_ItemFinderNearby** onward in bounded player-facing slices, then move through other system-ui source groups. Canonical Pokémon / MOVE / ITEM / TM / HM names and IDs remain English. No ROM/pointer writes or mass-repoint during translation-only passes.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 1,599 / 8,279 — 2026-10-08

System-ui continued immediately after the 1,527 checkpoint:
- `translations/system-ui/strings-items-berries-shop-01.vi.json`: **72**
- source slice begins at `gText_ItemFinderNearby` and runs through `gText_Var1AndYouWantedVar2`

Coverage:
- system-ui: **1,599 / 8,279**
- remaining: **6,680**

QA against pinned `src/strings.c`:
- labels: **72 / 72 found**
- missing source labels: **0**
- placeholder/control-token-order mismatches: **0**

Continue `src/strings.c` from the shop dialogue immediately after `gText_Var1AndYouWantedVar2`. Canonical Pokémon / MOVE / ITEM / TM / HM names and identifiers remain English. Translation-only passes still perform no ROM/pointer writes.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 1,800 / 8,279 — 2026-10-08

Continued `src/strings.c` source-driven localization after the 1,599 checkpoint.

New QA-clean manifests in this pass:
- `strings-shop-party-moves-01.vi.json`: **73**
- `strings-party-field-trade-01.vi.json`: **64**
- `strings-summary-egg-decor-01.vi.json`: **64**

Authoritative coverage:
- system-text: **2,319 / 2,319 complete**
- system-ui: **1,800 / 8,279**
- remaining system-ui: **6,479**

Source QA against pinned `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`:
- new strings checked this pass: **201**
- missing source labels: **0**
- placeholder/control-token-order mismatches after fixes: **0**

A first QA pass found three placeholder-order issues in the shop/party batch; these were corrected in commit `53f85fc` before this checkpoint.

Continue `src/strings.c` immediately after `gText_Mat`. Keep canonical Pokémon / MOVE / ITEM / TM / HM names and identifiers in English. Translation-only passes still perform no ROM/pointer writes or mass-repoint.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 1,857 / 8,279 + BATTLE 7 / 2,223 — 2026-10-08

Continued `src/strings.c` after the 1,800 checkpoint, then normalized catalog scope:
- `translations/system-ui/strings-decor-pc-contest-01.vi.json`: 64 source rows processed
- 7 labels whose names contain `battle` were moved from system-ui manifests into `translations/battle/strings-shared-ui-01.vi.json` because `build_source_text_catalog.py` categorizes those rows as `battle`

Authoritative coverage:
- system-text: **2,319 / 2,319 complete**
- system-ui: **1,857 / 8,279**
- battle: **7 / 2,223**
- remaining system-ui: **6,422**
- remaining battle: **2,216**

QA:
- source-driven labels preserved
- placeholder/control-token-order mismatches after fixes: **0**
- catalog scope is now aligned for the moved battle labels

Validator was also hardened: empty translations are accepted only when the catalog source string itself is empty, allowing intentional structural sentinels while still rejecting accidental blank translations.

Continue `src/strings.c` immediately after `gText_TypesOfContests`. Canonical Pokémon / MOVE / ITEM / TM / HM names and IDs remain English. No ROM/pointer writes or mass-repoint in translation-only passes.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 1,918 / 8,279 + BATTLE 10 / 2,223 — 2026-10-08

Latest source-driven `src/strings.c` slice after `gText_TypesOfContests`:
- system-ui: **61** strings in `translations/system-ui/strings-contest-bike-prizes-01.vi.json`
- battle: **3** mode labels added to `translations/battle/strings-shared-ui-01.vi.json`

Authoritative coverage:
- system-text: **2,319 / 2,319 complete**
- system-ui: **1,918 / 8,279**
- battle: **10 / 2,223**
- remaining system-ui: **6,361**
- remaining battle: **2,213**

QA:
- new source labels found: **64 / 64**
- placeholder/control-token-order mismatches: **0**
- category mismatches: **0**

Canonical Pokémon / MOVE / ITEM / TM / HM names and IDs remain English; canonical item names in the prize/vendor slice were intentionally retained. Continue `src/strings.c` immediately after `gText_YellowShard`. No ROM/pointer writes or mass-repoint.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 2,265 / 8,279 + BATTLE 23 / 2,223 — 2026-10-08

Continued the source-driven `src/strings.c` sweep from immediately after `gText_YellowShard`.

New work in this pass:
- `strings-menu-frontier-prizes-01.vi.json`: **70 system-ui**
- `strings-link-frontier-help-01.vi.json`: **63 system-ui**
- `strings-elevator-box-01.vi.json`: **72 system-ui**
- `strings-pc-pokenav-01.vi.json`: **71 system-ui**
- `strings-pokenav-easychat-01.vi.json`: **71 system-ui**
- battle-classified labels added to `translations/battle/strings-shared-ui-01.vi.json`: **13**

This pass processed **360 source rows total**:
- system-ui: **+347**
- battle: **+13**

Authoritative coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **2,319 / 2,319 complete**
- system-ui: **2,265 / 8,279**
- battle: **23 / 2,223**
- remaining system-ui: **6,014**
- remaining battle: **2,200**

QA for all new slices:
- source labels found: **360 / 360**
- placeholder/control-token-order mismatches: **0**
- catalog scope mismatches: **0**
- intentional empty-source sentinels remain empty and validate correctly

Canonical Pokémon / MOVE / ITEM / TM / HM names and identifiers remain English. Canonical item names, TM IDs and proper location names encountered in these slices were intentionally retained.

Continue `src/strings.c` immediately after `gText_AndFillOutTheQuestionnaire`. Translation-only passes still perform no ROM/pointer writes or mass-repoint.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 2,695 / 8,279 + BATTLE 89 / 2,223 — 2026-10-08

Continued the source-driven `src/strings.c` sweep from immediately after `gText_AndFillOutTheQuestionnaire` through `gJPText_Sama`.

New work in this pass:
- `strings-easychat-save-rtc-01.vi.json`: **69 system-ui**
- `strings-roulette-bp-prizes-01.vi.json`: **72 system-ui**
- `strings-trainercard-contest-input-01.vi.json`: **59 system-ui**
- `strings-chat-matchcall-berrycrush-01.vi.json`: **67 system-ui**
- `strings-frontierpass-minigames-01.vi.json`: **38 system-ui**
- `strings-mysterygift-frontier-records-01.vi.json`: **60 system-ui**
- `strings-options-link-event-01.vi.json`: **65 system-ui**
- battle-classified labels added to `translations/battle/strings-shared-ui-01.vi.json`: **66**

This pass processed **496 source rows total**:
- system-ui: **+430**
- battle: **+66**

Authoritative coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **2,319 / 2,319 complete**
- system-ui: **2,695 / 8,279**
- battle: **89 / 2,223**
- remaining system-ui: **5,584**
- remaining battle: **2,134**

QA:
- all seven new system-ui manifests plus current shared battle manifest rechecked against pinned `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`
- missing source labels: **0**
- placeholder/control-token-order mismatches: **0**
- catalog scope mismatches: **0**
- two token-order defects found during the pass (`gJPText_PlayersXPokemon`, `gJPText_UnableConnectWithEReader`) were fixed before this checkpoint
- Frontier facility proper names (BATTLE TOWER/DOME/PALACE/FACTORY/ARENA/PIKE/PYRAMID) are intentionally retained in English for consistency with BATTLE FRONTIER

Continue `src/strings.c` immediately after `gJPText_Sama`. Keep canonical Pokémon / MOVE / ITEM / TM / HM names and identifiers in English. Translation-only passes still perform no ROM/pointer writes or mass-repoint.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 3,071 / 8,279 + BATTLE 96 / 2,223 — 2026-10-08

Continued source-driven localization from immediately after `gJPText_Sama`.

This pass first finished **the remainder of `src/strings.c` through EOF**, then moved to additional player-facing system-ui source files.

New source coverage this pass:
- `strings-diploma-easychat-ladies-01.vi.json`: **71 system-ui**
- `strings-rental-wireless-wonder-01.vi.json`: **72 system-ui**
- `strings-mysterygift-daycare-relearner-01.vi.json`: **70 system-ui**
- `strings-matchcall-weather-final.vi.json`: **55 system-ui**
- `mystery-event-msg.vi.json`: **10 system-ui**
- `text-input-strings.vi.json`: **54 system-ui**
- `map-name-popup-pyramid.vi.json`: **8 system-ui**
- `berry-fix-program.vi.json`: **9 system-ui**
- `mystery-gift-scripts.vi.json`: **1 system-ui**
- `trade-screen-local.vi.json`: **26 system-ui**
- battle-classified additions: **7**

This pass processed **383 source rows total**:
- system-ui: **+376**
- battle: **+7**

Authoritative coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **2,319 / 2,319 complete**
- system-ui: **3,071 / 8,279**
- battle: **96 / 2,223**
- remaining system-ui: **5,208**
- remaining battle: **2,127**

Important state:
- `src/strings.c` is now complete through EOF for this source-driven sweep.
- `src/mystery_event_msg.c` is complete.
- `src/text_input_strings.c` is complete.
- `src/map_name_popup.c` player-facing Pyramid popup strings are complete.
- `src/berry_fix_program.c` is complete.
- `src/mystery_gift_scripts.c` player-facing local string is complete.
- `src/data/trade.h` text definitions are complete for this pass.
- Static/local labels that can collide across files use source identity keys of the form `label@@source_file:line`.

QA:
- missing source labels/identities: **0**
- placeholder/control-token-order mismatches after fixes: **0**
- catalog scope mismatches: **0**
- fixed one Pokédex diploma line-layout mismatch before checkpoint
- all source-identity manifests rechecked against pinned `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`

Next: continue source-catalog-first through another bounded player-facing system-ui source group. Prefer real visible prose/status/menu strings over credits/proper-name-only or formatting-only rows. Canonical Pokémon / MOVE / ITEM / TM / HM names and IDs remain English. No ROM/pointer writes or mass-repoint.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 3,272 / 8,279 + BATTLE 122 / 2,223 — 2026-10-08

After the 3,071 checkpoint, completed the entire player-facing text inventory in `src/data/union_room.h`.

Union Room coverage:
- `union-room-01.vi.json`: **76 system-ui**
- `union-room-02.vi.json`: **70 system-ui**
- `union-room-03.vi.json`: **55 system-ui**
- battle-classified Union Room labels: **26**
- total source rows represented: **227 / 227**

Authoritative coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **2,319 / 2,319 complete**
- system-ui: **3,272 / 8,279**
- battle: **122 / 2,223**
- remaining system-ui: **5,007**
- remaining battle: **2,101**

Current-turn progress from the previous 2,695 checkpoint:
- system-ui: **+577**
- battle: **+33**
- total source rows processed: **610**

QA:
- all 227 Union Room source identities found
- placeholder/control-token-order mismatches after fixes: **0**
- catalog scope mismatches: **0**
- two Trainer Card token-order issues in the final Union Room slice were corrected before this checkpoint
- static/local labels use source identity keys `label@@source_file:line`

Completed/reviewed source groups now also include:
- `src/strings.c` through EOF
- `src/mystery_event_msg.c`
- `src/text_input_strings.c`
- `src/berry_fix_program.c`
- `src/mystery_gift_scripts.c` local player-facing text
- `src/data/trade.h` text definitions
- `src/map_name_popup.c` Battle Pyramid popup labels
- `src/data/union_room.h` **227 / 227**

Next: continue source-catalog-first with another player-facing system-ui group, prioritizing visible prose/status/menu text. Good next candidates include Berry Blender UI and other local `sText_*` sources. Keep Pokémon / MOVE / ITEM / TM / HM names and IDs in English. No ROM/pointer writes or mass-repoint.

## AUTHORITATIVE HANDOFF — SYSTEM-UI 6,020 / 8,279 + BATTLE 191 / 2,223 — 2026-10-08

Continued from the authoritative 3,272 / 122 checkpoint with a broad source-catalog-first player-facing sweep.

This pass added **2,817 represented source rows**:
- system-ui: **+2,748**
- battle: **+69**

Authoritative coverage:
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **2,319 / 2,319 complete**
- system-ui: **6,020 / 8,279**
- battle: **191 / 2,223**
- remaining system-ui: **2,259**
- remaining battle: **2,032**

Important reconciliation:
- a temporary running total of 4,870 shown during the pass was **19 too high** because the 19 standard Ribbon strings were counted twice in arithmetic.
- the corrected total is based on the authoritative 3,272 checkpoint plus exact committed manifest counts.

Completed/reviewed source groups in this pass:
- `src/berry_blender.c`: **39 / 39**
- misc local player-facing/format strings: **18**
- Easy Chat vocabulary:
  - system-ui groups: **942**
  - battle-classified vocabulary: **66**
  - all direct `_()` Easy Chat vocabulary groups represented; MOVE/POKéMON groups contain no direct `_()` rows in their group files and continue to use canonical source lists
- standard Ribbon descriptions: **19**
- gift Ribbon descriptions: **46 system-ui + 1 battle**
- Hoenn landmark names: **42**, intentionally retained canonical English
- Berry descriptions: **86 / 86**
- Pokédex category names in `src/data/pokemon/pokedex_entries.h`: **387 / 387**
- Pokémon species names: **412 / 412**, reviewed and intentionally retained canonical English
- MOVE names: **355 / 355**, reviewed and intentionally retained canonical English
- ITEM names: **377 / 377**, reviewed and intentionally retained canonical English
- Nature names: **25 / 25**, localized with concise Vietnamese labels

QA:
- Pokédex categories: **387 unique / 387 source rows**, 0 missing, 0 duplicate, 0 token mismatch
- species names: **412 / 412**, 0 missing, 0 canonical changes
- MOVE names: **355 / 355**, 0 missing, 0 canonical changes
- ITEM names: **377 / 377**, 0 missing, 0 canonical changes
- Nature names: **25 / 25**, 0 missing
- Easy Chat batches checked source-by-source with 0 missing identities / 0 placeholder-control-token mismatches
- Berry/Ribbon/local batches source-QA clean
- latest confirmed CI through Pokédex category commit `a128f17`: PASS; newer canonical-name/Nature runs were still in progress at checkpoint creation

Terminology decisions remain mandatory:
- Pokémon species / MOVE / ITEM / TM / HM names and IDs remain English
- Ability names remain canonical English, matching `ability-names.vi.json`
- proper Hoenn landmark/facility names remain canonical English unless a concrete existing project convention says otherwise
- descriptive/help/UI prose is translated

No ROM bytes or pointers were modified. No mass-repoint or guessed shipping offset was used.

Next: continue catalog-first through the remaining **2,259 system-ui** rows, prioritizing visible player-facing prose/status/UI over credits or debug-like content. Then continue the remaining battle catalog independently.

