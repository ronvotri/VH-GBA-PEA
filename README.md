# Pokémon Emerald Arena – Việt hóa

Dự án Việt hóa **Pokémon Emerald Arena 0.13.0** sang tiếng Việt có dấu.

> Repo này theo dõi mã vá, tài liệu kỹ thuật và tiến độ. Không lưu ROM Pokémon gốc/ROM đầy đủ.

## Trạng thái hiện tại

**Nền ổn định: v0.3 – No Repoint / Dấu Tiếng Việt**

Đã xác nhận bằng test thực tế:

- Logo Pokémon đầu game hiển thị bình thường.
- Intro chạy được.
- Có font tiếng Việt có dấu.
- Kết thúc battle đầu tiên có thể quay lại overworld và chơi tiếp.
- Không thay pointer so với nền ổn định v0.1.
- Không vá vào vùng startup/title graphics.

SHA-256 của ROM test v0.3:

`8234d3945fc6d3a87a9669887a114114904b85c00fd9b3ddd026aaea40d636ec`

## Vấn đề còn lại

Bản dịch vẫn còn tình trạng **Anh–Việt xen kẽ** vì các chuỗi có độ dài vượt vùng gốc hoặc dùng chung suffix/pointer chưa được xử lý. Những chuỗi này trước đây từng gây corrupt title graphics và freeze sau battle khi repoint theo kiểu quét toàn ROM, nên hiện tại không ép vá bằng phương pháp đó.

## Hướng hoàn thiện

1. Giữ v0.3 làm baseline ổn định.
2. Xây catalog text từ các target thực sự của engine/script.
3. Ghép nội dung Việt hóa từ Emerald AowVN vào catalog.
4. Chuỗi vừa chỗ: thay trực tiếp.
5. Chuỗi dài/shared: chỉ repoint khi reference được xác nhận là text/script thật; không quét pointer toàn ROM.
6. Dịch riêng text mới của Emerald Arena (UI/battle real-time) không tồn tại trong Emerald gốc.
7. QA theo checkpoint: title → intro → overworld → battle → post-battle → save/load → menu/UI.

Xem [PROGRESS.md](PROGRESS.md) để biết checkpoint mới nhất.
