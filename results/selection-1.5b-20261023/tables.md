## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Easy | Medium | Hard |
|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 51.2 [43.2–59.7] | — | — | 4.00 | 57.1 | — | 86.5 | 58.1 | 17.3 |
| fixed K=4 | **CAV-3** | 54.0 [46.2–61.8] | +2.8 [+0.4, +5.2] | 0/4 (0.125) | 4.00 | 57.1 | 16% | 88.7 | 64.1 | 17.0 |
| fixed K=4 | **CAV-2 (grounding + join)** | 53.8 [45.8–62.2] | +2.6 [+1.1, +4.4] | 0/3 (0.250) | 4.00 | 57.1 | 15% | 88.7 | 62.0 | 18.8 |
| fixed K=4 | **Learned re-ranker (CV)** | 55.8 [48.0–63.8] | +4.6 [+1.5, +7.7] | 3/8 (0.227) | 4.00 | 57.1 | 26% | 85.4 | 66.9 | 21.5 |
| fixed K=8 | Vote (baseline) | 54.2 [45.5–62.8] | — | — | 8.00 | 114.2 | — | 87.9 | 63.1 | 19.2 |
| fixed K=8 | **CAV-3** | 57.0 [48.4–65.4] | +2.8 [-1.0, +6.7] | 0/6 (0.031) | 8.00 | 114.2 | 11% | 92.4 | 69.7 | 16.6 |
| fixed K=8 | **CAV-2 (grounding + join)** | 57.6 [49.2–66.1] | +3.4 [+1.2, +6.0] | 0/4 (0.125) | 8.00 | 114.2 | 13% | 92.4 | 67.2 | 20.9 |
| fixed K=8 | **Learned re-ranker (CV)** | 58.8 [50.4–67.0] | +4.6 [+1.0, +8.3] | 1/12 (0.003) | 8.00 | 114.2 | 18% | 89.6 | 71.2 | 22.1 |
| fixed K=16 | Vote (baseline) | 55.0 [46.0–64.0] | — | — | 16.00 | 228.4 | — | 88.5 | 64.1 | 20.0 |
| fixed K=16 | **CAV-3** | 56.0 [46.0–66.0] | +1.0 [-3.0, +6.0] | 2/3 (1.000) | 16.00 | 228.4 | 3% | 92.3 | 69.2 | 14.3 |
| fixed K=16 | **CAV-2 (grounding + join)** | 57.0 [47.0–66.0] | +2.0 [+0.0, +5.0] | 0/2 (0.500) | 16.00 | 228.4 | 6% | 92.3 | 66.7 | 20.0 |
| fixed K=16 | **Learned re-ranker (CV)** | 58.0 [48.0–67.0] | +3.0 [-2.0, +9.0] | 2/5 (0.453) | 16.00 | 228.4 | 9% | 88.5 | 74.4 | 17.1 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 54.2 [45.1–62.7] | — | — | 6.51 | 96.4 | — | 86.9 | 64.2 | 18.6 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 56.5 [47.3–65.1] | +2.3 [-0.5, +5.4] | 0/5 (0.062) | 6.51 | 96.4 | 10% | 89.8 | 69.5 | 17.2 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 56.6 [47.7–65.5] | +2.4 [+0.7, +4.8] | 0/4 (0.125) | 6.51 | 96.4 | 11% | 89.8 | 67.8 | 19.5 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 56.9 [48.3–65.7] | +2.8 [-0.1, +5.9] | 0/7 (0.016) | 6.51 | 96.4 | 12% | 88.9 | 71.4 | 17.1 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 54.7 [44.8–64.0] | — | — | 9.27 | 138.1 | — | 88.5 | 64.1 | 19.3 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 56.4 [47.2–66.1] | +1.7 [-1.3, +5.0] | 0/3 (0.250) | 9.27 | 138.1 | 6% | 91.1 | 69.2 | 16.4 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 56.7 [47.3–66.2] | +1.9 [+0.1, +4.5] | 0/2 (0.500) | 9.27 | 138.1 | 7% | 91.1 | 67.2 | 19.4 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 57.2 [48.8–66.4] | +2.4 [-0.9, +6.4] | 0/5 (0.062) | 9.27 | 138.1 | 9% | 88.8 | 72.2 | 16.9 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|
| CAV (3 checks) | +2.8 | +2.8 | +1.0 | +2.3 | +1.7 |
| CAV only degenerate | +1.4 | +0.9 | +0.0 | +0.9 | +0.6 |
| CAV without degenerate | +2.6 | +3.4 | +2.0 | +2.4 | +1.9 |
| CAV only ungrounded | +1.3 | +1.6 | +1.0 | +1.1 | +0.9 |
| CAV without ungrounded | +2.6 | +2.7 | +1.0 | +2.2 | +1.5 |
| CAV only bad_join | +1.2 | +1.7 | +1.0 | +1.3 | +1.0 |
| CAV without bad_join | +1.6 | +1.1 | +0.0 | +1.1 | +0.7 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 9.6% | 16.4% | 2.9% | 84.8% |
| Literal không có trong DB | 3.3% | 6.7% | 0.0% | 100.0% |
| JOIN không theo khóa ngoại | 5.9% | 11.8% | 0.1% | 98.8% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 3.3% | 6.7% | 0.0% | 100.0% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 54.2 | 6.51 | 96.4 | 81.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 56.5 | 6.51 | 96.4 | 81.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 56.0 | 6.96 | 103.4 | 78.3 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 54.7 | 9.27 | 138.1 | 57.3 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 56.4 | 9.27 | 138.1 | 57.3 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 56.2 | 9.16 | 136.3 | 59.0 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | +2.1 | +3.5 |
| fixed K=4 | CAV-2 (grounding + join) | +2.2 | +3.0 |
| fixed K=4 | Learned re-ranker (CV) | +3.0 | +6.2 |
| fixed K=8 | CAV-3 | +1.9 | +3.8 |
| fixed K=8 | CAV-2 (grounding + join) | +3.0 | +3.8 |
| fixed K=8 | Learned re-ranker (CV) | +3.3 | +5.9 |
| fixed K=16 | CAV-3 | +0.0 | +2.0 |
| fixed K=16 | CAV-2 (grounding + join) | +2.0 | +2.0 |
| fixed K=16 | Learned re-ranker (CV) | +0.0 | +6.0 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | +1.9 | +2.8 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | +2.3 | +2.5 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | +2.2 | +3.4 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | +1.3 | +2.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | +2.0 | +1.8 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | +1.4 | +3.5 |

Dữ liệu: 100 câu, pool 16 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 0.67 ms/ứng viên.