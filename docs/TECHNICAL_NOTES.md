# Ghi chú kỹ thuật

## ROM mục tiêu

- Pokémon Emerald Arena 0.13.0
- Dựa trên pret/pokeemerald + patch/overlay của Emerald Arena.
- ROM Arena phát hành: 32 MiB.
- ROM AowVN dùng làm nguồn tham chiếu Việt hóa: 16 MiB.

## Bài học từ các bản test

### Không được quét pointer toàn ROM

Một giá trị 32-bit trông giống địa chỉ GBA không có nghĩa nó là pointer text. Graphics, compressed data và code có thể tình cờ chứa byte pattern giống pointer. Các bản đầu đã sửa nhầm những vị trí này, dẫn tới title graphics bị phá và luồng hậu battle bị treo.

### Baseline v0.3

v0.3 giữ cơ chế **no-repoint** cho phần đã test ổn định. Các chuỗi tiếng Việt có thể ghi đè tại chỗ chỉ khi không vượt allocation gốc và không chồng lên chuỗi/suffix khác.

### Font

Font tiếng Việt đang dùng dựa trên glyph từ bản AowVN đã được xác nhận hiển thị dấu đúng. Lỗi logo ở các test đầu không phải do glyph tiếng Việt tự thân mà do patch ngoài vùng font.

## Mục tiêu bước tiếp theo

Chuyển từ vá nhị phân suy đoán sang catalog text có provenance rõ:

1. target phải là string thực;
2. reference phải đến từ script/code/table text đã xác minh;
3. nếu cần repoint, chỉ sửa đúng reference đó;
4. text mới đặt trong vùng trống được kiểm chứng;
5. mọi pass phải so diff với baseline và QA boot/battle/post-battle.
