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
