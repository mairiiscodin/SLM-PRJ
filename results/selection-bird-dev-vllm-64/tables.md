## Bảng 1. So sánh phương pháp chọn SQL (cùng pool ứng viên)

| Ngân sách | Phương pháp | EX % [CI95] | Δ EX (điểm) [CI95] | McNemar −/+ (p) | Ứng viên TB | Độ trễ (s) | Thu hẹp khoảng cách oracle | Simple | Moderate | Challenging |
|---|---|---|---|---|---|---|---|---|---|---|
| fixed K=4 | Vote (baseline) | 58.0 [55.9–60.1] | — | — | 4.00 | 8.9 | — | 66.0 | 48.2 | 38.6 |
| fixed K=4 | **CAV-3** | 61.5 [59.4–63.8] | +3.5 [+3.0, +4.0] | 2/54 (<0.001) | 4.00 | 8.9 | 36% | 68.8 | 52.7 | 43.3 |
| fixed K=4 | **CAV-2 (grounding + join)** | 60.7 [58.4–62.7] | +2.6 [+2.2, +3.1] | 3/39 (<0.001) | 4.00 | 8.9 | 27% | 68.0 | 51.9 | 42.3 |
| fixed K=4 | **Learned re-ranker (CV)** | 61.4 [59.2–63.5] | +3.3 [+2.9, +3.8] | 3/59 (<0.001) | 4.00 | 8.9 | 34% | 68.8 | 52.4 | 42.8 |
| fixed K=8 | Vote (baseline) | 59.8 [57.7–62.0] | — | — | 8.00 | 8.9 | — | 67.4 | 50.6 | 41.0 |
| fixed K=8 | **CAV-3** | 64.1 [62.0–66.4] | +4.3 [+3.6, +5.0] | 3/73 (<0.001) | 8.00 | 8.9 | 33% | 71.0 | 56.0 | 45.9 |
| fixed K=8 | **CAV-2 (grounding + join)** | 63.0 [60.7–65.1] | +3.1 [+2.5, +3.8] | 3/57 (<0.001) | 8.00 | 8.9 | 24% | 69.9 | 54.8 | 44.7 |
| fixed K=8 | **Learned re-ranker (CV)** | 63.9 [61.7–66.2] | +4.1 [+3.4, +4.8] | 4/76 (<0.001) | 8.00 | 8.9 | 32% | 70.9 | 55.7 | 45.6 |
| fixed K=16 | Vote (baseline) | 60.8 [58.5–63.1] | — | — | 16.00 | 8.9 | — | 68.2 | 51.8 | 42.6 |
| fixed K=16 | **CAV-3** | 65.5 [63.3–67.9] | +4.7 [+3.9, +5.6] | 6/73 (<0.001) | 16.00 | 8.9 | 30% | 72.4 | 57.6 | 47.3 |
| fixed K=16 | **CAV-2 (grounding + join)** | 64.2 [61.8–66.5] | +3.3 [+2.5, +4.1] | 8/53 (<0.001) | 16.00 | 8.9 | 21% | 71.0 | 56.2 | 45.9 |
| fixed K=16 | **Learned re-ranker (CV)** | 65.5 [63.2–67.7] | +4.6 [+3.8, +5.5] | 5/71 (<0.001) | 16.00 | 8.9 | 29% | 72.3 | 57.4 | 47.7 |
| fixed K=32 | Vote (baseline) | 61.3 [58.9–63.7] | — | — | 32.00 | 17.8 | — | 68.6 | 52.5 | 43.1 |
| fixed K=32 | **CAV-3** | 66.3 [64.0–68.5] | +5.0 [+4.0, +6.1] | 8/86 (<0.001) | 32.00 | 17.8 | 27% | 73.2 | 58.3 | 48.4 |
| fixed K=32 | **CAV-2 (grounding + join)** | 64.8 [62.5–67.1] | +3.4 [+2.6, +4.4] | 9/59 (<0.001) | 32.00 | 17.8 | 19% | 71.6 | 56.7 | 46.9 |
| fixed K=32 | **Learned re-ranker (CV)** | 66.3 [64.0–68.6] | +5.0 [+4.1, +6.0] | 4/76 (<0.001) | 32.00 | 17.8 | 27% | 72.9 | 58.6 | 49.1 |
| fixed K=64 | Vote (baseline) | 61.5 [59.1–64.0] | — | — | 64.00 | 35.6 | — | 68.6 | 53.2 | 42.8 |
| fixed K=64 | **CAV-3** | 67.1 [64.8–69.3] | +5.5 [+4.4, +6.8] | 9/94 (<0.001) | 64.00 | 35.6 | 26% | 73.9 | 58.8 | 49.7 |
| fixed K=64 | **CAV-2 (grounding + join)** | 65.3 [62.8–67.6] | +3.7 [+2.7, +4.8] | 9/66 (<0.001) | 64.00 | 35.6 | 17% | 72.2 | 56.9 | 47.6 |
| fixed K=64 | **Learned re-ranker (CV)** | 67.2 [64.8–69.6] | +5.7 [+4.5, +6.8] | 1/88 (<0.001) | 64.00 | 35.6 | 27% | 73.7 | 59.7 | 49.7 |
| adaptive 4-4-8 τ=0.5 m=2 | Vote (baseline) | 59.9 [57.6–62.2] | — | — | 5.71 | 11.8 | — | 67.4 | 50.9 | 41.5 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-3** | 63.3 [61.0–65.5] | +3.3 [+2.8, +3.9] | 4/58 (<0.001) | 5.71 | 11.8 | 32% | 70.1 | 55.2 | 45.5 |
| adaptive 4-4-8 τ=0.5 m=2 | **CAV-2 (grounding + join)** | 62.3 [60.2–64.6] | +2.4 [+1.9, +2.9] | 6/41 (<0.001) | 5.71 | 11.8 | 23% | 69.2 | 54.2 | 44.3 |
| adaptive 4-4-8 τ=0.5 m=2 | **Learned re-ranker (CV)** | 63.1 [61.0–65.3] | +3.2 [+2.7, +3.7] | 3/53 (<0.001) | 5.71 | 11.8 | 31% | 70.0 | 55.1 | 45.1 |
| adaptive 4-4-8 τ=0.75 m=2 | Vote (baseline) | 60.6 [58.4–63.0] | — | — | 7.79 | 14.8 | — | 68.0 | 51.6 | 42.2 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-3** | 64.0 [61.8–66.2] | +3.4 [+2.8, +4.0] | 5/58 (<0.001) | 7.79 | 14.8 | 29% | 70.8 | 56.1 | 45.9 |
| adaptive 4-4-8 τ=0.75 m=2 | **CAV-2 (grounding + join)** | 63.1 [60.8–65.2] | +2.4 [+1.9, +3.0] | 6/45 (<0.001) | 7.79 | 14.8 | 21% | 69.9 | 55.0 | 44.8 |
| adaptive 4-4-8 τ=0.75 m=2 | **Learned re-ranker (CV)** | 63.9 [61.6–66.1] | +3.3 [+2.8, +3.9] | 5/53 (<0.001) | 7.79 | 14.8 | 29% | 70.7 | 56.0 | 46.1 |

Δ và CI95: paired bootstrap trên câu hỏi; McNemar exact trên thứ tự ứng viên gốc (−: câu baseline đúng nhưng phương pháp sai, +: ngược lại). Thu hẹp khoảng cách oracle = Δ / (oracle@ngân sách − baseline).

## Bảng 2. Ablation từng kiểm tra (Δ EX so với vote, điểm %)

| Cấu hình | fixed K=4 | fixed K=8 | fixed K=16 | fixed K=32 | fixed K=64 | adaptive 4-4-8 τ=0.5 m=2 | adaptive 4-4-8 τ=0.75 m=2 |
|---|---|---|---|---|---|---|---|
| CAV (3 checks) | +3.5 | +4.3 | +4.7 | +5.0 | +5.5 | +3.3 | +3.4 |
| CAV only degenerate | +2.5 | +3.2 | +3.7 | +4.1 | +4.6 | +2.6 | +2.6 |
| CAV without degenerate | +2.6 | +3.1 | +3.3 | +3.4 | +3.7 | +2.4 | +2.4 |
| CAV only ungrounded | +1.4 | +1.9 | +2.3 | +2.4 | +2.7 | +1.5 | +1.6 |
| CAV without ungrounded | +3.1 | +3.7 | +4.0 | +4.3 | +4.8 | +2.9 | +2.9 |
| CAV only bad_join | +1.3 | +1.3 | +1.2 | +1.3 | +1.2 | +1.0 | +1.0 |
| CAV without bad_join | +2.9 | +3.8 | +4.4 | +4.9 | +5.5 | +3.0 | +3.1 |

## Bảng 3. Độ tin cậy của từng kiểm tra (trên mọi ứng viên chạy được)

| Kiểm tra | Tỷ lệ kích hoạt | Trên ứng viên sai | Trên ứng viên đúng | Precision (cờ ⇒ sai) |
|---|---|---|---|---|
| Kết quả rỗng / toàn NULL | 10.1% | 23.6% | 0.1% | 99.3% |
| Literal không có trong DB | 6.2% | 14.1% | 0.3% | 97.2% |
| JOIN không theo khóa ngoại | 7.8% | 15.4% | 2.2% | 83.9% |
| Dòng trùng lặp (chỉ dùng cho re-ranker) | 14.6% | 13.1% | 15.6% | 38.2% |

## Bảng 4. Dùng CAV cho cả điều kiện dừng sớm (adaptive)

| Ngân sách | Phương pháp | EX % | Ứng viên TB | Độ trễ (s) | Dừng sớm % |
|---|---|---|---|---|---|
| adaptive 4-4-8 τ=0.5 m=2 | vote (baseline) | 59.9 | 5.71 | 11.8 | 90.7 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) | 63.3 | 5.71 | 11.8 | 90.7 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV (3 checks) + CAV stopping | 63.7 | 6.01 | 12.3 | 90.3 |
| adaptive 4-4-8 τ=0.75 m=2 | vote (baseline) | 60.6 | 7.79 | 14.8 | 72.2 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) | 64.0 | 7.79 | 14.8 | 72.2 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV (3 checks) + CAV stopping | 64.2 | 7.49 | 14.4 | 76.8 |

## Bảng 5. Kiểm tra tính ổn định: Δ EX trên hai nửa dữ liệu (câu lẻ / chẵn)

| Ngân sách | Phương pháp | Δ nửa lẻ | Δ nửa chẵn |
|---|---|---|---|
| fixed K=4 | CAV-3 | +3.4 | +3.5 |
| fixed K=4 | CAV-2 (grounding + join) | +2.7 | +2.6 |
| fixed K=4 | Learned re-ranker (CV) | +3.2 | +3.4 |
| fixed K=8 | CAV-3 | +4.2 | +4.4 |
| fixed K=8 | CAV-2 (grounding + join) | +3.2 | +3.1 |
| fixed K=8 | Learned re-ranker (CV) | +3.8 | +4.4 |
| fixed K=16 | CAV-3 | +4.6 | +4.8 |
| fixed K=16 | CAV-2 (grounding + join) | +3.4 | +3.2 |
| fixed K=16 | Learned re-ranker (CV) | +4.3 | +5.0 |
| fixed K=32 | CAV-3 | +4.9 | +5.1 |
| fixed K=32 | CAV-2 (grounding + join) | +3.6 | +3.3 |
| fixed K=32 | Learned re-ranker (CV) | +4.5 | +5.5 |
| fixed K=64 | CAV-3 | +5.2 | +5.9 |
| fixed K=64 | CAV-2 (grounding + join) | +3.7 | +3.8 |
| fixed K=64 | Learned re-ranker (CV) | +4.9 | +6.4 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-3 | +3.3 | +3.4 |
| adaptive 4-4-8 τ=0.5 m=2 | CAV-2 (grounding + join) | +2.5 | +2.3 |
| adaptive 4-4-8 τ=0.5 m=2 | Learned re-ranker (CV) | +3.0 | +3.4 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-3 | +3.4 | +3.3 |
| adaptive 4-4-8 τ=0.75 m=2 | CAV-2 (grounding + join) | +2.6 | +2.3 |
| adaptive 4-4-8 τ=0.75 m=2 | Learned re-ranker (CV) | +3.1 | +3.5 |

Dữ liệu: 1534 câu, pool 64 ứng viên/câu, 201 hoán vị thứ tự, 2000 lần bootstrap. Chi phí kiểm tra: 1.35 ms/ứng viên.