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


## Source-level Vietnamese compilation experiment (2026-10-09)

To reduce manual ROM-pointer defects, the project now includes a [fail-closed source-text staging tool](tools/stage_source_map_translations.py) and a GitHub Actions **separate build smoke** of one translated LittlerootTown line. It retains the original symbol label and uses byte-encoded Vietnamese in assembler, letting the linker resolve any addresses. This is an **experimental compiler proof**, not the completed game localization: the inferred v0.4 glyph map is not visually validated and C/UI/dynamic strings are still pending. Details: [source-first checkpoint](docs/SOURCE_FIRST_VIETNAMESE_PILOT_2026-10-09.md). Also available: [40 script/table pointer candidates and 4 false byte matches](docs/SCRIPT_OPCODE_OWNER_QA_2026-10-09.md), with machine-readable [reference evidence](checkpoints/shared-owner-opcode-evidence-2026-10-09.csv). No new playable ROM issued in this turn.


## Source build experiment: 230 Vietnamese strings and font gate (2026-10-09)

[Actions run 37884608217](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37884608217) successfully compiled **200 translated map/story labels (85 safely reflowed) + 30 translated C UI messages (3 safely reflowed)** in an isolated source workspace. Source-owned labels are retained and assembler/linker resolve references automatically; this is **NOT** a full v0.5 game ROM release and still does not contain the verified v0.4 Vietnamese font glyphs. New SHA-locked font import/audit tools can check and transplant only **5,917** differing Latin glyph bytes across five exact clean/donor font arrays, but require a private source-built ROM and must pass glyph/scroll emulator QA. See [full source-first milestone and safety status](docs/SOURCE_FIRST_MAP_UI_FONT_2026-10-09.md). Keep old v0.4 rollback and do not publish copyrighted ROM binaries to GitHub.

## Source-first compilation expanded to 741 labels (2026-10-09)

Full [Actions build 37895308303](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37895308303) **PASS** with **500 map/story, 41 system UI, 100 player-name dynamic and 100 battle-script source texts**, 326 controlled reflows; donor Vietnamese font is **NOT** integrated and emulator QA is not complete. These are source-first compiled samples from a source translation manifest of 17,512 rows, not an end-user stable Vietnamese ROM. Source-built SHA256 `e63d4799b06c634d92b3dc003e07e27c933629e480c8c01047457b0029ef6cc7`.

Font audit established that v0.4 shares original English glyph bytes for **f/w/z** with Vietnamese **ấ/ằ/ắ** (and inferred codebook still has **Ừ/ừ** duplicate), a release blocker while English remains. Added a new read-only collision auditing script, a battle source-text integration mode and an independent source-text ownership verifier. Read [741 integration/font checkpoint](docs/SOURCE_LOCALIZATION_741_BATTLE_FONT_QA_2026-10-09.md). Preserve original v0.4 as safe rollback; avoid shipping stock-font source GBA as localized or uploading copyrighted ROMs.

## V0.5 source-first glyph collision repair (2026-10-09)

The [new collision-safe font checkpoint](docs/V05_COLLISION_SAFE_FONT_RELOCATION_2026-10-09.md) documents the exact f/w/z vs ấ/ằ/ắ glyph collision in original v0.4. `checkpoints/v05-collision-free-codebook.json` reserves free Latin slots **30/31/32** for the accented characters while retaining ASCII **DA/EB/EE**. A real private font-only diagnostic confirmed **15 relocated glyphs across five styles, all English f/w/z pictures preserved and zero writes outside font ranges**. The two small styles use a deterministic but visually unverified synthetic raster and uppercase `Ừ` is temporarily excluded.

The **741 source-text experimental build on the v0.5 codebook PASSed** in [Actions 37900453143](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37900453143) with exact independent source ownership QA (500 map, 41 UI, 100 name-variable and 100 battle strings). **The compiler build still contains stock fonts and is not a playable finished Vietnamese version.** A subsequent source-build scale-up targets up to 1000 map, 200 variable and 200 battle labels, with independently verified totals required before reporting progress. Public GitHub contains no proprietary ROM or donor font binaries; original v0.4 is kept as rollback.


## Source-first trial: 1,430 independently verified text labels (2026-10-09)

The [latest full GitHub Actions build](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37914622483) **PASSed compilation and independent source-string verification** with **1,000 map/story + 41 C UI + 134 PLAYER/RIVAL + 196 scripted battle + 59 new `src/battle_message.c` static battle texts**. All 1,430 installed source labels are unique, have exact FF termination, and have no overlap between groups; 749 translations were subject to conservative word-boundary reflow. [Read checkpoint details](docs/SOURCE_LOCALIZATION_1430_BATTLE_C_2026-10-09.md).

**Not a stable playable Vietnamese ROM yet:** the resulting source-built GBA still contains stock English font glyphs and has not undergone emulator QA. The user-facing translation source manifest contains 17,512 entries, not 17,512 integrated runtime strings. Keep the original working v0.4 ROM as rollback; do not upload copyrighted donor ROMs or private font asset bytes to this public repository. The next planned sweeps are 355 move descriptions and 310 item descriptions, followed by variable-sized battle templates and a separately gated, visually validated v0.5 font transplant.


## Source-built move and item descriptions — 2026-10-09

The [new verified GitHub Actions run](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37943838702) compiled and independently validated **1,961 Vietnamese source labels**: 1,000 NPC/map, 41 system UI, 134 PLAYER/RIVAL map strings, 255 battle strings, **246 move descriptions**, and **285 item descriptions**. Descriptions preserve the actual two-line move and two-/three-line item layout, reject unsafe dynamic placeholders and missing font glyphs, and keep original source-owned C symbol names. All integrated labels have terminal FF and no duplicates. This **still is not a playable Vietnamese font-grafted release**: the source ROM contains original English fonts. [Detailed source-localization checkpoint](docs/SOURCE_LOCALIZATION_1961_MOVE_ITEM_2026-10-09.md).

An opt-in guarded move-description word rebalance is under CI review. It can shift a newline between words without omitting, paraphrasing or adding lines; its actual acceptance count must come from the final GitHub Actions report. The original working v0.4 game ROM remains the rollback copy, and the exact title line remains **Việt hóa bởi Votri Valley**.


## Source compilation milestone: 2,000 text labels

After the 1,961-label source-build checkpoint, the [latest GitHub Actions CI](https://github.com/ronvotri/VH-GBA-PEA/actions/runs/37944716925) **PASSed 2,000 unique source-level Vietnamese texts** with 39 additional long move descriptions rebalanced to two 26-cell lines without deleting any words. Verified totals: **1,000 map/story, 41 C UI, 134 dynamic PLAYER/RIVAL, 196 battle scripts, 59 C battle, 285 move descriptions, 285 item descriptions**. Independently checked no duplicates or broken 0xFF terminators. See [move/item source QA checkpoint](docs/SOURCE_LOCALIZATION_1961_MOVE_ITEM_2026-10-09.md).

**Important:** this is still a **stock-English-font source compilation experiment**, NOT a Vietnamese-font-integrated downloadable GBA. Full source translation manifest coverage of 17,512 entries does not equal installed playable ROM localization. The game needs exact SHA-locked v0.5 donor font graft, visual/runtime QA and remaining text integration before a release. The working v0.4 rollback remains untouched.
