# FactoryPulse — Hiểu tác động sự cố. Thử trước phương án. Quyết định có căn cứ.

**DENSO Factory Hacks 2026 · D3 — Data / Chuẩn hóa & Khai thác**  
**Trạng thái: prototype nghiên cứu chạy được, không phải hệ thống triển khai tại DENSO.**

> **Một máy dừng, linh kiện giao muộn hoặc lô hàng bị giữ QA sẽ ảnh hưởng tới những công đoạn và đơn hàng nào? Nếu ưu tiên xử lý một đơn, liệu toàn bộ lịch sản xuất có trở nên tệ hơn?** FactoryPulse thử các phương án xử lý trên mô hình có ràng buộc, giúp người lập kế hoạch xem tác động và đánh đổi **trước khi ra quyết định**.

## ▶ Dùng thử ngay — không cần clone để hiểu bài toán

**Lựa chọn 1 — xem demo web (dễ nhất, dành cho BGK).** Đây là giao diện tương tác chạy bằng trình duyệt, dùng **dữ liệu giả lập** và mô hình xử lý sự cố dựa trên luật. Tại trang này, bạn có thể chọn tình huống **hỏng máy / thiếu vật tư / QA hold**, thay đổi thời gian thông tin đến, xem tác động đến đơn hàng, các đề xuất và xuất JSON. **Demo web này không phải giao diện chạy trực tiếp của CP-SAT, AI hay MAPF**; phần nghiên cứu đó có lệnh tái lập riêng ở dưới.

**Windows:** Tải mã nguồn bằng **Code → Download ZIP**, giải nén, nhấp đúp `RUN_DEMO_WINDOWS.cmd` rồi mở `http://localhost:8000` (script sẽ cố mở trình duyệt tự động). Yêu cầu có Python được cài trên máy. Nếu muốn chạy thủ công:

```powershell
cd <thu-muc-repo>
py -3 -m http.server 8000
# Truy cập http://localhost:8000 trên trình duyệt
```

**macOS / Linux:** mở terminal trong thư mục repo và chạy `python3 -m http.server 8000`, sau đó vào `http://localhost:8000`.

**Nếu BTC muốn xem mà không cài Python:** dùng bản **GitHub Pages** *nếu nhóm đã xuất bản và xác minh link hoạt động*. Hiện repository chưa xác nhận URL Pages công khai, vì vậy chúng tôi **không gắn link demo giả**. Cần có một URL đã triển khai trước khi nộp để BGK xem chỉ bằng một cú nhấp.

➡ **[Hướng dẫn demo chi tiết, tình huống để bấm và kết quả mong đợi](docs/DEMO_GUIDE_VI.md)**

## FactoryPulse gồm những gì?

| Thành phần | Vai trò | Cách xem / kiểm chứng |
|---|---|---|
| **Web demo D3** | Minh họa luồng thông tin liên phòng ban, tình huống sự cố và quyết định có ràng buộc | `RUN_DEMO_WINDOWS.cmd` → `http://localhost:8000` |
| **CP-SAT rescheduling** | Thử lịch thay thế, tôn trọng năng lực máy, thứ tự công đoạn, thời điểm vật tư và QA; so sánh các chính sách LOCAL / C1 / C2 / B3 | [Hướng dẫn chạy nghiên cứu](docs/DEMO_GUIDE_VI.md#b-thử-nghiệm-có-mã-nguồn-không-phải-giao-diện-web) |
| **AI Decision Risk Prediction** | Huấn luyện/đánh giá cảnh báo khi ưu tiên cục bộ có thể làm xấu độ trễ tổng thể | `factorypulse_experiment_v1/ai_swarm/risk.py`; kết quả còn yếu, chưa dùng tự quyết định |
| **Heterogeneous AMR / MAPF** | Mô phỏng robot khác loại, lỗi robot, tìm đường có đặt chỗ theo thời gian, đánh giá xung đột và tiến triển nhiệm vụ | `ai_swarm/cooperative_fleet.py`, `cooperative_stress.py` |
| **AMR → vật tư → CP-SAT → audit** | Kiểm tra một ca robot gặp lỗi làm đổi ETA vật tư và tác động lịch sản xuất | `ai_swarm/integration.py`; đây là pilot **một chuyến giao vật tư** |
| **Kiểm toán độc lập & CI** | Đối chiếu tính hợp lệ lịch, báo cáo KPI, hồi quy các tình huống | [GitHub Actions](https://github.com/engmeo/profree/actions) |

## Ba tình huống mà Ban giám khảo có thể theo dõi

**1. Hỏng máy:** một tài nguyên dừng hoạt động → công đoạn bị ảnh hưởng → lịch các công đoạn khác phải điều chỉnh. Câu hỏi cần trả lời không chỉ là “máy nào hỏng?” mà còn là “đơn hàng nào có thể trễ và đổi lịch có hợp lệ không?”.

**2. Vật tư / AMR:** linh kiện chưa đến hoặc robot giao hàng hỏng → ETA cấp phát thay đổi → sản xuất không được bắt đầu trước khi vật tư sẵn sàng. Bản nghiên cứu đã kiểm thử cầu nối ETA → ràng buộc vật tư → CP-SAT với một nhiệm vụ giao hàng mô phỏng.

**3. QA hold / rework:** hàng chưa qua QA phải chờ; nếu cần làm lại, công đoạn và điều kiện sản xuất được bổ sung vào phương án lập lịch.

**Điểm khác biệt:** thay vì chỉ tô đỏ cảnh báo, hệ thống nghiên cứu **thử lịch thay thế, kiểm tra ràng buộc và công khai các đánh đổi**; mọi quyết định sản xuất thực tế vẫn do con người phê duyệt.

## Bằng chứng đã có — và giới hạn cần hiểu đúng

- Các workflow chính trên `main` đã PASS ở bản chốt nghiên cứu (bao gồm CP-SAT, G4, AMR/material integration, AI study, MAPF). Có thể xem **từng lần chạy** tại [Actions](https://github.com/engmeo/profree/actions); kết quả CI không phải chứng nhận vận hành thực tế.
- Benchmark lập lịch trên các instance công khai `mk01`–`mk03`, sự cố/vật tư/QA **được giả lập**. Một số ưu tiên cục bộ có thể làm xấu độ trễ toàn hệ thống.
- AI đã được huấn luyện và kiểm tra trên instance giữ riêng; **độ chính xác hiện chưa đủ để tự động quyết định**. Đây là hướng nghiên cứu và cảnh báo bổ trợ.
- MAPF có tiến triển đáng kể so với điều phối tham lam, nhưng vẫn có ca không giải được; kiểm toán chỉ xác nhận các bất biến **trong môi trường lưới rời rạc**.
- **Không có dữ liệu vận hành DENSO, chưa đo ROI, chưa chứng minh cải thiện KPI thực địa và chưa chứng nhận an toàn robot vật lý.** Không trình bày các con số mô phỏng như kết quả tại DENSO.

Chi tiết: [AI / AMR — bằng chứng và giới hạn](factorypulse_experiment_v1/AI_SWARM_EVIDENCE_AND_LIMITS.md) · [Kế hoạch thẩm định](docs/VALIDATION_GATES.md).

## Nếu được chọn: thí điểm có kiểm soát trong 12 tuần

Chọn một line và KPI thực tế → chuẩn hóa nguồn ERP/MES/WMS/QA → phát lại sự cố lịch sử → chạy shadow mode (không sửa lịch thật) → so với quy trình hiện tại → quyết định Go/No-Go. Đo **thời gian ra quyết định an toàn, tỷ lệ lịch hợp lệ, độ trễ đơn hàng, số lần đổi lịch, công sức và chi phí**. ROI chỉ được tính từ số liệu thu được trong pilot.

## Người đánh giá / kỹ thuật viên muốn chạy lại toàn bộ?

Xem [DEMO_GUIDE_VI.md](docs/DEMO_GUIDE_VI.md) — có lựa chọn **demo web 2 phút**, **kiểm thử Node.js**, **mô phỏng MAPF**, **pilot AMR → CP-SAT** và **tái tạo benchmark/AI**. Các phần nghiên cứu yêu cầu Python và thư viện riêng; không đồng nhất với demo web.

**Mã nguồn:** [engmeo/profree](https://github.com/engmeo/profree) · **Giấy phép:** MIT (không bao gồm quyền sở hữu trí tuệ template BTC hoặc bộ dữ liệu bên thứ ba).
