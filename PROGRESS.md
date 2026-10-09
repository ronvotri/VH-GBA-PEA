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


## System-text checkpoint — 1,152 / 2,319 — 2026-10-08

Completed:
- `data/text/apprentice.inc`: **288 / 288**
  - `apprentice-01.vi.json`: 40
  - `apprentice-02.vi.json`: 40
  - `apprentice-03.vi.json`: 40
  - `apprentice-04.vi.json`: 40
  - `apprentice-05.vi.json`: 40
  - `apprentice-06.vi.json`: 40
  - `apprentice-07.vi.json`: 40
  - `apprentice-08.vi.json`: 8

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **1,152 / 2,319**
- remaining system-text: **1,167**

The eight Apprentice manifests were fetched back from GitHub `main`; total unique labels = **288**, with no duplicate manifest labels. No ROM bytes or pointers were modified.


## System-text checkpoint — 1,232 / 2,319 — 2026-10-08

Completed after the 1,152 checkpoint:
- `data/text/tv.inc` system-text rows **1-80 / 336**
  - `translations/system-text/tv-01.vi.json`: 40
  - `translations/system-text/tv-02.vi.json`: 40

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **1,232 / 2,319**
- remaining system-text: **1,087**

Validation:
- Apprentice rows 1-240 are already CI PASS through #145; final Apprentice runs #146-147 are processing.
- TV manifests were fetched back from GitHub `main` and parse successfully with 40 strings each.
- No ROM bytes or pointers were modified.


## System-text checkpoint — 1,272 / 2,319 — 2026-10-08

TV progress:
- `data/text/tv.inc` system-text subset: **120 / 336**
  - `tv-01.vi.json`: 40
  - `tv-02.vi.json`: 40
  - `tv-03.vi.json`: 40

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **1,272 / 2,319**
- remaining system-text: **1,047**
  - TV: **216**
  - trainers: **831**

`tv-03.vi.json` was fetched back from GitHub `main` and parses with exactly 40 translations. CI runs for final Apprentice and current TV chunks are processing; earlier Apprentice chunks through row 240 are PASS. No ROM bytes or pointers were modified.


## System-text checkpoint — 1,488 / 2,319 — 2026-10-08

Completed:
- `data/text/tv.inc` system-text subset: **336 / 336**
  - `tv-01.vi.json` through `tv-08.vi.json`: 40 strings each
  - `tv-09.vi.json`: 16 strings

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **1,488 / 2,319**
- remaining system-text: **831**

TV repository QA:
- all nine manifests fetched back from GitHub `main`
- total unique TV labels: **336**
- duplicate manifest labels: **0**
- all source slices were validated for placeholder/control-token order and terminators before commit

Only `data/text/trainers.inc` remains in system-text. No ROM bytes or pointers were modified.


## System-text checkpoint — 1,608 / 2,319 — 2026-10-08

Completed after the 1,488 checkpoint:
- `data/text/trainers.inc`: **120 / 831**
  - `trainers-01.vi.json`: 40
  - `trainers-02.vi.json`: 40
  - `trainers-03.vi.json`: 40

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **1,608 / 2,319**
- remaining system-text: **711**

All three trainer slices were validated for exact placeholder/control-token order and terminators before commit. GitHub `main` remains authoritative. No ROM bytes or pointers were modified.


## System-text checkpoint — 1,928 / 2,319 — 2026-10-08

Trainer progress:
- `data/text/trainers.inc`: **440 / 831**
- `trainers-01.vi.json` through `trainers-11.vi.json`: 40 strings each

Coverage now:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **1,928 / 2,319**
- remaining system-text: **391**

Repository QA:
- all 11 trainer manifests fetched back from GitHub `main`
- total unique trainer labels committed: **440**
- duplicate trainer manifest labels: **0**
- all source slices validated for control-token order and terminators before commit

No ROM bytes or pointers were modified.


## SYSTEM-TEXT COMPLETE — 2,319 / 2,319 — 2026-10-08

Completed final source block:
- `data/text/trainers.inc`: **831 / 831**
  - `trainers-01.vi.json` through `trainers-20.vi.json`: 40 strings each
  - `trainers-21.vi.json`: 31 strings

Final system-text coverage:
- map/story: **4,361 / 4,361 (100%)**
- Arena-only: **46 / 46 (100%)**
- system-text: **2,319 / 2,319 (100%)**
- remaining system-text: **0**

Trainer completion QA:
- source catalog contains exactly **831 unique trainer labels**
- trainer manifests cover source rows **1-831** in contiguous bounded slices
- all **21 trainer manifests** are present on GitHub `main`
- each source slice was checked for placeholder/control-token order and terminators before commit
- no ROM bytes, pointers, or mass-repoint operations were performed during translation-only work

Next localization phase is **not** more system-text. Continue with the remaining user-facing categories, primarily `system-ui` and `battle`, using the same source-catalog sweep approach.


## System-UI started — 66 / 8,279 — 2026-10-08

First completed system-ui group:
- `src/data/text/trainer_class_names.h`: **66 / 66**
- manifest: `translations/system-ui/trainer-class-names.vi.json`

System-ui coverage:
- translated: **66 / 8,279**
- remaining: **8,213**

Translation choices:
- canonical names/terms such as TEAM AQUA, TEAM MAGMA, ELITE FOUR, LEADER, CHAMPION and {PKMN} TRAINER are retained where appropriate
- ordinary trainer classes are localized into concise Vietnamese suitable for UI width
- anonymous catalog source identities are used as manifest keys
- placeholders are preserved

System-text remains complete at **2,319 / 2,319**. No ROM bytes or pointers were modified.


## Canonical Pokémon terminology rule — 2026-10-08

Do **not** translate canonical Pokémon terms used as names/identifiers:
- Pokémon species names
- move names
- item names
- TM/HM names and identifiers

Translate surrounding UI/help/description text, but keep those canonical names exactly in English. This rule is authoritative for all remaining `system-ui` and `battle` work.


## System-UI checkpoint — 461 / 8,279 — 2026-10-08

Completed/reviewed system-ui groups:
- Trainer class names: **66 / 66**
- Ability names + descriptions: **155 / 155**
  - Ability names intentionally retain canonical English names.
  - Ability descriptions localized.
- Move descriptions: **240 / 355 catalog rows processed**
  - translated named descriptions: **240**
  - canonical MOVE names remain English and are not localized

Authoritative terminology rule:
- keep Pokémon species names in English
- keep MOVE names in English
- keep ITEM names in English
- keep TM/HM names and identifiers in English
- translate descriptive/help/UI prose around those canonical terms

System-ui coverage counted in committed manifests: **461 / 8,279**
Remaining system-ui: **7,818**

No ROM bytes or pointers were modified.


## System-UI checkpoint — 655 / 8,279 — 2026-10-08

Completed/reviewed:
- Trainer class names: **66 / 66**
- Ability names + descriptions: **155 / 155**
- Move descriptions: **354 / 354 real descriptions complete**
  - 9 manifests
  - empty/null sentinel intentionally excluded
- Item descriptions: **80 translated**
  - `item-descriptions-01.vi.json`: 40
  - `item-descriptions-02.vi.json`: 40

Canonical terminology rule remains mandatory:
- Pokémon species names stay English
- MOVE names stay English
- ITEM names stay English
- TM/HM names and identifiers stay English
- descriptive/help/UI prose is translated

System-ui committed coverage: **655 / 8,279**
Remaining system-ui: **7,624**

No ROM bytes or pointers were modified.


### Pre-pass GitHub sync — 2026-10-08
Confirmed `main` is synchronized before continuing localization:
- system-text: **2,319 / 2,319**
- system-ui committed: **655 / 8,279**
- move descriptions: **354 / 354 real descriptions complete**
- item descriptions: **80 / 309**
- canonical Pokémon / MOVE / ITEM / TM / HM names remain English


## System-UI checkpoint — 884 / 8,279 — 2026-10-08

Completed/reviewed:
- Trainer class names: **66 / 66**
- Ability names + descriptions: **155 / 155**
- Move descriptions: **354 / 354 real descriptions complete**
- Item descriptions: **309 / 309 real descriptions complete**
  - 8 manifests: 40 + 40 + 40 + 40 + 40 + 40 + 40 + 29
  - dummy/null sentinel intentionally excluded

Canonical terminology remains mandatory:
- Pokémon species names stay English
- MOVE names stay English
- ITEM names stay English
- TM/HM names and identifiers stay English
- descriptive/help/UI prose is translated

System-ui committed coverage: **884 / 8,279**
Remaining system-ui: **7,395**

No ROM bytes or pointers were modified.


## System-UI checkpoint — 1,004 / 8,279 — 2026-10-08

Completed/reviewed:
- Trainer class names: **66 / 66**
- Ability names + descriptions: **155 / 155**
- Move descriptions: **354 / 354 real descriptions**
- Item descriptions: **309 / 309 real descriptions**
- Decoration descriptions: **120 / 120 complete**

Decoration QA:
- 3 manifests fetched back from GitHub `main`
- total unique decoration description labels: **120**
- duplicate labels: **0**
- canonical Pokémon / MOVE / ITEM names remain English
- source line-break counts preserved

System-ui committed coverage: **1,004 / 8,279**
Remaining system-ui: **7,275**

No ROM bytes or pointers were modified.


### Pre-pass GitHub sync — 2026-10-08
Confirmed `main` is synchronized before continuing:
- system-text: **2,319 / 2,319**
- system-ui committed: **1,004 / 8,279**
- move descriptions: **354 / 354**
- item descriptions: **309 / 309**
- decoration descriptions: **120 / 120**
- canonical Pokémon / MOVE / ITEM / TM / HM names remain English


## System-UI checkpoint — 1,124 / 8,279 — 2026-10-08

New completed work:
- Pokédex descriptive text: **120 / 387**
  - `pokedex-text-01.vi.json`: 40
  - `pokedex-text-02.vi.json`: 40
  - `pokedex-text-03.vi.json`: 40

Pokédex QA:
- 120 unique labels
- duplicate labels: 0
- all 120 entries preserve the source 4-line structure (3 `\n` tokens)
- Pokémon species names and canonical MOVE / ITEM / TM / HM names remain English

System-ui committed coverage: **1,124 / 8,279**
Remaining system-ui: **7,155**

No ROM bytes or pointers were modified.


## System-UI checkpoint — 1,204 / 8,279 — 2026-10-08

Pokédex descriptive text:
- `src/data/pokemon/pokedex_text.h`: **200 / 387**
- manifests `pokedex-text-01.vi.json` through `pokedex-text-05.vi.json`

QA:
- **200 unique Pokédex labels**
- duplicate labels: **0**
- all entries preserve the source 4-line structure (3 `\n` tokens)
- TENTACOOL layout defect found during QA was corrected in commit `df95c80`
- Pokémon species / MOVE / ITEM / TM / HM names remain canonical English

System-ui committed coverage: **1,204 / 8,279**
Remaining system-ui: **7,075**

No ROM bytes or pointers were modified.


### Pre-pass GitHub sync — 2026-10-08
Confirmed `main` before continuing Pokédex work:
- system-text: **2,319 / 2,319**
- system-ui checkpoint previously: **1,124 / 8,279**
- Pokédex text now committed through row **160 / 387**
- TENTACOOL layout fix is committed
- canonical Pokémon / MOVE / ITEM / TM / HM names remain English


## System-UI checkpoint — 1,391 / 8,279 — 2026-10-08

Completed/reviewed player-facing system-ui groups:
- Trainer class names: **66 / 66**
- Ability names + descriptions: **155 / 155**
- Move descriptions: **354 / 354 real descriptions**
- Item descriptions: **309 / 309 real descriptions**
- Decoration descriptions: **120 / 120**
- Pokédex descriptive text: **387 / 387 complete**

Pokédex QA:
- 10 manifests fetched back from GitHub `main`
- total labels: **387**
- duplicate labels: **0**
- malformed four-line entries: **0**
- TENTACOOL line-layout defect was fixed before completion
- canonical Pokémon / MOVE / ITEM / TM / HM names remain English

System-ui committed coverage: **1,391 / 8,279**
Remaining system-ui: **6,888**

No ROM bytes or pointers were modified.

## System-UI checkpoint — 1,527 / 8,279 — 2026-10-08

Added two QA-clean player-facing `src/strings.c` batches:
- Pokédex search/sort UI: **64**
- Hall of Fame + core Bag/menu UI: **72**

New manifests:
- `translations/system-ui/strings-pokedex-ui.vi.json`
- `translations/system-ui/strings-hof-bag-core.vi.json`

Coverage now:
- system-text: **2,319 / 2,319 (100%)**
- system-ui: **1,527 / 8,279**
- remaining system-ui: **6,752**

Source QA for the 136 new entries:
- exact manifest labels found in pinned `src/strings.c`: **136 / 136**
- missing source labels: **0**
- placeholder/control-token-order mismatches: **0**

Canonical Pokémon / MOVE / ITEM / TM / HM names and identifiers remain English. Translation-only work has not modified ROM bytes or pointers. Continue `src/strings.c` from `gText_ItemFinderNearby` onward.

## System-UI checkpoint — 1,599 / 8,279 — 2026-10-08

Added:
- `translations/system-ui/strings-items-berries-shop-01.vi.json`: **72** entries
- scope: ITEMFINDER/TM-HM use text, Bag pocket labels, Berry/Pokéblock UI, and the first shop dialogue slice

Coverage:
- system-ui: **1,599 / 8,279**
- remaining system-ui: **6,680**

QA:
- exact labels found in pinned `src/strings.c`: **72 / 72**
- placeholder/control-token-order mismatches: **0**
- no ROM bytes or pointers modified

Continue from the next shop-dialogue string after `gText_Var1AndYouWantedVar2`.

## System-UI checkpoint — 1,800 / 8,279 — 2026-10-08

Continued the player-facing `src/strings.c` sweep with three manifests:
- shop / party / move-learning UI: **73**
- party / field-move / participation / trade checks: **64**
- summary stats / Egg-Nature info / registry / decoration UI: **64**

This pass adds **201** system-ui strings.

Coverage now:
- system-text: **2,319 / 2,319 (100%)**
- system-ui: **1,800 / 8,279**
- remaining system-ui: **6,479**

QA:
- source labels found: **201 / 201**
- placeholder/control-token-order mismatches after correction: **0**
- no ROM bytes or pointers modified

Continue from the next `src/strings.c` string after `gText_Mat`.

## System-UI checkpoint — 1,857 / 8,279 + Battle 7 / 2,223 — 2026-10-08

Processed the next `src/strings.c` slice through `gText_TypesOfContests`, then corrected category ownership for labels containing `battle`.

Coverage:
- system-text: **2,319 / 2,319 (100%)**
- system-ui: **1,857 / 8,279**
- battle: **7 / 2,223**
- remaining system-ui: **6,422**
- remaining battle: **2,216**

Catalog-scope correction:
- 7 labels were moved into `translations/battle/strings-shared-ui-01.vi.json`
- these rows are classified as battle by `tools/build_source_text_catalog.py` even though they physically live in `src/strings.c`

Validator fix:
- empty source sentinel → empty translation is allowed
- non-empty source → empty translation remains an error

QA remains clean for source labels and placeholder/control-token order. No ROM bytes or pointers modified. Continue after `gText_TypesOfContests`.

## System-UI / Battle checkpoint — 1,918 / 8,279 + 10 / 2,223 — 2026-10-08

Processed the next 64 `src/strings.c` rows after `gText_TypesOfContests`:
- **61 system-ui**
- **3 battle** mode labels

Coverage:
- system-ui: **1,918 / 8,279**
- battle: **10 / 2,223**
- remaining system-ui: **6,361**
- remaining battle: **2,213**

QA:
- source labels: **64 / 64**
- placeholder/control-token-order mismatches: **0**
- catalog scope mismatches: **0**

Continue after `gText_YellowShard`. No ROM bytes or pointers modified.

## System-UI / Battle checkpoint — 2,265 / 8,279 + 23 / 2,223 — 2026-10-08

Continued `src/strings.c` through `gText_AndFillOutTheQuestionnaire`.

This pass processed **360 source rows**:
- **347 system-ui**
- **13 battle**

New system-ui manifests:
- `strings-menu-frontier-prizes-01.vi.json`: 70
- `strings-link-frontier-help-01.vi.json`: 63
- `strings-elevator-box-01.vi.json`: 72
- `strings-pc-pokenav-01.vi.json`: 71
- `strings-pokenav-easychat-01.vi.json`: 71

Battle-classified labels were added to:
- `translations/battle/strings-shared-ui-01.vi.json`

Coverage:
- system-ui: **2,265 / 8,279**
- battle: **23 / 2,223**
- remaining system-ui: **6,014**
- remaining battle: **2,200**

QA:
- exact source labels: **360 / 360**
- placeholder/control-token-order mismatches: **0**
- catalog scope mismatches: **0**
- no ROM bytes or pointers modified

Continue after `gText_AndFillOutTheQuestionnaire`.

## System-UI / Battle checkpoint — 2,695 / 8,279 + 89 / 2,223 — 2026-10-08

Continued `src/strings.c` through `gJPText_Sama`.

This pass processed **496 source rows**:
- **430 system-ui**
- **66 battle**

New system-ui manifests:
- `strings-easychat-save-rtc-01.vi.json`: 69
- `strings-roulette-bp-prizes-01.vi.json`: 72
- `strings-trainercard-contest-input-01.vi.json`: 59
- `strings-chat-matchcall-berrycrush-01.vi.json`: 67
- `strings-frontierpass-minigames-01.vi.json`: 38
- `strings-mysterygift-frontier-records-01.vi.json`: 60
- `strings-options-link-event-01.vi.json`: 65

Battle additions were merged into:
- `translations/battle/strings-shared-ui-01.vi.json`: now **89** strings total

Coverage:
- system-ui: **2,695 / 8,279**
- battle: **89 / 2,223**
- remaining system-ui: **5,584**
- remaining battle: **2,134**

QA:
- missing source labels: **0**
- placeholder/control-token-order mismatches: **0**
- catalog scope mismatches: **0**
- no ROM bytes or pointers modified

Continue after `gJPText_Sama`.

## System-UI / Battle checkpoint — 3,071 / 8,279 + 96 / 2,223 — 2026-10-08

This pass processed **383 source rows**:
- **376 system-ui**
- **7 battle**

Major milestone: the current `src/strings.c` sweep has reached **EOF**.

Additional complete/reviewed source groups in this pass:
- `src/mystery_event_msg.c`
- `src/text_input_strings.c`
- Battle Pyramid popup strings in `src/map_name_popup.c`
- `src/berry_fix_program.c`
- player-facing local string in `src/mystery_gift_scripts.c`
- text definitions in `src/data/trade.h`

Coverage:
- system-ui: **3,071 / 8,279**
- battle: **96 / 2,223**
- remaining system-ui: **5,208**
- remaining battle: **2,127**

QA:
- missing source labels/identities: **0**
- placeholder/control-token-order mismatches: **0**
- catalog scope mismatches: **0**
- static/local strings use source identity keys where labels may be ambiguous
- no ROM bytes or pointers modified

Continue with the next bounded player-facing system-ui source group; do not reopen completed source files without a concrete QA defect.

## System-UI / Battle checkpoint — 3,272 / 8,279 + 122 / 2,223 — 2026-10-08

Completed `src/data/union_room.h`: **227 / 227 source rows**.
- system-ui: **201**
- battle: **26**

Coverage now:
- system-ui: **3,272 / 8,279**
- battle: **122 / 2,223**
- remaining system-ui: **5,007**
- remaining battle: **2,101**

Since the previous 2,695 checkpoint this session added:
- **577 system-ui**
- **33 battle**
- **610 total source rows**

Union Room QA:
- source identities: **227 / 227**
- placeholder/control-token-order mismatches after corrections: **0**
- catalog scope mismatches: **0**

Other source groups completed this session include the remainder of `src/strings.c`, Mystery Event messages, text-input keyboards, Berry Program Update, trade-screen local text and Battle Pyramid popup labels.

No ROM bytes or pointers modified. Continue with the next bounded player-facing system-ui source group; prioritize visible prose/status/menu text and avoid reopening completed groups without a concrete QA defect.

## System-UI / Battle checkpoint — 6,020 / 8,279 + 191 / 2,223 — 2026-10-08

Broad source-driven pass completed **2,817 source rows** since the 3,272 / 122 checkpoint:
- **+2,748 system-ui**
- **+69 battle**

Coverage:
- system-ui: **6,020 / 8,279**
- battle: **191 / 2,223**
- remaining system-ui: **2,259**
- remaining battle: **2,032**

Major completed/reviewed groups:
- Berry Blender: 39
- misc local strings: 18
- Easy Chat system-ui vocabulary: 942
- Easy Chat battle vocabulary: 66
- Ribbon descriptions: 19
- Gift Ribbon: 46 system-ui + 1 battle
- Hoenn landmarks: 42 reviewed/canonical retained
- Berry descriptions: 86
- Pokédex category names: 387 / 387
- species names: 412 / 412 canonical retained
- MOVE names: 355 / 355 canonical retained
- ITEM names: 377 / 377 canonical retained
- Nature names: 25 / 25 localized

QA is source-driven and clean for these groups. A temporary 4,870 running total was corrected during reconciliation; it had double-counted the 19 standard Ribbon rows. The authoritative system-ui total is **6,020**.

No ROM bytes/pointers modified. Continue with the remaining 2,259 player-facing system-ui catalog rows, then battle.



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

## Safe binary integration engineering — 2026-10-09

Translation source/manifest phase **17,512 / 17,512 COMPLETE** (validated by GitHub Actions). Work shifted to **ROM integration readiness**, without modifying any ROM bytes.

From planner CI PASS `37827126689`:
- Source-changed player-facing rows: **13,097**
- Source-identical player-facing rows: **4,415**; none assumed a safe v0.4 no-op
- Verified shipping offset: **6,680** (6,557 source-changed, 123 source-identical)
- Still unresolved shipping offset: **10,832** (6,540 source-changed, 4,292 source-identical)
- v0.4 baseline byte comparisons: **0** (ROM unavailable)
- Safe binary writes/skips authorized: **0**

Added `tools/verify_local_rom_baselines.py`, `tools/audit_v04_verified_offsets.py`, safety regression tests and a GitHub Actions pre-build unit-test step. Test step passed after fixture correction in run `37827836450`; full workflow was still in progress at the time of update. See `docs/SAFE_ROM_INTEGRATION.md` for read-only commands, pinned hashes, exact blocking requirements, and runtime QA matrix.

No new patched ROM has been generated; clean ROM and v0.4 baseline bytes are required for the next binary integration gate. Do not upload ROMs to the public GitHub repository.


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


## Guarded recovery status — 2026-10-09
Engineering detail: docs/GUARDED_ROM_REPAIR_2026-10-09.md. Exact private candidate SHA256 5ec43ea41192e473939002d3ed809cd84d650e51e583124bd175f7f503dda6b3. All 64 known historical source pointer sites verified against clean ROM; 212 shared-suffix translations saved via individually verified owner relocations into pointer-free FF space; 29 additional source-manifest entries installed; 916 long translated text spans reflowed without length increase; 58 multi-reference/distant-source cases deferred. BPS/CRC and byte replay PASS. No emulator test and no public build: not release-ready.


## 2026-10-09 — Next binary integration checkpoint (UI43 and shared13)
New **internal** SHA-locked ROM derived from guarded recovery (`5ec43ea41192e473939002d3ed809cd84d650e51e583124bd175f7f503dda6b3`), output `187993098e11317873043a70751cd9009fc1556a8a46a550f017be233a2ec05e`: **43** new short English-to-accented-Vietnamese system-ui replacements (in-place) plus **13** shared-suffix translations in own pointer-free ROM tail text copies (31 verified local owner pointer sites), leaving **45** unresolved shared-suffix cases. Original 64 pointer corrections preserved; independent QA caught and rejected two initially proposed cases that would have modified already-restored pointers. Output exact 32MiB replay and bounded write audit PASS; CRC/BPS reconstruction PASS (patch SHA `363151649dd389f4aa2217e7b49257da2325860c3cc03be6f8de593ed35e8d02`, 3741 bytes). No emulator QA; **not release-ready**; original v0.4 preserved. Detailed evidence: [docs/UI43_SHARED13_GUARDED_CHECKPOINT_2026-10-09.md](docs/UI43_SHARED13_GUARDED_CHECKPOINT_2026-10-09.md).


## Read-only owner provenance and codepage QA — 2026-10-09

Exact earlier test2084 ROM + clean/shipping GBA, QA ZIP and CI symbol-map rechecked all 270 shared-suffix candidates. Counts reproduced: 212 single nearby refs, 13 multiple nearby refs, 41 distant/nonpreceding, 2 incidental code-area and 2 already-modified refs. Of the 45 left after previous 212+13 guarded recovery, 39 have plausible named EventScript/table references even though far from their text bytes; 2 are false matches within binary graphics, 2 are false code-word matches that also have a nearby plausible reference, and 2 overlap restored/damaged reference scenarios. New SHA-locked read-only tool with 7 tests: [tools/triage_shared_owner_provenance.py](tools/triage_shared_owner_provenance.py). Detailed [checkpoint](docs/SHARED_OWNER_PROVENANCE_RETRIAGE_2026-10-09.md). In the prior 5,469 source-byte English leftovers, 3,482 contain f/w/z that collide with repurposed Vietnamese glyph bytes (potential rendering risk). **No ROM mutation or new playable output this turn:** latest guarded+UI43+shared13 private binary was not mounted and must be reconstructed before updates; do not regress to older v5-2084. Emulator QA remains outstanding; keep stable v0.4 rollback.



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


## 2026-10-09 — 2,000 SOURCE-COMPILED VIETNAMESE TEXTS (MOVE & ITEM DESCRIPTION QA)

**FULL confirmed SUCCESS** [Actions 37944716925](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37944716925) on recent workflow with word-boundary-only move description `--rebalance`. Exact independently verified source trial GBA SHA256 `9b963b526870ffc5747df39f1eb07d1ba754724f42e3921c58ac13d7cd452efa` (32MiB, **STOCK ENGLISH FONT**, NOT a playable Vietnamese release). Source groups: **1000 map, 41 C UI, 134 PLAYER/RIVAL, 196 scripted battle, 59 C battle, 285 move descriptions and 285 item descriptions = 2000 unique labels, 0 duplicates, all final FF bytes valid**. 39/285 move descriptions were recovered from prior conservative 246 by relocating only a word-boundary newline while preserving full words and 2-line 26-cell limits. 59 move descriptions still cannot fit without rewording; ~5 missing `ỳ`, 2 missing `è`, and other glyphs; 16 item entries with dynamic/control tokens and 2 item descriptions with line-count conflicts left untouched. All source header label/pointer relationships remain compiler-managed. `tools/stage_source_descriptions.py` and `tools/tests/test_stage_source_descriptions.py` include reflow and strict C source guards. All C source description groups independently attested via `tools/verify_compiled_source_strings.py`.

**Read latest checked checkpoint** [docs/SOURCE_LOCALIZATION_1961_MOVE_ITEM_2026-10-09.md](docs/SOURCE_LOCALIZATION_1961_MOVE_ITEM_2026-10-09.md) section `Follow-up confirmed — EXACT 2,000 source-label milestone`, commit `cf2b272`. Do not confuse catalog **17,512 translated source entries** with **2,000 source-installed** experimental rows and certainly not a final ROM. **CORE BLOCKER:** source-built ROM still uses the original English font glyph blocks; must privately graft v0.5 collision-safe font with exact SHA and 5-symbol ownership, then emulator QA of accents, intro truck/Mom, battle, items, save/load. Stable v0.4 rollback unchanged; title credit `Việt hóa bởi Votri Valley` preserved. No user manual testing/technical ZIPs needed yet.


## 2026-10-09 — ALL 354 MOVE DESCRIPTIONS BUILT; ITEM GLYPH FOLLOW-UP

**VERIFIED [Actions #37950847854](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37950847854) FULL SUCCESS:** **2,069 unique compiled source text labels**; `354/354` translated move descriptions accepted, **39** automatically rebalanced to two lines, all 354 byte-coded in v0.5 glyph mapping. Compared against older 2,000-label build: +69 move labels. Wrote **62 contextual/manual overlong move rewrites** across 9 move manifest files and **7 missing-glyph contextual rewrites** (Body Slam, Supersonic, Psybeam, Submission, Splash, Wish, Magical Leaf) across 5 source files. New tests `tools/tests/test_condensed_move_descriptions.py` and `tools/tests/test_complete_move_descriptions.py` lock translated move mechanics and all 354 compact widths. Full source QA still 0 duplicates and valid FF. Read [docs/MOVE_DESCRIPTIONS_354_EDITORIAL_2026-10-09.md](docs/MOVE_DESCRIPTIONS_354_EDITORIAL_2026-10-09.md).

**CURRENT FOLLOW-UP:** Rewrote **7 static item descriptions** with absent glyphs/symbols (`ỷ`, `è`, `ỳ`, `%`, `&`, uppercase `Ố`) directly in `translations/system-ui/item-descriptions-01/02/04/05/06/08.vi.json`. `tools/tests/test_static_item_descriptions.py` enforces 293 static-item authored source rows fit GBA boxes and have no unknown v0.5 glyphs. Current [Actions #37952135212](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37952135212) is configured to require at least **292** integrated item descriptions; pending at checkpoint. **Do not report 2,076 compiled labels until it fully PASSes and source QA confirms actual total.**

**IMPORTANT NEW FONT BREAKAGE FOUND:** Pinned original Latin charmap has fixed `POKEBLOCK = 55 56 57 58 59` and `PKMN = 53 54`. v0.5 glyph aliases still put `đ=0x56` and `ì=0x59` within `POKEBLOCK`. Real 32MiB clean-vs-v0.4 glyph comparison confirms altered native POKEBLOCK pictures in Normal/Narrow/Short/Small. Blind private donor graft `tools/graft_collision_safe_v04_fonts.py` is **NOT SAFE FOR RELEASE** even though English f/w/z were previously protected. **16 item descriptions with `{POKEBLOCK}` remain deliberately blocked** until v0.6 remaps đ/ì into genuinely free 0x33/0x35, restores all stock glyph art 0x55..59 and tests visual output. Read [docs/POKEBLOCK_FONT_TOKEN_COLLISION_2026-10-09.md](docs/POKEBLOCK_FONT_TOKEN_COLLISION_2026-10-09.md). No full new source-built ROM with Vietnamese font exists or has been emulator-tested; safe v0.4 rollback untouched and title credit stays `Việt hóa bởi Votri Valley`.


## 2026-10-09 — V0.6 PKMN/POKEBLOCK FONT SAFETY + 2,093 SOURCE TEXT LABELS VERIFIED

**Read latest checkpoint first:** [docs/V06_POKEBLOCK_SAFE_SOURCE_2026-10-09.md](docs/V06_POKEBLOCK_SAFE_SOURCE_2026-10-09.md), full PASS update commit `fc387ff7`. **GitHub Actions [37960836736](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37960836736) FULL SUCCESS**: unit QA, actual GBA source build, independent stage attestation, title-credit build. Exact label totals: **1000 map/story, 41 C UI, 134 PLAYER/RIVAL map, 196 battle script, 59 C battle, 354 move descriptions (all), 293 static item descriptions, 16 native POKEBLOCK item descriptions = 2,093 source-compiled text labels**, 0 duplicate source labels, all final FF valid. `tools/stage_pokeblock_item_descriptions.py` compiled each of the 16 previously blocked berry/Pokeblock Case descriptions with native literal sequence **55 56 57 58 59**, preserving 3-line description semantics; `tools/verify_compiled_source_strings.py` now attests the native 5-byte token per item. No script pointer mass rewrites.

**CRITICAL FONT REPAIR:** The earlier proposed `ì→0x35` was WRONG: the pinned original Latin charmap has **`'=' = 0x35`**, which previous `line.split('=',1)` occupancy parser failed to recognize. Fixed with `rsplit('=',1)` and a regression test. Tracked v0.6 `checkpoints/v06-pokeblock-safe-codebook.json` remaps **`đ:0x56→0x33`** and **`ì:0x59→0x37`**, preserves **`=` (0x35)**, `LV` 0x34, semicolon 0x36, PKMN 53–54 and native POKEBLOCK 55–59, while retaining v0.5 ASCII f/w/z protection and 137 unique glyph codepoints. Added fail-closed `tools/plan_v06_pokeblock_safe_font.py`, `tools/graft_v06_pokeblock_safe_fonts.py` and tests. Documentation warning at [docs/POKEBLOCK_FONT_TOKEN_COLLISION_2026-10-09.md](docs/POKEBLOCK_FONT_TOKEN_COLLISION_2026-10-09.md) corrected to forbid 0x35.

**REAL PRIVATE FONT-ONLY QA (not source-localized GBA):** exact clean+v0.4 SHA locked, preview graft tested **25 nonblank glyph images across 5 Latin font styles**, **9 synthesized small-font glyphs** from donor Narrow, **6,053 bytes changed ONLY in 5 font/width regions**, original ASCII f/w/z, equals, native PKMN and Pokeblock icons preserved bitwise. Clean-ROM font-only diagnostic SHA256 `a06de5b32aa569dc83439b61dd86c61f546946a6f82008c407fe1086d5569006`. This is not yet a ROM with Vietnamese source text **AND** glyph font art grafted. The compiled source GBA in Actions still uses **STOCK English font pixels** and has not had emulator visual or gameplay QA. **DO NOT DISTRIBUTE AS RELEASE**. Original safe v0.4 remains as rollback; user does not want incremental testing. Required title credit unchanged: `Việt hóa bởi Votri Valley`.

**NEXT:** reproduce/extract the exact v0.6 compiled source ROM and its matching symbol map in a PRIVATE workspace, run SHA-locked `tools/graft_v06_pokeblock_safe_fonts.py`, independently check all 25 glyphs/13 protected token slots/5 widths, visually inspect title + intro truck/Mom, Pokeblock Case/berries, battle and save/load in mGBA; then continue remaining source-manifest integration (17,512 translation rows are NOT yet all installed).


**POST-ARTIFACT VERIFIED:** v0.6 2,093 source-compiled localized trial ROM SHA256 **`5cae1a20698fcd7036ccdc0f2bdbc0c0c80d942380ab48611fb3ec816ebcab7f`**. Use the artifact's **`SOURCE_LEVEL_FONT.sym`** (not baseline `pokeemerald.sym`) for exact transplanted-font target offsets: **SmallNarrow 0x71B59C; Small 0x72379C; Narrow 0x72B99C; Short 0x733B9C; Normal 0x73BD9C**. The source glyph audit validates 5 stock glyph blocks, donor_font_patched=false. The baseline `pokeemerald.sym` 0x71DEA0 etc. describes reference shipping, not compiled localized font addresses; using it would damage the v0.6 ROM. Updated technical detail: [docs/V06_POKEBLOCK_SAFE_SOURCE_2026-10-09.md](docs/V06_POKEBLOCK_SAFE_SOURCE_2026-10-09.md), commit `25eda69d`.

**Next REQUIRED action**: reproduce *this exact source-built 32MiB ROM* in a private workspace, apply `tools/graft_v06_pokeblock_safe_fonts.py` with `--expected-source-sha256 5cae1a...`, and the correct shipping/reference and localized/target `.sym`. Then verify actual GBA rendering and gameplay (Pokeblock, save/load, title credit). No matching source-built GBA full bytes in CI artifact; cannot declare local font graft or a playable end-user v0.6 done. Preserved original v0.4 rollback.


## 2026-10-10 — 2,560 SOURCE-INTEGRATED LABELS (FULL CI SUCCESS, STOCK FONT)

Verified [Actions #37971516257](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37971516257), committed implementation `ce4f4c85`:

| Source stage | Independently verified compiled labels |
| --- | ---: |
| Original v0.6 source build (unchanged) | 2,093 |
| New static map/story group (75 files, 156 wraps) | +292 |
| Safe literal-LF map/story recovery (23 files, 71 wraps) | +175 |
| **Single combined source-compiled trial GBA** | **2,560** |

Combined source-ROM SHA256: `ea47eddda541d66f6aedf9e61f0816e7135349a0b5ac23529776f8ac6a6b5530`. Source font target offsets (`SOURCE_EXPANDED_MAP_FONT.sym`): SmallNarrow `71AB04`, Small `722D04`, Narrow `72AF04`, Short `733104`, Normal `73B304` (hex). All five fonts remain exact stock English glyphs. The original `5cae1a...` / 2,093 source build is preserved separately; compiled source text QA confirms original labels unchanged, additions disjoint, all final FF bytes correct, and no change to title-credit source.

**Not a localized playable GBA.** This stage does not graft donor font artwork or confirm gameplay. The new SHA/offsets must be added to a strictly validated font-layout profile before any private graft; do not disable the original 2,093 SHA guard. Original v0.4 rollback remains intact; no commercial ROM or glyph asset committed. Full details and next action in `CONTINUE_WITH_MODEL.md` latest checkpoint.


## 2026-10-10 — NEW 3,060 COMPILER-INTEGRATED SOURCE TEXTS; CI SUCCESS

Full [GitHub Actions #37972752960](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37972752960) SUCCESS: old 2,560 original/extended source labels retained, **500 new system-text labels** source-staged across 12 `data/text/*.inc` files (190 line wraps), **3,060 unique compiled source labels total**, no duplicates or FF terminator errors. Verified trial GBA SHA256 `583dfab1a17f75f5643e3db962eac891c78197d67517abd990cfe2c059d49f7a`. Matching Latin-font offsets (SmallNarrow/Small/Narrow/Short/Normal): `0x71A904`, `0x722B04`, `0x72AD04`, `0x732F04`, `0x73B104`.

**Important:** Fonts remain the clean English bitmaps and this trial ROM is NOT released or mGBA-verified. Public repository contains only tooling, translation manifests and checkpoint hashes/symbol facts, no commercial ROM. v0.4 stable rollback remains untouched. Exact next steps and artifact filenames recorded in `CONTINUE_WITH_MODEL.md`.

