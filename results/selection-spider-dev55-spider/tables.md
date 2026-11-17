## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Easy | Medium | Hard | Extra |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 68.5 [56.9–79.1] | — | — | 4.00 | 57.4 | — | 69.3 | 83.7 | 66.4 | 41.4 |
| fixed K=4 | **CAV-3** | 67.2 [55.3–78.7] | -1.3 [-4.5, +1.1] | 1/0 (1.000) | 4.00 | 57.4 | -15% | 69.3 | 80.4 | 69.9 | 38.0 |
| fixed K=4 | **CAV-2 (grounding + join)** | 68.9 [57.0–79.8] | +0.4 [-0.2, +1.3] | 0/0 (1.000) | 4.00 | 57.4 | 4% | 69.3 | 83.7 | 69.1 | 41.1 |
| fixed K=4 | **Learned re-ranker (CV)** | 67.4 [56.1–78.7] | -1.0 [-2.1, -0.0] | 0/1 (1.000) | 4.00 | 57.4 | -11% | 68.8 | 82.3 | 66.5 | 39.3 |
| fixed K=8 | Vote (baseline) | 70.1 [57.9–80.7] | — | — | 8.00 | 114.9 | — | 67.7 | 84.9 | 74.3 | 42.8 |
| fixed K=8 | **CAV-3** | 67.3 [55.1–78.9] | -2.7 [-7.0, +0.1] | 2/0 (0.500) | 8.00 | 114.9 | -24% | 67.7 | 80.1 | 74.6 | 37.6 |
| fixed K=8 | **CAV-2 (grounding + join)** | 69.9 [58.1–81.2] | -0.1 [-0.4, +0.0] | 0/0 (1.000) | 8.00 | 114.9 | -1% | 67.7 | 84.9 | 74.4 | 42.1 |
| fixed K=8 | **Learned re-ranker (CV)** | 68.6 [57.0–79.7] | -1.4 [-3.3, -0.1] | 1/1 (1.000) | 8.00 | 114.9 | -12% | 68.6 | 84.0 | 71.0 | 38.8 |
| fixed K=16 | Vote (baseline) | 70.9 [58.2–81.8] | — | — | 16.00 | 229.8 | — | 66.7 | 85.0 | 77.8 | 45.5 |
| fixed K=16 | **CAV-3** | 67.3 [56.4–80.0] | -3.6 [-9.1, +0.0] | 2/0 (0.500) | 16.00 | 229.8 | -29% | 66.7 | 80.0 | 77.8 | 36.4 |
| fixed K=16 | **CAV-2 (grounding + join)** | 70.9 [60.0–81.8] | +0.0 [+0.0, +0.0] | 0/0 (1.000) | 16.00 | 229.8 | 0% | 66.7 | 85.0 | 77.8 | 45.5 |
| fixed K=16 | **Learned re-ranker (CV)** | 69.1 [56.4–80.0] | -1.8 [-5.5, +0.0] | 1/0 (1.000) | 16.00 | 229.8 | -14% | 66.7 | 85.0 | 77.8 | 36.4 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 69.9 [58.6–80.6] | — | — | 4.57 | 66.0 | — | 68.4 | 85.1 | 71.9 | 42.7 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 67.6 [55.2–79.0] | -2.3 [-6.2, +0.2] | 1/0 (1.000) | 4.57 | 66.0 | -28% | 68.4 | 81.3 | 72.6 | 37.5 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 69.9 [57.9–81.3] | -0.0 [-0.2, +0.1] | 0/0 (1.000) | 4.57 | 66.0 | -0% | 68.4 | 85.1 | 72.1 | 42.4 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 69.2 [57.2–80.1] | -0.8 [-2.0, +0.0] | 0/0 (1.000) | 4.57 | 66.0 | -9% | 68.4 | 85.1 | 70.7 | 39.9 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 70.3 [58.3–81.7] | — | — | 5.82 | 85.2 | — | 66.8 | 84.9 | 76.3 | 43.9 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 67.7 [55.2–79.4] | -2.7 [-6.8, +0.1] | 1/0 (1.000) | 5.82 | 85.2 | -31% | 66.8 | 81.0 | 76.6 | 37.3 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 70.4 [57.9–81.2] | +0.0 [+0.0, +0.1] | 0/0 (1.000) | 5.82 | 85.2 | 0% | 66.8 | 84.9 | 76.5 | 43.9 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 69.3 [56.5–80.3] | -1.0 [-3.1, +0.0] | 1/0 (1.000) | 5.82 | 85.2 | -12% | 66.8 | 84.9 | 76.3 | 38.8 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|
| CAV (3 checks) | -1.3 | -2.7 | -3.6 | -2.3 | -2.7 |
| CAV only degenerate | -1.3 | -2.7 | -3.6 | -2.3 | -2.7 |
| CAV without degenerate | +0.4 | -0.1 | +0.0 | -0.0 | +0.0 |
| CAV only ungrounded | +0.4 | +0.0 | +0.0 | +0.0 | +0.0 |
| CAV without ungrounded | -1.3 | -2.7 | -3.6 | -2.3 | -2.7 |
| CAV only bad_join | -0.1 | -0.1 | +0.0 | -0.1 | +0.0 |
| CAV without bad_join | -1.3 | -2.7 | -3.6 | -2.3 | -2.7 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 6.0% | 5.8% | 6.1% | 31.4% |
| Literal không có trong DB | 4.1% | 1.8% | 5.2% | 14.3% |
| JOIN không theo khóa ngoại | 3.3% | 9.8% | 0.2% | 96.4% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 6.4% | 12.7% | 3.3% | 64.8% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 69.9 | 4.57 | 66.0 | 96.9 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 67.6 | 4.57 | 66.0 | 96.9 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 67.6 | 4.77 | 69.2 | 95.5 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 70.3 | 5.82 | 85.2 | 86.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 67.7 | 5.82 | 85.2 | 86.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 67.6 | 5.81 | 85.5 | 86.6 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | -3.6 | +0.9 |
| fixed K=4 | CAV-2 (grounding + join) | -0.1 | +0.9 |
| fixed K=4 | Learned re-ranker (CV) | -1.7 | -0.4 |
| fixed K=8 | CAV-3 | -5.6 | +0.0 |
| fixed K=8 | CAV-2 (grounding + join) | -0.3 | +0.0 |
| fixed K=8 | Learned re-ranker (CV) | -1.7 | -1.2 |
| fixed K=16 | CAV-3 | -7.4 | +0.0 |
| fixed K=16 | CAV-2 (grounding + join) | +0.0 | +0.0 |
| fixed K=16 | Learned re-ranker (CV) | -3.7 | +0.0 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | -4.8 | +0.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | -0.1 | +0.1 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | -1.1 | -0.4 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | -5.5 | +0.1 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | +0.0 | +0.1 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | -2.1 | +0.0 |

Dữ liệu: 55 câu, pool 16 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 0.51 ms/ứng viên.