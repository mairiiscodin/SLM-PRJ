## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Simple | Moderate | Challenging |
|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 57.1 [50.5–63.6] | — | — | 4.00 | 97.4 | — | 66.4 | 44.7 | 36.7 |
| fixed K=4 | **CAV-3** | 61.2 [55.1–67.2] | +4.1 [+2.4, +6.4] | 0/10 (0.002) | 4.00 | 97.4 | 48% | 68.2 | 53.7 | 40.0 |
| fixed K=4 | **CAV-2 (grounding + join)** | 59.5 [53.4–65.8] | +2.5 [+1.0, +4.3] | 0/7 (0.016) | 4.00 | 97.4 | 28% | 67.2 | 51.1 | 37.2 |
| fixed K=4 | **Learned re-ranker (CV)** | 61.3 [55.1–67.3] | +4.3 [+2.4, +6.6] | 1/12 (0.003) | 4.00 | 97.4 | 49% | 68.2 | 53.9 | 40.9 |
| fixed K=4 | **Judge top-2** | 57.1 [50.7–63.2] | +0.1 [-0.3, +0.5] | 2/2 (1.000) | 4.00 | 97.4 | 1% | 66.5 | 44.4 | 37.8 |
| fixed K=4 | **CAV-2 + judge** | 59.5 [53.3–65.6] | +2.5 [-0.0, +5.0] | 4/9 (0.267) | 4.00 | 97.4 | 29% | 66.4 | 51.3 | 42.0 |
| fixed K=4 | **CAV-3 + judge** | 61.1 [55.1–67.5] | +4.1 [+1.3, +7.0] | 4/11 (0.118) | 4.00 | 97.4 | 47% | 67.2 | 54.3 | 44.0 |
| fixed K=8 | Vote (baseline) | 58.7 [52.2–64.7] | — | — | 6.14 | 150.7 | — | 67.2 | 47.3 | 40.2 |
| fixed K=8 | **CAV-3** | 64.2 [57.9–70.1] | +5.6 [+3.0, +8.2] | 0/14 (<0.001) | 6.14 | 150.7 | 50% | 70.9 | 57.9 | 41.6 |
| fixed K=8 | **CAV-2 (grounding + join)** | 61.5 [55.0–68.2] | +2.9 [+1.0, +5.1] | 0/9 (0.004) | 6.14 | 150.7 | 26% | 68.4 | 55.1 | 37.9 |
| fixed K=8 | **Learned re-ranker (CV)** | 64.2 [57.9–70.2] | +5.5 [+3.0, +8.2] | 1/14 (<0.001) | 6.14 | 150.7 | 49% | 70.6 | 58.0 | 42.3 |
| fixed K=8 | **Judge top-2** | 59.5 [52.9–65.8] | +0.8 [-0.5, +2.4] | 3/7 (0.344) | 6.14 | 150.7 | 8% | 68.6 | 46.3 | 42.8 |
| fixed K=8 | **CAV-2 + judge** | 62.1 [55.8–68.5] | +3.4 [+0.5, +6.4] | 4/14 (0.031) | 6.14 | 150.7 | 31% | 68.0 | 55.0 | 46.5 |
| fixed K=8 | **CAV-3 + judge** | 64.5 [58.2–70.9] | +5.9 [+2.5, +9.3] | 4/18 (0.004) | 6.14 | 150.7 | 52% | 70.0 | 58.9 | 47.4 |
| fixed K=16 | Vote (baseline) | 59.5 [53.0–66.0] | — | — | 9.22 | 228.9 | — | 66.1 | 51.7 | 42.1 |
| fixed K=16 | **CAV-3** | 65.0 [58.0–71.5] | +5.5 [+2.5, +8.5] | 0/11 (<0.001) | 9.22 | 228.9 | 44% | 70.2 | 61.7 | 42.1 |
| fixed K=16 | **CAV-2 (grounding + join)** | 61.5 [55.0–68.0] | +2.0 [-0.5, +4.5] | 1/5 (0.219) | 9.22 | 228.9 | 16% | 66.9 | 58.3 | 36.8 |
| fixed K=16 | **Learned re-ranker (CV)** | 64.8 [58.0–71.0] | +5.3 [+2.0, +9.0] | 1/12 (0.003) | 9.22 | 228.9 | 43% | 71.1 | 59.5 | 42.1 |
| fixed K=16 | **Judge top-2** | 60.3 [53.3–67.1] | +0.8 [-1.5, +3.5] | 3/4 (1.000) | 9.22 | 228.9 | 6% | 68.6 | 47.7 | 47.4 |
| fixed K=16 | **CAV-2 + judge** | 62.4 [55.5–69.2] | +2.9 [-0.5, +6.4] | 3/9 (0.146) | 9.22 | 228.9 | 23% | 67.8 | 56.2 | 47.4 |
| fixed K=16 | **CAV-3 + judge** | 65.0 [58.5–71.5] | +5.5 [+1.5, +9.5] | 3/14 (0.013) | 9.22 | 228.9 | 44% | 70.2 | 60.0 | 47.4 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 58.8 [51.9–65.3] | — | — | 5.98 | 137.1 | — | 66.7 | 49.3 | 39.0 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 63.2 [56.6–69.5] | +4.4 [+2.4, +6.7] | 0/8 (0.008) | 5.98 | 137.1 | 48% | 69.3 | 58.2 | 40.2 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 61.0 [54.3–67.4] | +2.2 [+0.6, +4.1] | 1/4 (0.375) | 5.98 | 137.1 | 24% | 67.5 | 55.5 | 37.2 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 62.9 [56.3–69.2] | +4.0 [+1.9, +6.6] | 0/8 (0.008) | 5.98 | 137.1 | 44% | 69.4 | 56.8 | 40.5 |
| adaptive 4-4-8 τ=0.5 m=2 | **Judge top-2** | 58.6 [51.9–65.3] | -0.2 [-1.1, +0.5] | 2/1 (1.000) | 5.98 | 137.1 | -2% | 67.3 | 47.2 | 39.3 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 + judge** | 60.9 [54.5–67.1] | +2.0 [-0.4, +4.6] | 3/6 (0.508) | 5.98 | 137.1 | 22% | 67.1 | 54.1 | 42.8 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3 + judge** | 62.8 [56.1–69.0] | +4.0 [+1.1, +6.8] | 3/10 (0.092) | 5.98 | 137.1 | 44% | 68.5 | 57.3 | 44.1 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 59.4 [52.5–66.1] | — | — | 7.37 | 178.8 | — | 66.3 | 51.1 | 41.1 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 63.8 [57.5–70.4] | +4.4 [+2.2, +7.2] | 0/10 (0.002) | 7.37 | 178.8 | 45% | 69.3 | 59.9 | 41.2 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 61.4 [54.3–68.3] | +2.0 [+0.3, +4.2] | 1/5 (0.219) | 7.37 | 178.8 | 21% | 67.1 | 57.3 | 38.2 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 63.5 [57.1–69.8] | +4.1 [+1.5, +7.2] | 1/11 (0.006) | 7.37 | 178.8 | 42% | 69.9 | 57.8 | 41.2 |
| adaptive 4-4-8 τ=0.75 m=2 | **Judge top-2** | 59.3 [52.7–65.8] | -0.0 [-1.6, +1.4] | 3/4 (1.000) | 7.37 | 178.8 | -0% | 67.7 | 48.2 | 41.6 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 + judge** | 61.4 [54.5–68.0] | +2.1 [-0.9, +4.9] | 3/9 (0.146) | 7.37 | 178.8 | 21% | 67.3 | 55.2 | 43.7 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3 + judge** | 63.4 [56.8–69.8] | +4.0 [+1.0, +7.3] | 3/13 (0.021) | 7.37 | 178.8 | 40% | 68.9 | 58.3 | 43.9 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|
| CAV (3 checks) | +4.1 | +5.6 | +5.5 | +4.4 | +4.4 |
| CAV only degenerate | +2.8 | +3.9 | +4.0 | +3.1 | +3.0 |
| CAV without degenerate | +2.5 | +2.9 | +2.0 | +2.2 | +2.0 |
| CAV only ungrounded | +1.0 | +1.0 | +0.5 | +1.1 | +0.8 |
| CAV without ungrounded | +3.2 | +4.5 | +4.5 | +3.3 | +3.4 |
| CAV only bad_join | +1.0 | +0.9 | +0.5 | +0.7 | +0.7 |
| CAV without bad_join | +3.2 | +4.4 | +4.5 | +3.6 | +3.5 |
| CAV-2 + judge | +2.5 | +3.4 | +2.9 | +2.0 | +2.1 |
| CAV + judge | +4.1 | +5.9 | +5.5 | +4.0 | +4.0 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 11.2% | 21.3% | 0.2% | 99.4% |
| Literal không có trong DB | 6.0% | 11.5% | 0.0% | 100.0% |
| JOIN không theo khóa ngoại | 9.7% | 15.3% | 3.6% | 82.4% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 16.5% | 16.4% | 16.7% | 51.9% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 58.8 | 5.98 | 137.1 | 85.5 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 63.2 | 5.98 | 137.1 | 85.5 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 63.6 | 6.11 | 140.3 | 81.6 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 59.4 | 7.37 | 178.8 | 73.8 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 63.8 | 7.37 | 178.8 | 73.8 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 63.8 | 7.02 | 168.3 | 73.8 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | +3.7 | +4.5 |
| fixed K=4 | CAV-2 (grounding + join) | +2.4 | +2.6 |
| fixed K=4 | Learned re-ranker (CV) | +3.7 | +4.8 |
| fixed K=4 | Judge top-2 | -0.2 | +0.4 |
| fixed K=4 | CAV-2 + judge | +1.5 | +3.5 |
| fixed K=4 | CAV-3 + judge | +2.8 | +5.4 |
| fixed K=8 | CAV-3 | +5.4 | +5.7 |
| fixed K=8 | CAV-2 (grounding + join) | +2.9 | +2.8 |
| fixed K=8 | Learned re-ranker (CV) | +5.1 | +5.9 |
| fixed K=8 | Judge top-2 | +0.5 | +1.2 |
| fixed K=8 | CAV-2 + judge | +2.2 | +4.6 |
| fixed K=8 | CAV-3 + judge | +4.7 | +7.0 |
| fixed K=16 | CAV-3 | +6.0 | +5.0 |
| fixed K=16 | CAV-2 (grounding + join) | +2.0 | +2.0 |
| fixed K=16 | Learned re-ranker (CV) | +4.7 | +6.0 |
| fixed K=16 | Judge top-2 | -0.4 | +2.0 |
| fixed K=16 | CAV-2 + judge | +0.7 | +5.0 |
| fixed K=16 | CAV-3 + judge | +4.0 | +7.0 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | +3.9 | +4.8 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | +1.9 | +2.5 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | +3.1 | +5.0 |
| adaptive 4-4-8 τ=0.5 m=2 | Judge top-2 | -0.7 | +0.3 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 + judge | +0.5 | +3.6 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 + judge | +2.4 | +5.6 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | +4.6 | +4.3 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | +2.0 | +2.1 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | +3.3 | +5.0 |
| adaptive 4-4-8 τ=0.75 m=2 | Judge top-2 | -0.5 | +0.5 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 + judge | +0.4 | +3.7 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 + judge | +2.6 | +5.3 |

Dữ liệu: 200 câu, pool 16 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 1.72 ms/ứng viên.