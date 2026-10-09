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

**Toàn bộ catalog user-facing đã hoàn tất ở mức manifest/source QA: 17,512 / 17,512 (100%).**

Coverage được GitHub Actions xác nhận:
- map/story: **4,361 / 4,361**
- Arena-only: **46 / 46**
- system-text: **2,319 / 2,319**
- system-ui: **8,563 / 8,563**
- battle: **2,223 / 2,223**
- debug-internal: **0 / 1** — chỉ còn test signpost nội bộ, cố tình không thuộc bản dịch phát hành

Run xác nhận: **37824308095 — PASS**, với **0 unresolved manifest key** và **0 duplicate catalog row**.

Điều còn lại **không còn là dịch text**. Bước tiếp theo là **tích hợp 17,512 row user-facing vào ROM v0.4**, xác minh shipping layout cho các scope chưa được attest, kiểm tra encoding/fit tiếng Việt, rồi mới cho phép in-place write hoặc repoint từng reference đã được source xác minh. Vì vậy ROM v0.4 hiện tại vẫn chưa phải bản Việt hóa hoàn chỉnh.

Không được quay lại cách quét/repoint pointer toàn ROM vì cách đó từng gây:

- vỡ logo Pokémon;
- crash intro;
- freeze sau battle.

## Cổng tích hợp ROM an toàn (đang triển khai)

- Toàn bộ **17.512/17.512 bản dịch nguồn đã có manifest**, nhưng **chưa phải bản ROM hoàn chỉnh**.
- Mới có **6.680 vị trí trong ROM phát hành được attest**, còn **10.832 vị trí cần xác minh** (trước khi tính số byte cần ghi).
- Công cụ `tools/plan_user_facing_integration.py` phân biệt chuỗi giống source English với chuỗi đã đổi. **Giống source không tự động có nghĩa là v0.4 không cần vá**: bản v0.4 phải được so byte độc lập trước.
- `tools/verify_local_rom_baselines.py` từ chối ROM sai hash, chỉ đọc, không ghi ROM hoặc pointer; các test fail-closed được chạy trước build.
- Xem **[Hướng tích hợp ROM an toàn và bảng kiểm runtime](docs/SAFE_ROM_INTEGRATION.md)**. Không commit hoặc upload ROM đầy đủ vào repo công khai.

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

## Read-only local ROM audit — 2026-10-09

The exact clean Arena 0.13.0 and v0.4 donor binaries have been independently checked in a private session; **no ROM files are stored in GitHub**. A restricted English source-byte audit identified **7,024 additional candidates** at source-build offsets beyond the **6,680 previously attested** addresses; none are automatically safe to patch or skip. See [the local ROM audit checkpoint](docs/LOCAL_ROM_AUDIT_2026-10-09.md) and `tools/audit_local_rom_source_byte_candidates.py` for a reproducible full pinned-charmap check. The playable v0.5 has **not** been built.


## Ghi công Việt hóa trên title screen

Bản localized cuối sẽ hiện thêm một dòng nhỏ:

**Việt hóa bởi Votri Valley**

Dòng này được tạo thành sprite graphic riêng ở title screen, nằm giữa **PRESS START** và dòng copyright gốc. Cách này không sửa logo Pokémon và không phụ thuộc vào text window/font runtime. Công cụ nguồn: `tools/apply_title_credit.py`; hướng dẫn: [docs/TITLE_CREDIT.md](docs/TITLE_CREDIT.md).

Lưu ý: credit chỉ được áp dụng cho **localized build cuối**, không áp dụng vào workflow shipping-layout/symbol-map để tránh làm lệch địa chỉ nguồn đang dùng cho tích hợp ROM an toàn.


## Source-byte English leftovers audit (2026-10-09)

[Runtime English sweep](docs/RUNTIME_ENGLISH_SWEEP_2026-10-09.md) examined all 17,512 user-facing catalog rows in the actual v0.4 ROM. **7,553 translated-source entries still have English source bytes at an attested or candidate offset; 4,651 are long passages**. The first 4,772 located cases have attested original shipping offsets; the other 2,781 are build-offset candidates requiring verification. This is a read-only backlog, not a released v0.5. Full ROM bytes and patch data remain private.

## Experimental ROM integration — 1,823 strings (2026-10-09)

A private **test ROM** has been produced from the existing v4 title-credit/menu baseline by applying **1,289 map/story, 456 system-text and 78 system-ui** UTF-8 manifest translations as bounded in-place encoded strings, plus a separate Birch `Nữ` label repair. This is an **experimental binary, not the complete v0.5** and has not passed in-emulator QA. No new pointer edits were made. A 142 KB BPS patch was CRC/round-trip tested. Source provenance, exact hashes, safety limitations and the statistically inferred (not yet visually approved) v0.4 Vietnamese glyph codebook are in [the integration checkpoint](docs/LOCAL_BINARY_INTEGRATION_1823_2026-10-09.md). The completed 17,512-entry source manifest still requires further binary integration and runtime QA.

## Experimental 2,084-string gameplay test — truck/intro fix (2026-10-09)

The user's intro screenshots exposed two causes: the variable-containing `MOM: {PLAYER}, we're here, honey!` wasn't integrated and English `w` shares a Vietnamese glyph in the v0.4 font; a **corrupted InsideOfTruck reference** at ROM `0x00251192` pointed to the middle of the words `ột chuyện hay` in a *different map's* Sootopolis text. A new **test** based on the previous 1,823-row build integrates 261 additional variable/script strings and restores eight individually source-verified cross-map pointers, including the truck pointer `0x0823BF75` → `0x08251199`. A read-only survey identified **64 changed source pointer sites; the remaining 56 were not automatically changed**. The BPS round-trip/CRC tests pass but **emulator QA remains outstanding**. Full SHA hashes and reproducibility: [Early game text/pointer recovery](docs/DYNAMIC_EARLY_GAME_POINTER_RECOVERY_2026-10-09.md). This is not the full 17,512-string integrated ROM; keep original v0.4 as rollback.


## Guarded UI/shared-text integration (2026-10-09)

The latest **internal, non-release** test candidate adds **43 short UI translations** with exact shipping-byte and reference checks, plus **13** relocated shared-suffix translations with **31 individually verified owner-reference edits**. An independent pre-release QA pass rejected 2 unsafe pointer conflicts, so all prior **64 historical pointer restorations** remain intact. All changed bytes are allowlisted, BPS CRCs and binary replay PASS. **45** shared-suffix cases remain unresolved and emulator glyph/scroll/line-width QA is outstanding; do not confuse this with fully integrated 17,512-source-text Vietnamese. Details in [the UI43/shared13 checkpoint](docs/UI43_SHARED13_GUARDED_CHECKPOINT_2026-10-09.md). Original safe v0.4 retained as rollback.


## Shared string pointer provenance follow-up (2026-10-09)

[The read-only shared owner investigation](docs/SHARED_OWNER_PROVENANCE_RETRIAGE_2026-10-09.md) reproduces all 270 prior shared-suffix warnings using exact ROM hashes and source symbols. Of 45 still deferred after the prior 212+13 internal guarded integration, 39 have candidate named script/table owners, 2 pointer-like matches are in graphics, 2 extra matches are in executable code, and 2 conflict with prior reference restorations. A [reproducible source-controlled verifier](tools/triage_shared_owner_provenance.py) with 7 unit tests prevents accidental data/code repoint. **No newer game ROM has been built in this resumed turn**: the previous guarded private output must be reproduced without discarding its existing fixes. All source-manifest translations are NOT yet installed in runtime ROM.
