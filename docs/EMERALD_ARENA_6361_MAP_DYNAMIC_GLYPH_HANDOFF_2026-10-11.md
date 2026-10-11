# Pokémon Emerald Arena — bản giao việc NPC dynamic + Unicode (11/10/2026)

## Cập nhật sau khi CI FULL PASS

- [Actions **#38148731660**](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38148731660): **FULL PASS**, thêm **167** nhãn thoại NPC/map có biến động, đưa mốc xác minh lên **6.528** nhãn nguồn.
- **1.552** nhãn hệ thống và **2.867** nhãn map cũ vẫn được so từng byte tại vị trí nguồn ELF/GBA; 167 nhãn mới cũng được xác minh.
- Source ROM stock-font SHA256: `d79e18647a01bb7f639fc07c1a64dfd46ffb19ed7be8d963d9ba86111c5d8f45`; vùng đuôi linker trống **1.810.364 byte**. Chưa có font Việt v0.4 trong ROM này.
- Glyph audit đầu PASS nhưng gắn nhầm các chuỗi C/UI không có ký hiệu kết thúc `# Pokémon Emerald Arena — bản giao việc NPC dynamic + Unicode (11/10/2026)

 là "malformed GBA text terminator". **Bỏ số blocker 11.950/17.512 của audit đầu** vì trộn sai định dạng `.c` và `.inc`.
- Đã sửa audit để dùng `source_file` phân biệt C/UI với GBA native text, có test hồi quy. [CI thử lại #38149462164](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38149462164) **đang chạy** khi ghi checkpoint. Chỉ dùng bảng glyph mới sau khi nó PASS; không điều chỉnh câu dịch cho vừa codebook.

## Mốc thật sự đã xác minh

- **6.361** nhãn nguồn tiếng Việt được biên dịch và kiểm chứng ELF/GBA tại [CI #38146099792](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38146099792). Đây là mốc chắc chắn trước lượt mới.
- Manifest bản dịch **17.512/17.512** hoàn thành ở cấp nguồn; **không phải** số nhãn đã vào ROM.
- Build source vẫn dùng **5 ngân hàng font pixel tiếng Anh gốc**, chưa ghép bộ nét Việt v0.4 người dùng duyệt, chưa thử mGBA/gameplay. ROM v0.4 riêng vẫn là chuẩn/rollback (SHA256 `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`).

## Đã thực hiện trong lượt này

1. `tools/stage_dynamic_map_static_budget.py`: tái sử dụng bộ mã hóa và dàn dòng STR_VAR đã PASS cho các nhãn nguồn bản đồ/NPC `data/maps/**/*.inc`. Chỉ ghi nguồn khi nguyên văn tiếng Anh, nhãn và owner chính xác. Loại trừ 8 report map trước đó (2.867 nhãn); không trùng source, không đoán độ dài runtime `STR_VAR_1..3`, không băng qua `\\p`, giữ thứ tự mọi từ, giữ byte biến và ngưỡng ô chữ tĩnh của dòng tiếng Anh.
2. `tools/tests/test_stage_dynamic_map_static_budget.py`: regression kiểm tra biến tên động, mã trang, toàn vẹn chữ và nhãn nguồn; bảo đảm các trường hợp sai bị từ chối.
3. `tools/verify_dynamic_map_static_budget.py`: kiểm chứng lại nguyên mốc 6.361, gồm **1.552** nhãn system và **2.867** nhãn map theo owner; kiểm chứng từng nhãn map mới với mã UTF-8 Vietnamese đã mã hóa và đúng byte tại địa chỉ ELF/GBA liên kết, đồng thời xác thực 5 font stock chưa thay và khoảng trống ROM.
4. `tools/audit_missing_vietnamese_source_glyphs.py` và `tools/tests/test_audit_missing_vietnamese_source_glyphs.py`: phân tích các ký tự Unicode thực sự chưa có mã trong source codebook v0.6 trên manifest 17.512 câu, tách code điều khiển/biến trò chơi, bảo vệ byte Pokéblock/PKMN/equals, thống kê theo ký tự, nhãn và nhóm. **Read-only**: không sinh font, không sửa bản dịch, không chỉnh ROM.
5. `.github/workflows/arena-map.yml` chạy cả hai công cụ, xuất `SOURCE_VIETNAMESE_GLYPH_BLOCKERS.json` và `SOURCE_MAP_DYNAMIC_STATIC_BUDGET_ATTESTATION.json` vào artifact.

## CI cần xem tiếp

[GitHub Actions #38148375167](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38148375167) **đang chạy khi viết checkpoint**. Chỉ tăng số tích hợp từ 6.361 nếu **FULL PASS** và `new_dynamic_map_source_labels` là số dương. Nếu không, đọc lỗi và sửa thật sự, không ép nới lỏng QA.

Nhóm ký tự chưa có mã trong v0.6 là vấn đề bảng mã nguồn/dữ liệu hiển thị, **không được suy ra** là bộ font v0.4 của người dùng xấu hay cần vẽ lại. Không thay dấu, không chuyển chữ có dấu thành Latin không dấu để lấy số liệu tích hợp cao hơn.

## Hạn chế phát hành

Không upload ROM Pokémon thương mại; không gọi bản 1.0 hay «xong» chỉ vì catalog 17.512 mục hoàn thành. Kiểm tra hình font v0.4 riêng và chạy title → intro → map → battle → postbattle → save/load → menu Arena khi có bản ghép font đúng, đảm bảo vẫn có dòng **Việt hóa bởi Votri Valley** mà không phá logo.
