## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Easy | Medium | Hard | Extra |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 67.3 [61.7–72.8] | — | — | 4.00 | 49.8 | — | 85.4 | 64.3 | 50.7 | 59.6 |
| fixed K=4 | **CAV-3** | 67.7 [62.3–73.2] | +0.4 [-1.0, +1.8] | 1/6 (0.125) | 4.00 | 49.8 | 4% | 85.5 | 65.0 | 53.9 | 55.9 |
| fixed K=4 | **CAV-2 (grounding + join)** | 67.4 [61.5–73.3] | +0.1 [-0.8, +0.9] | 0/4 (0.125) | 4.00 | 49.8 | 1% | 85.5 | 64.8 | 50.5 | 58.4 |
| fixed K=4 | **Learned re-ranker (CV)** | 68.5 [62.6–74.0] | +1.2 [+0.2, +2.3] | 2/11 (0.022) | 4.00 | 49.8 | 11% | 86.6 | 66.3 | 51.1 | 58.2 |
| fixed K=8 | Vote (baseline) | 69.3 [63.4–75.0] | — | — | 8.00 | 97.7 | — | 85.9 | 67.3 | 48.8 | 66.0 |
| fixed K=8 | **CAV-3** | 69.9 [64.2–75.6] | +0.6 [-1.5, +2.8] | 2/4 (0.688) | 8.00 | 97.7 | 5% | 86.0 | 67.9 | 56.0 | 59.1 |
| fixed K=8 | **CAV-2 (grounding + join)** | 69.4 [63.6–75.2] | +0.1 [-1.4, +1.3] | 1/2 (1.000) | 8.00 | 97.7 | 1% | 86.0 | 67.7 | 50.6 | 62.6 |
| fixed K=8 | **Learned re-ranker (CV)** | 70.7 [64.7–76.4] | +1.3 [+0.2, +2.6] | 1/2 (1.000) | 8.00 | 97.7 | 11% | 87.1 | 69.3 | 50.9 | 64.4 |
| fixed K=16 | Vote (baseline) | 70.5 [64.0–77.0] | — | — | 16.00 | 195.4 | — | 85.2 | 70.7 | 45.2 | 69.6 |
| fixed K=16 | **CAV-3** | 71.5 [65.0–77.5] | +1.0 [-2.0, +4.0] | 4/6 (0.754) | 16.00 | 195.4 | 7% | 85.2 | 70.7 | 58.1 | 60.9 |
| fixed K=16 | **CAV-2 (grounding + join)** | 70.5 [64.0–76.5] | +0.0 [-2.0, +2.0] | 2/2 (1.000) | 16.00 | 195.4 | 0% | 85.2 | 70.7 | 48.4 | 65.2 |
| fixed K=16 | **Learned re-ranker (CV)** | 72.0 [65.5–78.0] | +1.5 [-0.5, +4.0] | 1/4 (0.375) | 16.00 | 195.4 | 11% | 87.0 | 70.7 | 51.6 | 69.6 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 69.6 [63.4–75.6] | — | — | 5.33 | 72.8 | — | 86.7 | 67.8 | 47.4 | 66.7 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 70.6 [64.7–76.4] | +1.0 [-0.8, +2.9] | 1/5 (0.219) | 5.33 | 72.8 | 10% | 86.8 | 68.8 | 54.4 | 61.7 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 70.0 [64.1–75.7] | +0.4 [-0.8, +1.5] | 0/2 (0.500) | 5.33 | 72.8 | 4% | 86.8 | 68.6 | 48.6 | 64.7 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 70.5 [64.7–76.5] | +0.9 [-0.5, +2.3] | 1/6 (0.125) | 5.33 | 72.8 | 9% | 87.8 | 68.3 | 50.7 | 65.5 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 70.3 [64.3–76.2] | — | — | 7.17 | 98.8 | — | 85.8 | 70.0 | 45.8 | 68.5 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 71.4 [65.4–77.0] | +1.0 [-1.3, +3.2] | 1/5 (0.219) | 7.17 | 98.8 | 9% | 85.8 | 70.7 | 54.3 | 62.9 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 70.5 [63.8–76.3] | +0.1 [-1.1, +1.5] | 0/2 (0.500) | 7.17 | 98.8 | 1% | 85.8 | 70.4 | 47.0 | 66.2 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 71.4 [65.1–77.4] | +1.1 [-0.6, +3.0] | 1/4 (0.375) | 7.17 | 98.8 | 10% | 87.2 | 70.0 | 50.5 | 68.5 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|
| CAV (3 checks) | +0.4 | +0.6 | +1.0 | +1.0 | +1.0 |
| CAV only degenerate | +0.3 | +0.2 | +0.5 | +0.5 | +0.6 |
| CAV without degenerate | +0.1 | +0.1 | +0.0 | +0.4 | +0.1 |
| CAV only ungrounded | -0.1 | -0.6 | -1.0 | -0.4 | -0.6 |
| CAV without ungrounded | +0.5 | +0.9 | +1.5 | +1.1 | +1.2 |
| CAV only bad_join | +0.3 | +0.8 | +1.0 | +0.7 | +0.7 |
| CAV without bad_join | +0.3 | +0.0 | +0.0 | +0.4 | +0.3 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 12.2% | 19.2% | 8.6% | 54.0% |
| Literal không có trong DB | 11.4% | 7.8% | 13.2% | 23.7% |
| JOIN không theo khóa ngoại | 3.3% | 7.3% | 1.2% | 76.3% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 2.2% | 4.0% | 1.2% | 62.5% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 69.6 | 5.33 | 72.8 | 91.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 70.6 | 5.33 | 72.8 | 91.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 70.8 | 5.60 | 77.2 | 89.4 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 70.3 | 7.17 | 98.8 | 74.9 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 71.4 | 7.17 | 98.8 | 74.9 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 71.2 | 7.08 | 97.5 | 76.1 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | -0.1 | +1.0 |
| fixed K=4 | CAV-2 (grounding + join) | +0.2 | +0.0 |
| fixed K=4 | Learned re-ranker (CV) | +1.7 | +0.6 |
| fixed K=8 | CAV-3 | -0.3 | +1.5 |
| fixed K=8 | CAV-2 (grounding + join) | +0.3 | -0.2 |
| fixed K=8 | Learned re-ranker (CV) | +1.6 | +1.1 |
| fixed K=16 | CAV-3 | -1.0 | +3.0 |
| fixed K=16 | CAV-2 (grounding + join) | +0.0 | +0.0 |
| fixed K=16 | Learned re-ranker (CV) | +1.0 | +2.0 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | -0.1 | +2.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | +0.3 | +0.4 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | +0.2 | +1.6 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | -0.7 | +2.7 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | -0.2 | +0.4 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | +0.3 | +1.9 |

Dữ liệu: 200 câu, pool 16 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 0.52 ms/ứng viên.