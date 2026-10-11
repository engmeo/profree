# FactoryPulse — Mô phỏng nhà máy 2D và 3D

## Những gì thực sự chạy

- **2D:** `digital_factory.html` — sơ đồ luồng công đoạn, các trạm, tiến trình sự cố, bảng ETA, phương án, kiểm tra phê duyệt. Giữ lại để debug và demo dự phòng.
- **3D:** `factory_3d.html` — nhà máy không gian ba chiều tạo bằng **CSS 3D transforms**, có camera xoay bằng kéo chuột, zoom cuộn chuột, chọn trạm, hoạt ảnh máy CNC/băng chuyền/thùng hàng, điểm cảnh báo, đồ thị tác động và bảng lựa chọn phương án.
- **Engine dùng chung:** `src/worlds.mjs` (dữ liệu tổng hợp), `src/core.mjs` (evaluate, decide, eligible). Giao diện 3D sử dụng `src/factory_3d_logic.mjs` làm adapter. Mọi ETA/điểm tổn thất/khuyến nghị đều do engine tính, không tạo số ngẫu nhiên trên UI.

**Giới hạn:** Đây là trình diễn 3D bằng CSS, không phải Three.js/WebGL, photorealistic 3D, mô hình nhà máy DENSO hay digital twin đã hiệu chuẩn. Thao tác tương tác/camera/render là thật, nhưng các ràng buộc và dữ liệu là giả lập. Dự báo ở đây là **what-if impact projection** sau sự cố, không phải mô hình ML dự báo thời điểm máy hỏng. Gợi ý không điều khiển thiết bị hoặc tự động phê duyệt.

## Cài / Chạy ngay trên Windows

Chép **nội dung trong `REPO_OVERLAY`** vào thư mục `C:\Users\tuant\profree`, giữ nguyên các file khác.

Từ PowerShell tại gốc repo:

```powershell
cd C:\Users\tuant\profree
py -m http.server 8000
```

Truy cập:
- `http://localhost:8000/factory_3d.html` — 3D
- `http://localhost:8000/digital_factory.html` — 2D (nếu trước đó đã chép gói 2D)
- `http://localhost:8000/index.html` — dashboard hiện có

**Nếu gặp 404**, chạy `Test-Path .\factory_3d.html` tại gốc repo; file phải trả về `True`. Nếu cổng bận, chạy `py -m http.server 8080` và đổi URL tương ứng. Không mở trực tiếp file HTML qua `file://` vì trình duyệt có thể chặn ES module.

## Cách demo 3 tình huống

1. Chọn **Máy hỏng**, nhấn `Chạy mô phỏng`: quan sát M-CUT-01 chuyển từ chạy sang cảnh báo, đồ thị tô sáng QA/TMS, ETA tính lại.
2. Thử `Wait`, `Expedite maintenance`, `Route to approved backup` (tên action từ model), so sánh `Tổng thời gian trễ` và `Điểm tổn thất`.
3. Tắt `Cho phép...` để thấy phương án rủi ro bị vô hiệu; tắt `Dữ liệu mới` để hệ thống yêu cầu `VERIFY`.
4. Chọn **Thiếu vật tư**: WMS cảnh báo, MES/QA/TMS bị ảnh hưởng; chọn thúc nhập hoặc vật tư thay thế đã duyệt.
5. Chọn **QA hold**: trạm kiểm định cảnh báo, cổng giao hàng bị ảnh hưởng; so sánh kiểm định lại có phê duyệt.
6. Kéo chuột xoay nhà máy, cuộn zoom, bấm vào trạm, rồi `Xuất JSON kết quả` để xem dữ liệu thực tính.

## Đóng góp file mới (không ghi đè file cũ)

```text
factory_3d.html
FACTORY_SIMULATIONS_README.md
src/factory_3d.css
src/factory_3d.mjs
src/factory_3d_logic.mjs
tests/factory_3d.test.mjs
```

`core.mjs`, `worlds.mjs` trong ZIP chỉ là **bản chạy độc lập** và không cần ghi đè trong repo hiện hữu. Trên repo hiện tại, **KHÔNG thay thế** chúng. Có thể dùng thư mục `STANDALONE_DEMO` để chạy thử tách biệt trước khi đưa lên Git.

## Kiểm thử

```powershell
node --test tests/factory_3d.test.mjs
```

Để test toàn bộ demo: `npm test` tại gốc repo nếu Node đã cài. Hai giao diện dùng chung `core.mjs`, nên thay đổi logic chung sẽ phản ánh lên cả hai.

## Phân biệt 2D và 3D khi nộp

- **2D** chứng minh các chỉ số và luồng phụ thuộc có thể kiểm tra.
- **3D** trực quan hóa cùng một kịch bản, hỗ trợ quay video và trình diễn trực tiếp.
- **Kết quả nghiên cứu G3/G4/B3** thuộc hệ solver Python riêng trong `factorypulse_experiment_v1`; giao diện JS không tự chạy CP-SAT khi chọn sự cố. Không mô tả hai hệ là tích hợp hoàn toàn.
