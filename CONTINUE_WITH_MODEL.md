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



## AUTHORITATIVE HANDOFF — ALL USER-FACING CATALOG COVERAGE COMPLETE — 2026-10-09

Corrected source catalog totals (17,513 rows total):
- map/story: **4,361 / 4,361 complete**
- Arena-only: **46 / 46 complete**
- system-text: **2,319 / 2,319 complete**
- system-ui: **8,563 / 8,563 complete**
- battle: **2,223 / 2,223 covered by manifests**
- debug-internal: **0 / 1 intentionally excluded** — `data/scripts/test_signpost.inc` test signpost only

Therefore all user-facing categories represent **17,512 / 17,512 catalog rows**. The sole catalog row outside coverage is the explicit debug/internal test signpost and is not shipping localization work.

Final reconciliation sequence:
- authoritative CI run `37821907688` passed with battle **2,116 / 2,223**, leaving exactly **107** battle rows:
  - `data/text/match_call.inc`: **42**
  - `data/text/tv.inc`: **65**
- `translations/battle/match-call-frontier-final.vi.json`: **42 / 42**, source-QA clean
- `translations/battle/tv-battle-final-01.vi.json`: **32 / 32**, source-QA clean after one placeholder-order correction
- `translations/battle/tv-battle-final-02.vi.json`: **33 / 33**, source-QA clean
- exact final missing-set arithmetic: **2,116 + 107 = 2,223 / 2,223 battle**

Large battle groups also completed and source-QA clean:
- `src/battle_message.c`: **541 / 541** catalog rows, 0 duplicate, 0 missing, 0 token mismatch
- `data/text/trainers.inc`: **311 / 311 battle rows**, 0 duplicate, 0 token mismatch
- remaining Frontier / Trainer Hill / Apprentice / Battle Tent / Battle Dome / Cable Club / Battle Count / Ability rows were completed in the intervening PASS commits before run `37821907688`.

System-ui final authoritative CI confirmation already PASSed at **8,563 / 8,563** with 0 unresolved manifest keys and 0 duplicate catalog rows.

Safety/terminology remain unchanged:
- canonical Pokémon species / MOVE / ITEM / TM / HM names and IDs remain English
- facility/proper names are retained where established by project convention
- translation-only work performed **no ROM writes, no pointer writes, no guessed shipping offsets, no mass-repoint**
- map/story shipping layout remains verified for the exact corrected catalog hash and source-build hash checkpoint

Final GitHub Actions runs for the last 107 battle rows were still in progress when this checkpoint text was prepared. Recheck the newest workflow before claiming final CI PASS in a future session. If PASS, do **not** reopen translation coverage; move to integration/build/test planning and runtime QA instead.


## FINAL CI CONFIRMATION — USER-FACING TRANSLATION PHASE COMPLETE — 2026-10-09

GitHub Actions run **37824308095** completed **SUCCESS** after the final TV battle manifests.

Authoritative coverage audit:
- catalog entries: **17,513**
- represented rows: **17,512**
- unresolved manifest keys: **0**
- duplicate catalog rows represented: **0**
- Arena-only: **46 / 46**
- battle: **2,223 / 2,223**
- map/story: **4,361 / 4,361**
- system-text: **2,319 / 2,319**
- system-ui: **8,563 / 8,563**
- debug-internal: **0 / 1**, intentionally excluded test signpost at `data/scripts/test_signpost.inc`

Therefore the source/manifest translation phase is complete for **all 17,512 user-facing catalog rows**. Do not resume broad translation sweeps unless runtime QA proves a concrete defect.

Next phase: safe ROM integration.
- Existing verified shipping offsets: **6,680 / 17,512** user-facing rows (map/story 4,361 + system-text 2,319).
- Still needs shipping-layout verification before any binary write: **10,832** rows (Arena-only 46 + system-ui 8,563 + battle 2,223).
- `tools/plan_user_facing_integration.py` and the corresponding CI step were added to make this readiness split explicit without modifying a ROM.
- Clean shipping Arena 0.13.0 and v0.4 baseline are not currently available in the active file surface, so no attempt was made to resolve those 10,832 offsets or write the ROM.
- Safety remains: **0 guessed offsets, 0 pointer writes, 0 mass-repoint**.

## INTEGRATION ENGINEERING HANDOFF — 2026-10-09 — NO ROM WRITES

The user-facing source translation phase is already COMPLETE (17,512/17,512 source catalog entries). Do not resume translations or count raw English source-identical entries as already patched in v0.4.

New safe-integration groundwork committed to GitHub `main`:
- `tools/plan_user_facing_integration.py`: source text equality classification (`source-identical` / `source-changed`), category/scope mismatch rejection, explicit `v04_baseline_byte_comparison=unresolved`, `is_safe_to_skip_binary_write=false`, no binary action authorization.
- `tools/tests/test_plan_user_facing_integration.py`: regression tests for no-op assumptions, scope mismatch and duplicates.
- `tools/verify_local_rom_baselines.py`: read-only SHA-256-locked checks for the clean shipping Arena ROM and Vietnamese v0.4, optional v0.3 protected-title/startup comparison.
- `tools/tests/test_verify_local_rom_baselines.py`: fail-closed hash and binary-diff helper tests.
- `tools/audit_v04_verified_offsets.py`: read-only clean-versus-v0.4 byte comparisons only at shipping-verified catalog positions; NEVER authorizes skipping/writing and NEVER verifies runtime pointers.
- `tools/tests/test_audit_v04_verified_offsets.py`: regression tests. A first test fixture accidentally used a longer fake string and failed CI; fixed with same-length corruption at commit `266ac2c`. Run `37827836450` passed the `Test integration planner safety` step after this fix; overall workflow was still running at this handoff.
- `.github/workflows/arena-map.yml`: runs these safety unit tests before source build and publishes integration-readiness details to GitHub Actions step summary.
- `docs/SAFE_ROM_INTEGRATION.md`: exact local preflight/audit commands and runtime QA matrix. `README.md` links this guide.

Authoritative integration planner CI run `37827126689` PASS:
- source text changed: **13,097**
- source text identical to English: **4,415** (NOT yet verified no-ops on v0.4)
- shipping offsets already verified: **6,680**, consisting of **6,557 changed** + **123 source-identical**
- shipping offsets unresolved: **10,832**, consisting of **6,540 changed** + **4,292 source-identical**
- v0.4 byte comparisons actually completed in CI: **0**
- automatically safe to skip ROM writes: **0**
- source/manifest coverage: **17,512 / 17,512**
- ROM writes: **0**, pointer writes: **0**, mass-repoint: **false**

Binary inputs are not available in current active file surface; no generated patched GBA exists for this handoff. Do not upload copyrighted ROMs into the public GitHub repo.

NEXT:
1. Check most recent workflow status; unit test step PASS on `37827836450`.
2. With the exact private clean shipping Arena 0.13.0 ROM and Vietnamese v0.4 ROM accessible, run `verify_local_rom_baselines.py`.
3. Use the latest workflow's `arena-0.13.0-symbol-map` artifact and pinned pret charmap with `audit_v04_verified_offsets.py`, strictly read-only.
4. Resolve remaining shipping layout/reference sites against exact clean binary and verify actual v0.4 pointers/encoder. Only then consider a bounded patch dry-run and actual ROM build.
5. Regression-test title/intro/overworld/battle/post-battle/save/load, glyphs and UI before distributing any v0.5 build.

Safety: NEVER mass-repoint; NEVER infer shipping offsets from build symbols alone; source-identical is not by itself v0.4 byte-identical. Keep v0.4 as baseline.


## RESUME CHECKPOINT — 2026-10-09 — INTEGRATION PLANNER FAIL-CLOSED HARDENING

Translation source/manifest coverage remains **17,512 / 17,512 user-facing**; **no new ROM was generated**. Preserve v0.4 and the exact baseline SHA-256 gate. Do not return to translation sweeps or re-run mass-repoint.

Two new main-branch commits:
- `b3cb8a3`: `tools/plan_user_facing_integration.py` now refuses duplicate source-catalog identities before building the identity lookup (previously dict creation could silently collapse an accidental duplicate). It also labels a `verified:` shipping offset as blocked if the address is malformed or outside the 32 MiB ROM range, instead of counting it as ready.
- `fb23ce2`: Adds regression tests for duplicate source-catalog identities, malformed verified offsets, and out-of-range verified offsets.

GitHub Actions run `37829747129`: **Test integration planner safety = SUCCESS**; the full Arena source build was still in progress when checked. Recheck the full run before reporting full CI success.

Current integration readiness remains source/manifest complete but binary blocked:
- 6,680 shipping offsets had been attested by prior checkpoint, pending actual v0.4 byte/reference verification.
- 10,832 shipping offsets remain unresolved for Arena-only/system-ui/battle.
- No private clean shipping Arena 0.13.0 ROM or v0.4 ROM currently accessible to this chat's binary runtime, and no user ROM is stored in the public repository.

Next: once the exact private clean and v0.4 ROM inputs are available, run the read-only hash preflight and shipping-offset byte audit from `docs/SAFE_ROM_INTEGRATION.md`, then verify v0.4 reference integrity/encoding/overlap before proposing a bounded dry-run. No speculative writes.


## LOCAL ROM INPUTS + READ-ONLY BINARY AUDIT — 2026-10-09

Clean Arena 0.13.0, Vietnamese v0.4, and AowVN donor ROMs were supplied locally and verified by SHA-256. **Do not upload these ROMs to public GitHub.** Exact hashes and source-catalog analysis: [docs/LOCAL_ROM_AUDIT_2026-10-09.md](docs/LOCAL_ROM_AUDIT_2026-10-09.md).

- Source translation manifest coverage remains **17,512/17,512**, not yet applied to a playable new ROM.
- Previous shipping offset checkpoint: **6,680**. Local clean-v0.4 source span audit found **4,893 byte-identical** and **1,787 byte-different** at the original offset.
- Of **10,832** previously unresolved, local restricted-English-charmap subset found **7,024 additional byte-exact build-offset CANDIDATES** against exact clean shipping ROM. These are **NOT verified runtime references and DO NOT authorize writes or skips**. **3,808** remain unresolved by this subset, including **3,686** without build offsets.
- Across the 13,704 located spans, **7,553** source-changed translations still have clean English bytes at the original v0.4 offset; **89** source-identical manifest rows have differing v0.4 bytes at the original offset. Neither figure proves what runtime currently displays because references might differ.
- Protected startup/title `[0, 0x1F0000)` clean-v0.4 bytes are identical; no new ROM/pointer writes made.
- AowVN donor byte matches: **1,695** of **1,787** changed checkpoint source spans (terminated strings of >=12 bytes). Byte match alone is not rendering or translation QA.
- New read-only reproducible CLI: `tools/audit_local_rom_source_byte_candidates.py`, uses full pinned pret charmap, with `tools/tests/test_audit_local_rom_source_byte_candidates.py`. This was committed after the exploratory audit; GitHub Actions `Test integration planner safety` step has passed; recheck the final full-run conclusion before reporting CI fully PASS.
- Local user-facing audit ZIP was generated in the chat containing 17,512 CSV rows, JSON summary and README (not committed to repo). Reconstruct with new CLI and actual private ROM inputs if local copy is unavailable.

NEXT: use full pinned charmap for latest exact-byte candidate audit, verify actual shipping and v0.4 references, Vietnamese v0.4 encoding/font/control tokens, allocation/overlap and guarded dry-run. No speculative new v0.5 GBA; v0.4 stays the rollback baseline.


## TITLE CREDIT CHECKPOINT — 2026-10-09 — VOTRI VALLEY

User explicitly requested **one new line on the Pokémon Emerald Arena logo/title screen**, exact string: **`Việt hóa bởi Votri Valley`**.

A separate **v0.4 + title credit** local ROM and a verified **6,468-byte BPS patch** were produced from hash-locked original v0.4. This is *not* an integrated v0.5. Full details, exact input/output/BPS hashes, ROM offsets, controlled one-title-pointer exception, LZ77 QA, and pending emulator QA: **`docs/TITLE_CREDIT_VOTRI_VALLEY.md`** (commit `5e29461`).

Important: Previous safety rule against changing startup/title remains active for all other modifications. The title credit has **one intentional, source-verified pointer literal change** at `0x000BF900` to relocate only the BG2 logo graphics; it also modifies only the compressed title tilemap at `0x00EE0644` and new graphic data at trailing ROM offset `0x01FF0700`. Original v0.4 ROM is preserved.

The generated local binary is currently **static QA verified but not emulator-runtime verified**. Obtain the original v0.4 ROM and saved private patch/builder for future sessions if necessary. **Do not commit a copyrighted full ROM to GitHub.** Preserve this explicit title credit requirement when implementing final full-translation integration.

Translation source/manifest coverage remains **17,512 / 17,512**, but live runtime integration is still pending.


## SOURCE-DRIVEN ENGLISH RUNTIME BACKLOG — 2026-10-09

A new full-catalog read-only English leftovers audit has been completed from the exact clean Arena 0.13.0 ROM, Vietnamese v0.4 donor, local v2 title-credit prototype, and pinned GitHub Actions artifact `arena-0.13.0-symbol-map` (workflow `37829747129`). See **[docs/RUNTIME_ENGLISH_SWEEP_2026-10-09.md](docs/RUNTIME_ENGLISH_SWEEP_2026-10-09.md)** for all counts, example source strings and exact safety qualifiers.

**All 17,512 user-facing rows were classified** by source-manifest translation difference and v0.4 byte state. Among source-changed rows, **7,553** retain clean English source bytes at original/candidate offset: **4,772** with shipping-checkpoint-attested original offset and **2,781** at source-build byte-exact offset candidate only. Of the 7,553, **4,651 are longer text** (3,555 attested + 1,096 candidates). The full private sweep ZIP in this chat includes two filterable UTF-8 CSVs, a JSON summary, 4,651 priority prose JSON rows, README and reproducible read-only audit script. **Do not interpret original-offset byte state as definitive runtime pointer or translation status.**

High-volume missing prose source files: `data/text/trainers.inc` (573), `src/data/pokemon/pokedex_text.h` (386), `data/text/tv.inc` (293), `data/text/apprentice.inc` (273). Also dozens of early-game story dialogues. Specific user reports are reproduced by source evidence: `SootopolisCity_House4_Text_AncientTreasuresWaitingInSea` English in v0.4 at verified offset `0x0023BF5F`; `gText_BirchGirl` English in v0.4 at source-build candidate offset `0x006DA94F`, manifest wants `NỮ`.

**Important correction:** Earlier v2 prototype changed `GIRL` to `Gái`, not `NỮ`, and rewrote the Sootopolis dialogue **without diacritics**. Do not treat those isolated edits as complete/approved. The title credit style is still not an exact clone of the in-game UI glyphs. The current sweep generated **no ROM/pointer writes** and no new v0.5. The next required step is bounded reference verification and recovery of the actual Vietnamese text encoding/accents and allocated spans; preserve v0.4 rollback safety.


## TITLE CREDIT V3 — USER SCREENSHOT RE-CENTER FIX — 2026-10-09

User reported that the v2 title credit was shifted right on actual GBA screen. Root cause: screen BG2 translated ~+29px, but credit bitmap had been centered on BG2 x=121 instead of x=92. A v3 title-only-geometry adjustment now centers the pixel bounding box around **screen x=120.5px** (240px GBA width; screen center 120). Static LZ77/byte-range/BPS CRC round-trip checks PASS; runtime emulator has not been tested. Exact SHA/checks and BPS v2→v3: [docs/TITLE_CREDIT_CENTER_FIX_V3.md](docs/TITLE_CREDIT_CENTER_FIX_V3.md), commit `bed5ecd`.

**Important**: v3 preserves v2's other text edits, including unfinished `Gái` instead of `Nữ` and unaccented temporary Sootopolis line. No broad English-dialogue integration was done here. Actual translated source coverage 17,512/17,512 is still not runtime ROM integration. Continue safe source-provenance, Vietnamese encoder, reference validation and gameplay QA instead of screenshot-by-screenshot patching. Keep unchanged v0.4 baseline for rollback.


## IN-PLACE SOURCE MANIFEST INTEGRATION TEST — 1,823 ROWS — 2026-10-09

User asked to continue broad English-to-Vietnamese integration, not screenshot-by-screenshot fixes. This session produced an actual **experimental 32 MiB patched GBA** (not a final v0.5) plus BPS, from exact v4 menu/title donor. Comprehensive engineering checkpoint: **[docs/LOCAL_BINARY_INTEGRATION_1823_2026-10-09.md](docs/LOCAL_BINARY_INTEGRATION_1823_2026-10-09.md)**.

Exact hashes:
- input v4 menu/title donor: `ee82c588a960bcb59466ea950fb6a6a1ce1ab94ada62c6b9f8fceaa8dd0d47c3`
- output test ROM: `ae1e00595ba3d1f193bcdbd8fcff44394b37e582c0a202e7c0c0df97f645d4d0`
- v4→test BPS patch (142,034 bytes): `14896804c7295189cb26183d9b5fcf7fce86aa67160105bcf25482eff810eee3`

Runtime ROM changes in this session: **1,289 map/story, 456 system-text, 78 system-ui = 1,823 localized manifest rows**, plus a separate `Gái`→`Nữ` gender-label correction. Sootopolis ancient-ruin dialogue was explicitly repaired from the earlier unaccented temporary hack to the UTF-8 source manifest's accented Vietnamese. New in-place span writes use source/ROM byte and allocation checks; **zero new pointers or repoints**. 78 system-ui entries were attested locally through exact source English build-offset bytes and original unchanged direct literal pointer evidence, but are **not counted as part of older 6,680 officially checkpoint-attested rows**.

Critical advance: reverse-engineered a **CANDIDATE single-byte v0.4 Vietnamese codebook** by matching 1,005 existing translated donor spans and voted glyph mappings. Stored as `checkpoints/v04-inferred-vietnamese-codebook.json`. This is not a visually/emulator validated glyph encoding. Unknown/control-heavy/oversized/repoint-needed strings were left untouched. The source translation catalog remains 17,512/17,512 complete but **far from 100% integrated into a playable ROM**.

BPS reconstruction and all three CRCs PASS; title/startup and v4 menu source-literal bytes preserved; emulator QA **NOT RUN**. The chat has the test GBA plus a private patchkit ZIP (contains no full ROM). **Next phase:** emulator visual glyph/line-wrap validation for intro and gameplay; continue the unpatched placeholder/overlong/system-ui/battle rows with source-reference-aware bounded allocations. DO NOT call this a fully localized v0.5. Never put full ROM in public repository.


## 2026-10-09 — FIXED REAL TRUCK/INTRO BUGS + 261 DYNAMIC STRINGS

**Read first:** [docs/DYNAMIC_EARLY_GAME_POINTER_RECOVERY_2026-10-09.md](docs/DYNAMIC_EARLY_GAME_POINTER_RECOVERY_2026-10-09.md) (commit `d5ac2d2`). User saw `MOM: O, ắ’re here, honey!` and truck box showing `ột chuyện hay`. ROOT CAUSES identified: English `w` reuses a Vietnamese glyph in v0.4 font while untranslated `{PLAYER}` text remained; **wrong source script pointer** at `0x00251192` points `0x0823BF75` into the middle of the word `một` in a Sootopolis text, instead of proper truck description `0x08251199`. Avoid incorrect text-side bandaid `1 chuyện hay`: restoring exact verified pointer fixes the wrong dialogue.

New test ROM from SHA-locked **1823-string v5** `ae1e00595ba3d1f193bcdbd8fcff44394b37e582c0a202e7c0c0df97f645d4d0`: **261** additional long/variable strings (259 strict manifest + 2 reviewed MOM/Littleroot) -> **2,084** cumulative manifest strings, plus **8 exactly-reviewed cross-map reference restorations**. Output ROM SHA-256 `575515ff66f640e22b77a38d06395ce3e53a9c459c1e34ab6ebd125f12d34859`. BPS source=1823-v5, output=test-2084, SHA-256 `952072c62cfceed81ccb854ae41224444459b864261aa41fdebfd072acba7518` (30,302 bytes): CRC+full reconstructed image PASS. Nothing is committed as copyrighted ROM; chat contains GBA, BPS, ZIP patchkit.

**Unsafe cases deferred**: **58** text spans had ROM pointer references into their interiors; **56** additional changed pointers from the exhaustive 64-pointer clean-v5 survey remain unresolved (some may be legitimate translated relocations). DO NOT revert all. New test still uses inferential v0.4 Vietnamese glyph codebook, and gameplay/font/spacing emulator QA has not run. v0.4 stays safe rollback; v5-2084 is an **experimental test only**, not a completed 17,512-string Vietnamese release.

Next priority: emulator gameplay QA first (truck, Mom, menu, battle and post-battle), then verify the remaining source-pointer anomalies and safe allocation of placeholder strings. Preserve existing title credit `Việt hóa bởi Votri Valley` as centered in v3/v4.


## FAIL-CLOSED v5-2084 STATIC AUDIT — 2026-10-09 (USER DOES NOT WANT TO TEST YET)

Independent, read-only SHA-locked audit completed. **READ FIRST:** [docs/STATIC_QA_V5_2084_2026-10-09.md](docs/STATIC_QA_V5_2084_2026-10-09.md), commit `c11d908`.

Audit against clean 0.13.0 + v0.4 + v5-2084 and full 17,512 user-facing manifest: **5,469 translated-source rows** still match *English source bytes at their original or candidate address* (**2,767 attested, 2,702 candidate**), not guaranteed visible English. Further **3,808** have no trusted original location. Category English-byte counts: **1,696 map/story, 1,071 system-text, 1,976 UI, 705 battle, 21 Arena**. Opening-area source paths: 35 Littleroot, 2 Oldale, 5 Route102, 79 Petalburg, 102 Rustboro (some later story content).

**New critical blocker:** exactly 64 formerly changed source-pointer values checked: 8 previously repaired; among 56 unresolved are **15 pointers into all-FF filler and 1 pointer at an FF terminator**; all 16 already existed in **v0.4**. DO NOT mass-revert. **270** previously in-place-patched text spans have possible pointer-like values into their interiors (262 observable in the original clean ROM), revealing batch01 lacked the interior-pointer guard used by dynamic batch. These are risk candidates not proof of all live references. **596** patched rows have a line over 36 encoded bytes (not pixel proof), including up to 108 bytes. Codebook has 7 duplicate byte mappings; English glyphs like w/f/z can be misrendered. Good news: 2,083 tracked new spans compare perfectly to v5 ROM, all have terminal FF, zero explicit overlap; one manual Sootopolis row accounts for 2,084 total. **No ROM modified and no emulator run during this audit.**

Next: fix/triage pointer provenance and 270 shared-suffix candidates BEFORE further batch writing; integrate source-line wraps and verify glyph codes; continue remaining source-byte English + unresolved with explicit checks. The user's chat has downloadable ZIP `Emerald-Arena-2084-Static-QA-2026-10-09.zip` with full CSV/JSON reports and read-only repro script; SHA `ae0dde4b4aac9890f0bfd8a0427270f09de74c40700f1dd74eb7af5b3a5b3a1f`. **Do not ask user to test yet, do not claim v5 stable or complete, preserve v0.4 fallback.**


## Guarded recovery handoff (2026-10-09)
See docs/GUARDED_ROM_REPAIR_2026-10-09.md (commit 2032edbc). Internal ROM candidate SHA256: 5ec43ea41192e473939002d3ed809cd84d650e51e583124bd175f7f503dda6b3. Static BPS+CRC PASS. Historical source pointer corrections 64/64, 212 source-owned translations relocated with pointer-free allocation, 29 safe new in-place translations, 916 line-reflow edits, 58 shared-suffix cases deferred. No emulator QA; not release-ready. Runtime-local scripts and allowlists: /mnt/data/arena_safe_repair/. Preserve v0.4 as rollback, and do not request user testing yet.


## 2026-10-09 — UI43 + SHARED13 NEW INTERNAL TEST (NO USER TEST YET)

Read [docs/UI43_SHARED13_GUARDED_CHECKPOINT_2026-10-09.md](docs/UI43_SHARED13_GUARDED_CHECKPOINT_2026-10-09.md), commit `eb19d47`. New exact private candidate from previous guarded ROM SHA `5ec43ea41192e473939002d3ed809cd84d650e51e583124bd175f7f503dda6b3`: output SHA `187993098e11317873043a70751cd9009fc1556a8a46a550f017be233a2ec05e`. Added 43 short Vietnamese-accented system-ui strings in place, with unchanged original pointer sites and >=1 source reference, plus 13 multiple-owner shared-suffix translations relocated into old-pointer-free tail space and 31 exact locally owned pointer updates; 45 of 58 prior shared-suffix cases remain unresolved. Independent review caught **2 preliminary modifications that would re-point freshly repaired historical references**; blocked both before final build. Therefore **all 64 historical pointer restorations remain intact**. Final static checks: 32 MiB replay, all changed bytes allowlisted, BPS source/target/patch CRC32 PASS and independent reconstruction PASS. New BPS (guarded -> UI43+shared13) SHA `363151649dd389f4aa2217e7b49257da2325860c3cc03be6f8de593ed35e8d02` (3741 bytes). Local scripts and audit live in `/mnt/data/arena_safe_repair/`: `triage_ui_candidates.py`, `integrate_verified_ui_v7.py`, `relocate_verified_multi_owner_v8.py`, `verify_ui_multi_stage_v8.py`, `ui43-allowlist.json`, `multi-owner-new-allowlist.json`, `ui43-multi15-independent-verify.json`. NO GBA emulator QA; glyph codebook and text pagination are NOT visually validated. DO NOT claim finished or ask user to test yet; do not commit commercial ROM; preserve safe v0.4.


## 2026-10-09 — SHARED OWNER RE-TRIAGE; SOURCE-CONTROLLED READ-ONLY TOOL

Read [docs/SHARED_OWNER_PROVENANCE_RETRIAGE_2026-10-09.md](docs/SHARED_OWNER_PROVENANCE_RETRIAGE_2026-10-09.md), commit `daea72d`. Reused exact clean Arena SHA `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b` and prior test2084 SHA `575515ff66f640e22b77a38d06395ce3e53a9c459c1e34ab6ebd125f12d34859`, the 270-alias QA artifact, 64 historical pointer source sites, and pinned `pokeemerald.sym`. Reproduced **212 one-nearby, 13 multiple-nearby, 41 distant/nonpreceding, 2 incidental protected-code and 2 already-modified owner sites** = 270. Of 41 distant, **39** have a plausible named EventScript/data-table owner in the build-symbol map and **2** are coincidental words in `gMonFrontPic_Numel` and `gRaySceneTakesFlight_Bg_Tilemap` graphics, not actual text pointers. The 2 protected-code matches occur in `MoveWordSelectCursor` and `LoopedTask_CloseMonMarkingsWindow` and also are not text-pointer evidence. Two historically repaired-reference conflict labels remain blocked. Source/build symbol provenance is NOT enough alone to authorize ROM writes.

New tracked tool `tools/triage_shared_owner_provenance.py` + `tools/tests/test_triage_shared_owner_provenance.py` (7 regression tests; unit-test job passed) does SHA-locked read-only symbol attribution. **No new GBA or BPS produced in this turn**, because prior private guarded+UI43+Shared13 candidate SHA `187993098e11317873043a70751cd9009fc1556a8a46a550f017be233a2ec05e` and its transient builder scripts were NOT mounted in the resumed runtime. Only previously shared older 2084 GBA is mounted; it must NOT be mislabeled as a successor. Reconstruct latest guarded output from a source-controlled deterministic recipe before further mutations. Full source translation still 17512/17512, not runtime installed. Among 5469 English-at-original-offset manifest rows, 3482 contain f/w/z codebook-collision characters (risk, not confirmed on-screen failures). **User does not want repeated test requests; don't ask for screenshots or ROM testing yet.** Preserve v0.4 rollback and title credit.



## 2026-10-09 — SOURCE-FIRST VIETNAMESE PILOT (NOT A ROM RELEASE)

**Read first:** [docs/SOURCE_FIRST_VIETNAMESE_PILOT_2026-10-09.md](docs/SOURCE_FIRST_VIETNAMESE_PILOT_2026-10-09.md). Source-first prototype added to GitHub to avoid broken manual ROM repointing: `tools/stage_source_map_translations.py` + 11 unit tests, strictly replace one exact matching `data/maps/LittlerootTown/scripts.inc` `.string` group with v0.4-codebook `.byte` bytes in an **isolated checkout**, retaining source symbol for linker. `.github/workflows/arena-map.yml` now does independent assembler/linker smoke, exports report/hash only (no ROM). It is *not* font/rendering or gameplay QA. Existing binary guarded+UI43+shared13 private ROM SHA `187993098e11317873043a70751cd9009fc1556a8a46a550f017be233a2ec05e` is absent from this resumed session; **do not fall back to old v5-2084 and claim a successor**. Original v0.4 safe rollback unchanged. Tool refuses unknown glyphs/dynamic codes (`{PLAYER}`), early terminator, string drift, long lines, and unsupported controls. Broader patching after compiler smoke and font asset compatibility QA.

Also added script owner analysis tool `tools/triage_actual_script_ownership.py` (9 unit tests) plus `checkpoints/shared-owner-opcode-evidence-2026-10-09.csv`: 44 source-identified literal word locations; 13 `0F` text loadword cases, 16 `5C` trainerbattle cases, 11 aligned text tables, 2 graphics false coincidences, 2 instruction false coincidences. These 40 plausible source references are **not yet authorized ROM pointer edits**; all exact current latest guarded refs still need SHA match. Read [docs/SCRIPT_OPCODE_OWNER_QA_2026-10-09.md](docs/SCRIPT_OPCODE_OWNER_QA_2026-10-09.md). Both unit-test suites locally PASS; full GitHub source-smoke CI must be checked before claiming it passes.



## 2026-10-09 — SOURCE FIRST PILOT COMPILER CHECKPOINT VERIFIED

**GitHub Actions run [37879032524](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37879032524) PASSED overall.** Its artifact `arena-0.13.0-symbol-map` contains `SOURCE_LEVEL_VIETNAMESE_PILOT.json` verifying exactly **1 map-story source label** (`LittlerootTown_Text_GoodLuckCatchingPokemon`) staged and compiled as Vietnamese byte text in `data/maps/LittlerootTown/scripts.inc`. Original source ROM SHA `eb1a7dd2b7eaccc4138b5d5d51f244911fc08c01c1ed7189354b033e18fba5ab`; pilot compiled ROM SHA `58fc4ea962d652c367e731725402924e8ccae4160cd2215d21df998433b75340` (different). This validates assembler/linker staging but NOT v0.4 font rendering/gameplay. **No ROM uploaded to public repo.** After this confirmed pass, `arena-map.yml` was updated (commit `2df31ed`) to attempt up to **100** safe `data/maps/` source texts using same guards, in isolated workspace. Track [run 37879483206](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37879483206); still in progress at checkpoint, do not report pass before final result. This source-first track is separate from older inaccessible guarded+UI43+shared13 binary and not a replacement release.


## SOURCE-FIRST 200 MAP + C UI + FONT GATE — 2026-10-09

Read **[docs/SOURCE_FIRST_MAP_UI_FONT_2026-10-09.md](docs/SOURCE_FIRST_MAP_UI_FONT_2026-10-09.md)**. Confirmed [CI run 37883943966](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37883943966) compiled **200 Vietnamese map/story labels across 24 files**, with **85** auto-wrapped (carefully at word boundaries, `\\n` and `\\l`) and 215 ambiguous extra-line candidates deferred. GitHub Actions report `SOURCE_LEVEL_VIETNAMESE_PILOT.json` from artifact, source-build SHA `47f9cdc86d063eaa2152b038945e9d33ab82dd92f131a11d68096738fe0e7a53`. THIS IS A SOURCE BUILD, NOT THE LIVE v0.4 DONOR ROM OR A PLAYABLE VIETNAMESE RELEASE.

Added `tools/stage_source_ui_translations.py` to stage long static C `src/strings.c` named UI notices without changing their symbols. The first combined build FAILED due to implicit C string FF terminators being different from map `$` convention. Corrected in tool and regression tests; **do not claim C UI source-build PASS until latest CI proves it**. The next combined smoke targets 200 map + up to 30 UI labels.

Major font groundwork: compared SHA-locked released clean v0.13.0 and Vietnamese v0.4 at five exact 32-KiB Latin glyph blocks: **5,917 bytes differ** (16 small-narrow, 550 small, 2,078 narrow, 906 short, 2,367 normal); no width table changes at verified normal-width location. Added `tools/import_v04_glyphs_into_source_build.py`: donor/private SHA locks, exact original font offsets, target source-build symbol map, full font block equality check, no overlap/pointers, only verified donor glyph delta. Local test using clean ROM as stand-in passed 5,917 font-only changes. **Not yet verified against an actual source-built ROM or visually in emulator**. Added `tools/audit_source_font_layout.py` with tests and workflow digest gate so source-built ROM's stock font arrays must match released clean before import is considered. Latest workflow commit `b6400f3` should be checked for full CI status; prior failures must not be hidden.

Candidate codebook expanded with independently inferred `ẹ=0x5A` (six donor contexts) and `ẻ=0x08` (three donor contexts), still unverified visually. GBA gameplay/scroll/font still untested; **do not send user ROM yet**. Original stable v0.4 preserved as rollback. Previous guarded+UI43+shared13 private output SHA `187993098e11317873043a70751cd9009fc1556a8a46a550f017be233a2ec05e` remains unavailable in active runtime; never claim to supersede it by rebuilding from older v5-2084. NEVER upload copyrighted ROM bytes to GitHub.


## VERIFIED 230 SOURCE-BUILT VIETNAMESE STRINGS (2026-10-09)

After initial UI C string implicit-terminator regression was corrected, [Actions run 37884608217](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37884608217) PASSED. Downloaded its artifact and inspected both reports: **200 map/story source label translations (24 source script files, 85 reflowed)** and **30 `src/strings.c` C UI notifications (3 reflowed)** compiled **TOGETHER** by GBA assembler/linker. Pilot ROM SHA-256 **`950f15995a78783d58ac405cf4cc72199ec725d2b2e7c80f3b6acd2759befffe`**. This is NOT the user's local v0.4/v5 ROM, which remains separate. Source glyph assets are still stock. Reproducible details and exact CI: [docs/SOURCE_FIRST_MAP_UI_FONT_2026-10-09.md](docs/SOURCE_FIRST_MAP_UI_FONT_2026-10-09.md), source import utilities in `tools/`.

New local font feasibility test: five SHA-locked released vs v0.4 glyph blocks differ **5,917** bytes and retain 32 KiB layout. `tools/import_v04_glyphs_into_source_build.py` can overlay only verified font deltas after strict equality against clean for each exact source-build font symbol. `tools/audit_source_font_layout.py` + tests and a latest workflow step (commit `b6400f3`) check compiled font block hashes first. **Check the latest full CI run before declaring that source font compatibility gate PASS.** The font is NOT yet physically imported into the compiled 230-label ROM, nor emulator visual verified. Continue source-first over dynamic `{PLAYER}`, extra pages, UI/battle groups, and font only after exact gates. Codebook candidate `ẹ=0x5A` from 6 independent donor labels and `ẻ=0x08` from 3 also stored in GitHub, not visually verified. No stable ROM release yet; v0.4 rollback preserved. Never confuse earlier guarded binary test SHA `187993098e11317873043a70751cd9009fc1556a8a46a550f017be233a2ec05e` with this separate compiler experiment.

## VERIFIED 260-STRING SOURCE-FIRST + 50 DYNAMIC FOLLOW-UP (2026-10-09)

Full [Actions run 37886532765](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37886532765) PASS; its exact artifact confirms 200 map/story (24 files, 87 auto-wrapped), 30 C system UI (3 auto-wrapped), and 30 static-layout PLAYER/RIVAL map dialogues (22 source script files) **compiled together with Votri title credit**. Source pilot ROM SHA256 `e7900c6fa34881ebafe0143fff24bb371e41b77c4a0cc337e1eefd10e44138b9`. This is a separate experimental source-build, **not** user's playable v0.4/v5 ROM. Source font-layout safety passed; Vietnamese donor font not imported, glyphs not emulator-confirmed. No ROM bytes stored in GitHub.

New guarded dynamic name wrapping: `tools/wrap_dynamic_map_text.py`, new 8 tests `tools/tests/test_wrap_dynamic_map_text.py`, and `tools/stage_dynamic_map_translations.py --auto-wrap`. Keeps all dynamic tokens ordered and page break count, name width 7 from pinned PLAYER_NAME_LENGTH, injects only word-boundary `\\n/\\l`, and rejects ambiguous strings. Workflow attempts up to 50 dynamic labels (plus 200 map +30 UI and Votri credit). Current verification run [37886877864](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37886877864) was still building; verify result and `SOURCE_LEVEL_DYNAMIC_PILOT.json` before reporting actual 50.

Early Littleroot localization correction: `translations/map-story/early-game-littleroot-route101-oldale.vi.json` changed 21 labels `MẸ:` → `Mẹ:` (verified codebook has lowercase `ẹ` but no uppercase `Ẹ`), and intro uses `Đây là thị trấn Littleroot.` instead of uppercase unsupported accented lettering. Preserves all placeholders and source label identities.

Checkpoint detail: [docs/DYNAMIC_PLAYER_RIVAL_SOURCE_PILOT_2026-10-09.md](docs/DYNAMIC_PLAYER_RIVAL_SOURCE_PILOT_2026-10-09.md). Continue by checking full CI, then improving variable-width text and actually importing v0.4 glyphs in SHA-locked source ROM before playable runtime QA. Never treat source manifest 17,512 translated as 17,512 installed. Keep stable v0.4 rollback and original guarded internal pipeline separate.

## EARLY-GAME PRIORITY BUILD PASS + FONT IMPORT GATE — 2026-10-09

**Read first**: [docs/EARLY_STORY_SOURCE_FONT_GATE_2026-10-09.md](docs/EARLY_STORY_SOURCE_FONT_GATE_2026-10-09.md), commit `7b036fc`.

**CONFIRMED GitHub Actions PASS** [run 37888719823](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37888719823) on `6dd568803`. Source-built experiment contains **200 map/story (29 files, 91 reflows) + 50 PLAYER/RIVAL map (22 files, 39 reflows) + 30 C UI (3 reflows) = 280 source-label translations**. Experimental source-built ROM SHA256 `961859be16b07bd3c286002880d052c3d7689179f41a7e660dbd64c7bbdf34ff` (NOT user's shipped v0.4). The CI requires THREE formerly broken early-game sources by label, proven in artifact: `InsideOfTruck_Text_BoxPrintedWithMonLogo`, `LittlerootTown_Text_OurNewHomeLetsGoInside`, `LittlerootTown_Text_WaitPlayer`. Source patch staged with linker-owned references rather than manual mass-repoint.

Deterministic priority in both `tools/stage_source_map_translations.py` and `tools/stage_dynamic_map_translations.py` processes truck/Littleroot/Route101/Oldale/Route102/Petalburg/Rustboro before late-game; tests pin stable ordering. Truck text translation changed to short 25/18/26-cell lines in `translations/map-story/map-story-final-misc.vi.json`, preserving paragraph semantics. Prior Mom labels now `Mẹ:` instead of unsupported `MẸ:`.

**Private font preflight** checked exact clean+v0.4 SHA; 5 original Latin font glyph blocks differ by exactly **5917** bytes; stock source-built font blocks separately matched all 5 clean hash gates. `tools/import_v04_glyphs_into_source_build.py` now REQUIRES `--expected-source-sha256` before private ROM output; a new test checks copying donor glyphs to *shifted source-built font symbols* without touching old positions. **NO donor font actually installed into a source-built ROM yet** because CI deliberately uploads only metadata/SHA, not a copyrighted compiled ROM. No visual GBA emulator test; do not release this as final v0.5. Preserve original safe v0.4 and newest guarded binary checkpoint. Avoid claiming 17,512 installed just because 17,512 source translations exist.

NEXT: obtain/reproduce exact source-built pilot ROM safely (without placing full copyrighted ROM on public GitHub), run glyph-only private transplant with exact SHA+symbol gates and visual font validation, then expand source integration and runtime QA; keep title credit style as requested. User does not want repeated small test requests.

## 2026-10-09 — CONFIRMED 741 SOURCE-COMPILED VIETNAMESE LABELS (BATTLE INCLUDED)

**Read full checkpoint first:** [docs/SOURCE_LOCALIZATION_741_BATTLE_FONT_QA_2026-10-09.md](docs/SOURCE_LOCALIZATION_741_BATTLE_FONT_QA_2026-10-09.md). **FULL PASS:** [Actions 37895308303](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37895308303), exact artifact source pilot SHA256 `e63d4799b06c634d92b3dc003e07e27c933629e480c8c01047457b0029ef6cc7` (not existing v0.4 ROM). Source-owned compiled totals: **500 map/story (205 reflow), 41 C UI (4 reflow), 100 PLAYER/RIVAL dynamic map (75 reflow), 100 battle from `data/text` (42 reflow)** = **741 unique labels, 326 reflowed**. Game source compile/title-credit+five-original-font-shapes-check PASS; Vietnamese donor glyphs NOT grafted and gameplay/emulator NOT run. Source manifest 17,512/17,512 does NOT mean 17,512 installed.

New `tools/stage_source_map_translations.py --category battle --source-prefix data/text/` reuses strict label/source/placeholder guards; currently 100 battle labels via assembler. Added `tools/audit_v04_font_code_collisions.py` + 5 tests: v0.4 font reassigns **English f=0xDA to ấ**, **w=0xEB to ằ**, **z=0xEE to ắ** in some fonts, which will corrupt remaining untranslated English if donor font pasted blindly. Small/small-narrow fonts did not receive those glyph edits; source codebook has ambiguous `Ừ`/`ừ` = 0x50. This is a release blocker. NO unverified glyph relocation to 'free' ROM/codepoints should be performed.

New independent stage verification `tools/verify_compiled_source_strings.py` (and unit tests) checks every map/UI/dynamic/battle source byte array, unique label, FF terminator and source path; the first workflow attempt FAILed because C UI per-row records omit source path (stored in report header). Fixed UI path fallback in `tools/verify_compiled_source_strings.py` at `8384e06` with regression test `e4df5cab`. **Check current [Actions latest](https://github.com/ronvotri/VH-GBA-PEA/actions)** and `SOURCE_TEXT_INDEPENDENT_QA.json` before declaring independent verification pass; on checkpoint writing the final CI had not completed. Workflow now has concurrency cancel-in-progress to avoid wasting time on obsolete rebuilds (`31019124`). Keep v0.4 rollback. Do not ask user to manually test until font/battle/story integration and source QA are stable.

## 2026-10-09 — V0.5 COLLISION-SAFE FONT PROTOTYPE (NOT RELEASE)

**Read [docs/V05_COLLISION_SAFE_FONT_RELOCATION_2026-10-09.md](docs/V05_COLLISION_SAFE_FONT_RELOCATION_2026-10-09.md) first** (commit `0b68d06d`). Independently verified older source compiled **741/741 source-labels** against their installed C/.inc files in full PASS [Actions 37896025115](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37896025115); it used stock fonts and *old inferred v0.4 codebook* (not a release). Real donor/source ROM glyph scan showed **only English ASCII f/w/z** at `DA/EB/EE` were overwritten in Normal/Narrow/Short by accented `ấ/ằ/ắ`. Donor Small and SmallNarrow retained English f/w/z, and `Ừ`/`ừ` still shared slot `0x50`.

**New durable collision-free source mapping** `checkpoints/v05-collision-free-codebook.json` (137 unique codepoint slots): `ấ=>30`, `ằ=>31`, `ắ=>32`; ASCII f/w/z restored to original unchanged DA/EB/EE; ambiguous uppercase `Ừ` removed (NOT translated until drawn separately). `tools/plan_collision_free_vietnamese_font.py` checks pinned Latin charmap reserves 0x30..32 and rejects other collisions; current GitHub Action [run 37900453143](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37900453143) is configured to generate and compare v2 mapping then compile map/UI/dynamic/battle using the new codebook. Check actual CI conclusion and artifact before claiming new v2 source compile PASS.

Font raster tools `tools/pokemon_gba_font_glyphs.py` implement source-compatible Pokémon 16x16 four-tile glyph decode/encode, and `tools/graft_collision_safe_v04_fonts.py` performs *PRIVATE SHA-locked source font transplant* by true symbol offsets, restoring ASCII f/w/z; three accents in Small/SmallNarrow fonts synthesized as 13px-high reductions of real donor Narrow glyphs. Tests in `tools/tests/test_*.py` guard original ASCII, no non-font writes and 5 styles; TWO small styles require real visual QA.

**REAL private ROM FONT-ONLY PROTOTYPE smoke verified:** clean Arena + actual v0.4 font donor, remapped glyph art at reserved slots, produced a 32MiB test image SHA `19ba06b191c403d7ad32f1eed52d0059d189d508d2e55c7899b814d480e069c8` with **6,095 changed bytes inside font+width areas ONLY**, 15/15 nonblank accented glyph raster data and all five original English f/w/z glyph shapes preserved bit-for-bit. This test is *NOT source translated*, NO emulator QA, NO user-facing binary, should NOT be called final ROM. Actual source-built translated GBA binary not uploaded to public GitHub (artifact metadata only) and no private donor font graft to actual source-built 741 has yet happened.

**Next work:** confirm v2 source compiler and independent QA; obtain exact new v2 source-built ROM privately, apply SHA-lock font graft and validate glyph/page/gameplay; continue hundreds/thousands of manifest entries in source, especially battle templates and unsupported uppercase accents; preserve stable v0.4 rollback and exact title credit. Do not ask user for interim tests or send technical zips.

## 2026-10-09 — VERIFIED V0.5 CODEBOOK SOURCE BUILD AND LARGER COVERAGE RUN

**Confirmed PASS**: [GitHub Actions 37900453143](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37900453143), current source-first compiler with collision-free `checkpoints/v05-collision-free-codebook.json`, exact ROM SHA `419c7578193dc08cd4af04965690fa65a30c89a0e5c11ef6af320409e67b43e1`. Source text QA **741/741 correct unique labels** (500 map/story, 41 UI, 100 PLAYER/RIVAL, 100 battle), FF terminators intact; original English f/w/z slots retained as English and accent ấ/ằ/ắ reserved separately at 0x30..0x32, `Ừ` remains QUARANTINED. No Vietnamese font graft applied to this compiled ROM; stock fonts only. Symbol-aware graft must target actual new codebook compiled font addresses: 0x71CC64 SmallNarrow, 0x724E64 Small, 0x72D064 Narrow, 0x735264 Short, 0x73D464 Normal, not old clean shipping positions.

A private SHA-locked font-only prototype applied actual v0.4 donor accent bitmaps to a copy of clean Arena (NOT this source-translated build), synthesized Small/SmallNarrow from narrowed font through original text.c-compatible glyph compression and preserved f/w/z at old ASCII glyphs. **6,095** byte changes entirely inside 5 font+width ranges, **15/15** accent glyphs nonempty, source binary SHA `19ba06b191c403d7ad32f1eed52d0059d189d508d2e55c7899b814d480e069c8`. Preview/manual font visual QA is still incomplete; no emulator/ROM release. Tools `tools/graft_collision_safe_v04_fonts.py`, `tools/pokemon_gba_font_glyphs.py`, `tools/plan_collision_free_vietnamese_font.py` plus tests are committed.

Read full checkpoint [docs/V05_COLLISION_SAFE_FONT_RELOCATION_2026-10-09.md](docs/V05_COLLISION_SAFE_FONT_RELOCATION_2026-10-09.md). **Current next larger source-build CI** [Actions run after commit d4a501f7](https://github.com/ronvotri/VH-GBA-PEA/actions) expands from 500/100/100 to **up to 1000 map, 200 named-variable and 200 battle source labels**; this total is merely configured, not yet confirmed — inspect source artifact actual totals and independent QA when done. The UI cap remains 80 with ~41 eligible. Preserve user’s v0.4 rollback and title credit. No copyrighted original ROM or font binaries on public GitHub.


## 2026-10-09 — NEW SOURCE-FIRST 1,430-LABEL BUILD, STATIC BATTLE C INTEGRATION

**Full verified GitHub Actions PASS**: [37914622483](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37914622483), source commit `c564a97c6a33f8427c8dd1063d13236bdf90eccc`. Exact source-compiled trial ROM SHA-256 `3abc84cd46c2ea283eedd1218c091d5e97b9c724bb03854a35e809f6450230cd` (32MiB, **STOCK LATIN FONT, not an end-user localized build**). Artifact independent source QA: **1,430 unique translated source labels, 0 duplicates, valid FF terminators**: **1,000 map/story** (543 reflows), **41 C UI** (4), **134 dynamic-name map** (102), **196 text-script battle** (96), **59 NEW static C battle messages** (4) = 749 controlled reflows. Title credit remains `Việt hóa bởi Votri Valley` in source build.

New tracked tools `tools/stage_source_battle_c_messages.py`, `tools/tests/test_stage_source_battle_c_messages.py`, updated `tools/verify_compiled_source_strings.py` and independent test suite. Correctly reads pinned `src/battle_message.c` static const C arrays, stages only full variable-free texts whose English match exactly and codebook/line/page guards pass. New compiled battle messages include Critical Hit, Super Effective, Can't Escape, weather, other standalone effects. **363 battle C rows with dynamic engine tokens** and 71 fragments deliberately blocked; 14 complex-page/missing-glyph rows blocked. Never assume all battle templates integrated.

**Read detailed and corrected checkpoint** [docs/SOURCE_LOCALIZATION_1430_BATTLE_C_2026-10-09.md](docs/SOURCE_LOCALIZATION_1430_BATTLE_C_2026-10-09.md), latest corrective commit `dec498f`. User does NOT need to download reports or test the game yet. **Key blocker remains source-build stock font**: v0.5 injective byte map slots 0x30/31/32 require exact SHA-locked font raster graft from the private v0.4 donor, proper five-font small-style visual QA, followed by emulator validation. User's playable v0.4 rollback must remain untouched. Whole manifest 17,512 source translations is NOT installed runtime total.

NEXT: source-first 355 move descriptions in `src/data/text/move_descriptions.h`, 310 item descriptions in `src/data/text/item_descriptions.h`, then dynamic battle templates with widths and tokens; do not blind-patch arbitrary ROM pointers. Await exact source-built private glyph integration before shipping ROM.


## 2026-10-09 — 1,961 COMPILER-INTEGRATED SOURCE TEXTS (MOVE/ITEM DESCRIPTIONS)

**Read** [docs/SOURCE_LOCALIZATION_1961_MOVE_ITEM_2026-10-09.md](docs/SOURCE_LOCALIZATION_1961_MOVE_ITEM_2026-10-09.md), commit `c499c722`. **GitHub Actions #37943838702 full SUCCESS**, independent source QA **1,961 unique labels, 0 duplicates, FF-terminated**; experimental source ROM SHA `c108adbca891bb6164ad99a08e54c0733f81456ea18d30c3c99c1e8ce415ac67`. Groups: **1,000 map, 41 UI, 134 dynamic PLAYER/RIVAL, 196 battle script, 59 battle C, 246 NEW move descriptions, 285 NEW item descriptions**. Five compiled font glyph arrays still STOCK ENGLISH (SHA audits pass), so **NOT end-user localized/release-ready GBA**. Votri Valley title credit retained.

New `tools/stage_source_descriptions.py` strictly parses the actual pinned upstream two-/three-line quoted C descriptions, preserves exact C label/English source, outputs compiled Vietnamese byte arrays with same line control count and no pointer changes; skips unknown glyphs, long lines, dynamic placeholders and unsupported page controls. Independent `tools/verify_compiled_source_strings.py` expanded to move-desc/item-desc; tests added. **98** move rows too long in first pass, **16** item descriptions contain dynamic/control placeholders (skipped). New opt-in `--rebalance` for move descriptions can safely shift a newline between words only if both lines fit 26 characters; corpus audit found **42 possibly recoverable** overlong move strings before glyph QA. Its current CI [#37944716925](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37944716925) was pending when checkpoint written; verify actual result before claiming additional rows.

Whole source manifest coverage remains 17,512/17,512, not runtime installation count. Core outstanding BLOCKER: new source ROM does not have v0.5 collision-safe Vietnamese font artwork integrated/emulator verified; require exact target SHA for private graft, preserve English f/w/z glyphs, verify small-font synthetic accents, battle and save/load runtime. Original stable v0.4 rollback untouched. User does not want piecemeal test requests or technical ZIPs.
