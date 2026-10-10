# FactoryPulse D3 — Research evidence / Bằng chứng nghiên cứu

> **Research only · Not a deployed DENSO system.** This repository tests whether selective dynamic rescheduling has any advantage over strong baselines. It does **not** claim to reduce actual factory costs or improve DENSO operations.

**DENSO Factory Hacks 2026 — D3.** Việc thiếu liên kết dữ liệu chuỗi sản xuất, suy luận tác động và hành động ứng phó là ba đầu ra được nghiên cứu. Repository hiện **chỉ** thực hiện một lát cắt: ngừng máy trong bài toán Flexible Job-Shop Scheduling; không giả vờ đã tích hợp MES/ERP/PLC/QA.

## Vấn đề và giá trị có thể kiểm chứng

Một máy dừng giữa ca có thể làm thay đổi nhiều công đoạn và lịch sử dụng máy thay thế. Việc tính lại *toàn bộ* có thể tốn thời gian, còn chỉ sửa những công đoạn trực tiếp bị ảnh hưởng có thể bỏ sót xung đột tài nguyên. **Giả thuyết chưa được xác nhận:** giải lại có chọn lọc với kiểm tra độc lập sẽ có lợi trong một số cấu trúc bài toán.

## Hiện trạng (2026-10-10)

| Thành phần | Trạng thái |
|---|---|
| Parser dữ liệu Brandimarte `mk01` (10 jobs, 6 machines, 55 operations) | Có |
| Validator lịch tĩnh & hậu sự cố + mutant unit tests | Có; kiểm tra ràng buộc đã mô hình hóa |
| B1 heuristic tái lập lịch động | Có; kết quả thô trong `results/dynamic_baselines.json` |
| B2 CP-SAT full rescheduling | **Đã viết, CHƯA chạy trong môi trường phát triển**; phụ thuộc `ortools` |
| B3a/b/c selective rescheduling | Chưa có |
| Liên kết dữ liệu DENSO, ba ca D3, tối ưu chi phí thực | Chưa có |

## Chạy lại (Python 3.10+)

```bash
python -m unittest discover -s tests -v
python run_experiment.py --data data/mk01.txt
python -m pip install -r requirements.txt
python run_experiment.py --data data/mk01.txt --with-cpsat --out results/cpsat_local.json
```

OR-Tools cần kết nối internet khi cài gói. Nếu chưa có `ortools`, **không** sử dụng tùy chọn `--with-cpsat`; chương trình sẽ báo ImportError thay vì tự chế kết quả. B2 sử dụng tối đa 10 giây mỗi ca, một worker, seed 11. Số wall-clock của từng máy không thể so sánh trực tiếp nếu khác phần cứng.

## Nguồn dữ liệu

- [SchedulingLab/fjsp-instances, Brandimarte mk01](https://github.com/SchedulingLab/fjsp-instances/blob/main/brandimarte/mk01.txt), lưu bản nguyên gốc trong `data/mk01.txt`; SHA256 trong `results/dynamic_baselines.json`.
- Trạng thái ngừng máy là **synthetic augmentation**, không phải trường gốc của benchmark hoặc log từ nhà máy.
- Vui lòng kiểm tra giấy phép tái phân phối của dữ liệu nghiên cứu nguyên gốc trước khi tái sử dụng ngoài phạm vi thử nghiệm. Mã tự viết có thể được cấp phép riêng, không tự động cấp phép lại cho benchmark.

## Giới hạn và yêu cầu Red Team

Đọc `EXPERIMENT_PROTOCOL_v1.0.md`; công khai mọi khác biệt về giao thức trong `PROTOCOL_DEVIATIONS.md`. B1 không phải SOP DENSO. CP-SAT không tự là oracle nếu chưa chứng minh tối ưu. Không dùng kết quả B1/metadata để quảng cáo lợi ích của FactoryPulse.

Red Team nên tập trung audit việc đóng băng công đoạn tại t, chính sách restart công đoạn đang hỏng, đầy đủ của validator và công bằng B1/B2 trước khi xây B3.

## English overview

**Problem:** disruption-aware flexible job-shop rescheduling under fixed execution state and machine downtime. **Evidence:** a public FJSP instance, separately labeled synthetic downtime, an independent feasibility validator, dynamic greedy baseline and a CP-SAT implementation awaiting execution. **Not supported:** any claim of industrial deployment, cost savings, algorithmic novelty or superiority over global rescheduling.

### GitHub Actions

GitHub Actions workflow ở `.github/workflows/experiment.yml` chạy ba ca CP-SAT để kiểm tra tính khả thi, **không** phải benchmark so sánh đầy đủ. Hãy upload **nội dung thư mục `factorypulse_experiment_v1/` lên root của một repo nghiên cứu** (hoặc chỉnh working-directory và path filters tương ứng nếu để trong thư mục con); nếu upload cả thư mục ngoài như một thư mục con thì workflow nằm sai vị trí và sẽ không kích hoạt.
