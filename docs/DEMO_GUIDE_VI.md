# FactoryPulse — Hướng dẫn tự demo cho Ban giám khảo

Tài liệu này phân biệt **giao diện web có thể thao tác bằng chuột** và **các thí nghiệm Python chạy bằng terminal**. Không phải mọi mô-đun nghiên cứu đều đã tích hợp vào cùng một dashboard.

## A. Demo bằng trình duyệt (khoảng 2–3 phút)

**Yêu cầu:** Python 3, trình duyệt hiện đại. Không cần GPU, API hay dữ liệu nhà máy. Mọi dữ liệu trong demo là giả lập.

**Windows:** nhấp đúp `RUN_DEMO_WINDOWS.cmd` ở thư mục gốc, hoặc chạy:

```powershell
py -3 -m http.server 8000
```

**Linux/macOS:** `python3 -m http.server 8000`.

Mở `http://localhost:8000`.

**Bước giới thiệu:** FactoryPulse minh họa chuỗi đơn hàng, vật tư, máy, QA và ETA giao hàng. Chọn một trong ba nhóm sự cố: **máy dừng**, **thiếu vật tư**, **QA hold**.

**Bước so sánh:** Thay đổi độ trễ tìm kiếm dữ liệu thủ công và độ trễ cập nhật dữ liệu tích hợp. Xem chỉ số thời gian quyết định, ETA đơn hàng và kết quả so sánh. Demo mô phỏng hai chính sách quyết định giống nhau về luật; khác nhau chủ yếu ở **thời điểm thông tin đến**. Không diễn giải thành AI tối ưu tự động.

**Bước phản biện:** Thử trường hợp thông tin tích hợp đã cũ: hệ thống chuyển về `VERIFY`, không âm thầm đưa ra đề xuất. Thử giới hạn phê duyệt/năng lực để quan sát các lựa chọn không hợp lệ bị chặn. Xuất JSON của lần chạy nếu muốn.

**Điểm cần nói rõ:** Đây là demo giao diện cho thông điệp D3. CP-SAT, AI Risk và Cooperative MAPF có các chương trình nghiên cứu độc lập bên dưới; thao tác trên web **không gọi** trực tiếp các solver/mô hình đó.

**Nếu cổng 8000 bận:** dùng `py -3 -m http.server 8001` rồi mở `http://localhost:8001`.

## B. Thử nghiệm có mã nguồn (không phải giao diện web)

**Yêu cầu:** Python 3.11 khuyến nghị, cài thư viện với mạng Internet, Git. Chạy lệnh tại thư mục `factorypulse_experiment_v1`. Các kết quả mô phỏng không dùng dữ liệu DENSO.

```powershell
cd factorypulse_experiment_v1
py -3 -m pip install -r requirements.txt scikit-learn==1.6.1 numpy==2.2.4
```

**B1 — Mô phỏng điều phối 20 robot với MAPF:**

```powershell
py -3 -m ai_swarm.cooperative_stress --seeds 100 --out results_mapf.json
```

Đọc các trường `complete_scenarios`, `unsolved_seed_examples`, `independent_audit_failed_scenarios`. Có 20 agent/kịch bản, một robot hỏng được cố định tại chỗ. Các ca chưa giải được vẫn được công khai. Đây **không phải mô hình an toàn robot vật lý**.

**B2 — AMR lỗi → thời điểm vật tư → CP-SAT → audit:**

```powershell
$env:PYTHONPATH = "src;."
py -3 -m ai_swarm.integration
```

Chương trình in hai phương án `BASELINE` và `AMR_FAILURE`, ETA vật tư, lịch công đoạn, trạng thái solver và `independent_audit_errors`. Đặt `$env:PYTHONPATH="src;."` cho phiên PowerShell hiện tại. Trên Linux/macOS: `PYTHONPATH=src:. python3 -m ai_swarm.integration`.

**B3 — Đọc kết quả AI Risk hiện có:**

Vào [GitHub Actions](https://github.com/engmeo/profree/actions), mở workflow **FactoryPulse AI Risk + Heterogeneous Fleet Research**, tải artifact `factorypulse-ai-swarm-exploratory-evidence` của lần chạy thành công. Báo cáo chứa dữ liệu train/holdout, PR-AUC, precision, recall; kết quả vẫn mang tính nghiên cứu.

**B4 — Tái tạo benchmark AI trên máy (nặng hơn):**

```powershell
py -3 fetch_public_instances.py --names mk02 mk03
py -3 official_lab/expanded_matrix.py --data data/mk01.txt data/mk02.txt data/mk03.txt --out results/expanded_matrix --timeout 2
py -3 official_lab/expanded_audit.py --out results/expanded_matrix --data data/mk01.txt data/mk02.txt data/mk03.txt
py -3 ai_swarm/risk.py --results results/expanded_matrix/results.json --out results/ai_swarm/risk_report.json
```

Cần tạo thư mục trước nếu chưa có: `New-Item -ItemType Directory -Force results/ai_swarm | Out-Null`. Các bài toán tối ưu có thể tốn thời gian, phụ thuộc phần cứng và dữ liệu public cần tải. **Không bắt buộc chạy lại B4 để hiểu demo chính.**

## C. Kiểm thử tự động của bản demo web

Yêu cầu Node.js 18+; tại thư mục gốc:

```powershell
npm test
npm run benchmark
```

`npm run benchmark` là tập các tình huống web giả lập do nhóm thiết kế, **khác với benchmark nghiên cứu CP-SAT** trong `factorypulse_experiment_v1`. Không lấy kết quả của bộ này làm hiệu quả sản xuất DENSO.

## D. Nếu BGK chỉ có 2 phút

Mở giao diện web → chọn một ca máy dừng → xem ảnh hưởng và điều chỉnh độ trễ thông tin → thử ca dữ liệu cũ để xem `VERIFY`. Đọc bảng “FactoryPulse gồm những gì?” trong README để hiểu các nhánh nghiên cứu thêm.

## E. Điều chưa được chứng minh

- Không có vận hành trực tiếp trên dữ liệu và dây chuyền DENSO.
- Không có URL demo hosted đã được xác minh; cách chạy chắc chắn nhất hiện là tải ZIP và mở server tại máy.
- Không thể suy ra nguồn gốc nhân quả thật từ những sự cố giả lập.
- Không có chứng nhận an toàn cho 20 AMR thật, không chứng minh ROI hay cải thiện KPI thực địa.
