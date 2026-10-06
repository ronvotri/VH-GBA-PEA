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

1. Đọc:
   - `README.md`
   - `PROGRESS.md`
   - `docs/TECHNICAL_NOTES.md`
   - `.github/workflows/arena-map.yml`
2. Kiểm tra GitHub Actions **Build Arena symbol map**.
3. Lấy `pokeemerald.map` / `pokeemerald.sym` nếu workflow đã chạy thành công.
4. Dùng map/source để dựng catalog chính xác:
   - source label;
   - source file;
   - ROM offset;
   - pointer/reference sites;
   - English;
   - Vietnamese;
   - original allocation;
   - patch strategy.
5. Quét **toàn bộ user-facing vanilla Emerald text**, không chỉ ảnh người dùng báo.
6. Match AowVN khi có; dịch mới khi không có.
7. Với câu dài: biên tập gọn trước; chỉ repoint reference đã xác minh nếu thực sự cần.
8. Sau vanilla coverage, xử lý text riêng Emerald Arena: HUD, realtime battle, control/help, status/options.
9. Xuất candidate mới + audit manifest để người dùng test một lượt lớn.

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
