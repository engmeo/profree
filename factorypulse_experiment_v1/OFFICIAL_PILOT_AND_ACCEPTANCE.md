# FactoryPulse — pilot vận hành và tiêu chí nghiệm thu (đề xuất, chưa triển khai tại DENSO)

**Phạm vi:** nguyên mẫu hỗ trợ quyết định qua mô phỏng. Không tự động can thiệp thiết bị, không nhận dữ liệu nhà máy theo thời gian thực, không tuyên bố ROI đo tại DENSO.

## Đối tượng sử dụng và điểm đau

Trong một chuỗi sản xuất, quyết định ưu tiên một job có thể giúp job đó hoàn thành sớm nhưng khiến những đơn hàng khác trễ hơn. Hệ thống cho phép đối chiếu lịch LOCAL, C1 (sửa lịch bảo thủ), C2 (tối ưu makespan) và B3-B (có chi phí đổi máy/độ dịch lịch), cùng ràng buộc máy và thông tin vật tư, QA mô phỏng. **C2 tối ưu makespan, không trực tiếp tối ưu tổng tardiness**; do đó chỉ tuyên bố KPI thực đo từ mỗi lịch, không mặc định C2 tối ưu mọi chỉ số.

## Dữ liệu cần để thử nghiệm thực tế

| Nguồn | Trường tối thiểu | Đích và kiểm tra |
|---|---|---|
| ERP/APS | order_id, sku, quantity, due_time, priority, planned_start | Kết nối đơn hàng với job, giữ nguồn và phiên bản thay đổi |
| MES | operation_id, job_id, sequence, machine_id, actual_start/end, status | Kiểm tra thời gian theo timezone, uniqueness, thứ tự công đoạn |
| Máy/maintenance | machine_id, downtime_start/end, capacity, eligible_operations | Xác thực sự cố, hiệu chuẩn đơn vị và ca vận hành |
| WMS | material_id, lot, on_hand, reserved, inbound_eta, BOM | Ledger tồn kho không âm, tránh tính trùng hàng đặt trước |
| QMS | job/lot id, hold_start/end, disposition, rework_route | Không giả định QA hold đồng nghĩa phải tái gia công |
| TMS/shipping | order_id, ready_to_ship, pickup_deadline, promised_delivery | Kiểm tra độ trễ sản xuất khác với giao hàng thực |

**Liên kết dữ liệu:** khóa thống nhất order→job→operation→machine; BOM→material; QA→lot/job; shipping→order. Ghi phiên bản/timestamp, nguồn mỗi record; lỗi liên kết hoặc timestamp thiếu sẽ được gắn trạng thái không chắc chắn, không tự suy luận.

## Pilot có kiểm soát (đề xuất 12 tuần)

- **Tuần 1–2:** ký phê duyệt dữ liệu, scope một line/pilot; map nguồn ERP–MES–WMS–QMS–TMS; rà soát định nghĩa KPI và quy tắc an toàn với kỹ sư DENSO.
- **Tuần 3–4:** nhập lịch sử sự cố/lịch và tái dựng trạng thái tại thời điểm quyết định; kiểm tra completeness, đối chiếu timestamp, các job chưa hoàn thành.
- **Tuần 5–6:** tái phát các sự cố lịch sử trong mô hình; so sánh lịch thực tế với C1/C2/B3; xác thực manual sign-off của trưởng ca.
- **Tuần 7–9:** **shadow mode** tại một dây chuyền: nhận snapshot dữ liệu, tính khuyến nghị, không thực thi; log suggestion/ground truth/decision và lý do từ chối.
- **Tuần 10–11:** đánh giá theo ngày và theo loại sự cố, đối chứng same-snapshot, kiểm tra dữ liệu thiếu và độ trễ, phỏng vấn planners/QA/logistics.
- **Tuần 12:** họp nghiệm thu pilot; chỉ đề xuất mở rộng khi tất cả gate an toàn và chất lượng dữ liệu đạt ngưỡng đã thống nhất trước pilot.

## KPI và cách đo

1. **On-time delivery rate:** số đơn giao đúng hẹn / số đơn đến hạn; phân biệt dự báo ready-to-ship với dữ liệu giao hàng thực.
2. **Total weighted tardiness:** tổng `priority × max(0, completion - due)` trên cùng tập order. Thời gian và priority phải có quy định tại pilot, không tái chỉnh trọng số sau khi xem kết quả.
3. **Schedule disruption:** machine reassignment count, sum absolute start-time shifts, machine order inversions. Giảm đổi máy chưa đủ để tuyên bố giảm chi phí thực.
4. **Decision latency:** thời gian nhận snapshot→khuyến nghị khả dụng; báo median và p95, bao gồm thời gian dựng model và truy xuất dữ liệu.
5. **Safety/feasibility:** tỷ lệ lịch không vi phạm máy, precedences, frozen work, material ledger, QA hold; trường hợp UNKNOWN phải được giữ nguyên.
6. **Trust:** tỷ lệ planner chấp nhận/từ chối và lý do; tách khả năng giải thích khỏi việc cải thiện KPI.

## Cổng nghiệm thu thử nghiệm

- **Gate 1 (Dữ liệu):** có phê duyệt, định danh nhất quán, đầy đủ thời điểm trạng thái; mọi nguồn có audit trail. Ngưỡng completeness do bên triển khai và DENSO ký trước pilot, không tự đặt thành sự thật.
- **Gate 2 (Kỹ thuật):** mọi lịch đề xuất phải qua validator riêng và bất biến máy/vật tư/QA; thất bại hoặc dữ liệu mâu thuẫn → không tự động khuyến nghị.
- **Gate 3 (Thực nghiệm):** có paired baseline trên cùng snapshot, toàn bộ WIN/TIE/LOSS/INFEASIBLE/UNKNOWN; kiểm tra theo loại incident, mức tải, tổ/ca. Không cherry-pick.
- **Gate 4 (Vận hành):** chuyên gia đồng ý nguyên nhân liên quan, chi phí thay đổi lịch và khả thi triển khai. KPI đạt mục tiêu được ký trước pilot; không đưa % cải thiện hoặc ROI khi chưa đo.
- **Gate 5 (An toàn):** human-in-the-loop; cảnh báo QA và thiếu vật tư là hard constraints; rollback thử nghiệm và giám sát log.

## Định vị công nghệ

FactoryPulse hiện là **simulation-based decision-support prototype with digital-twin architecture**, chưa phải digital twin đồng bộ vật lý hai chiều. Đồ thị thể hiện quan hệ phụ thuộc theo mô hình, không xác nhận nhân quả thực nghiệm. Stress Finder thăm dò các điều kiện bất lợi hữu hạn, không chứng minh mọi trường hợp bất khả thi. Việc chạy bằng benchmark Brandimarte và policies tổng hợp không chứng minh hiệu quả tại nhà máy DENSO.
