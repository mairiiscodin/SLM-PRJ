## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Easy | Medium | Hard | Extra |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 68.8 [56.3–80.0] | — | — | 4.00 | 57.4 | — | 80.7 | 79.3 | 59.1 | 41.4 |
| fixed K=4 | **CAV-3** | 67.5 [55.3–79.3] | -1.2 [-4.4, +1.3] | 1/0 (1.000) | 4.00 | 57.4 | -23% | 80.7 | 75.9 | 63.1 | 38.0 |
| fixed K=4 | **CAV-2 (grounding + join)** | 69.1 [56.4–80.6] | +0.4 [-0.2, +1.3] | 0/0 (1.000) | 4.00 | 57.4 | 7% | 80.7 | 79.3 | 61.8 | 41.1 |
| fixed K=4 | **Learned re-ranker (CV)** | 67.7 [55.5–79.0] | -1.1 [-2.4, -0.1] | 0/2 (0.500) | 4.00 | 57.4 | -21% | 79.7 | 78.6 | 57.8 | 39.5 |
| fixed K=8 | Vote (baseline) | 70.0 [57.7–81.3] | — | — | 8.00 | 114.9 | — | 80.0 | 79.9 | 64.6 | 42.8 |
| fixed K=8 | **CAV-3** | 67.3 [54.8–79.7] | -2.7 [-6.9, +0.1] | 2/0 (0.500) | 8.00 | 114.9 | -42% | 80.0 | 75.0 | 65.1 | 37.6 |
| fixed K=8 | **CAV-2 (grounding + join)** | 69.9 [57.8–81.3] | -0.1 [-0.4, +0.0] | 0/0 (1.000) | 8.00 | 114.9 | -2% | 80.0 | 79.9 | 64.7 | 42.1 |
| fixed K=8 | **Learned re-ranker (CV)** | 68.2 [56.6–79.4] | -1.8 [-3.8, -0.3] | 1/1 (1.000) | 8.00 | 114.9 | -28% | 80.0 | 79.4 | 59.2 | 39.1 |
| fixed K=16 | Vote (baseline) | 70.9 [58.2–81.8] | — | — | 16.00 | 229.8 | — | 80.0 | 80.0 | 66.7 | 45.5 |
| fixed K=16 | **CAV-3** | 67.3 [54.5–80.0] | -3.6 [-9.1, +0.0] | 2/0 (0.500) | 16.00 | 229.8 | -50% | 80.0 | 75.0 | 66.7 | 36.4 |
| fixed K=16 | **CAV-2 (grounding + join)** | 70.9 [58.2–81.8] | +0.0 [+0.0, +0.0] | 0/0 (1.000) | 16.00 | 229.8 | 0% | 80.0 | 80.0 | 66.7 | 45.5 |
| fixed K=16 | **Learned re-ranker (CV)** | 69.1 [56.4–80.0] | -1.8 [-5.5, +0.0] | 1/0 (1.000) | 16.00 | 229.8 | -25% | 80.0 | 80.0 | 66.7 | 36.4 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 69.8 [57.8–80.7] | — | — | 4.57 | 66.0 | — | 80.2 | 79.7 | 63.6 | 42.7 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 67.5 [54.9–78.7] | -2.3 [-6.2, +0.3] | 1/0 (1.000) | 4.57 | 66.0 | -48% | 80.2 | 75.9 | 64.6 | 37.5 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 69.8 [57.5–81.2] | -0.0 [-0.2, +0.1] | 0/0 (1.000) | 4.57 | 66.0 | -1% | 80.2 | 79.7 | 63.8 | 42.4 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 69.0 [57.3–80.5] | -0.9 [-2.1, +0.1] | 0/1 (1.000) | 4.57 | 66.0 | -18% | 80.2 | 79.7 | 61.5 | 40.1 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 70.4 [58.0–81.8] | — | — | 5.82 | 85.2 | — | 80.0 | 79.7 | 65.9 | 43.9 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 67.7 [55.2–79.9] | -2.7 [-6.8, +0.1] | 1/0 (1.000) | 5.82 | 85.2 | -61% | 80.0 | 75.9 | 66.2 | 37.3 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 70.4 [57.8–81.5] | +0.0 [+0.0, +0.1] | 0/0 (1.000) | 5.82 | 85.2 | 1% | 80.0 | 79.7 | 66.2 | 43.9 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 69.3 [56.7–80.6] | -1.1 [-3.2, +0.0] | 1/1 (1.000) | 5.82 | 85.2 | -24% | 80.0 | 79.7 | 65.7 | 38.8 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|
| CAV (3 checks) | -1.2 | -2.7 | -3.6 | -2.3 | -2.7 |
| CAV only degenerate | -1.2 | -2.7 | -3.6 | -2.3 | -2.7 |
| CAV without degenerate | +0.4 | -0.1 | +0.0 | -0.0 | +0.0 |
| CAV only ungrounded | +0.4 | +0.0 | +0.0 | +0.0 | +0.0 |
| CAV without ungrounded | -1.2 | -2.7 | -3.6 | -2.3 | -2.7 |
| CAV only bad_join | -0.1 | -0.1 | +0.0 | -0.1 | +0.0 |
| CAV without bad_join | -1.2 | -2.7 | -3.6 | -2.3 | -2.7 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 6.0% | 5.9% | 6.0% | 31.4% |
| Literal không có trong DB | 4.1% | 1.9% | 5.2% | 14.3% |
| JOIN không theo khóa ngoại | 3.3% | 10.0% | 0.2% | 96.4% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 6.4% | 0.7% | 9.0% | 3.7% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 69.8 | 4.57 | 66.0 | 96.9 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 67.5 | 4.57 | 66.0 | 96.9 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 67.5 | 4.77 | 69.2 | 95.5 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 70.4 | 5.82 | 85.2 | 86.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 67.7 | 5.82 | 85.2 | 86.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 67.7 | 5.81 | 85.5 | 86.6 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | -3.4 | +0.9 |
| fixed K=4 | CAV-2 (grounding + join) | -0.1 | +0.9 |
| fixed K=4 | Learned re-ranker (CV) | -2.3 | +0.1 |
| fixed K=8 | CAV-3 | -5.6 | +0.0 |
| fixed K=8 | CAV-2 (grounding + join) | -0.3 | +0.0 |
| fixed K=8 | Learned re-ranker (CV) | -2.8 | -0.9 |
| fixed K=16 | CAV-3 | -7.4 | +0.0 |
| fixed K=16 | CAV-2 (grounding + join) | +0.0 | +0.0 |
| fixed K=16 | Learned re-ranker (CV) | -3.7 | +0.0 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | -4.7 | +0.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | -0.1 | +0.1 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | -1.3 | -0.4 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | -5.5 | +0.1 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | +0.0 | +0.1 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | -2.2 | +0.0 |

Dữ liệu: 55 câu, pool 16 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 0.51 ms/ứng viên.