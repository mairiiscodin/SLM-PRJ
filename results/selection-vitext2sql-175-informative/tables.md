## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Easy | Medium | Hard | Extra |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 65.3 [59.6–71.7] | — | — | 4.00 | 50.3 | — | 85.4 | 62.1 | 48.8 | 52.8 |
| fixed K=4 | **CAV-3** | 67.0 [60.8–72.8] | +1.7 [+0.8, +2.8] | 0/6 (0.031) | 4.00 | 50.3 | 17% | 85.6 | 64.3 | 52.3 | 53.4 |
| fixed K=4 | **CAV-2 (grounding + join)** | 65.9 [59.6–72.0] | +0.6 [+0.1, +1.3] | 0/4 (0.125) | 4.00 | 50.3 | 6% | 85.6 | 63.3 | 48.7 | 53.3 |
| fixed K=4 | **Learned re-ranker (CV)** | 67.2 [60.7–73.0] | +1.9 [+0.6, +3.2] | 2/10 (0.039) | 4.00 | 50.3 | 18% | 85.7 | 64.9 | 51.3 | 54.0 |
| fixed K=8 | Vote (baseline) | 67.3 [60.7–73.8] | — | — | 8.00 | 99.2 | — | 85.7 | 65.5 | 47.2 | 59.1 |
| fixed K=8 | **CAV-3** | 69.9 [63.2–76.1] | +2.6 [+1.2, +4.3] | 0/4 (0.125) | 8.00 | 99.2 | 20% | 85.7 | 68.4 | 55.0 | 59.1 |
| fixed K=8 | **CAV-2 (grounding + join)** | 68.3 [61.8–74.5] | +1.0 [+0.3, +1.9] | 0/2 (0.500) | 8.00 | 99.2 | 7% | 85.7 | 66.9 | 49.2 | 59.1 |
| fixed K=8 | **Learned re-ranker (CV)** | 69.8 [63.3–76.1] | +2.4 [+0.9, +4.2] | 1/5 (0.219) | 8.00 | 99.2 | 19% | 85.8 | 68.8 | 52.5 | 59.6 |
| fixed K=16 | Vote (baseline) | 68.6 [61.7–75.4] | — | — | 16.00 | 198.4 | — | 85.7 | 68.8 | 43.3 | 63.2 |
| fixed K=16 | **CAV-3** | 72.0 [65.1–78.3] | +3.4 [+1.1, +6.3] | 0/6 (0.031) | 16.00 | 198.4 | 23% | 85.7 | 71.4 | 56.7 | 63.2 |
| fixed K=16 | **CAV-2 (grounding + join)** | 69.7 [62.3–76.0] | +1.1 [+0.0, +2.9] | 0/2 (0.500) | 16.00 | 198.4 | 8% | 85.7 | 70.1 | 46.7 | 63.2 |
| fixed K=16 | **Learned re-ranker (CV)** | 71.4 [64.6–77.7] | +2.9 [+0.6, +5.7] | 0/5 (0.062) | 16.00 | 198.4 | 19% | 85.7 | 71.4 | 53.3 | 63.2 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 67.5 [60.7–73.7] | — | — | 5.34 | 70.4 | — | 86.6 | 65.7 | 45.8 | 60.4 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 70.0 [63.6–76.2] | +2.5 [+1.1, +4.2] | 0/5 (0.062) | 5.34 | 70.4 | 24% | 86.7 | 68.4 | 52.9 | 60.5 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 68.5 [62.1–74.9] | +1.0 [+0.2, +2.1] | 0/2 (0.500) | 5.34 | 70.4 | 10% | 86.7 | 67.3 | 47.1 | 60.4 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 70.1 [63.8–76.1] | +2.6 [+1.2, +4.3] | 0/6 (0.031) | 5.34 | 70.4 | 25% | 86.6 | 68.5 | 53.4 | 60.5 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 68.2 [61.6–74.6] | — | — | 7.28 | 98.3 | — | 85.8 | 67.9 | 44.2 | 62.2 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 70.8 [63.9–77.2] | +2.5 [+0.7, +4.7] | 0/5 (0.062) | 7.28 | 98.3 | 22% | 85.8 | 70.4 | 52.6 | 62.2 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 69.1 [62.5–75.6] | +0.8 [+0.0, +2.1] | 0/2 (0.500) | 7.28 | 98.3 | 7% | 85.8 | 69.3 | 45.5 | 62.2 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 71.1 [64.7–77.6] | +2.8 [+0.8, +5.3] | 0/6 (0.031) | 7.28 | 98.3 | 25% | 85.8 | 70.3 | 54.6 | 62.2 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|
| CAV (3 checks) | +1.7 | +2.6 | +3.4 | +2.5 | +2.5 |
| CAV only degenerate | +1.3 | +1.8 | +2.3 | +1.6 | +1.7 |
| CAV without degenerate | +0.6 | +1.0 | +1.1 | +1.0 | +0.8 |
| CAV only ungrounded | +0.3 | +0.3 | +0.0 | +0.2 | +0.0 |
| CAV without ungrounded | +1.5 | +2.5 | +3.4 | +2.3 | +2.5 |
| CAV only bad_join | +0.4 | +0.9 | +1.1 | +0.8 | +0.8 |
| CAV without bad_join | +1.5 | +2.0 | +2.3 | +1.7 | +1.7 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 5.8% | 15.9% | 0.0% | 100.0% |
| Literal không có trong DB | 2.0% | 5.3% | 0.0% | 100.0% |
| JOIN không theo khóa ngoại | 2.8% | 6.9% | 0.4% | 91.5% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 2.3% | 3.8% | 1.5% | 60.0% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 67.5 | 5.34 | 70.4 | 91.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 70.0 | 5.34 | 70.4 | 91.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 70.3 | 5.50 | 73.7 | 90.2 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 68.2 | 7.28 | 98.3 | 74.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 70.8 | 7.28 | 98.3 | 74.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 70.8 | 7.09 | 96.0 | 76.0 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | +1.9 | +1.5 |
| fixed K=4 | CAV-2 (grounding + join) | +0.6 | +0.6 |
| fixed K=4 | Learned re-ranker (CV) | +2.3 | +1.4 |
| fixed K=8 | CAV-3 | +2.2 | +3.0 |
| fixed K=8 | CAV-2 (grounding + join) | +0.4 | +1.6 |
| fixed K=8 | Learned re-ranker (CV) | +1.9 | +3.0 |
| fixed K=16 | CAV-3 | +2.3 | +4.5 |
| fixed K=16 | CAV-2 (grounding + join) | +0.0 | +2.3 |
| fixed K=16 | Learned re-ranker (CV) | +2.3 | +3.4 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | +1.9 | +3.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | +0.3 | +1.7 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | +2.3 | +2.9 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | +1.7 | +3.3 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | +0.0 | +1.6 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | +2.6 | +3.0 |

Dữ liệu: 175 câu, pool 16 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 0.50 ms/ứng viên.