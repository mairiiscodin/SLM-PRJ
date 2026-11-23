# Chạy trên Kaggle để so sánh với bài báo SLM-SQL

Mục tiêu: với mỗi model của bài báo, có hai con số:

1. **Tái lập**: bỏ phiếu (self-consistency) với đúng thiết lập của bài báo (prompt Appendix E.1, temperature 0.8, top-p 1.0, `max_new_tokens` 1024, vLLM), để kiểm tra pipeline khớp bài báo.
2. **Phương pháp mới** (cải tiến 3 trong [cai-tien-so-voi-bai-bao.md](cai-tien-so-voi-bai-bao.md)): hai vòng sinh, vòng hai chỉ cho model xem phần schema mà vòng một đã dùng, chọn bằng CAV-3. Tổng số mẫu sinh **bằng ngân sách của bài báo** và không dùng model merge.

| Tập | Bảng bài báo | Ngân sách | Vòng 1 (schema đầy đủ) | Vòng 2 (schema rút gọn) | Phương pháp mới |
|---|---|---|---|---|---|
| BIRD dev | Bảng 2 (64 mẫu + CSC) | 64 | 64 mẫu (để có Vote@64) | 32 mẫu, schema theo 32 mẫu đầu | 32 mẫu đầu vòng 1 + 32 vòng 2 |
| Spider dev | Bảng 3, Dev EX (SC 16 mẫu; CSC) | 16 | 16 mẫu (để có Vote@16) | 8 mẫu, schema theo 8 mẫu đầu | 8 mẫu đầu vòng 1 + 8 vòng 2 |

Bước rút gọn schema chỉ đọc SQL do model sinh ra ở vòng 1, không bao giờ nhìn đáp án. Nó chạy ngay trong notebook (`evaluation.schema_keep`), nên mỗi notebook chạy cả hai vòng liền nhau.

Với SLM-SQL-1.5B trên BIRD, cả hai vòng đã có: vote 61.54, CAV-3 66.95, hai vòng + CAV-3 là 67.86 (w=1) và **68.19** (w=2), so với 67.08 của bài báo.

## 1. Danh sách notebook

Các notebook nằm trong [notebooks/paper/](../notebooks/paper/), sinh bằng `python scripts/make_paper_notebooks.py`. Tên file theo dạng `<tập>_<model>_<số mẫu hoặc giai đoạn>_2vong`; zip kết quả trùng tên notebook.

| Notebook | Kaggle dataset | Model chạy | Thư mục kết quả (vòng 1, vòng 2) | Bài báo | Thời gian (T4 x2) |
|---|---|---|---|---|---|
| `bird-dev_SLM-SQL-0.5B_64mau_2vong` | `slmsql-bird-dev` | `cycloneboy/SLM-SQL-0.5B` | `bird-dev-0.5b-rl`, `…-prune32` | 56.87 | vòng 1 **đã xong**, vòng 2: 2–3 giờ |
| `bird-dev_SLM-SQL-0.6B_64mau_2vong` | `slmsql-bird-dev` | `cycloneboy/SLM-SQL-0.6B` | `bird-dev-0.6b-rl`, `…-prune32` | 59.52 | 15–17 giờ, 2 version (vòng 1 đo thật ~11 giờ: Qwen3 sinh dài) |
| `bird-dev_SLM-SQL-Base-1B_64mau_2vong` | `slmsql-bird-dev` | `cycloneboy/SLM-SQL-Base-1B` (SFT) | `bird-dev-1b-sft`, `…-prune32` | 54.78 (SFT + RL) | 7–10 giờ |
| `bird-dev_SLM-SQL-1.3B_64mau_2vong` | `slmsql-bird-dev` | `cycloneboy/SLM-SQL-1.3B` | `bird-dev-1.3b-rl`, `…-prune32` | 62.19 | 24–36 giờ (3 version) |
| (đã có) | | `cycloneboy/SLM-SQL-1.5B` | `bird-dev-vllm-64`, `bird-dev-prune32` | 67.08 | |
| `spider-dev_0.5B-Qwen2.5-Coder-0.5B-Instruct_base-sft-rl_2vong` | `slmsql-spider-dev` | RL, SFT, base | `spider-dev-0.5b-{rl,sft,base}`, `…-prune8` | 70.60 / 65.31 / 42.13 | 2–3 giờ |
| `spider-dev_0.6B-Qwen3-0.6B_base-sft-rl_2vong` | `slmsql-spider-dev` | RL, SFT, base | `spider-dev-0.6b-…` | 72.05 / 68.02 / 63.19 | 3–5 giờ |
| `spider-dev_1B-Llama-3.2-1B-Instruct_base-sft-rl_2vong` | `slmsql-spider-dev` | SFT, base | `spider-dev-1b-…` | – / 63.77 / 30.79 | 2–3 giờ |
| `spider-dev_1.3B-deepseek-coder-1.3b-instruct_base-sft-rl_2vong` | `slmsql-spider-dev` | RL, SFT, base | `spider-dev-1.3b-…` | 75.47 / 72.86 / 48.23 | 6–9 giờ |
| `spider-dev_1.5B-Qwen2.5-Coder-1.5B-Instruct_base-sft-rl_2vong` | `slmsql-spider-dev` | RL, SFT, base | `spider-dev-1.5b-…` | 75.15 / 74.53 / 63.54 | 3–5 giờ |

Số bài báo của Spider là cột SC (16 mẫu) theo thứ tự SFT + RL / SFT / base; cột CSC có trong bảng so sánh.

Model gốc (base): `Qwen/Qwen2.5-Coder-0.5B-Instruct`, `Qwen/Qwen3-0.6B`, `unsloth/Llama-3.2-1B-Instruct` (bản sao không cần xin quyền của `meta-llama/…`), `deepseek-ai/deepseek-coder-1.3b-instruct`, `Qwen/Qwen2.5-Coder-1.5B-Instruct`. SFT = `cycloneboy/SLM-SQL-Base-*`, SFT + RL = `cycloneboy/SLM-SQL-*` (theo model card của tác giả).

Thời gian là ước tính. Chỉ 0.5B BIRD vòng 1 đã đo thật: khoảng 20 s/câu mỗi GPU cho 64 mẫu, tức khoảng 4,5 giờ. Kaggle cho khoảng 30 giờ GPU/tuần, mỗi phiên tối đa 12 giờ. Toàn bộ vào khoảng 70–90 giờ, tức 3 tuần quota. Nên chạy Spider trước (nhanh); 1.3B BIRD tốn nhất, có thể để cuối hoặc bỏ.

Hạn chế đã biết:

- **SLM-SQL-1B (Llama, SFT + RL) chưa được tác giả công bố**, nên BIRD dùng bản SFT `SLM-SQL-Base-1B` (dự kiến thấp hơn 54.78), còn Spider bỏ dòng SFT + RL.
- **Trọng số w=2** cho mẫu vòng 2 được chọn trên 1.5B BIRD sau khi xem kết quả (ước lượng kiểm định chéo: 67.95). Với các model khác, w=2 được **giữ cố định từ trước**, nên không bị chọn theo kết quả của chính model đó. Bảng vẫn in thêm w=1.
- **Pool cũ `results/bird-dev-slm13` (1.3B, 16 mẫu) không dùng được**: được sinh trước khi sửa lỗi KV-cache của `vllm_collect`, 30% mẫu không có SQL, vote chỉ 39.4. Notebook 1.3B sinh lại từ đầu.
- Qwen3-0.6B gốc mặc định *thinking*; với 1024 token mới, một phần mẫu có thể bị cắt trước khi ra SQL.
- Bài báo không công bố đáp án từng câu, nên chênh lệch với bài báo không kiểm định thống kê được. Phép so ghép cặp chỉ làm được giữa các phương pháp trên cùng pool của project.

## 2. Đóng gói và upload dataset (một lần)

Trên máy local, từ thư mục project:

```powershell
.\.venv\Scripts\python.exe scripts/pack_kaggle.py --dataset data/benchmarks/spider_dev.json --output dist/slmsql-spider-dev.zip
.\.venv\Scripts\python.exe scripts/pack_kaggle.py --dataset data/benchmarks/bird_dev.json --output dist/slmsql-bird-dev.zip
```

Kết quả: `dist/slmsql-spider-dev.zip` (khoảng 30 MB) và `dist/slmsql-bird-dev.zip` (khoảng 330 MB). Mỗi zip chứa code, file câu hỏi và database của tập đó.

Trên Kaggle → *Datasets* → *New Dataset* (hoặc *New Version* nếu đã có):

1. Upload `slmsql-spider-dev.zip`, đặt tên **`slmsql-spider-dev`**, để **Private** (Spider/BIRD không phân phối lại công khai).
2. Upload `slmsql-bird-dev.zip`, đặt tên **`slmsql-bird-dev`**, **Private**.

Notebook chỉ dùng code đã có trong dataset (`vllm_collect --keep-schema`, `schema_keep`), nên dataset đã upload trước đó vẫn chạy được. Đóng gói lại khi cập nhật code.

## 3. Chạy một notebook

1. Kaggle → *Code* → *New Notebook* → *File* → *Import Notebook* → chọn file `.ipynb` trong `notebooks/paper/`. Đặt tên notebook trùng tên file để dễ nhận.
2. *Settings*: **Accelerator = GPU T4 x2**, **Internet = On**.
3. *Add Input* → *Datasets* → *Your Datasets* → dataset ghi trong bảng (`slmsql-bird-dev` cho notebook `bird-dev_…`, `slmsql-spider-dev` cho `spider-dev_…`). Gắn nhầm thì cell chép code báo rõ đang có dataset nào.
4. **Chạy thử**: ở cell *Cấu hình* đặt `LIMIT = 20`, *Run All*. Kiểm tra log có cả hai dòng `vòng 1` và `vòng 2`, dòng `questions pruned` của `schema_keep`, và cell *EX tạm tính* có số.
5. **Chạy thật**: đặt lại `LIMIT = None`, bấm **Save Version → Save & Run All (Commit)**. Có thể tắt trình duyệt; theo dõi ở *Versions* → *Logs*.

Cell cấu hình:

```python
ROUND2_SEED = 300000
JOBS = [  # (results/<RUN>, model Hugging Face, số mẫu vòng 1, seed offset, số mẫu vòng 2 với schema rút gọn)
    ("spider-dev-0.5b-rl", "cycloneboy/SLM-SQL-0.5B", 16, 0, 8),
    ...
]
LIMIT = None  # 20 để chạy thử nhanh
```

Với mỗi model, notebook chạy vòng 1, tính schema rút gọn, rồi chạy vòng 2 (`results/<RUN>-prune<N>/`, có kèm `keep.json`). Mỗi vòng chia câu hỏi cho 2 GPU (`shard0/`, `shard1/`).

### Chạy tiếp khi hết 12 giờ (hoặc khi vòng 1 đã có)

Mỗi version là một máy mới. Để chạy tiếp:

1. Mở notebook → *Edit* → *Add Input* → *Notebooks* → chọn notebook có output trước đó.
2. *Save Version → Save & Run All* lại. Cell sinh mẫu tìm `results/<RUN>/shard*/pool.jsonl` (và `results/<RUN>-prune<N>/shard*/pool.jsonl`) trong input, chép sang và chỉ sinh các câu còn thiếu.

**BIRD 0.5B**: vòng 1 đã chạy xong bằng notebook cũ `bird-dev_SLM-SQL-0.5B_64mau`. Import notebook mới `…_64mau_2vong`, *Add Input* thêm output của notebook cũ trên Kaggle, rồi *Save & Run All*: vòng 1 được bỏ qua ngay (không nạp model), chỉ còn vòng 2. Nếu output cũ trên Kaggle không còn, notebook sẽ sinh lại vòng 1 (thêm khoảng 4,5 giờ).

## 4. Lấy kết quả về và so sánh

1. Trang notebook → version đã xong → tab **Output** → tải `<tên notebook>.zip`.
2. Giải nén **vào thư mục project**, sao cho có `results/<RUN>/shard0/pool.jsonl` và `results/<RUN>-prune<N>/shard0/pool.jsonl`. Không để lồng `results/<tên zip>/results/…`.

```powershell
Expand-Archive "$env:USERPROFILE\Downloads\bird-dev_SLM-SQL-0.5B_64mau_2vong.zip" -DestinationPath . -Force
```

3. Lập bảng so sánh với bài báo (không cần GPU, chạy được khi mới có một phần kết quả):

```powershell
.\.venv\Scripts\python.exe -m evaluation.paper_compare --write-pool --method
```

Lệnh ghi `results/paper-compare/tables.md` gồm hai bảng:

- **Tái lập**: Vote@16, Vote@64, Oracle, độ chính xác trung bình 1 mẫu, so với số của bài báo.
- **Phương pháp mới**: Vote@K, CAV-3@K, hai vòng + vote, hai vòng + CAV-3 (w=1, **w=2**), số của bài báo và Δ so với cột CSC (cấu hình đầy đủ của bài báo). Model chưa có vòng 2 hiện "chưa có vòng 2".

Lần đầu `--method` chạy lại mỗi SQL một lần để tính cờ CAV (vài phút mỗi run BIRD), sau đó dùng cache trong `results/paper-compare/flags/`. `--write-pool` ghép các shard thành `pool.jsonl` cho các lệnh phân tích khác.

4. (Tùy chọn) Phân tích chi tiết (khoảng tin cậy, mất/cứu, p) cho một model:

```powershell
.\.venv\Scripts\python.exe -m evaluation.selection_study results/bird-dev-0.5b-rl --metric set --output results/selection-bird-dev-0.5b-rl
.\.venv\Scripts\python.exe -m evaluation.ensemble_study results/bird-dev-0.5b-rl results/bird-dev-0.5b-rl-prune32 --flags results/selection-bird-dev-0.5b-rl/candidate_flags.json --tune data/benchmarks/bird_dev200.json --extra 32 --output results/ensemble-bird-dev-0.5b-rl
```

Spider dùng `--metric spider`, `--extra 8` và bỏ `--tune`.
