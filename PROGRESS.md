# Tiến độ Việt hóa Pokémon Emerald Arena

Cập nhật: 2026-10-07 — map/story catalog hoàn tất 100%

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


## Translation pass — Route 120 → Lilycove core checkpoint (2026-10-07)

Đã hoàn tất:

- `translations/map-story/route120-route121-mtpyre.vi.json`
  - Route 120 + Route 121 + toàn Mt. Pyre/Summit: **92 / 92**
- `translations/map-story/lilycove-core.vi.json`
  - Lilycove city core + Harbor + Cove Lily Motel + houses + Move Deleter + Pokemon Center 1F: **107 / 107**

Lượt này thêm: **199 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **2,120 / 4,361 string (~48.6%)**.
Còn **2,241 map/story string** chưa có manifest hoàn chỉnh.

QA:
- 0 label thiếu;
- placeholder `{...}` giữ đúng thứ tự;
- số paragraph control `\p` khớp source;
- terminator `$` đầy đủ;
- chưa patch ROM / chưa ghi pointer ở bước dịch.

Phần Lilycove còn lại đã đếm chính xác:
- Contest Hall/Lobby + Department Store + Museum + Trainer Fan Club: **163 string**.

**Bước kế tiếp:** hoàn tất 163 Lilycove còn lại, sau đó Route 122/123 → Safari Zone / Aqua Hideout / Mossdeep.


## Repository integrity audit — 2026-10-07

Đã rà lại trực tiếp `translations/map-story` trên GitHub để chắc chắn không bị sót khi handoff.

Phát hiện và sửa 2 manifest từng bị commit nhầm thành nội dung lỗi file-reference thay vì JSON:

- `route103-route104-petalburgwoods.vi.json` — phục hồi **81 translations**
- `route110-mauville.vi.json` — phục hồi **178 translations**

Sau sửa:
- cả hai file đã có kích thước/nội dung JSON bình thường trên `main`;
- quét toàn repo không còn chuỗi lỗi `The requested file reference is not currently visible`;
- đã thêm `translations/map-story/INDEX.md` làm inventory chuẩn của **18 manifest**, tổng **2,120 / 4,361** map/story strings;
- `sootopolis.vi.json.gz` chỉ là duplicate convenience artifact, không tính hai lần.

Từ checkpoint này, khi tiếp tục dịch phải đối chiếu `translations/map-story/INDEX.md` trước khi tăng tổng coverage.


## Translation pass — Lilycove complete checkpoint (2026-10-07)

Đã hoàn tất toàn bộ **163 string Lilycove còn lại** và QA chéo trực tiếp với source:

- `translations/map-story/lilycove-contest.vi.json`: **53 / 53**
- `translations/map-story/lilycove-department-store.vi.json`: **29 / 29**
- `translations/map-story/lilycove-museum.vi.json`: **43 / 43**
- `translations/map-story/lilycove-trainer-fan-club.vi.json`: **38 / 38**

Cộng với `lilycove-core.vi.json` **107 / 107**, toàn Lilycove hiện là **270 / 270**.

Tổng map/story manifest hoàn chỉnh hiện tại: **2,283 / 4,361 (~52.4%)**.
Còn **2,078 map/story string** chưa có manifest hoàn chỉnh.

QA 163 string mới:
- 0 label thiếu / dư;
- placeholder `{...}` giữ đúng thứ tự;
- số paragraph control `\p` khớp source;
- terminator `$` đầy đủ;
- cả 4 manifest đã chuyển sang `translation-complete-source-qa`;
- chưa patch ROM / chưa ghi pointer ở bước dịch.

**Bước kế tiếp:** Route 122 / Route 123 → Safari Zone → Aqua Hideout → Mossdeep.


## Translation pass — Route 123 / Aqua Hideout / Mossdeep checkpoint (2026-10-07)

Sau checkpoint Lilycove **2,283 / 4,361**, đã hoàn tất thêm:

- `translations/map-story/route123.vi.json`: **6 / 6**
  - Route 122 và Safari Zone không có map-local `.string` entry trong source scope này.
- `translations/map-story/aqua-hideout.vi.json`: **34 / 34**
- `translations/map-story/mossdeep-core.vi.json`: **52 / 52**
- `translations/map-story/mossdeep-gym.vi.json`: **52 / 52**
- `translations/map-story/mossdeep-space-center-steven.vi.json`: **65 / 65**

Lượt bổ sung sau Lilycove: **209 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **2,492 / 4,361 (~57.1%)**.
Còn **1,869 map/story string** chưa có manifest hoàn chỉnh.

QA:
- Route 123: 6/6 sạch;
- Aqua Hideout: 34/34 sạch;
- Mossdeep: 169/169 sạch;
- 0 label thiếu / dư;
- placeholder `{...}` đúng thứ tự;
- paragraph control `\p` khớp source;
- terminator `$` đầy đủ;
- chưa patch ROM / chưa ghi pointer.

**Bước kế tiếp:** Route 124/125 + Shoal Cave → Route 126/127/128 → Seafloor Cavern → Route 129/130/131/Sky Pillar.


## Translation pass — Seafloor → Pokémon League checkpoint (2026-10-07)

Đã hoàn tất thêm 4 manifest:

- `translations/map-story/route124-131-shoal-seafloor-skypillar.vi.json`: **63 / 63**
  - Route 124/Treasure Hunter, Route 128, Seafloor Cavern, Shoal Cave local text, Sky Pillar
  - Route 125/126/127/129/130/131 và nhiều phòng cave có 0 map-local `.string` trong scope này
- `translations/map-story/pacifidlog-route132-134.vi.json`: **34 / 34**
  - Pacifidlog Town; Route 132/133/134 có 0 map-local `.string`
- `translations/map-story/victory-road.vi.json`: **54 / 54**
- `translations/map-story/ever-grande-pokemon-league.vi.json`: **36 / 36**
  - Ever Grande + Elite Four + Champion + Hall of Fame

Lượt này thêm: **187 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **2,679 / 4,361 (~61.4%)**.
Còn **1,682 map/story string** chưa có manifest hoàn chỉnh.

QA:
- 0 label thiếu / dư;
- placeholder `{...}` đúng thứ tự;
- paragraph control `\p` khớp source;
- terminator `$` đầy đủ;
- chưa patch ROM / chưa ghi pointer.

Main-story progression hiện đã có manifest QA-clean tới **Pokémon League / Hall of Fame**.

**Bước kế tiếp:** audit và dịch các gap map/story còn lại, ưu tiên New Mauville / Abandoned Ship / Magma Hideout / legendary & post-game / Battle Frontier.


## Translation pass — New Mauville / Abandoned Ship / Magma Hideout (2026-10-07)

Đã hoàn tất:

- `translations/map-story/new-mauville-abandoned-ship.vi.json`: **62 / 62**
  - New Mauville: 6
  - Abandoned Ship: 56
- `translations/map-story/magma-hideout.vi.json`: **56 / 56**

Lượt này thêm: **118 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **2,797 / 4,361 (~64.1%)**.
Còn **1,564 map/story string** chưa có manifest hoàn chỉnh.

QA:
- 0 label thiếu / dư;
- placeholder `{...}` đúng thứ tự;
- paragraph control `\p` khớp source;
- terminator `$` đầy đủ;
- chưa patch ROM / chưa ghi pointer.

**Bước kế tiếp:** audit/dịch các gap optional/post-game còn lại, ưu tiên legendary/sealed/island content rồi Battle Frontier/Battle Tent.


## Translation pass — Battle Arena + optional legendary text (2026-10-07)

Đã hoàn tất:

- `translations/map-story/battle-frontier-arena.vi.json`: **66 / 66**
- `translations/map-story/optional-legendary-islands.vi.json`: **1 / 1**
  - Faraway Island có 1 map-local `.string`; nhóm Regi / Southern Island / Birth Island / Terra Cave / Marine Cave / Navel Rock đã audit và không có map-local text trong source scope này.

Lượt này thêm: **67 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **2,864 / 4,361 (~65.7%)**.
Còn **1,497 map/story string** chưa có manifest hoàn chỉnh.

QA:
- 0 label thiếu / dư;
- placeholder `{...}` đúng thứ tự;
- paragraph control `\p` khớp source;
- terminator `$` đầy đủ;
- chưa patch ROM / chưa ghi pointer.

**Bước kế tiếp:** Battle Dome (**113 string đã inventory**) rồi các facility Battle Frontier còn lại.


## Translation pass — Battle Dome / Factory / Palace (2026-10-07)

Đã hoàn tất và QA sạch:

- `translations/map-story/battle-frontier-dome.vi.json`: **113 / 113**
- `translations/map-story/battle-frontier-factory.vi.json`: **95 / 95**
- `translations/map-story/battle-frontier-palace.vi.json`: **67 / 67**

Lượt này thêm: **275 string**.

Tổng map/story manifest hoàn chỉnh hiện tại: **3,139 / 4,361 (~72.0%)**.
Còn **1,222 map/story string** chưa có manifest hoàn chỉnh.

QA cả ba batch:
- 0 label thiếu / dư;
- placeholder `{...}` đúng thứ tự;
- paragraph control `\p` khớp source;
- terminator `$` đầy đủ;
- chưa patch ROM / chưa ghi pointer.

Đã inventory sẵn bước kế:
- Battle Pike: **97**
- Battle Pyramid: **81**
- Battle Tower: **112**

**Bước kế tiếp:** Battle Pike → Battle Pyramid → Battle Tower, sau đó shared Battle Frontier services/post-game gaps.


## Translation pass — Battle Pike (2026-10-07)

- `translations/map-story/battle-frontier-pike.vi.json`: **97 / 97**
- QA: 0 label thiếu/dư; placeholder đúng thứ tự; `\p` khớp; `$` đầy đủ.

Tổng map/story hiện tại: **3,236 / 4,361 (~74.2%)**.
Còn **1,125** map/story string.

**Bước kế tiếp:** Battle Pyramid (**81**) → Battle Tower (**112**), sau đó shared Battle Frontier services/post-game gaps.


## Translation pass — Battle Pyramid / Tower (2026-10-07)

- `translations/map-story/battle-frontier-pyramid.vi.json`: **81 / 81**
- `translations/map-story/battle-frontier-tower.vi.json`: **112 / 112**

Cộng với Battle Pike vừa chốt, phần mới sau checkpoint 3,139 là **290 string**.

Tổng map/story hiện tại: **3,429 / 4,361 (~78.6%)**.
Còn **932** map/story string.

QA: 0 label thiếu/dư; placeholder đúng thứ tự; `\p` khớp; `$` đầy đủ.

**Bước kế tiếp:** remaining Battle Frontier shared services / Battle Tent / optional-postgame map/story gaps.


## Translation pass — Shared Battle Frontier (2026-10-07)

QA-clean:
- `battle-frontier-exchange-lounges.vi.json`: **87 / 87**
- `battle-frontier-outside-mart.vi.json`: **72 / 72**
- `battle-frontier-services-scott.vi.json`: **60 / 60**

Lượt này thêm **219 string** sau Tower.

Tổng map/story: **3,648 / 4,361 (~83.7%)**.
Còn **713** map/story string.

**Bước kế tiếp:** audit chính xác 713 string còn lại theo source map, ưu tiên Battle Tent + optional/post-game gaps.


## Translation checkpoint — final handoff before new chat (2026-10-07)

Repository `main` was re-audited before handing off.

Latest additional QA-clean manifest:
- `translations/map-story/battle-frontier-pyramid-dynamic.vi.json`: **128 / 128**
  - Battle Pyramid dynamic floor hints / item counts / trainer counts.
  - Six incorrect keys `OneItemsRemaining1..6` were corrected to source labels `OneItemRemaining1..6`.
  - Source QA now passes: 0 missing labels, 0 placeholder-order errors, 0 paragraph-control errors, 0 terminator errors.
  - The source-only `BattleFacility_TrainerBattle_PlaceholderText` is intentionally excluded as sample/debug placeholder text.

Current committed map/story coverage: **3,776 / 4,361 (~86.6%)**.
Remaining map/story backlog: **585 strings**.

Integrity:
- repo-wide search: 0 occurrences of the earlier bad file-reference error text;
- use `translations/map-story/INDEX.md` as canonical committed inventory;
- all previously repaired manifests remain present on `main`.

**Next chat:** audit the exact remaining 585 source-map strings, then translate Battle Tent leftovers and remaining optional/post-game gaps. Do not reopen font/pointer/catalog research unless patch/build QA exposes a real blocker. Still no ROM patch/pointer-write step yet.


## Translation pass — map/story catalog complete (2026-10-07)

Đã hoàn tất **toàn bộ 585 map/story string còn lại** từ checkpoint 3,776 / 4,361.

Audit mới:
- thêm `tools/audit_remaining_map_story.py`;
- workflow xuất `map-story-remaining.json` + `map-story-remaining-summary.txt`;
- catalog authoritative xác nhận trước batch cuối: **4,270 / 4,361**, còn đúng **91** label;
- cả 91 label đều thuộc `BattleFrontier_BattleTowerMultiPartnerRoom`;
- manifest cuối chứa đúng 91 label đó và đã qua QA placeholder / `\p` / terminator.

Các batch đóng backlog 585:
- Trainer Hill: **27**
- S.S. Tidal: **48**
- Route 105 + Desert Underpass + Mirage Tower: **8**
- Cave of Origin / Wallace: **6**
- Battle Frontier Exchange + Lounges 2/3/5/7: **150**
- misc map/story: **5**
- Battle Tower Multi Partner Room: **341**
  - regular partner roster: **250**
  - apprentice/shared roster: **91**

**Coverage map/story hiện tại: 4,361 / 4,361 = 100%.**
**Backlog map/story theo catalog: 0.**

Lưu ý QA/CI:
- workflow từng đỏ không phải do batch dịch mới mà vì validator đếm `sootopolis.vi.json.gz` như một manifest độc lập và báo duplicate với `sootopolis.vi.json`;
- validator đã được sửa để chỉ xem các manifest JSON canonical, bỏ qua bản nén convenience duplicate.

### Bước tiếp theo

Map/story đã xong ở mức **manifest/source QA**, nhưng **chưa được áp toàn bộ vào ROM**.

Tiếp theo:
1. dùng v0.4 làm baseline;
2. ghép 4,361 bản dịch map/story vào shipping-verified catalog;
3. inplace khi vừa allocation; chỉ relocate/repoint đúng reference đã xác minh khi cần;
4. tiếp tục các nhóm còn lại: system-text → Arena-only → system/UI/battle user-facing;
5. build candidate ROM rồi QA title/intro/overworld/battle/post-battle/save-load/story/post-game.

Nguyên tắc vẫn giữ: **không screenshot-by-screenshot patch, không mass-repoint, không ghi pointer khi chưa có provenance.**


## Integration planning checkpoint — 2026-10-07

Map/story translation remains **4,361 / 4,361 (100%)**.

Added:
- `tools/plan_map_story_integration.py`
- workflow step **Plan map story integration**

The planner:
- requires exactly 4,361 map/story catalog rows;
- rejects duplicate, missing or extra translation labels;
- joins each canonical manifest label to source/shipping catalog metadata;
- marks rows as ready only when a shipping offset is explicitly verified;
- does **not** modify ROM bytes;
- performs **0 pointer writes** and no mass-repoint.

The workflow now emits:
- `map-story-integration-plan.json`
- `map-story-integration-summary.json`

Binary integration is still blocked in this chat because the clean shipping Arena ROM and the tested v0.4 baseline binary are not available in the current Project/Library workspace. Do not infer or recreate those bytes from documentation alone.


## System-text checkpoint — 2026-10-07

Authoritative translation coverage:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **131 / 2,319**
  - core services/news/events: 62
  - save/PC/items/Birch/Surf/Mystery Gift/Shoal Cave/Southern Island: 69

Shipping-layout checkpoint CI #116 PASS:
- restored verified shipping offsets: map-story 4,361; system-text 2,319;
- map/story integration planner: **4,361 / 4,361 ready:verified-shipping-offset**;
- no ROM modification, pointer scan, pointer write, or mass-repoint.

Latest system-text batch is committed; continue with remaining **2,188** system-text strings, prioritizing player-facing shared systems before trainer chatter.


## System-text checkpoint — 295 / 2,319 — 2026-10-07

New completed manifests:
- \`translations/system-text/cable-club.vi.json\`: **82**
- \`translations/system-text/move-tutors.vi.json\`: **41**
- \`translations/system-text/berries.vi.json\`: **41**

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **295 / 2,319**
- remaining system-text: **2,024**

The three new manifests contain **164** player-facing system-text strings. Source-side QA preserved placeholder/control-token order and terminators; all three manifests parse as valid JSON. No ROM bytes or pointers were modified.


## System-text checkpoint — 398 / 2,319 — 2026-10-07

Additional completed manifests after the 295 checkpoint:
- \`translations/system-text/trick-house-mechadolls.vi.json\`: **45**
- \`translations/system-text/secret-base-trainers.vi.json\`: **30**
- \`translations/system-text/frontier-brain.vi.json\`: **28**

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **398 / 2,319**
- remaining system-text: **1,921**

Current validation state:
- Cable Club corrected control-code escape commit: CI #121 PASS.
- Berry batch: CI #123 PASS.
- Trick House / Secret Base / Frontier Brain manifests parse as valid JSON; later CI runs are still processing.
- No ROM bytes or pointers were modified.


## System-text checkpoint — 488 / 2,319 — 2026-10-07

Completed in this batch:
- `translations/system-text/contest-painting.vi.json`: **27**
- `translations/system-text/pokedex-rating.vi.json`: **25**
- `translations/system-text/mauville-man-giddy.vi.json`: **18**
- `translations/system-text/contest-link.vi.json`: **11**
- `translations/system-text/check-furniture.vi.json`: **7**
- `translations/system-text/record-mix.vi.json`: **2**

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **488 / 2,319**
- remaining system-text: **1,831**

All six manifests were source-catalog QA checked for exact label coverage, placeholder/control-token order and terminators before commit, then fetched back from GitHub `main` and parsed successfully. No ROM bytes or pointers were modified.


## System-text checkpoint — 688 / 2,319 — 2026-10-07

Completed after the 488 checkpoint:
- `contest_strings.inc`: **200 / 200**
  - `translations/system-text/contest-strings-effects.vi.json`: 50
  - `translations/system-text/contest-strings-core.vi.json`: 50
  - `translations/system-text/contest-strings-results-a.vi.json`: 50
  - `translations/system-text/contest-strings-results-b.vi.json`: 50

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **688 / 2,319**
- remaining system-text: **1,631**

Contest source QA:
- exact source labels: **200 / 200**
- missing labels: **0**
- extra labels: **0**
- placeholder/control-token order mismatches: **0**
- all four manifests fetched back from GitHub `main` and parsed successfully.

No ROM bytes or pointers were modified.


## System-text checkpoint — 864 / 2,319 — 2026-10-07

Completed after the 688 checkpoint:
- `data/text/match_call.inc`: **176 / 176**
  - `translations/system-text/match-call-01.vi.json`: 44
  - `translations/system-text/match-call-02.vi.json`: 44
  - `translations/system-text/match-call-03.vi.json`: 44
  - `translations/system-text/match-call-04.vi.json`: 44

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **864 / 2,319**
- remaining system-text: **1,455**

Match Call source QA:
- exact source labels: **176 / 176**
- missing labels: **0**
- extra labels: **0**
- placeholder/control-token order mismatches: **0**
- missing terminators: **0**
- all four final manifests fetched back from GitHub `main` and parsed successfully.

No ROM bytes or pointers were modified.


## System-text checkpoint — 944 / 2,319 — 2026-10-07

Completed in this pass:
- `data/text/match_call.inc`: **176 / 176**
  - four manifests × 44 strings
  - CI #139 PASS
- `data/text/apprentice.inc`: **80 / 288**
  - `translations/system-text/apprentice-01.vi.json`: 40
  - `translations/system-text/apprentice-02.vi.json`: 40

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **944 / 2,319**
- remaining system-text: **1,375**

Source QA for the new translations:
- Match Call: 176/176 exact labels, 0 missing/extra, 0 placeholder/control-token mismatches, 0 missing terminators.
- Apprentice rows 1-80: exact source-slice coverage, 0 placeholder/control-token mismatches.
- All committed manifests were fetched back from GitHub `main` and parsed successfully.

No ROM bytes or pointers were modified.
