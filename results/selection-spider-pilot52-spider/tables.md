## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Easy | Medium | Hard | Extra |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 66.7 [54.4–77.8] | — | — | 4.00 | 58.1 | — | 66.8 | 81.7 | 66.4 | 42.2 |
| fixed K=4 | **CAV-3** | 65.3 [52.9–77.0] | -1.4 [-5.0, +1.2] | 1/0 (1.000) | 4.00 | 58.1 | -14% | 66.8 | 78.1 | 70.2 | 38.3 |
| fixed K=4 | **CAV-2 (grounding + join)** | 67.1 [54.5–78.3] | +0.4 [-0.3, +1.5] | 0/0 (1.000) | 4.00 | 58.1 | 4% | 66.8 | 81.7 | 69.3 | 41.6 |
| fixed K=4 | **Learned re-ranker (CV)** | 65.8 [53.9–76.9] | -0.9 [-2.3, +0.5] | 0/1 (1.000) | 4.00 | 58.1 | -9% | 67.6 | 79.8 | 66.9 | 39.5 |
| fixed K=8 | Vote (baseline) | 68.4 [55.7–79.9] | — | — | 8.00 | 116.3 | — | 65.6 | 83.3 | 74.0 | 43.2 |
| fixed K=8 | **CAV-3** | 65.5 [53.7–77.3] | -2.9 [-7.3, +0.2] | 2/0 (0.500) | 8.00 | 116.3 | -24% | 65.6 | 78.0 | 74.5 | 37.7 |
| fixed K=8 | **CAV-2 (grounding + join)** | 68.2 [55.3–80.5] | -0.2 [-0.9, +0.2] | 0/0 (1.000) | 8.00 | 116.3 | -2% | 65.6 | 83.3 | 74.4 | 41.9 |
| fixed K=8 | **Learned re-ranker (CV)** | 67.3 [54.9–78.4] | -1.2 [-2.9, -0.0] | 1/0 (1.000) | 8.00 | 116.3 | -10% | 65.8 | 82.3 | 74.1 | 38.9 |
| fixed K=16 | Vote (baseline) | 69.2 [55.8–80.8] | — | — | 16.00 | 232.6 | — | 64.3 | 83.3 | 77.8 | 45.5 |
| fixed K=16 | **CAV-3** | 65.4 [51.9–78.8] | -3.8 [-9.6, +0.0] | 2/0 (0.500) | 16.00 | 232.6 | -29% | 64.3 | 77.8 | 77.8 | 36.4 |
| fixed K=16 | **CAV-2 (grounding + join)** | 69.2 [55.8–80.8] | +0.0 [+0.0, +0.0] | 0/0 (1.000) | 16.00 | 232.6 | 0% | 64.3 | 83.3 | 77.8 | 45.5 |
| fixed K=16 | **Learned re-ranker (CV)** | 67.3 [53.8–78.8] | -1.9 [-5.8, +0.0] | 1/0 (1.000) | 16.00 | 232.6 | -14% | 64.3 | 83.3 | 77.8 | 36.4 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 68.1 [56.1–79.7] | — | — | 4.61 | 67.3 | — | 66.1 | 83.3 | 70.9 | 43.4 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 65.4 [52.9–77.3] | -2.7 [-7.1, +0.2] | 1/0 (1.000) | 4.61 | 67.3 | -30% | 66.1 | 79.0 | 71.6 | 37.2 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 68.0 [55.9–79.6] | -0.1 [-0.3, +0.1] | 0/0 (1.000) | 4.61 | 67.3 | -1% | 66.1 | 83.3 | 71.0 | 42.9 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 67.4 [54.6–78.8] | -0.7 [-2.0, +0.0] | 0/0 (1.000) | 4.61 | 67.3 | -7% | 66.1 | 83.3 | 70.9 | 40.3 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 68.8 [56.9–80.6] | — | — | 6.04 | 89.3 | — | 64.5 | 83.1 | 76.4 | 44.5 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 65.7 [52.5–77.3] | -3.1 [-7.9, +0.1] | 1/0 (1.000) | 6.04 | 89.3 | -34% | 64.5 | 78.8 | 76.6 | 36.8 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 68.8 [55.5–80.1] | +0.0 [+0.0, +0.1] | 0/0 (1.000) | 6.04 | 89.3 | 0% | 64.5 | 83.1 | 76.5 | 44.5 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 67.4 [54.2–79.0] | -1.4 [-4.1, +0.0] | 1/0 (1.000) | 6.04 | 89.3 | -15% | 64.5 | 83.1 | 76.4 | 38.1 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|
| CAV (3 checks) | -1.4 | -2.9 | -3.8 | -2.7 | -3.1 |
| CAV only degenerate | -1.4 | -2.9 | -3.8 | -2.7 | -3.1 |
| CAV without degenerate | +0.4 | -0.2 | +0.0 | -0.1 | +0.0 |
| CAV only ungrounded | +0.5 | +0.1 | +0.0 | +0.0 | +0.0 |
| CAV without ungrounded | -1.4 | -2.9 | -3.8 | -2.7 | -3.1 |
| CAV only bad_join | -0.1 | -0.3 | +0.0 | -0.1 | +0.0 |
| CAV without bad_join | -1.4 | -2.9 | -3.8 | -2.7 | -3.1 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 6.4% | 5.8% | 6.7% | 31.4% |
| Literal không có trong DB | 4.4% | 1.8% | 5.7% | 14.3% |
| JOIN không theo khóa ngoại | 3.5% | 9.8% | 0.2% | 96.4% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 6.7% | 12.7% | 3.6% | 64.8% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 68.1 | 4.61 | 67.3 | 96.7 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 65.4 | 4.61 | 67.3 | 96.7 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 65.5 | 4.80 | 70.4 | 95.3 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 68.8 | 6.04 | 89.3 | 84.5 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 65.7 | 6.04 | 89.3 | 84.5 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 65.7 | 5.98 | 88.8 | 85.5 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | -3.8 | +1.0 |
| fixed K=4 | CAV-2 (grounding + join) | -0.2 | +1.0 |
| fixed K=4 | Learned re-ranker (CV) | -1.4 | -0.4 |
| fixed K=8 | CAV-3 | -5.9 | +0.1 |
| fixed K=8 | CAV-2 (grounding + join) | -0.6 | +0.1 |
| fixed K=8 | Learned re-ranker (CV) | -2.0 | -0.3 |
| fixed K=16 | CAV-3 | -7.7 | +0.0 |
| fixed K=16 | CAV-2 (grounding + join) | +0.0 | +0.0 |
| fixed K=16 | Learned re-ranker (CV) | -3.8 | +0.0 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | -5.4 | +0.0 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | -0.2 | +0.0 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | -1.3 | +0.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | -6.2 | +0.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | +0.0 | +0.0 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | -2.7 | +0.0 |

Dữ liệu: 52 câu, pool 16 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 0.87 ms/ứng viên.