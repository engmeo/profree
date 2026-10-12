# FactoryPulse — Bản đồ repository và quy tắc chọn demo

## Điểm vào duy nhất

**`demo_hub.html`** là trang điều hướng cho người chấm: dashboard / 2D / 3D / resilience / research. Khi chạy HTTP server ở root, mở `/demo_hub.html`. README liên kết tới trang này ở phần trên cùng.

## Ranh giới kỹ thuật — phải nói đúng khi trình bày

| Phần | Mã chạy | Đầu vào | Kết quả | Giới hạn |
|---|---|---|---|---|
| Dashboard | `index.html`, `src/app.mjs`, `src/core.mjs`, `src/worlds.mjs` | Kịch bản JS giả lập | Quyết định, ETA, so sánh thông tin | Không gọi CP-SAT Python |
| 2D | `digital_factory.html`, `src/digital_factory.mjs` | Cùng JS core / worlds | Tác động theo trạm, ETA | Animation chỉ là trình diễn |
| 3D CSS | `factory_3d.html`, `src/factory_3d.mjs`, `src/factory_3d_logic.mjs` | Cùng JS core / worlds | Trực quan hóa 3D, lựa chọn | Không phải 3D vật lý đã hiệu chuẩn |
| Backfire demo | `resilience_lab/index.html` | Mô hình JS nhỏ riêng | So sánh quyết định cục bộ và hệ thống | Không phải solver G3/G4 |
| Official CP-SAT viewer | `factorypulse_experiment_v1/official_lab/web/` | Python CP-SAT / dữ liệu công khai | Lịch và bằng chứng solver | Cần backend Python, Three.js có thể cần mạng |
| AI Risk / Fleet / MAPF | `factorypulse_experiment_v1/ai_swarm/` | Thí nghiệm Python mô phỏng | Metrics và bài kiểm toán | Không tự chạy trong JS demo |

## Phân loại file, không xóa ở đợt chốt

**Dùng để trình diễn:** `index.html`, `digital_factory.html`, `factory_3d.html`, `resilience_lab/index.html`, `demo_hub.html`.

**Thí nghiệm / kiểm toán:** `factorypulse_experiment_v1/`, `.github/workflows/`, `docs/COOPERATIVE_MAPF_EVIDENCE.md`, `docs/VALIDATION_GATES.md`.

**Phiên bản dự phòng / di sản cần kiểm tra trước khi chuyển kho:** `standalone.html`, `FactoryPulse_Experiment_v1_0_Review/`. Không xóa vì còn có thể được liên kết từ hướng dẫn cũ hoặc dùng để tái lập.

**Tài nguyên:** `assets/` chứa dữ liệu tĩnh cho các giao diện. Không xóa theo kích thước hay tên file nếu chưa kiểm tra tham chiếu CSS/JS.

## Chạy và thử

```powershell
# ở thư mục root repository
py -3 -m http.server 8000
# vào http://localhost:8000/demo_hub.html
```

Trong cửa sổ khác:

```powershell
npm test
node --test tests/demo_hub_links.test.mjs
```

Các bài test Node kiểm tra logic/href chứ **không thay thế kiểm tra tương tác bằng trình duyệt**. Trước khi nộp: mở cả 4 demo dễ dùng, thử ba tình huống, xác minh không có lỗi console/404; kiểm thử official viewer riêng vì phụ thuộc server và dữ liệu.

## Nguyên tắc bảo trì

1. Mọi demo mới phải đăng ký ở `demo_hub.html` và được mô tả engine đúng tên.
2. Không ghi JS dashboard chạy CP-SAT, AI hoặc MAPF nếu chưa có adapter/backend thật và test E2E.
3. Nếu muốn di chuyển/xóa bản dự phòng, kiểm tra tất cả tham chiếu và so sánh nội dung trước; nên làm ở PR sau kỳ nộp.
4. Không đổi benchmark đã khóa chỉ để cải thiện cách trình bày repository.
