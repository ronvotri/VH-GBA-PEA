# BÀN GIAO CHO CLAUDE — Pokémon Emerald Arena Việt hóa

**Chốt tài liệu:** 2026-10-13 (Asia/Ho_Chi_Minh). **Kho:** https://github.com/ronvotri/VH-GBA-PEA — nhánh `main`.  
**Mục tiêu:** Hoàn thành bản Pokémon Emerald Arena 0.13.0 Việt hóa có dấu, font đúng bản đã được duyệt, không lỗi trận đấu, không còn câu tiếng Anh hiển thị, bảo toàn gameplay, giữ ghi công `Việt hóa bởi Votri Valley`.

> **ĐỌC TRƯỚC KHI LÀM:** `AGENTS.md`, `README.md`, `PROGRESS.md`, `docs/EMERALD_ARENA_FIRST_BATTLE_TEST_GATE_2026-10-13.md`, `docs/EMERALD_ARENA_2026-10-12_PLUS341_REGRESSION_ROLLBACK.md`, và tài liệu này. `CONTINUE_WITH_MODEL.md` có rất nhiều checkpoint cũ, không được nhầm các số cũ với trạng thái mới. Luôn xem commit `main` và GitHub Actions mới nhất trước khi tăng mốc.

## 1. Trạng thái thực tế: ba nhánh KHÁC NHAU

| Trục công việc | Mốc đáng tin | Ý nghĩa / giới hạn |
| --- | --- | --- |
| **Bản dịch catalog** | **17.512 / 17.512** user-facing mục đã có nội dung dịch | Dịch ở cấp manifest; **không** có nghĩa ROM chơi được đã chứa đủ 17.512 mục. Mục `debug-internal` cố tình bỏ qua. |
| **ROM biên dịch từ mã nguồn** | **7.134 distinct source-integrated Vietnamese labels**; [FULL PASS #38161452509](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38161452509) | ELF/source/GBA byte verification. Đây là build thử nghiệm **5 ngân hàng font pixel tiếng Anh stock**, **chưa** dùng nét font v0.4. GitHub Actions [#38214295899](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38214295899) về sau cũng **success**, nhưng không có bằng chứng mốc nhãn mới lớn hơn 7.134. |
| **ROM riêng dựa trên donor v0.4/v5** | Có các bản in-place TEST (128 câu, 390 câu, v5 +34, +69, Intro12...), khác nhánh source; **chưa đủ QA runtime** | Không cộng các số TEST này vào 7.134. **+341 relocation EXPERIMENTAL bị từ chối do lỗi sau battle**, tuyệt đối không làm nền. |
| **Trạng thái phát hành** | **CHƯA HOÀN THÀNH** | Lỗi treo sau trận đầu, ràng buộc font/codebook và dịch còn thiếu trong ROM thực tế phải xử lý. |

Số liệu trong manifest được xác nhận theo nhóm: `map/story 4.361`, `Arena-only 46`, `system-text 2.319`, `system-ui 8.563`, `battle 2.223`. **Không lấy 7.134/17.512 làm tỷ lệ chính xác màn hình đã Việt hóa** vì mẫu số là catalog còn tử số là nhãn đã link; cũng không nhầm số source compile với những chỗ thật sự đã hiển thị và chơi thử.

### ROM, phiên bản và mã SHA để phân biệt tuyệt đối

- **Shipping clean 0.13.0** SHA256: `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`.
- **v0.4 Text Cluster Pass, FONT ĐÃ ĐƯỢC NGƯỜI DÙNG DUYỆT** SHA256: `c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9`. Đây là tham chiếu font/hình dáng và baseline rollback; bản v0.3/v0.4 từng được xác nhận intro → battle → trở lại overworld, nhưng việc tái thử còn phải làm.
- **v5 credit / 1.823-string TEST** SHA256: `ae1e00595ba3d1f193bcdbd8fcff44394b37e582c0a202e7c0c0df97f645d4d0`; KHÔNG mặc nhiên xem ổn định runtime.
- **v5 +341 relocation EXPERIMENTAL, PHẢI LOẠI** SHA256: `0bf451fda75f1e32c5b2fc865386009f02b6339d191c721d1346bacd8807e11b`; người dùng bị freeze sau battle.
- **v0.4 Intro12/TruckBoxFix TEST** SHA256: `2fef97006bb35293aa43764c74d1f7e0df5c8c8674a3fd42a559af6bc5a994f5`; người dùng **vẫn báo treo trên No$GBA**, không được gọi PASS.
- **Source-built 7.134 STOCK-font trial** SHA256: `df7e47319aa9c054bd952d39ccb6cef8b2c36eedbc0ae1e7d1422cc558acf5fc`; không được lẫn với donor v0.4.

**Không commit, gửi công khai, hay chứa ROM thương mại hoàn chỉnh hoặc glyph bank lấy từ donor trong GitHub repo.** Nếu Claude cần so binary/font, người dùng phải cung cấp **riêng tư** file gốc và donor đúng SHA. ROM 32 MiB; kiểm tra hash trước khi vá.

## 2. LỖI PHẢI ƯU TIÊN: FREEZE SAU TRẬN ĐẦU

Người dùng nhiều lần phải chơi intro tới trận Birch rồi ROM treo. Đừng bắt thử lại từng build từ đầu hoặc đưa câu trả lời «đã fix» khi chưa qua gameplay.

1. Xem `docs/EMERALD_ARENA_FIRST_BATTLE_TEST_GATE_2026-10-13.md`. Trên **No$GBA**, nguyên nhân có thể liên quan **Sound Output đang Disabled**. Thử bật **Digital Mono** hoặc sound output trước khi đụng binary — đây mới là **giả thuyết**, chưa được người dùng xác nhận.
2. Dùng **mGBA phiên bản ổn định** làm phép thử độc lập với No$GBA. Dùng save thật (battery `.sav`) ngay **trước trận Birch** để tái sử dụng mỗi lần, không dùng save state `.ss0/.sgm` như `.sav`. Công cụ Windows thử nhanh từng được tạo riêng là `Emerald-Arena-Battle-QA-Kit.zip` (đã lưu ngoài repo trong cuộc trò chuyện, **không có ROM**); Claude có thể yêu cầu người dùng đính kèm.
3. A/B xác thực trên cùng emulator, cài đặt, vùng save: **clean → donor v0.4 → candidate test**. Ghi checksum ROM, tên emulator và Sound Output, trạng thái trước battle, kết quả trở lại overworld, save/load. Nếu v0.4 cũng treo, tìm lỗi thiết lập/emulator/savestate trước khi tự ý sửa script.
4. **Reject +341 và bất kỳ bản vá có pointer/scene động chưa được QA**. SHA/CRC/BPS/ELF PASS chỉ chứng minh byte, **không** chứng minh gameplay.
5. Chỉ chấp nhận `battle → overworld → đi tiếp → save/load` sau khi thực tế thao tác trong emulator thành công. Không ép người dùng replay nhiều lần nếu có thể tạo một checkpoint dùng lại.

### Lỗi người dùng đã phát hiện phải có regression test

- Lựa chọn giới tính **Nam/Nữ** không được xuất hiện lại dạng `Nam / Girl`; nhân vật May và mẹ May phải dùng xưng hô **đúng người/quan hệ**, câu tiếng Việt tự nhiên. Không được đảo câu chào mẹ May khiến hiểu nhầm giới tính.
- Một số câu mẹ/đồng hồ/tuyến đầu vẫn **tiếng Anh hoặc tiếng Việt không dấu**, kể cả bản mang số phiên bản cao.
- Trong font donor v0.4 có lịch sử **đè glyph lên byte chữ f/w/z** để chứa dấu Việt. Câu tiếng Anh chưa Việt hóa có các chữ này có thể hiện thành ký tự lỗi. Cần thiết kế migration **giữ nét chữ đã duyệt**, tránh thay bằng font máy méo chữ.
- Đảm bảo hiển thị credit **`Việt hóa bởi Votri Valley`** tại title, nhưng bản test v0.4 phục hồi intro chưa port credit vì muốn giữ startup ổn định. Không được tuyên bố credit đã vào mọi ROM.
- QA cả Pokédex, battle HUD, Ability/Match Call, Easy Chat, Pokéblock, Arena tiny HUD, tên Pokémon và menu.

## 3. Nút thắt lớn — bản dịch đã có, chưa tích hợp/hiển thị đúng

Đây là bài toán **binary/font/runtime integration**, không phải thiếu người dịch thêm 10.000 câu. Những phần còn khó:
- Source owner khác loại (`data/maps/*.inc`, `data/text/*.inc`, các C string ở `src/strings.c`, `src/battle_message.c`, mô tả move/item, Ability/Match Call, Easy Chat và `Arena-only`) có cách render, token, kích thước khác nhau. Đừng dồn chung một encoder.
- Read-only glyph audit của codebook thử nghiệm tìm **141 ký tự Unicode chưa hỗ trợ**; **4.726 mục** chịu ảnh hưởng bởi ký tự thiếu *hoặc* vấn đề định dạng. Đây không phải số câu lỗi font thực tế trên donor v0.4. Không xóa dấu để tăng số lượng.
- Với `STR_VAR` giá trị lúc chạy có thể dài hơn tên mẫu. Không tự đoán độ dài; giữ thứ tự token, page `\\p`, line `\\n/\\l`, số ô chữ tĩnh và kiểm chứng nguồn.
- Không dùng tiny Arena HUD bitmap ASCII như trình render thoại thông thường. Phải test đúng renderer và font bank.
- Repoint/reallocate chỉ khi **đúng owner/reference đã xác minh** và đã có kiểm thử gameplay. Việc +341 với 272 pointer relocation dù binary QA đạt vẫn đã gây lỗi runtime, **không được tái nhập**.

Các công cụ/code đã có: `tools/plan_user_facing_integration.py`, `tools/stage_source_map_translations.py`, `tools/stage_system_dynamic_static_budget_reflow.py`, `tools/stage_dynamic_map_static_budget.py`, `tools/stage_map_dynamic_page_line_repair.py`, `tools/stage_map_multi_dynamic_line_slots.py`, `tools/stage_easy_chat_word_groups.py`, `tools/audit_missing_vietnamese_source_glyphs.py`, `tools/audit_source_font_layout.py`, `tools/verify_local_rom_baselines.py`, `tools/verify_private_rom_text_delta.py` cùng test tương ứng. `.github/workflows/arena-map.yml` là build pipeline hiện có. **Đừng tự viết lại toàn bộ nếu đã có tool an toàn được kiểm chứng.**

## 4. Công việc Claude nên làm theo thứ tự

**P0 — Bắt buộc:** Reproduce/triage freeze sau trận Birch với âm thanh No$GBA và mGBA + checkpoint `.sav`; lưu log và kết quả QA. **Tuyệt đối không xuất bản ROM mới khi trạng thái này chưa rõ**.

**P1 — Font:** Ghép tương thích **chính hình dạng glyph v0.4 đã duyệt** vào source/binary có bản dịch mới; kiểm tra mã byte/ký tự ở năm font bank, Pokéblock/PKMN, chữ Latin `f/w/z`, dấu hoa `Ồ/À/Ô/Ư`, khung hội thoại và HUD nhỏ. Không dùng font máy dựng thay nét.

**P2 — Tích hợp số lượng lớn:** Từ catalog đủ 17.512 mục, lập danh sách **source owner đã vào ROM / chưa vào ROM / cần encoder khác / bị font / không tồn tại trong shipping**. Ưu tiên diện người chơi thấy trước (title/intro, NPC tuyến đầu, battle/postbattle, menus, Pokédex/Arena). Batching lớn nhưng có kiểm thử và checkpoint cho mỗi batch. Không hạ tiêu chuẩn để tăng KPI.

**P3 — Khép QA:** Chu trình mới-game và lưu-game: title/credit → chọn giới tính → nhà và đồng hồ → Birch/battle đầu và return → mẹ May → đi map NPC → chiến đấu tiếp → save/load → PC/Bag/Pokédex/move/item/Ability/Easy Chat/Pokéblock → Arena/Battle Frontier. Rà lỗi dịch nửa Anh nửa Việt, dấu, xưng hô, tên dài, crash/freeze.

**P4 — Bàn giao thực tế:** Phát hành bản vá delta BPS/IPS có checksum đầu vào/đầu ra, script Windows một-click nếu cần, changelog, rollback và hướng dẫn mGBA; **không public ROM gốc hoặc full game**. Có thể gọi `1.0 DONE` **chỉ khi runtime QA đạt và người chơi không còn English user-facing**.

## 5. Hướng dẫn kỹ thuật khởi động

1. Checkout repo `main`, xem `git log -n 15 --oneline` và HEAD. Nếu repo khác trạng thái trong tài liệu này, **kiểm chứng trạng thái mới**, không ghi đè code mới bằng checkpoint cũ.
2. Chạy test Python từ repo: `python -m unittest discover -s tools/tests -p "test_*.py"`. Sửa các lỗi thực tế mà không làm rớt invariant. Xem workflow `.github/workflows/arena-map.yml` để xác định các tool nguồn/pinned deps/attestations; không dựa vào đơn vị test thay thế linker verify.
3. Mở [Actions #38214295899](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/38214295899), tải artifact `arena-0.13.0-symbol-map` chứa các báo cáo nguồn/plan. Tại 2026-10-13 artifact này còn tồn tại và **dự kiến hết hạn 2026-10-19 06:57 UTC**. Các bản report mới phải có cùng owner/source, tránh lệ thuộc artifact quá hạn.
4. Nếu cần thử ROM/font, nhận đầu vào private từ người dùng, so SHA256, giữ binary ngoài kho công khai. Chạy BPS/IPS verification độc lập, sau đó thực sự chạy gameplay.
5. Trước mọi thay đổi: lập mục tiêu batch và số nguồn dự kiến; sau: chạy unit tests, GitHub Actions, attestation, report những nhãn **thực sự tăng**, commit GitHub và cập nhật checkpoint. Không tuyên bố FULL PASS khi Actions còn pending.

## 6. Các file Claude nên mở ngay

- `AGENTS.md` — nguyên tắc mã và an toàn.
- `README.md`, `PROGRESS.md`, `CONTINUE_WITH_MODEL.md` — trạng thái và lịch sử (chú ý checkpoint cũ).
- `docs/EMERALD_ARENA_FIRST_BATTLE_TEST_GATE_2026-10-13.md` — lỗi treo, Sound Output và kit tránh replay.
- `docs/EMERALD_ARENA_2026-10-12_PLUS341_REGRESSION_ROLLBACK.md` — vì sao 272 pointer relocation bị loại.
- `docs/EMERALD_ARENA_2026-10-12_V04_STABLE_RECOVERY_INTRO12.md` — các sửa đầu game an toàn tại ROM v0.4 nhưng **vẫn chưa qua runtime**.
- `docs/V04_PRIVATE_128_INPLACE_QA_HANDOFF_2026-10-12.md` — nhánh private khác, không trộn source counts.
- `docs/EMERALD_ARENA_7091_EASY_CHAT_HANDOFF_2026-10-12.md` — bằng chứng source 7.134.
- `docs/SAFE_ROM_INTEGRATION.md`, `docs/POKEBLOCK_FONT_TOKEN_COLLISION_2026-10-09.md`.
- `translations/map-story/INDEX.md`, `checkpoints/v06-pokeblock-safe-codebook.json`, `.github/workflows/arena-map.yml`, `tools/tests/`.

## 7. Những file người dùng **đính kèm riêng tư** cho Claude (GitHub KHÔNG có)

- **Bắt buộc để patch binary:** ROM Arena 0.13.0 shipping sạch, ROM donor **v0.4 Text Cluster Pass** đúng SHA ở trên. Claude có thể dùng file v0.4 chứa nguyên hình font đã duyệt; **không tự tải ROM game từ site lạ**.
- **Để chẩn đoán regression:** v0.4 Intro12/TruckBoxFix TEST, v5 +341 bị lỗi chỉ làm đối chứng read-only; bản v5 có credit nếu muốn phân tích công nghệ chèn credit an toàn.
- **Để tránh chơi lại trận Birch:** `Emerald-Arena-Battle-QA-Kit.zip` và nếu có **battery save** trước trận đầu (`.sav`). Bản kit và `.sav` là file ngoài repo.
- **Để tích hợp có provenance:** GitHub Actions artifact `arena-0.13.0-symbol-map` của run #38214295899 (tải trước khi hết hạn). Artifact chứa báo cáo và plan chứ **không phải ROM đã Việt hóa hoàn chỉnh**.

**Quy ước báo cáo Claude:** Mỗi lần thông báo `(1) authored: 17512`, `(2) source-linked verified: 7134 hoặc số mới có CI`, `(3) donor-v0.4 private modified spans`, `(4) emulator gameplay QA: PASS/FAIL/NOT RUN`, `(5) font-v0.4 graft: YES/NO`, `(6) release ready: YES/NO`. Không gộp các cột này thành một tỷ lệ phần trăm.

---

**Ưu tiên lớn nhất từ người dùng:** *Giữ font Việt đẹp bản đầu, đừng làm mất Nam/Nữ và câu thoại mẹ May, đừng để mất ghi công Votri Valley, đừng bắt chơi từ đầu đến battle để test mỗi bản và đừng gọi hoàn thành khi ROM còn treo hoặc lẫn tiếng Anh.*
