# Pokémon Emerald Arena – Việt hóa

Dự án Việt hóa **Pokémon Emerald Arena 0.13.0** sang tiếng Việt có dấu.

> Repo này theo dõi mã vá, công cụ, tài liệu kỹ thuật và tiến độ. Không lưu ROM Pokémon gốc/ROM đầy đủ.

## Trạng thái hiện tại

**Baseline làm việc: v0.4 – Text Cluster Pass**

v0.4 được dựng trên baseline v0.3 đã xác nhận ổn định và **không ghi pointer mới**. Người chơi đã test thực tế qua phần đầu game, battle và tiếp tục đi sâu hơn trong game mà không gặp lại lỗi logo/crash/freeze của các test cũ.

Điểm đã chốt:

- Logo/title không bị corrupt.
- Font tiếng Việt có dấu hoạt động.
- Intro chạy được.
- Battle đầu chạy được.
- Sau battle quay lại overworld và tiếp tục chơi được.
- v0.4 thêm 462 cụm text shared/overlap nhưng vẫn giữ chiến lược **0 pointer write**.
- Vùng startup/title của v0.4 giữ nguyên byte-for-byte so với v0.3.

SHA-256:

- Arena 0.13.0 sạch: `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`
- v0.3: `8234d3945fc6d3a87a9669887a114114904b85c00fd9b3ddd026aaea40d636ec`
- v0.4: `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`

## Vấn đề còn lại

**Catalog dịch map/story đã hoàn tất 4,361 / 4,361 (100%) ở mức manifest/source QA.** Câu English từng thấy trong game đã được neo vào catalog và nằm trong phạm vi manifest hoàn chỉnh.

Điều còn lại không phải là “dịch thêm map/story”, mà là **tích hợp toàn bộ manifest vào ROM v0.4** và tiếp tục các nhóm user-facing khác như system-text, Arena-only, UI và battle text. Vì vậy bản ROM hiện tại vẫn chưa được gọi là Việt hóa hoàn chỉnh.

Không được quay lại cách quét/repoint pointer toàn ROM vì cách đó từng gây:

- vỡ logo Pokémon;
- crash intro;
- freeze sau battle.

## Hướng hoàn thiện hiện tại

1. Dùng v0.4 làm baseline làm việc.
2. Dùng source/map/symbol của Emerald Arena để xác định **đúng string + đúng reference**.
3. Catalog text từ target thực sự của script/code; không coi mọi giá trị giống pointer là pointer text.
4. Ghép bản dịch AowVN khi có đối ứng.
5. Chuỗi vừa allocation: thay tại chỗ.
6. Chuỗi dài/shared: chỉ repoint reference đã xác minh bằng source/map.
7. Dịch riêng text mới của Emerald Arena.
8. QA liên tục: title → intro → overworld → battle → post-battle → save/load → UI/menu → main story.

Workflow `.github/workflows/arena-map.yml` đã được tạo để build đúng source Arena 0.13.0 và xuất `pokeemerald.map` + symbol list phục vụ mapping ROM.

Map/story canonical inventory: **4,361 / 4,361 (100%)** tại `translations/map-story/INDEX.md`. `tools/audit_remaining_map_story.py` dùng catalog authoritative để kiểm tra phần còn thiếu trước mỗi integration checkpoint.

**Phiên mới nên đọc [CONTINUE_WITH_MODEL.md](CONTINUE_WITH_MODEL.md) trước.**

Xem [PROGRESS.md](PROGRESS.md) để biết checkpoint chi tiết.


## Map/story translation status

Map/story manifest coverage is now **4,361 / 4,361 (100%)**. This is source/manifest completion, not yet a fully integrated ROM. The next phase uses the safe integration planner and shipping-verified provenance before any new binary writes.
