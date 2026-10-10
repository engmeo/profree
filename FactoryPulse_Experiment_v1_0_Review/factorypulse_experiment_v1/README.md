# FactoryPulse — thí nghiệm tiền đăng ký (v1.0)

> Experimental scaffolding only. No demonstrated FactoryPulse improvement, DENSO integration or CP-SAT result.

Gói này KHÔNG phải phần mềm FactoryPulse hoàn chỉnh. Nó chỉ gồm dữ liệu FJSP `mk01` từ nguồn tham chiếu, parser strict, validator lịch độc lập với heuristic, 11 unit tests và một greedy smoke test.

## Chạy lại (Python 3.10+; chỉ standard library)

```bash
cd factorypulse_experiment_v1
python -m unittest discover -s tests -v
PYTHONPATH=src python - <<'PY'
from fjsp import parse_fjsp, greedy, validate_schedule, makespan
x=parse_fjsp('data/mk01.txt')
s=greedy(x)
print(len(x['jobs']),x['machines'],sum(len(j) for j in x['jobs']))
print('makespan',makespan(s),'errors',validate_schedule(x,s))
PY
```

Xem `EXPERIMENT_PROTOCOL_v1.0.md` để biết định nghĩa sự cố, split, đối chứng, ngân sách và điều kiện thất bại. Xem `results/smoke_results.json` cho output thô.

**Lưu ý nguồn:** https://github.com/SchedulingLab/fjsp-instances ; xem LICENSE ở upstream và kiểm tra quyền bộ dữ liệu của bài báo gốc khi công bố bản phân phối.

**Chưa thực hiện:** OR-Tools CP-SAT (không có thư viện trong môi trường offline); baseline động; tiêm sự cố có trạng thái; B3a/B3b/B3c; đánh giá holdout. Mốc makespan tối ưu mk01=40 đến từ metadata công khai, không phải nghiệm của chương trình này.
