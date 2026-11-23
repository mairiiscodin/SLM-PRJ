## BIRD dev (bài báo Bảng 2: 64 mẫu + CSC; metric set)

| Model | Train | Run | Số câu | Mẫu/câu | Vote@16 | Vote@64 | Oracle | TB 1 mẫu | Bài báo (64 + CSC) | Δ Vote − bài báo |
|---|---|---|---|---|---|---|---|---|---|---|
| cycloneboy/SLM-SQL-0.5B | SFT + RL | bird-dev-0.5b-rl | 1534/1534 | 64 | 48.89 | 49.41 | 74.51 | 34.90 | 56.87 | -7.46 |
| cycloneboy/SLM-SQL-1.5B | SFT + RL | bird-dev-vllm-64 | 1534/1534 | 64 | 61.67 | 61.54 | 82.79 | 51.36 | 67.08 | -5.54 |

## Spider dev (bài báo Bảng 3, Dev EX: 16 mẫu; metric spider)

| Model | Train | Run | Số câu | Mẫu/câu | Vote@16 | Vote@64 | Oracle | TB 1 mẫu | Bài báo SC | Bài báo CSC | Δ Vote − bài báo |
|---|---|---|---|---|---|---|---|---|---|---|---|

Ghi chú:
- Vote@K: bỏ phiếu (self-consistency) trên K mẫu đầu của mỗi câu; ứng với cột SC của bài báo.
- BIRD: bài báo chỉ công bố cấu hình đầy đủ 64 mẫu + CSC (merge revision), nên Vote@64 thường thấp hơn vài điểm; CAV-3 tính bằng `evaluation.selection_study`.
- Δ: BIRD so Vote@64 (hoặc @16 nếu pool chỉ có 16) với 64 + CSC; Spider so Vote@16 với SC.
- Số câu < tổng: run chưa xong (LIMIT hoặc hết 12 giờ Kaggle), chưa so được.

# Phương pháp mới so với bài báo (cùng số mẫu sinh)

## BIRD dev, 64 mẫu/câu (bài báo: 64 mẫu + CSC)

| Model | Train | Số câu | Vote@64 | CAV-3@64 | 2 vòng 32+32 + vote | 2 vòng + CAV-3 (w=1) | **2 vòng + CAV-3 (w=2)** | Bài báo (64 + CSC) | Δ phương pháp mới − bài báo |
|---|---|---|---|---|---|---|---|---|---|
| cycloneboy/SLM-SQL-0.5B | SFT + RL | 1534/1534 | 49.22 | 58.28 | 52.61 | 59.91 | 59.78 | 56.87 | +2.91 |
| cycloneboy/SLM-SQL-1.5B | SFT + RL | 1534/1534 | 61.34 | 66.95 | 61.99 | 67.86 | 68.19 | 67.08 | +1.11 |

## Spider dev, 16 mẫu/câu (bài báo: 16 mẫu SC, + CSC)

| Model | Train | Số câu | Vote@16 | CAV-3@16 | 2 vòng 8+8 + vote | 2 vòng + CAV-3 (w=1) | **2 vòng + CAV-3 (w=2)** | Bài báo SC | Bài báo CSC | Δ phương pháp mới − bài báo |
|---|---|---|---|---|---|---|---|---|---|---|

Ghi chú:
- 2 vòng: K/2 mẫu đầu với schema đầy đủ + K/2 mẫu sinh lại với schema rút gọn theo các SQL của vòng 1 (không nhìn đáp án). Tổng số mẫu sinh bằng bài báo, không dùng model merge.
- w = trọng số phiếu của mẫu vòng 2. w=2 được chọn trên SLM-SQL-1.5B BIRD (chọn sau khi xem kết quả, ước lượng kiểm định chéo 67.95) rồi giữ cố định cho mọi model khác.
- Δ so với cột CSC của bài báo (cấu hình đầy đủ của bài báo). Bài báo không công bố đáp án từng câu nên không kiểm định thống kê được phép so này.
- CAV-3 ở đây phá hoà theo `ensemble_study` nên có thể lệch ±0.15 so với `selection_study`.
