# Ghi chú kỹ thuật

## ROM mục tiêu

- Pokémon Emerald Arena 0.13.0.
- Dựa trên pret/pokeemerald + patch/overlay Emerald Arena.
- Shipping ROM: 32 MiB / 33,554,432 bytes.
- SHA-256 shipping Arena: `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`.
- SHA-1 shipping Arena: `a3247882b469fecb491e2875d45ddc3b4b49e310`.
- AowVN 16 MiB được dùng làm nguồn tham chiếu font/nội dung Việt hóa, không được chép gameplay/mod của AowVN sang Arena.

## Baseline patch

### v0.3

No-repoint baseline đã được test:

- logo OK;
- intro OK;
- font dấu OK;
- battle đầu OK;
- post-battle OK.

### v0.4

Text Cluster Pass:

- thêm 462 cụm text shared/overlap;
- 43,044 byte thay đổi so với v0.3;
- 0 pointer write;
- startup/title giữ nguyên so với v0.3;
- người chơi đã đi tiếp qua phần đầu game nhưng vẫn gặp English user-facing.

## Vì sao không được quét pointer toàn ROM

Giá trị 32-bit nằm trong dải `0x08000000..0x09FFFFFF` không nhất thiết là pointer text. Nó có thể là:

- literal trong code;
- dữ liệu graphics/compression;
- table khác;
- byte ngẫu nhiên trùng pattern.

Test 1/2 đã chứng minh thay pointer kiểu heuristic có thể phá title graphics và flow hậu battle.

## Catalog text

Hai bộ lọc cuối phiên trên shipping Arena:

- broad text-like pointer targets: 24,916;
- stricter plausible-English targets: 20,383.

Con số này **không phải số string cần dịch cuối cùng**. Nhiều target là suffix/substrings hoặc data dùng chung. Bước tiếp theo phải dùng symbol map/source provenance để thu hẹp.

## Source build / symbol map

Workflow: `.github/workflows/arena-map.yml`.

Pinned inputs:

- `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`
- `pret/agbcc@da598c1d918402c42c0c0d7128ba14567f3175e9`
- `GBurgardt/pokemon-emerald-arena@v0.13.0`

Artifact mong đợi:

- `pokeemerald.map`
- `pokeemerald.sym`
- `ROM_SHA1.txt`
- `ROM_SHA256.txt`

Mục tiêu: biết chính xác label nào nằm ở địa chỉ ROM nào và C/ASM/script reference nào cần đổi.

## Chiến lược patch cuối

1. Build catalog từ source labels + symbol map.
2. Match English shipping Arena ↔ AowVN translation khi đáng tin.
3. Giữ control code/placeholders nguyên nghĩa.
4. In-place khi translated payload <= allocation.
5. Nếu dài hơn:
   - ưu tiên biên tập tiếng Việt gọn;
   - nếu vẫn không vừa, đưa text vào pool và repoint **chỉ reference đã xác minh**.
6. Arena-only text dịch riêng từ source Arena.
7. Mỗi batch có manifest + diff + QA checkpoint.

## Checkpoint English còn sót

Ví dụ mới nhất từ test thực tế:

`There could be treasures just waiting to be discovered down there.`

Đây là loại string mà pass kế tiếp phải bắt được từ source/catalog thay vì chờ người chơi chụp từng ảnh.
