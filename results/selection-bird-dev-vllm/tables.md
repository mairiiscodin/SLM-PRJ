## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Simple | Moderate | Challenging |
|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 58.3 [56.1–60.4] | — | — | 4.00 | 9.1 | — | 66.0 | 48.7 | 39.9 |
| fixed K=4 | **CAV-3** | 61.7 [59.5–63.9] | +3.4 [+2.9, +4.0] | 2/54 (<0.001) | 4.00 | 9.1 | 35% | 68.8 | 53.1 | 43.8 |
| fixed K=4 | **CAV-2 (grounding + join)** | 60.8 [58.5–63.0] | +2.6 [+2.1, +3.0] | 3/39 (<0.001) | 4.00 | 9.1 | 26% | 67.9 | 52.2 | 42.9 |
| fixed K=4 | **Learned re-ranker (CV)** | 61.5 [59.3–63.7] | +3.3 [+2.7, +3.8] | 4/58 (<0.001) | 4.00 | 9.1 | 34% | 68.6 | 53.0 | 43.8 |
| fixed K=8 | Vote (baseline) | 60.2 [58.0–62.5] | — | — | 8.00 | 9.1 | — | 67.5 | 51.4 | 42.5 |
| fixed K=8 | **CAV-3** | 64.4 [62.2–66.7] | +4.2 [+3.4, +5.0] | 3/73 (<0.001) | 8.00 | 9.1 | 33% | 71.0 | 56.7 | 46.9 |
| fixed K=8 | **CAV-2 (grounding + join)** | 63.2 [60.9–65.3] | +3.0 [+2.3, +3.7] | 3/57 (<0.001) | 8.00 | 9.1 | 24% | 69.8 | 55.6 | 45.5 |
| fixed K=8 | **Learned re-ranker (CV)** | 64.3 [62.2–66.6] | +4.1 [+3.3, +5.0] | 3/76 (<0.001) | 8.00 | 9.1 | 32% | 70.8 | 56.7 | 47.3 |
| fixed K=16 | Vote (baseline) | 61.7 [59.3–64.1] | — | — | 16.00 | 9.1 | — | 68.8 | 53.0 | 44.1 |
| fixed K=16 | **CAV-3** | 66.1 [63.7–68.6] | +4.4 [+3.3, +5.5] | 6/73 (<0.001) | 16.00 | 9.1 | 30% | 72.8 | 58.0 | 49.0 |
| fixed K=16 | **CAV-2 (grounding + join)** | 64.6 [62.2–67.0] | +2.9 [+1.9, +4.0] | 8/53 (<0.001) | 16.00 | 9.1 | 20% | 71.4 | 56.7 | 46.9 |
| fixed K=16 | **Learned re-ranker (CV)** | 66.2 [63.8–68.4] | +4.5 [+3.4, +5.6] | 2/71 (<0.001) | 16.00 | 9.1 | 30% | 72.6 | 58.4 | 49.7 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 60.5 [58.3–62.8] | — | — | 5.71 | 12.0 | — | 67.6 | 51.9 | 43.0 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 63.8 [61.5–65.9] | +3.2 [+2.6, +3.9] | 4/58 (<0.001) | 5.71 | 12.0 | 33% | 70.3 | 56.0 | 47.0 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 62.8 [60.6–65.0] | +2.3 [+1.8, +2.9] | 6/41 (<0.001) | 5.71 | 12.0 | 23% | 69.4 | 55.1 | 45.6 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 63.7 [61.5–66.0] | +3.2 [+2.6, +3.8] | 1/52 (<0.001) | 5.71 | 12.0 | 32% | 70.2 | 56.0 | 46.9 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 61.4 [59.1–63.7] | — | — | 7.80 | 15.1 | — | 68.5 | 52.9 | 43.8 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 64.5 [62.2–66.9] | +3.1 [+2.4, +3.9] | 5/58 (<0.001) | 7.80 | 15.1 | 29% | 71.1 | 56.7 | 47.8 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 63.6 [61.2–66.0] | +2.2 [+1.5, +2.9] | 6/45 (<0.001) | 7.80 | 15.1 | 21% | 70.3 | 55.8 | 46.3 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 64.5 [62.1–66.8] | +3.1 [+2.4, +3.8] | 2/53 (<0.001) | 7.80 | 15.1 | 29% | 70.9 | 56.8 | 48.1 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|
| CAV (3 checks) | +3.4 | +4.2 | +4.4 | +3.2 | +3.1 |
| CAV only degenerate | +2.5 | +3.3 | +3.5 | +2.6 | +2.4 |
| CAV without degenerate | +2.6 | +3.0 | +2.9 | +2.3 | +2.2 |
| CAV only ungrounded | +1.4 | +1.9 | +1.9 | +1.4 | +1.3 |
| CAV without ungrounded | +3.0 | +3.6 | +3.7 | +2.8 | +2.7 |
| CAV only bad_join | +1.2 | +1.2 | +1.1 | +0.9 | +0.9 |
| CAV without bad_join | +2.9 | +3.8 | +4.1 | +3.0 | +2.9 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 9.9% | 23.3% | 0.1% | 99.2% |
| Literal không có trong DB | 6.1% | 14.1% | 0.3% | 97.0% |
| JOIN không theo khóa ngoại | 7.7% | 15.4% | 2.1% | 84.3% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 14.7% | 13.4% | 15.6% | 38.7% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 60.5 | 5.71 | 12.0 | 88.5 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 63.8 | 5.71 | 12.0 | 88.5 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 64.2 | 6.00 | 12.5 | 86.5 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 61.4 | 7.80 | 15.1 | 69.9 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 64.5 | 7.80 | 15.1 | 69.9 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 64.7 | 7.48 | 14.7 | 73.5 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | +3.6 | +3.3 |
| fixed K=4 | CAV-2 (grounding + join) | +2.8 | +2.3 |
| fixed K=4 | Learned re-ranker (CV) | +3.3 | +3.3 |
| fixed K=8 | CAV-3 | +4.3 | +4.1 |
| fixed K=8 | CAV-2 (grounding + join) | +3.3 | +2.7 |
| fixed K=8 | Learned re-ranker (CV) | +4.0 | +4.2 |
| fixed K=16 | CAV-3 | +4.4 | +4.3 |
| fixed K=16 | CAV-2 (grounding + join) | +3.1 | +2.7 |
| fixed K=16 | Learned re-ranker (CV) | +4.2 | +4.8 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | +3.3 | +3.1 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | +2.5 | +2.1 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | +2.9 | +3.4 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | +3.2 | +3.0 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | +2.5 | +2.0 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | +2.9 | +3.3 |

Dữ liệu: 1534 câu, pool 16 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 3.86 ms/ứng viên.