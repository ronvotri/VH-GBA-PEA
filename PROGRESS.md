# Tiến độ Việt hóa Pokémon Emerald Arena

Cập nhật: 2026-10-06

## Baseline đã chốt

**v0.3 – No Repoint / Dấu Tiếng Việt**

Người test đã xác nhận:

- [x] Logo Pokémon đầu game bình thường.
- [x] Intro khởi động bình thường.
- [x] Font tiếng Việt có dấu hoạt động.
- [x] Battle đầu tiên chạy.
- [x] Sau battle quay lại overworld và chơi tiếp được.
- [x] Không còn freeze hậu battle như Test 1/2.
- [x] Không repoint pointer ở baseline ổn định.

SHA-256 v0.3:

`8234d3945fc6d3a87a9669887a114114904b85c00fd9b3ddd026aaea40d636ec`

## Pass mới: v0.4 – Text Cluster Pass

Mục tiêu của pass này là xử lý nhóm câu mà v0.3 cố tình bỏ qua do **nhiều label/string dùng chung suffix hoặc chồng lấn vùng text**.

Kết quả build:

- [x] Khôi phục thêm **462 cụm text shared/overlap** từ bản dịch cũ.
- [x] Chỉ chép **byte text** trong các cụm đã xác minh.
- [x] **Không ghi pointer mới**.
- [x] Vùng startup/title trước `0x1F0000` giữ nguyên byte-for-byte so với v0.3.
- [x] Mọi byte thay đổi mới đều nằm trong các cluster text được chấp nhận.
- [ ] Cần người chơi test lại logo + intro + battle + hậu battle trước khi nâng v0.4 thành baseline.

SHA-256 v0.4 candidate:

`c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`

## Tình trạng còn lại

Vấn đề chính vẫn là **độ phủ bản dịch**: vẫn còn text tiếng Anh ở những chuỗi:

1. bản AowVN không có bản dịch tương ứng;
2. bản dịch dài hơn allocation gốc;
3. text mới do Emerald Arena thêm riêng;
4. reference cần repoint nhưng chưa được chứng minh chắc chắn là script/code thật.

Từ v0.3 trở đi **không quay lại cách quét/repoint pointer toàn ROM**, vì phương pháp đó từng gây vỡ logo và freeze hậu battle.

## Chiến lược hoàn thiện

### Pass A — catalog an toàn
- [x] Xác định baseline ROM Arena 0.13.0.
- [x] Giữ font AowVN đã hiển thị tiếng Việt đúng.
- [x] Khóa vùng startup/title khỏi mọi patch text.
- [x] Tách riêng nhóm text overlap/shared và xử lý bằng cluster pass.
- [ ] Catalog toàn bộ string được script/code tham chiếu thật sự.
- [ ] Loại substring/suffix target và pointer giả.

### Pass B — phủ bản dịch Emerald gốc
- [x] Chép các câu vừa allocation ở chế độ in-place.
- [x] Khôi phục thêm text shared/overlap không cần repoint ở v0.4.
- [ ] Viết lại tiếng Việt gọn cho chuỗi dài nhưng vẫn tự nhiên.
- [ ] Chỉ dùng text pool/repoint với reference đã xác minh là script/code thật.
- [ ] Quét và xử lý nốt các đoạn story/map còn English.
- [ ] Không sửa graphics, battle engine hoặc bảng dữ liệu gameplay.

### Pass C — text riêng Emerald Arena
- [ ] UI real-time battle.
- [ ] Hướng dẫn điều khiển Arena.
- [ ] HUD/status/battle messages mới.
- [ ] Text/options mới không tồn tại trong Emerald vanilla.

### Pass D — QA
- [x] Logo/title trên v0.3.
- [x] Battle đầu + hậu battle trên v0.3.
- [ ] Re-test v0.4: title → intro → overworld → battle → post-battle.
- [ ] Littleroot / Route 101 / Oldale / Route 103.
- [ ] Petalburg → Rustboro → Dewford.
- [ ] Menu / Bag / Pokémon / Pokédex.
- [ ] Save / load / tiếp tục game.
- [ ] Battle dài / faint / level up / item / capture.
- [ ] Toàn bộ main story và post-game.

## Nguyên tắc release

Không gọi bản là "hoàn thiện" chỉ vì boot được. Bản release cuối phải đồng thời:

- không lỗi logo/title;
- không crash/freeze;
- không còn Anh–Việt xen kẽ ở nội dung người chơi nhìn thấy;
- font dấu hiển thị ổn định;
- giữ nguyên gameplay của Emerald Arena 0.13.0.

## Lịch sử test

| Bản | Kết quả |
|---|---|
| Test 1 | Có dấu nhưng corrupt logo + crash intro |
| Test 2 | Logo vẫn lỗi, text lẫn Anh–Việt, freeze hậu battle |
| Test 3 | Không repoint rộng nhưng vẫn còn lỗi do nền vá cũ |
| Test 4 | Gameplay ổn, logo ổn, nhưng chủ yếu không dấu |
| v0.1 | Nền gameplay ổn định, độ phủ đầu game tăng |
| v0.2 | Có dấu hơn nhưng repoint vẫn làm logo lỗi |
| **v0.3** | **Baseline đã xác nhận: logo ổn + battle/post-battle ổn + font dấu** |
| **v0.4 candidate** | **Thêm 462 cụm text shared/overlap, 0 pointer write; chờ test gameplay** |
