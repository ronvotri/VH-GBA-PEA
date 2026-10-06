# Tiến độ Việt hóa Pokémon Emerald Arena

Cập nhật: 2026-10-06 — handoff cuối phiên

## Baseline hiện tại

### v0.4 – Text Cluster Pass

ROM v0.4:

`c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`

Được dựng trên v0.3:

`8234d3945fc6d3a87a9669887a114114904b85c00fd9b3ddd026aaea40d636ec`

Arena 0.13.0 sạch:

- SHA-256: `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`
- SHA-1: `a3247882b469fecb491e2875d45ddc3b4b49e310`
- Size: `33,554,432` bytes

## QA thực tế đã đạt

- [x] Logo Pokémon không còn lỗi.
- [x] Intro chạy được.
- [x] Font dấu tiếng Việt hoạt động.
- [x] Battle đầu tiên chạy được.
- [x] Sau battle đi tiếp được, không freeze.
- [x] Người chơi đã tiếp tục tới khu vực sâu hơn sau phần đầu game bằng v0.4.
- [x] Không có pointer write mới trong v0.4.
- [x] Startup/title v0.4 giống byte-for-byte v0.3.

**Chưa được coi là QA toàn game.** Save/load, toàn bộ story, menu/UI và các battle case đặc biệt vẫn cần kiểm tra.

## Vấn đề hiện tại

Mục tiêu số 1 bây giờ không còn là sửa crash mà là **xóa tình trạng Anh–Việt xen kẽ**.

Checkpoint người chơi mới nhất vẫn gặp text tiếng Anh:

`There could be treasures just waiting to be discovered down there.`

Điều này chứng minh cluster pass vẫn chưa phủ hết user-facing text.

## Kết quả phân tích text cuối phiên

Trên ROM Arena sạch 32 MiB:

- Target text theo bộ lọc rộng: **24,916**
- Target text theo bộ lọc English/plausibility chặt hơn: **20,383**

Các target này được suy ra từ giá trị ROM pointer trỏ vào vùng decode được như text. **Không được tự động repoint toàn bộ 20,383 target**; đây chỉ là catalog candidate để tiếp tục đối chiếu với source/map.

## Build/source mapping

Đã tạo:

`.github/workflows/arena-map.yml`

Workflow:

1. checkout đúng `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`;
2. checkout `agbcc@da598c1d918402c42c0c0d7128ba14567f3175e9`;
3. lấy `GBurgardt/pokemon-emerald-arena v0.13.0`;
4. apply `game/native-engine.patch` + overlay;
5. build Arena;
6. xuất `pokeemerald.map`, `pokeemerald.sym`, SHA-1/SHA-256 dưới dạng GitHub Actions artifact.

Mục tiêu của map/symbol là biến việc patch từ **đoán pointer nhị phân** thành **mapping symbol/source → ROM address**.

## Những gì đã học được từ Test 1 → v0.4

| Bản | Kết quả |
|---|---|
| Test 1 | Có dấu nhưng corrupt logo + crash intro |
| Test 2 | Logo lỗi, text lẫn Anh–Việt, freeze hậu battle |
| Test 3 | Giảm repoint nhưng vẫn dựa nền vá chưa sạch |
| Test 4 | Gameplay ổn, logo ổn, phần lớn text không dấu |
| v0.1 | Nền gameplay ổn định |
| v0.2 | Repoint lọc vẫn làm logo lỗi |
| v0.3 | No-repoint, logo + battle + post-battle ổn |
| **v0.4** | **Thêm 462 cluster shared/overlap, 0 pointer write; đã chơi tiếp được nhưng vẫn còn English** |

## Việc tiếp theo — ưu tiên

### 1. Lấy symbol map thật
- [ ] Chạy/kiểm tra GitHub Actions `Build Arena symbol map`.
- [ ] Tải artifact `arena-0.13.0-symbol-map`.
- [ ] Xác nhận hash ROM build so với shipping Arena.
- [ ] Nếu build hash lệch, vẫn dùng map nếu layout tương ứng và ghi rõ chênh lệch; tốt nhất sửa workflow/build tới khi map đáng tin.

### 2. Dựng catalog có provenance
- [ ] Mỗi string cần: label/source file, ROM address, references, English source, Vietnamese candidate, length/allocation, strategy.
- [ ] Tách các nhóm: map/story, system/UI, battle vanilla, Arena-only.
- [ ] Loại false positive và substring/suffix target khỏi danh sách “cần dịch độc lập”.

### 3. Hoàn thiện bản dịch
- [ ] Ưu tiên toàn bộ user-facing story/map English còn sót.
- [ ] Dịch tự nhiên, có dấu; không dịch từng mảnh làm câu nửa Anh nửa Việt.
- [ ] Chuỗi dài: rút gọn hợp lý hoặc repoint **đúng reference đã xác minh**.
- [ ] Dịch text riêng của Arena sau khi vanilla coverage sạch.

### 4. QA
- [ ] Title/intro sau mỗi batch.
- [ ] Battle/post-battle sau mỗi batch có repoint.
- [ ] Save/load.
- [ ] Menu / Bag / Pokémon / Pokédex.
- [ ] Story từ Littleroot tới Elite Four + post-game.
- [ ] Arena UI/control/help/HUD.

## Nguyên tắc bất biến

- Không quét/repoint pointer toàn ROM.
- Không chép nguyên patch AowVN vào Arena.
- Không sửa graphics/code chỉ vì byte pattern “trông giống text pointer”.
- Không gọi bản “hoàn thiện” khi còn English user-facing.
- Repo không lưu ROM thương mại đầy đủ.


## Checkpoint catalog source → shipping (2026-10-06)

Workflow `Build Arena symbol map` run #9 đã **PASS** sau khi mở parser cho cả C-style `.inc`.

Catalog provenance hiện tại:

- **17,513** source text entries.
- **13,833** named entries + **3,680** anonymous source strings.
- **13,827** entry nối được ELF symbol.
- **13,171** entry có source-level reference.
- **4,361** map/story.
- **2,319** system text.
- **8,279** system/UI.
- **2,223** battle.
- **46** Arena-only.
- **285** debug/internal.

Đối chiếu trực tiếp với ROM Arena 0.13.0 shipping sạch (SHA-256 `a8d36c0c...c645b`) đã xác minh:

- **4,361 / 4,361 map/story** khớp byte-for-byte tại build offset.
- **2,319 / 2,319 system-text** khớp byte-for-byte tại build offset.
- Checkpoint English từng thấy trong game `There could be treasures just waiting to be discovered down there.` được neo đúng vào `SootopolisCity_House4_Text_AncientTreasuresWaitingInSea` tại ROM offset **`0x23BF5F`**, reference từ `SootopolisCity_House4_EventScript_Man`.

Điều này cho phép dùng symbol/source để định vị hai nhóm user-facing lớn nhất mà **không suy diễn từ pointer scan**.

Tool mới: `tools/resolve_shipping_catalog.py`.

- Chỉ ghi shipping offset khi encoded source bytes khớp tuyệt đối.
- Từ chối ROM sai SHA-256.
- Không sửa ROM.
- Không quét pointer.
- Không mass-repoint.

Bước tiếp theo: dùng catalog shipping-verified để đánh dấu coverage của baseline v0.4, ghép bản dịch đáng tin, ưu tiên map/story → system text → Arena-only → UI/battle; chỉ repoint reference đã xác minh khi bản dịch không thể vừa allocation.


## Translation pass — map/story (2026-10-06)

Đã chuyển hẳn sang **dịch nội dung**, không tiếp tục mở rộng nghiên cứu kỹ thuật nếu không có lỗi thật sự.

Các manifest đã QA và commit:

- `translations/map-story/early-game-littleroot-route101-oldale.vi.json`
  - Littleroot Town: **119 / 119**
  - Route 101: **7 / 7**
  - Oldale Town: **20 / 20**
  - Tổng: **146**
- `translations/map-story/route102-petalburg.vi.json`
  - Route 102: **7 / 7**
  - Petalburg City (gồm Gym/nhà/Mart/Center/Wally): **105 / 105**
  - Tổng: **112**
- `translations/map-story/route103-route104-petalburgwoods.vi.json`
  - Route 103: **11 / 11**
  - Route 104 + Mr. Briney: **41 / 41**
  - Petalburg Woods: **29 / 29**
  - Tổng: **81**
- `translations/map-story/sootopolis.vi.json`
  - Sootopolis toàn khu: **155 / 155**

Tổng manifest map/story đã hoàn chỉnh: **494 string**.

QA của các batch trên:
- không thiếu label trong phạm vi;
- placeholder `{...}` giữ đúng thứ tự;
- số paragraph control `\p` giữ nguyên;
- terminator `$` giữ nguyên;
- `\n/\l` được reflow khi cần cho tiếng Việt tự nhiên;
- chưa patch ROM / chưa ghi pointer ở bước dịch.

**Bước dịch kế tiếp:** Rustboro City và khu liên quan. Không quay lại font/pointer/catalog trừ khi việc build/patch thật sự phát hiện lỗi.


## Translation pass — Rustboro → Dewford checkpoint (2026-10-06)

Đã dịch tiếp theo tuyến chơi chính và QA source-level:

- `translations/map-story/rustboro-city.vi.json`
  - Rustboro City toàn khu: **177 / 177**
- `translations/map-story/route116-rusturf-tunnel.vi.json`
  - Route 116 + Tunneler's Rest House + Rusturf Tunnel: **38 / 38**
- `translations/map-story/dewford-route106-granite-cave.vi.json`
  - Dewford Town + Gym + Hall + Route 106 + Granite Cave: **103 / 103**

Lượt này thêm: **318 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **812 string**.

QA:
- 0 label thiếu trong phạm vi batch;
- placeholder `{...}` giữ đúng thứ tự;
- số paragraph control `\p` giữ nguyên;
- terminator `$` giữ nguyên;
- `\n/\l` chỉ reflow cho tiếng Việt dễ đọc;
- chưa patch ROM / chưa ghi pointer ở bước dịch.

**Bước kế tiếp:** Route 109 + Slateport City (catalog hiện có **257 map/story string** trong cụm này).


## Translation pass — Slateport → Verdanturf checkpoint (2026-10-06)

Đã tiếp tục dịch map/story theo tuyến chơi chính, không quay lại technical discovery:

- `translations/map-story/route109-slateport.vi.json`
  - Route 109 + Seashore House + toàn Slateport: **257 / 257**
- `translations/map-story/route110-mauville.vi.json`
  - Route 110 main + hai cổng Cycling Road + toàn Mauville: **178 / 178**
- `translations/map-story/route110-trick-house.vi.json`
  - Trick House Entrance + Puzzle 1–8 + End: **146 / 146**
- `translations/map-story/route117-verdanturf.vi.json`
  - Route 117 + toàn Verdanturf: **55 / 55**

Lượt này thêm: **636 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **1,448 string**.

QA cho cả 4 batch:
- 0 label thiếu;
- placeholder `{...}` giữ đúng thứ tự;
- số paragraph control `\p` giữ nguyên;
- terminator `$` giữ nguyên;
- `\n/\l` chỉ reflow cho tiếng Việt dễ đọc;
- chưa patch ROM / chưa ghi pointer ở bước dịch.

**Bước kế tiếp:** Route 111 (**40**) + Route 112 (**11**), sau đó Jagged Pass / Lavaridge. Tiếp tục dịch; không mở lại font/pointer/catalog nếu chưa có blocker thật.


## Translation pass — Route 111 → Lavaridge checkpoint (2026-10-06)

Tiếp tục sau checkpoint 1,448 string:

- `translations/map-story/route111-route112.vi.json`
  - Route 111 + Old Lady's Rest Stop + Winstrate House + Route 112 + Cable Car Station: **51 / 51**
- `translations/map-story/mtchimney-jaggedpass-lavaridge.vi.json`
  - Mt. Chimney + Cable Car Station + Jagged Pass + toàn Lavaridge/Gym: **159 / 159**

Lượt bổ sung này: **210 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **1,658 string**.

Toàn bộ batch tiếp tục đạt:
- 0 label thiếu;
- placeholder `{...}` đúng thứ tự;
- số `\p` khớp source;
- terminator `$` đầy đủ;
- chưa patch ROM / chưa ghi pointer.

**Bước kế tiếp nên lấp đoạn story đã bỏ qua trước Mt. Chimney:** Route 113 (**21**) + Fallarbor (**40**) + Route 114 (**21**) + Meteor Falls (**37**) = **119 string**.


## Translation pass — Fallarbor / Meteor Falls checkpoint (2026-10-06)

Đã hoàn tất batch story bị bỏ qua trước Mt. Chimney:

- `translations/map-story/route113-fallarbor-route114-meteorfalls.vi.json`
  - Route 113 + Glass Workshop: **21 / 21**
  - Fallarbor Town + Battle Tent + nhà/phụ trợ: **40 / 40**
  - Route 114 + Fossil Maniac + Lanette: **21 / 21**
  - Meteor Falls + Steven's Cave: **37 / 37**
  - Tổng: **119 / 119**

Tổng map/story manifest hoàn chỉnh hiện tại: **1,777 string**.

QA:
- 0 label thiếu;
- placeholder `{...}` giữ đúng thứ tự;
- số paragraph control `\p` khớp source;
- terminator `$` đầy đủ;
- chưa patch ROM / chưa ghi pointer ở bước dịch.

**Bước kế tiếp:** tiếp tục theo tuyến sau Lavaridge/Petalburg, ưu tiên Route 115 / các đoạn story còn hở trước khi sang Fortree.


## Translation pass — Route 115 → Fortree checkpoint (2026-10-06)

Đã tiếp tục lấp tuyến sau Petalburg/Lavaridge tới Fortree:

- `translations/map-story/route115-route118-route119-weather-institute.vi.json`
  - Route 115: **3 / 3**
  - Route 118: **9 / 9**
  - Route 119 + House: **20 / 20**
  - Weather Institute 1F/2F: **34 / 34**
  - Tổng: **66 / 66**
- `translations/map-story/fortree-city.vi.json`
  - Fortree City + Gym + Decoration Shop + houses + Mart + Pokemon Center 1F: **78 / 78**

Lượt này thêm: **144 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **1,921 string**.

QA cho cả hai batch:
- 0 label thiếu;
- placeholder `{...}` giữ đúng thứ tự;
- số paragraph control `\p` khớp source;
- terminator `$` đầy đủ;
- chưa patch ROM / chưa ghi pointer ở bước dịch.

**Bước kế tiếp:** Route 120 → Route 121 → Lilycove/Mt. Pyre, tiếp tục theo tuyến story chính. Không mở lại technical discovery nếu chưa có blocker thật.
