# FactoryPulse D3 — Giao thức thí nghiệm v1.0 (Pre-registration)

**Ngày khóa bản thiết kế:** 2026-10-10. **Trạng thái:** Thiết kế trước benchmark so sánh; CHƯA chạy CP-SAT/B3. Các sửa đổi sau này phải ghi trong CHANGELOG trước khi mở tập test. Không phải kết quả hiệu quả tại DENSO.

## 1. Câu hỏi và phạm vi

H1: trong một số tình huống máy dừng giữa ca của Flexible Job Shop Scheduling (FJSP), tái lập lịch có chọn lọc có thể cho lịch hợp lệ và makespan gần với bộ giải toàn cục, với thời gian đầu-cuối thấp hơn. Thí nghiệm này không kiểm tra thiếu vật tư, QA, MES/ERP hay hiệu quả tại DENSO.

Tách 3 cấp kết luận: (i) lịch hợp lệ; (ii) chất lượng và tốc độ cạnh tranh; (iii) cải thiện quyết định trong nhà máy thực. Chỉ nghiên cứu (i) và (ii), không suy diễn (iii).

## 2. Nguồn, bản gốc và đối soát

Nguồn chính: https://github.com/SchedulingLab/fjsp-instances/blob/main/brandimarte/mk01.txt ; metadata https://github.com/SchedulingLab/fjsp-instances/blob/main/instances.json . Đọc README và bài báo Brandimarte gốc khi viện dẫn benchmark. Repo GitHub có LICENSE MIT cho repo; cần xác minh quyền phát hành lại dữ liệu thuộc bài báo gốc trước khi phân phối rộng. Tệp trong thư mục data được chép từ nội dung công khai qua GitHub connector ngày 10/10/2026; đối soát hash với bản GitHub raw khi mạng cho phép. SHA256 cục bộ ghi trong results/smoke_results.json. Không sửa tệp gốc để tiêm sự cố.

Schema gốc: số jobs, số machines; mỗi job là chuỗi operations; mỗi operation có tập (machine_id zero-based, processing_time > 0). Đơn vị thời gian là *đơn vị benchmark*, không mặc định là phút thật.

## 3. Trạng thái nhà máy mô phỏng tại thời điểm sự cố

S0 = (instance, feasible_baseline_schedule, event_time=t, disruption=(machine_m, interval_[t,t+d)), operation_status). Lịch gốc được xây từ một phương pháp công bố trước, lưu nguyên tệp và cung cấp giống nhau cho B1/B2/B3.

- `FINISHED`: end <= t; cố định machine/start/end.
- `RUNNING_UNAFFECTED`: start < t < end trên máy không hỏng; tiếp tục non-preemptive và cố định.
- `RUNNING_FAILED`: start < t < end trên máy hỏng; **chính sách thử nghiệm v1:** công đoạn hỏng được coi là chưa hoàn thành và bắt buộc thực hiện lại từ đầu sau t trên một máy hợp lệ; phần thời gian đã chạy trước t là sunk cost, không ghi như một operation hoàn tất. Điều này là giả định mô phỏng, KHÔNG phải quy tắc DENSO.
- `NOT_STARTED`: start >= t; có thể tái lập lịch, nhưng không được đặt thời điểm bắt đầu trước t.

Khi đánh giá lịch sau sự cố: chỉ lưu một bản ghi cuối cùng cho mỗi operation; thao tác đang hỏng được reschedule toàn phần, không giữ lịch xử lý cũ dưới dạng operation song song. Phần đã hoàn thành hoặc đang chạy không hỏng là immutable. Không cho phép hoạt động trên máy m trong [t,t+d). Mọi phương pháp dùng đúng chính sách này.

## 4. Quy tắc sinh sự cố v1

Trên mỗi lịch gốc, lấy thời điểm sự cố tương ứng 25%, 50%, 75% makespan ban đầu (làm tròn xuống). Chọn máy theo ID tăng dần, loại trường hợp không có operation liên quan tới trạng thái lịch tại hoặc sau t và ghi rõ số ca loại. Thời lượng d thuộc {5,15} *đơn vị benchmark*, không gọi phút. Seed {11,23,37,53,71}; dùng seed cho thứ tự tình huống nếu phải giới hạn ngân sách. Không chọn ca vì B3 thắng. Tỷ lệ loại ca, máy gây sự cố và thời điểm phải được công bố.

**Lưu ý trước khi code:** một sự cố có thể rơi đúng ranh giới công đoạn; định nghĩa interval nửa mở [start,end), `start <= t < end` là đang chạy. Nếu không có máy nào bị ảnh hưởng trực tiếp tại thời điểm t, vẫn có thể có ảnh hưởng tương lai vì downtime chồng lịch dự kiến.

## 5. Baseline / đối chứng

- **B1:** heuristic earliest-completion, với cùng phần đã cố định tại t và cùng tập operation còn lại; trước khi hoàn thành B1 động, không sử dụng heuristic tĩnh hiện có như bằng chứng so sánh.
- **B2:** OR-Tools CP-SAT toàn cục; tất cả công đoạn đủ điều kiện tái lập được đưa vào mô hình, giữ phần immutable. Công bố phiên bản solver, num_search_workers=1 để giảm tính bất định, random_seed theo seed thí nghiệm, max_time_in_seconds=10 giây cho lượt chính. Ghi wall-time toàn luồng và thời gian solver riêng, status/best bound/objective.
- **B3a:** chọn vùng chỉ bằng precedence.
- **B3b:** bổ sung expansion theo tranh chấp tài nguyên/eligible alternative machines.
- **B3c:** chuỗi lần thử vùng nhỏ → mở rộng → fallback B2; tổng thời gian gồm tất cả lần thử và fallback, phải tuân cùng tổng budget 10 giây, kể cả thời gian xây mô hình/kiểm tra. Một lần fallback thành công KHÔNG được ghi như thắng lợi của chọn lọc.

B3a/b/c chưa được cài đặt; không giả định trước chất lượng của chúng. Phần lịch ngoài vùng cố định có thể khiến mô hình mất cơ hội tối ưu toàn cục dù vẫn hợp lệ. Bộ kiểm tra lịch chỉ chứng minh tính hợp lệ, không chứng minh tối ưu.

## 6. Chỉ số, kiểm tra độc lập, điều kiện loại trừ

Validator độc lập với optimizer, kiểm tra một bản ghi duy nhất/operation; eligible machine; positive duration đúng lựa chọn máy; precedence; no overlaps; downtime; immutable operations; mọi operation có đủ. Validator cần được mở rộng test disruption state *trước B3*. Lịch invalid được tính vào tỷ lệ thất bại, không loại im lặng.

Metrics: valid_rate; makespan; `delta_makespan = (C_B3 - C_B2)/C_B2` (B2 là mốc thực nghiệm nếu chưa OPTIMAL); changed_machine_count; changed_start_count; end-to-end seconds; solver seconds; selected-region-size; retry_count; fallback_rate; feasibility errors. Với solver TIMEOUT/UNKNOWN, ghi nguyên trạng thái và không tự coi là infeasible. Tách số liệu theo instance, tỷ lệ lựa chọn máy, thời điểm downtime và mức d.

Ngưỡng để phát triển H1 (ngưỡng sàng lọc nghiên cứu, CHƯA được DENSO phê duyệt): **100% lịch được xuất là hợp lệ**, median end-to-end B3 <= 0.8 × B2, median makespan B3 <= 1.05 × B2, fallback < 20% trên tập test. Báo cáo phân bố và worst case; không được loại các ca xấu khỏi mẫu số. Nếu B2 đã chạy quá nhanh (<0.1s median) thì chênh lệch tương đối không đủ để khẳng định lợi ích thực tế dù đạt ngưỡng. Các ngưỡng không đại diện KPI DENSO.

Các trường hợp loại khỏi mẫu so sánh theo quy tắc trước: tệp parse hỏng do nguồn; instance vượt giới hạn phần cứng khiến cả hai phương pháp không tạo được kết quả trong 10s; sự cố không tác động lịch dự kiến (được ghi riêng); lỗi môi trường phải báo thay vì che. Không loại kết quả vì B3 thua.

## 7. Dataset split, khóa thuật toán và thay đổi giao thức

- **Smoke/dev:** mk01, mk02 và mk03; chỉ để kiểm tra parser, consistency, solver và phát triển B3. Không dùng số này tuyên bố hiệu quả tổng quát.
- **Holdout:** mk04, mk05, mk06, mk07, mk08, mk09, mk10 (chỉ nếu tải/kiểm chứng được). Chạy theo thứ tự tên công bố, không chọn sau khi thấy kết quả; giữ nguyên B3 và metric trước khi xem holdout.
- Ngoài Brandimarte, thí nghiệm xác nhận chéo trên Hurink chỉ sau khi khóa cách chọn cụ thể. Kết quả không suy diễn ra mọi cấu trúc nhà máy.

Nếu bug khiến phải sửa thuật toán hoặc thước đo sau khi xem holdout, coi kết quả holdout trước đó là khám phá, công khai thay đổi và cần tập xác nhận mới.

## 8. Thứ tự phát triển/gates

G1 parser strict + hash + metadata; G2 validator độc lập + mutant negative tests; G3 B1 động/B2 CP-SAT baseline và log; G4 generator sự cố theo protocol; G5 B3 variants; G6 holdout. Không đi tiếp nếu gate trước chưa được chứng minh bằng kết quả có thể tái lập.

## 9. Trạng thái thực hiện ngay lúc viết

G1 đã đọc mk01 và lưu hash cục bộ. G2 mới kiểm tra lịch tĩnh/downtime/frozen trong test đơn vị; cần bổ sung lịch hậu sự cố đúng chính sách tại mục 3. Có greedy tĩnh làm smoke test, CHƯA có baseline B1 động. OR-Tools chưa cài được trong môi trường, B2 chưa chạy. G4–G6 chưa triển khai. Tuyệt đối không trình bày smoke test như xác nhận H1.
