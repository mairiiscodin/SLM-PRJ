# Chạy trên Kaggle để so sánh với bài báo SLM-SQL

Mục tiêu: đo lại hai bảng của bài báo bằng cùng thiết lập (prompt Appendix E.1, temperature 0.8, top-p 1.0, `max_new_tokens` 1024, vLLM):

- **Bảng 2, BIRD dev**: 5 model SLM-SQL (cấu hình đầy đủ của bài báo: 64 mẫu + CSC).
- **Bảng 3, Spider dev, cột SC**: mỗi model gốc ở 3 giai đoạn (base, SFT, SFT + RL), 16 mẫu/câu.

## 1. Danh sách notebook

Các notebook nằm trong [notebooks/paper/](../notebooks/paper/), sinh bằng `python scripts/make_paper_notebooks.py`. Tên file theo dạng `<tập>_<model>_<số mẫu hoặc giai đoạn>`; file zip kết quả trùng tên notebook.

| Notebook | Kaggle dataset | Model chạy | Thư mục kết quả | Bài báo | Thời gian (T4 x2) |
|---|---|---|---|---|---|
| `bird-dev_SLM-SQL-0.5B_64mau` | `slmsql-bird-dev` | `cycloneboy/SLM-SQL-0.5B` | `results/bird-dev-0.5b-rl` | 56.87 | 3–5 giờ |
| `bird-dev_SLM-SQL-0.6B_64mau` | `slmsql-bird-dev` | `cycloneboy/SLM-SQL-0.6B` | `results/bird-dev-0.6b-rl` | 59.52 | 4–6 giờ |
| `bird-dev_SLM-SQL-Base-1B_64mau` | `slmsql-bird-dev` | `cycloneboy/SLM-SQL-Base-1B` (SFT) | `results/bird-dev-1b-sft` | 54.78 (SFT + RL) | 4–6 giờ |
| `bird-dev_SLM-SQL-1.3B_64mau` | `slmsql-bird-dev` | `cycloneboy/SLM-SQL-1.3B` | `results/bird-dev-1.3b-rl` | 62.19 | 16–24 giờ (2–3 version) |
| (đã có) | | `cycloneboy/SLM-SQL-1.5B` | `results/bird-dev-vllm-64` | 67.08 | |
| `spider-dev_0.5B-Qwen2.5-Coder-0.5B-Instruct_base-sft-rl` | `slmsql-spider-dev` | RL, SFT, base | `results/spider-dev-0.5b-{rl,sft,base}` | 70.60 / 65.31 / 42.13 | 1–2 giờ |
| `spider-dev_0.6B-Qwen3-0.6B_base-sft-rl` | `slmsql-spider-dev` | RL, SFT, base | `results/spider-dev-0.6b-{rl,sft,base}` | 72.05 / 68.02 / 63.19 | 2–3 giờ |
| `spider-dev_1B-Llama-3.2-1B-Instruct_base-sft-rl` | `slmsql-spider-dev` | SFT, base | `results/spider-dev-1b-{sft,base}` | – / 63.77 / 30.79 | 1–2 giờ |
| `spider-dev_1.3B-deepseek-coder-1.3b-instruct_base-sft-rl` | `slmsql-spider-dev` | RL, SFT, base | `results/spider-dev-1.3b-{rl,sft,base}` | 75.47 / 72.86 / 48.23 | 4–6 giờ |
| `spider-dev_1.5B-Qwen2.5-Coder-1.5B-Instruct_base-sft-rl` | `slmsql-spider-dev` | RL, SFT, base | `results/spider-dev-1.5b-{rl,sft,base}` | 75.15 / 74.53 / 63.54 | 2–3 giờ |

Model gốc (base): `Qwen/Qwen2.5-Coder-0.5B-Instruct`, `Qwen/Qwen3-0.6B`, `unsloth/Llama-3.2-1B-Instruct` (bản sao không cần xin quyền của `meta-llama/…`), `deepseek-ai/deepseek-coder-1.3b-instruct`, `Qwen/Qwen2.5-Coder-1.5B-Instruct`. SFT = `cycloneboy/SLM-SQL-Base-*`, SFT + RL = `cycloneboy/SLM-SQL-*` (theo model card của tác giả).

Thời gian là ước tính từ các lần chạy trước (1.5B: khoảng 9 s/câu cho 16 mẫu trên 1 T4; 1.3B: khoảng 20 s/câu), chưa đo cho các model mới. Kaggle cho khoảng 30 giờ GPU/tuần, mỗi phiên tối đa 12 giờ. Tất cả notebook cộng lại khoảng 40–55 giờ, tức khoảng 2 tuần quota. Nên chạy Spider trước (nhanh, so trực tiếp được với cột SC).

Hạn chế đã biết:

- **SLM-SQL-1B (Llama, SFT + RL) chưa được tác giả công bố**, nên BIRD dùng bản SFT `SLM-SQL-Base-1B` (dự kiến thấp hơn 54.78), còn Spider bỏ dòng SFT + RL.
- **BIRD: bài báo chỉ công bố 64 mẫu + CSC.** Notebook chỉ sinh 64 mẫu, nên vote@64 sẽ thấp hơn vài điểm (với 1.5B: vote 61.54 so với 67.08). Muốn so đúng cấu hình phải thêm bước merge (mục 5).
- **Pool cũ `results/bird-dev-slm13` (1.3B, 16 mẫu) không dùng được**: sinh trước khi sửa lỗi KV-cache của `vllm_collect`, 30% mẫu không có SQL, vote chỉ 39.4. Notebook 1.3B sinh lại cả 64 mẫu.
- Qwen3-0.6B gốc mặc định *thinking*; với 1024 token mới, một phần mẫu có thể bị cắt trước khi ra SQL.

## 2. Đóng gói và upload dataset (một lần)

Trên máy local, từ thư mục project:

```powershell
.\.venv\Scripts\python.exe scripts/pack_kaggle.py --dataset data/benchmarks/spider_dev.json --output dist/slmsql-spider-dev.zip
.\.venv\Scripts\python.exe scripts/pack_kaggle.py --dataset data/benchmarks/bird_dev.json --output dist/slmsql-bird-dev.zip
```

Kết quả: `dist/slmsql-spider-dev.zip` (khoảng 30 MB) và `dist/slmsql-bird-dev.zip` (khoảng 330 MB). Mỗi zip chứa code, file câu hỏi và database của tập đó.

Trên Kaggle → *Datasets* → *New Dataset*:

1. Upload `slmsql-spider-dev.zip`, đặt tên **`slmsql-spider-dev`**, để **Private** (Spider/BIRD không phân phối lại công khai).
2. Upload `slmsql-bird-dev.zip`, đặt tên **`slmsql-bird-dev`**, **Private**.

Khi sửa code (ví dụ cập nhật repo), đóng gói lại và upload bằng *New Version* của dataset đó.

## 3. Chạy một notebook

1. Kaggle → *Code* → *New Notebook* → *File* → *Import Notebook* → chọn file `.ipynb` trong `notebooks/paper/`. Đặt tên notebook trùng tên file để dễ nhận.
2. *Settings*: **Accelerator = GPU T4 x2**, **Internet = On** (cần xác minh số điện thoại để bật Internet).
3. *Add Input* → *Datasets* → *Your Datasets* → dataset ghi trong bảng (`slmsql-bird-dev` hoặc `slmsql-spider-dev`).
4. **Chạy thử**: ở cell *Cấu hình* đặt `LIMIT = 20`, *Run All*. Kiểm tra cell *EX tạm tính* có số, log không báo lỗi, dòng `samples without SQL` thấp.
5. **Chạy thật**: đặt lại `LIMIT = None`, bấm **Save Version → Save & Run All (Commit)**. Có thể tắt trình duyệt; theo dõi ở trang notebook → *Versions* → *Logs*.

Cell cấu hình (sửa được nếu cần):

```python
JOBS = [  # (thư mục kết quả results/<RUN>, model Hugging Face, số mẫu/câu, seed offset)
    ("spider-dev-0.5b-rl", "cycloneboy/SLM-SQL-0.5B", 16, 0),
    ...
]
LIMIT = None  # 20 để chạy thử nhanh
```

Notebook Spider chạy các model lần lượt (RL trước, rồi SFT, rồi base). Mỗi model chia câu hỏi cho 2 GPU (`shard0/`, `shard1/`). Nếu chỉ có 1 GPU (P100) notebook vẫn chạy, chậm gấp đôi.

### Chạy tiếp khi hết 12 giờ

Mỗi version là một máy mới. Để chạy tiếp version bị dừng:

1. Mở notebook → *Edit* → *Add Input* → *Notebooks* → chọn **chính notebook này** (dùng output của version trước).
2. *Save Version → Save & Run All* lại. Cell sinh mẫu tìm `results/<RUN>/shard*/pool.jsonl` trong input, chép sang và chỉ sinh các câu còn thiếu. Với notebook Spider, model đã xong được bỏ qua nhanh.
3. Zip của version mới chứa đủ cả phần cũ lẫn phần mới.

## 4. Lấy kết quả về

1. Trang notebook → version đã xong → tab **Output** → tải `<tên notebook>.zip` (ví dụ `spider-dev_0.5B-Qwen2.5-Coder-0.5B-Instruct_base-sft-rl.zip`).
2. Giải nén **vào thư mục project**: zip đã chứa sẵn `results/<RUN>/…`, nên sau khi giải nén phải có, ví dụ, `results/spider-dev-0.5b-rl/shard0/pool.jsonl`. Không để lồng `results/results/` hay `results/<tên zip>/results/`.

```powershell
Expand-Archive "$env:USERPROFILE\Downloads\spider-dev_0.5B-Qwen2.5-Coder-0.5B-Instruct_base-sft-rl.zip" -DestinationPath . -Force
```

3. Lập bảng so sánh với bài báo (không cần GPU, chạy được khi mới có một phần kết quả):

```powershell
.\.venv\Scripts\python.exe -m evaluation.paper_compare --write-pool
```

Lệnh in và ghi `results/paper-compare/tables.md`: với mỗi run có Vote@16, Vote@64 (bỏ phiếu trên 16/64 mẫu đầu, ứng với cột SC), Oracle, độ chính xác trung bình 1 mẫu, số của bài báo và chênh lệch. Run chưa có kết quả hiện "chưa chạy". `--write-pool` ghép các shard thành `results/<RUN>/pool.jsonl` để dùng tiếp các lệnh dưới.

4. (Tùy chọn) Phân tích chi tiết từng run, ví dụ CAV-3 và theo độ khó:

```powershell
.\.venv\Scripts\python.exe -m evaluation.selection_study results/spider-dev-0.5b-rl --metric spider --output results/selection-spider-dev-0.5b-rl
.\.venv\Scripts\python.exe -m evaluation.selection_study results/bird-dev-0.5b-rl --metric set --output results/selection-bird-dev-0.5b-rl
```

BIRD dùng metric `set` (EX chính thức của BIRD), Spider dùng `spider`.

## 5. (Tùy chọn) CSC cho BIRD, như cấu hình đầy đủ của bài báo

Làm giống quy trình đã chạy cho 1.5B (README, mục *Merge revision bằng model của bài báo*), thay tên thư mục:

```powershell
.\.venv\Scripts\python.exe -m evaluation.selection_study results/bird-dev-0.5b-rl --metric set --output results/selection-bird-dev-0.5b-rl
.\.venv\Scripts\python.exe -m evaluation.vllm_merge prepare results/bird-dev-0.5b-rl --flags results/selection-bird-dev-0.5b-rl/candidate_flags.json --output data/benchmarks/bird_dev_0.5b_merge_pairs.jsonl
```

Sau đó đóng gói lại `slmsql-bird-dev` với `--extra data/benchmarks/bird_dev_0.5b_merge_pairs.jsonl`, chạy `notebooks/kaggle_vllm_merge.ipynb` với `PAIRS` và `RUN` tương ứng, rồi `evaluation.merge_study`. Bài báo không ghi rõ model merge dùng cho từng cỡ model; tác giả công bố bản 0.5B và 1.5B (`cycloneboy/CscSQL-Merge-Qwen2.5-Coder-{0.5B,1.5B}-Instruct`).
