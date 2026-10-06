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

SHA-256:

`8234d3945fc6d3a87a9669887a114114904b85c00fd9b3ddd026aaea40d636ec`

## Tình trạng hiện tại

Vấn đề còn lại chính là **độ phủ bản dịch**: trong game vẫn có đoạn tiếng Anh xen lẫn tiếng Việt.

Nguyên nhân đã xác định:

1. Một số chuỗi tiếng Việt dài hơn vùng text gốc.
2. Nhiều chuỗi Emerald dùng chung suffix/địa chỉ con bên trong cùng một câu.
3. Quét/repoint pointer toàn ROM có thể nhận nhầm dữ liệu graphics/code và từng làm:
   - vỡ logo Pokémon;
   - crash intro;
   - freeze sau battle.
4. Vì vậy từ v0.3 trở đi không dùng lại phương pháp repoint toàn ROM.

## Chiến lược hoàn thiện

### Pass A — catalog an toàn
- [x] Xác định baseline ROM Arena 0.13.0.
- [x] Giữ font AowVN đã hiển thị tiếng Việt đúng.
- [x] Khóa vùng startup/title khỏi mọi patch text.
- [ ] Catalog toàn bộ string được script/code tham chiếu thật sự.
- [ ] Loại substring/suffix target và pointer giả.

### Pass B — phủ bản dịch Emerald gốc
- [ ] Ghép catalog tiếng Anh Arena với nội dung tiếng Việt AowVN.
- [ ] Chuỗi vừa allocation: ghi tại chỗ.
- [ ] Chuỗi dài: viết lại tiếng Việt gọn nhưng tự nhiên để vừa allocation khi có thể.
- [ ] Chỉ dùng text pool/repoint với reference đã xác minh là script/code thật.
- [ ] Không sửa graphics, battle engine hoặc bảng dữ liệu gameplay.

### Pass C — text riêng Emerald Arena
- [ ] UI real-time battle.
- [ ] Hướng dẫn điều khiển Arena.
- [ ] HUD/status/battle messages mới.
- [ ] Text/options mới không tồn tại trong Emerald vanilla.

### Pass D — QA
- [ ] Intro từ đầu đến khi nhận Pokémon.
- [ ] Littleroot / Route 101 / Oldale / Route 103.
- [ ] Rival battle + hậu battle.
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
| **v0.3** | **Baseline hiện tại: logo ổn + battle/post-battle ổn + có font dấu** |
