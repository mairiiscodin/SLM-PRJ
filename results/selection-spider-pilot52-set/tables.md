## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Easy | Medium | Hard | Extra |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 67.1 [53.5–78.8] | — | — | 4.00 | 58.1 | — | 79.0 | 76.8 | 59.6 | 42.2 |
| fixed K=4 | **CAV-3** | 65.7 [52.4–78.3] | -1.4 [-5.0, +1.3] | 1/0 (1.000) | 4.00 | 58.1 | -25% | 79.1 | 73.2 | 63.7 | 38.3 |
| fixed K=4 | **CAV-2 (grounding + join)** | 67.5 [54.5–79.4] | +0.4 [-0.3, +1.5] | 0/0 (1.000) | 4.00 | 58.1 | 7% | 79.0 | 76.8 | 62.5 | 41.6 |
| fixed K=4 | **Learned re-ranker (CV)** | 66.5 [53.9–78.4] | -0.7 [-1.9, +0.5] | 0/2 (0.500) | 4.00 | 58.1 | -12% | 79.1 | 75.6 | 60.5 | 40.2 |
| fixed K=8 | Vote (baseline) | 68.3 [55.6–80.0] | — | — | 8.00 | 116.3 | — | 78.6 | 77.5 | 64.6 | 43.2 |
| fixed K=8 | **CAV-3** | 65.4 [52.3–78.1] | -2.9 [-7.3, +0.2] | 2/0 (0.500) | 8.00 | 116.3 | -44% | 78.6 | 72.2 | 65.2 | 37.7 |
| fixed K=8 | **CAV-2 (grounding + join)** | 68.1 [55.1–80.6] | -0.2 [-0.9, +0.2] | 0/0 (1.000) | 8.00 | 116.3 | -3% | 78.6 | 77.5 | 65.0 | 41.9 |
| fixed K=8 | **Learned re-ranker (CV)** | 67.1 [54.7–78.8] | -1.2 [-2.9, -0.1] | 1/1 (1.000) | 8.00 | 116.3 | -18% | 78.8 | 76.9 | 63.8 | 39.1 |
| fixed K=16 | Vote (baseline) | 69.2 [55.8–82.7] | — | — | 16.00 | 232.6 | — | 78.6 | 77.8 | 66.7 | 45.5 |
| fixed K=16 | **CAV-3** | 65.4 [51.9–78.8] | -3.8 [-9.6, +0.0] | 2/0 (0.500) | 16.00 | 232.6 | -50% | 78.6 | 72.2 | 66.7 | 36.4 |
| fixed K=16 | **CAV-2 (grounding + join)** | 69.2 [55.8–80.8] | +0.0 [+0.0, +0.0] | 0/0 (1.000) | 16.00 | 232.6 | 0% | 78.6 | 77.8 | 66.7 | 45.5 |
| fixed K=16 | **Learned re-ranker (CV)** | 67.3 [53.8–78.8] | -1.9 [-5.8, +0.0] | 1/0 (1.000) | 16.00 | 232.6 | -25% | 78.6 | 77.8 | 66.7 | 36.4 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 68.1 [56.0–80.2] | — | — | 4.61 | 67.3 | — | 78.7 | 77.5 | 63.2 | 43.4 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 65.5 [52.3–77.1] | -2.6 [-7.1, +0.3] | 1/0 (1.000) | 4.61 | 67.3 | -54% | 78.8 | 73.2 | 64.2 | 37.2 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 68.1 [55.3–80.1] | -0.1 [-0.3, +0.1] | 0/0 (1.000) | 4.61 | 67.3 | -2% | 78.7 | 77.5 | 63.3 | 42.9 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 67.7 [55.1–80.2] | -0.4 [-1.6, +0.4] | 0/1 (1.000) | 4.61 | 67.3 | -9% | 78.7 | 77.5 | 63.9 | 40.9 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 68.9 [57.1–80.7] | — | — | 6.04 | 89.3 | — | 78.6 | 77.5 | 66.2 | 44.5 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 65.8 [52.5–78.8] | -3.1 [-7.9, +0.1] | 1/0 (1.000) | 6.04 | 89.3 | -72% | 78.6 | 73.2 | 66.4 | 36.8 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 68.9 [55.5–80.5] | +0.0 [+0.0, +0.1] | 0/0 (1.000) | 6.04 | 89.3 | 0% | 78.6 | 77.5 | 66.3 | 44.5 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 67.6 [54.2–79.3] | -1.3 [-3.8, +0.0] | 1/1 (1.000) | 6.04 | 89.3 | -29% | 78.6 | 77.5 | 66.1 | 38.7 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|
| CAV (3 checks) | -1.4 | -2.9 | -3.8 | -2.6 | -3.1 |
| CAV only degenerate | -1.4 | -2.9 | -3.8 | -2.6 | -3.1 |
| CAV without degenerate | +0.4 | -0.2 | +0.0 | -0.1 | +0.0 |
| CAV only ungrounded | +0.5 | +0.1 | +0.0 | +0.0 | +0.0 |
| CAV without ungrounded | -1.4 | -2.9 | -3.8 | -2.6 | -3.1 |
| CAV only bad_join | -0.1 | -0.3 | +0.0 | -0.1 | +0.0 |
| CAV without bad_join | -1.4 | -2.9 | -3.8 | -2.6 | -3.1 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 6.4% | 5.9% | 6.6% | 31.4% |
| Literal không có trong DB | 4.4% | 1.9% | 5.6% | 14.3% |
| JOIN không theo khóa ngoại | 3.5% | 10.0% | 0.2% | 96.4% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 6.7% | 0.7% | 9.8% | 3.7% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 68.1 | 4.61 | 67.3 | 96.7 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 65.5 | 4.61 | 67.3 | 96.7 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 65.5 | 4.80 | 70.4 | 95.3 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 68.9 | 6.04 | 89.3 | 84.5 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 65.8 | 6.04 | 89.3 | 84.5 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 65.8 | 5.98 | 88.8 | 85.5 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | -3.8 | +1.0 |
| fixed K=4 | CAV-2 (grounding + join) | -0.2 | +1.0 |
| fixed K=4 | Learned re-ranker (CV) | -1.3 | +0.0 |
| fixed K=8 | CAV-3 | -5.9 | +0.1 |
| fixed K=8 | CAV-2 (grounding + join) | -0.6 | +0.1 |
| fixed K=8 | Learned re-ranker (CV) | -2.3 | +0.0 |
| fixed K=16 | CAV-3 | -7.7 | +0.0 |
| fixed K=16 | CAV-2 (grounding + join) | +0.0 | +0.0 |
| fixed K=16 | Learned re-ranker (CV) | -3.8 | +0.0 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | -5.3 | +0.0 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | -0.2 | +0.0 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | -0.8 | +0.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | -6.2 | +0.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | +0.0 | +0.0 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | -2.5 | +0.0 |

Dữ liệu: 52 câu, pool 16 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 1.29 ms/ứng viên.