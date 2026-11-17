# Các cải tiến so với bài báo SLM-SQL

Tài liệu này giải thích, cho người chưa biết gì về lĩnh vực này, project đã làm gì khác bài báo gốc, vì sao cách làm đó có tác dụng, và số liệu so sánh cụ thể.

- Bài báo gốc: Sheng & Xu (2025), *SLM-SQL: An Exploration of Small Language Models for Text-to-SQL*, [arXiv 2507.22478](https://arxiv.org/abs/2507.22478), Findings IJCNLP-AACL 2025.
- Model dùng trong mọi thí nghiệm: `cycloneboy/SLM-SQL-1.5B`, model 1,5 tỉ tham số do chính tác giả bài báo công bố. Project **không huấn luyện lại** model; mọi cải tiến nằm ở cách dùng model.
- Bộ dữ liệu: BIRD dev, 1.534 câu hỏi trên 11 cơ sở dữ liệu thật.

---

## 1. Bài toán trong năm phút

### 1.1 Text-to-SQL là gì?

Một cơ sở dữ liệu (database) giống một tập các bảng Excel liên kết với nhau. Muốn lấy thông tin từ đó, người ta phải viết một câu lệnh bằng ngôn ngữ **SQL**. Ví dụ, để hỏi "Siêu anh hùng Abomination có siêu năng lực gì?", phải viết:

```sql
SELECT superpower.power_name
FROM superhero
JOIN hero_power ON superhero.id = hero_power.hero_id
JOIN superpower ON hero_power.power_id = superpower.id
WHERE superhero.superhero_name = 'Abomination';
```

**Text-to-SQL** là cho máy tự viết câu SQL đó từ câu hỏi bằng ngôn ngữ thường. Người dùng không cần biết SQL.

### 1.2 Model nhỏ (SLM) và vì sao nó hay sai

Các model lớn như GPT-4 làm việc này khá tốt nhưng đắt và phải gửi dữ liệu ra ngoài. Bài báo SLM-SQL dùng model **nhỏ** (0,5 đến 1,5 tỉ tham số), chạy được trên một máy tính thường. Đổi lại, model nhỏ hay sai: nhầm tên cột, quên một điều kiện, nối sai hai bảng...

### 1.3 Mẹo chung: hỏi nhiều lần rồi bỏ phiếu

Vì model sinh câu trả lời có yếu tố ngẫu nhiên, hỏi cùng một câu nhiều lần sẽ được nhiều câu SQL khác nhau. Mỗi câu SQL như vậy gọi là một **mẫu** (sample).

Cách chọn đơn giản nhất là **bỏ phiếu** (vote, còn gọi là *self-consistency*): chạy tất cả các câu SQL trên database, câu nào cho **cùng kết quả** thì gom vào một nhóm, rồi chọn nhóm đông nhất. Giống như hỏi 64 người, ý kiến nào được nhiều người nói nhất thì tin ý kiến đó.

Điểm yếu: nếu model **sai một cách nhất quán**, phần đông sẽ cùng sai và phiếu bầu chọn luôn cái sai.

### 1.4 Cách bài báo xử lý: CSC (model thứ hai làm trọng tài)

Bài báo thêm một bước gọi là **CSC** (*Corrective Self-Consistency*, hay *merge revision*): lấy hai nhóm đứng đầu cuộc bỏ phiếu, đưa cho **một model 1,5B thứ hai** (được huấn luyện riêng cho việc này) đọc cả hai câu SQL và viết ra câu cuối cùng. Cấu hình đầy đủ của bài báo là **64 mẫu + CSC**, đạt **67,08%**.

### 1.5 Đo bằng gì?

- **EX (Execution Accuracy)**: tỉ lệ câu hỏi mà câu SQL được chọn cho **đúng kết quả** như câu SQL chuẩn (gold) do người viết. Đây là thước đo chính thức của BIRD. EX 67,08% nghĩa là trả lời đúng 1.029 / 1.534 câu.
- **Oracle**: tỉ lệ câu hỏi có **ít nhất một** mẫu đúng trong số các mẫu đã sinh. Đây là trần trên: dù chọn khéo đến đâu cũng không vượt được oracle, vì không thể chọn đúng nếu không có mẫu nào đúng.
- **Ngân sách mẫu**: số lần cho model sinh SQL cho mỗi câu hỏi. Đây là chi phí chính (thời gian GPU). So sánh công bằng thì phải so ở cùng ngân sách.
- **Mất / cứu và p**: khi so hai phương pháp trên cùng các câu hỏi, "cứu" là số câu phương pháp mới làm đúng mà phương pháp cũ làm sai, "mất" là ngược lại. Giá trị **p** (kiểm định McNemar) cho biết khả năng chênh lệch đó chỉ do may rủi; p < 0,05 thường được coi là có ý nghĩa thống kê.

---

## 2. Tóm tắt kết quả

| Cấu hình | Model dùng | Mẫu / câu | EX trên 1.534 câu |
|---|---|---|---|
| Bài báo: vote, không CSC | 1 model 1,5B | 64 | 61,95 |
| Bài báo: 16 mẫu + CSC | 2 model 1,5B | 16 | 64,84 |
| **Bài báo: 64 mẫu + CSC (cấu hình đầy đủ)** | 2 model 1,5B | 64 | **67,08** |
| Project: vote (tái lập) | 1 model 1,5B | 64 | 61,54 |
| Project: **CAV-3** (cải tiến 1) | 1 model 1,5B | 16 | **66,1** |
| Project: **CAV-3** (cải tiến 1) | 1 model 1,5B | 64 | **67,08** |
| Project: **Hai vòng, schema rút gọn + CAV-3** (cải tiến 3) | 1 model 1,5B | 64 | **67,86 – 68,19** (ước lượng không chệch **67,95**) |

Nói gọn:

1. **CAV-3** đạt bằng bài báo ở 64 mẫu và hơn bài báo ở 16 mẫu, mà **không cần model thứ hai**.
2. **Hai vòng với schema rút gọn** là cách đầu tiên vượt 67,08 ở cùng 64 mẫu: hơn khoảng 0,9 điểm theo ước lượng trung thực nhất.
3. **Sinh thích ứng** giảm một nửa số mẫu, đổi lấy 1,6 điểm EX.

Chi tiết từng cải tiến ở các mục dưới, kèm cả những thứ đã thử mà **không** có tác dụng (mục 6).

---

## 3. Cải tiến 1: CAV-3, lọc mẫu sai bằng kiểm tra tự động thay cho model trọng tài

### 3.1 Ý tưởng

Thay vì nhờ một model thứ hai phân xử, ta để **máy tính tự kiểm tra** từng câu SQL bằng ba quy tắc đơn giản, không cần biết đáp án đúng. Câu nào bị "gắn cờ" (nghi ngờ) thì không được bỏ phiếu, trừ khi tất cả đều bị gắn cờ. Sau đó bỏ phiếu như bình thường trong số còn lại.

Ba kiểm tra (tên trong code: `degenerate`, `ungrounded`, `bad_join`):

| Kiểm tra | Câu SQL bị gắn cờ khi... | Ví dụ dễ hiểu |
|---|---|---|
| **Kết quả rỗng** (`degenerate`) | Chạy ra bảng rỗng, hoặc toàn giá trị trống (NULL) | Hỏi "Abomination có năng lực gì?" mà câu SQL trả về không có dòng nào. Câu hỏi của BIRD luôn có đáp án, nên kết quả rỗng gần như chắc chắn là sai. |
| **Giá trị không có thật** (`ungrounded`) | So sánh một cột với một chuỗi chữ không hề xuất hiện trong cột đó | Viết `WHERE gender = 'Female'` trong khi cột `gender` chỉ chứa `'F'` và `'M'`. |
| **Nối bảng vô lý** (`bad_join`) | Nối hai bảng bằng hai cột khoá không có quan hệ khoá ngoại nào | Nối `bảng_khách_hàng.id = bảng_sản_phẩm.id` chỉ vì cả hai cùng tên `id`. |

"CAV" là viết tắt của *Consistency-Aware Voting*; "3" là dùng cả ba kiểm tra. Mỗi kiểm tra chỉ là chạy lại SQL và tra schema, mất khoảng **4 mili giây** mỗi câu SQL, không gọi model nào.

### 3.2 Vì sao có tác dụng

Model nhỏ hay mắc đúng ba kiểu lỗi trên, và các lỗi đó thường **lặp lại nhiều lần** trong 64 mẫu nên thắng được cuộc bỏ phiếu. Loại chúng trước khi bỏ phiếu giúp nhóm đúng (vốn ít phiếu hơn) có cơ hội thắng. Các kiểm tra này rất ít khi gắn cờ nhầm câu đúng: với hai kiểm tra đầu, 97–99% câu bị gắn cờ đúng là câu sai.

### 3.3 Số liệu (BIRD dev, 1.534 câu)

| Cấu hình | Mẫu / câu | EX | Theo độ khó: dễ / vừa / khó |
|---|---|---|---|
| Vote (project) | 16 | 61,7 | 68,8 / 53,0 / 44,1 |
| Bài báo: 16 mẫu + CSC | 16 | 64,84 | (không công bố) |
| **CAV-3** | 16 | **66,1** | 72,8 / 58,0 / 49,0 |
| Vote (project) | 64 | 61,5 | 68,6 / 53,2 / 42,8 |
| Bài báo: vote | 64 | 61,95 | |
| Bài báo: 64 mẫu + CSC | 64 | **67,08** | 73,30 / 59,91 / 51,03 |
| **CAV-3** | 64 | **67,08** | 73,9 / 58,8 / 49,7 |

So sánh **ghép cặp** (cùng câu hỏi, cùng các mẫu, chỉ khác cách chọn) với phương pháp CSC của bài báo mà project chạy lại bằng đúng model merge của tác giả:

| Cách chọn trên cùng 64 mẫu | EX | So với CAV-3 | Mất / cứu | p |
|---|---|---|---|---|
| Vote | 61,54 | −5,54 | 94 / 9 | < 0,001 |
| CSC của bài báo (chạy lại) | 65,12 | −1,96 | 47 / 17 | < 0,001 |
| **CAV-3** | **67,08** | | | |

### 3.4 Đọc kết quả thế nào

- **Ở 16 mẫu, CAV-3 hơn bài báo khoảng 1,3 điểm** (66,1 so với 64,84) và không cần model thứ hai.
- **Ở 64 mẫu, CAV-3 bằng đúng bài báo** (67,08), cũng không cần model thứ hai.
- Trên cùng một tập mẫu, CAV-3 tốt hơn CSC chạy lại gần 2 điểm và chênh lệch này chắc chắn về thống kê (p < 0,001). Tuy vậy, CSC chạy lại chỉ đạt 65,12, thấp hơn con số 67,08 bài báo công bố, có thể do khác chi tiết cài đặt.
- Các kiểm tra được thiết kế khi xem 200 câu (`bird_dev200`). Trên 1.334 câu còn lại, chưa từng nhìn thấy khi thiết kế, mức tăng so với vote vẫn là +5,5 điểm, nên không phải do "học thuộc" dữ liệu.

---

## 4. Cải tiến 2: Sinh thích ứng, sinh ít mẫu cho câu dễ

### 4.1 Ý tưởng

Không phải câu hỏi nào cũng cần 16 hay 64 mẫu. Với câu dễ, 4 mẫu đầu đã đồng ý với nhau gần như tuyệt đối. Project sinh theo vòng **4 → 4 → 8**: sau mỗi vòng, nếu nhóm đông nhất chiếm ít nhất 75% số mẫu (ngưỡng τ = 0,75) thì dừng; nếu chưa thì sinh tiếp.

### 4.2 Số liệu (1.534 câu)

| Cấu hình | Mẫu / câu (trung bình) | EX |
|---|---|---|
| CAV-3, luôn 16 mẫu | 16 | 66,1 |
| **Sinh thích ứng 4-4-8 + CAV-3** | **7,80** | **64,5** |
| Bài báo: 16 mẫu + CSC | 16 | 64,84 |

**Ý nghĩa:** dùng **ít hơn một nửa** số mẫu (7,8 so với 16) mà đạt gần bằng cấu hình 16 mẫu + CSC của bài báo, và không cần model thứ hai. So với CAV-3 luôn 16 mẫu thì mất 1,6 điểm; đây là đánh đổi giữa chi phí và độ chính xác.

---

## 5. Cải tiến 3: Hai vòng sinh, vòng hai chỉ cho model xem phần schema cần thiết

Đây là cải tiến mới nhất và là cách duy nhất cho đến nay **vượt 67,08 ở cùng 64 mẫu**.

### 5.1 Vấn đề

Để viết SQL, model phải được xem **schema**: danh sách mọi bảng, mọi cột, kèm vài giá trị ví dụ. Database của BIRD có thể có hàng chục bảng và hàng trăm cột. Model nhỏ dễ bị "rối mắt": chọn nhầm một cột có tên na ná, hoặc nối thêm một bảng không cần thiết.

### 5.2 Ý tưởng

Chia 64 lần sinh thành hai vòng, mỗi vòng 32 mẫu:

1. **Vòng 1:** sinh 32 mẫu với schema **đầy đủ**, như bài báo.
2. **Rút gọn schema:** đọc 32 câu SQL vừa sinh (chỉ những câu chạy được) và ghi lại các bảng, cột mà chúng dùng. Giữ thêm các cột khoá (khoá chính, khoá ngoại) để model vẫn thấy được cách nối bảng. Mọi bảng và cột khác bị ẩn đi.
3. **Vòng 2:** sinh 32 mẫu nữa, lần này model chỉ được xem schema **đã rút gọn**.
4. **Chọn:** gộp cả 64 mẫu lại và chọn bằng CAV-3 như mục 3. Có thể cho mỗi mẫu vòng 2 nặng phiếu hơn (trọng số 1,5 hoặc 2), vì chúng chính xác hơn.

Cách này giống người làm bài thi: lần đầu đọc toàn bộ tài liệu và nháp nhiều cách giải; sau đó gạch bỏ phần không liên quan, chỉ giữ lại những trang mình đã dùng, rồi làm lại cho kỹ.

Điểm quan trọng về tính hợp lệ: bước rút gọn **chỉ dùng câu SQL do chính model sinh ra**, không bao giờ nhìn đáp án đúng. Tổng số lần sinh vẫn là 32 + 32 = 64, đúng bằng ngân sách của bài báo.

### 5.3 Rút gọn được bao nhiêu, có làm mất cột cần thiết không?

Đo trên 1.534 câu, không cần chạy model:

| Chỉ số | Giá trị |
|---|---|
| Phần schema còn lại | 21% số cột |
| Độ dài prompt còn lại | khoảng 34% |
| Câu mà schema rút gọn vẫn chứa đủ mọi bảng, cột của đáp án đúng | 91,8% |

Tức là ở khoảng 8% câu, vòng 2 chắc chắn thiếu một cột cần thiết. Đó là lý do vẫn giữ 32 mẫu vòng 1 (schema đầy đủ) trong cuộc bỏ phiếu cuối.

### 5.4 Số liệu (1.534 câu, chọn bằng CAV-3)

| Cấu hình | Mẫu / câu | EX [khoảng tin cậy 95%] | Dễ / vừa / khó | So với CAV-3 64 mẫu gốc: mất / cứu | p |
|---|---|---|---|---|---|
| CAV-3, 32 mẫu schema đầy đủ | 32 | 66,69 [64,3 – 69,1] | 73,5 / 58,6 / 49,0 | 19 / 15 | 0,61 |
| CAV-3, 64 mẫu schema đầy đủ (mốc) | 64 | 66,95 [64,7 – 69,3] | 73,6 / 58,8 / 50,3 | | |
| CAV-3, chỉ 32 mẫu vòng 2 (rút gọn) | 64 (32 + 32) | 67,80 [65,6 – 70,2] | 74,3 / 60,6 / 49,7 | 45 / 58 | 0,24 |
| **Hai vòng, trọng số 1** | 64 (32 + 32) | **67,86** [65,6 – 70,0] | 74,6 / 60,1 / 49,7 | 19 / 33 | 0,070 |
| **Hai vòng, trọng số 2** | 64 (32 + 32) | **68,19** [65,9 – 70,5] | 75,2 / 59,9 / 49,7 | 25 / 44 | 0,029 |
| **Hai vòng, trọng số chọn bằng kiểm định chéo** | 64 (32 + 32) | **67,95** | | | |
| Bài báo: 64 mẫu + CSC | 64 | 67,08 | 73,30 / 59,91 / 51,03 | | |

Ghi chú: dòng "chỉ 32 mẫu vòng 2" vẫn tốn 64 mẫu, vì muốn có vòng 2 thì phải sinh vòng 1 trước. Mốc 66,95 thấp hơn con số 67,08 ở mục 3 một chút, vì script này phá hoà (hai nhóm bằng phiếu) khác với script chính; mọi dòng trong bảng này dùng cùng một script nên so với nhau là công bằng.

### 5.5 Vì sao có tác dụng

| Chỉ số (32 mẫu) | Schema đầy đủ | Schema rút gọn |
|---|---|---|
| Tỉ lệ mẫu đúng | 51,3% | **54,2%** |
| Oracle (có ít nhất một mẫu đúng) | 79,7% | 79,5% |

Khi bị ẩn bớt phần không liên quan, **mỗi mẫu đúng nhiều hơn** (+2,9 điểm) mà **độ đa dạng gần như không giảm** (oracle chỉ giảm 0,2). Có nhiều mẫu đúng hơn thì nhóm đúng dễ thắng cuộc bỏ phiếu hơn. Gộp hai vòng còn tận dụng được ưu điểm của cả hai: vòng 1 cứu các câu mà vòng 2 bị thiếu cột, vòng 2 cứu các câu mà vòng 1 bị rối vì schema quá lớn. Oracle của 32 + 32 mẫu là 82,7%, gần bằng 64 mẫu schema đầy đủ (82,8%).

So sánh với một thí nghiệm khác để thấy điều này không hiển nhiên: hạ "độ ngẫu nhiên" khi sinh (temperature 0,8 xuống 0,5) cũng làm mỗi mẫu đúng hơn (54,0%), nhưng oracle giảm xuống 78,0% và EX sau khi chọn **giảm** 1,8 điểm. Các mẫu trở nên giống nhau, sai thì sai đồng loạt. Rút gọn schema thì không gặp vấn đề này.

Mức tăng nằm ở câu dễ (73,6 → 75,2) và vừa (58,8 → 59,9); câu khó không tăng (50,3 → 49,7).

### 5.6 Hạn chế, cần nói rõ khi báo cáo

- **Trọng số 2 được chọn sau khi xem kết quả.** 200 câu dành riêng để chọn trọng số không phân biệt được các mức. Vì vậy con số trung thực nhất là **67,95**, tính bằng kiểm định chéo 5 phần lặp 200 lần (mỗi lần chọn trọng số trên 4/5 số câu và đo trên 1/5 còn lại). Con số này hơn bài báo **0,87 điểm**, chưa tới 1 điểm.
- **Mới chạy một lần.** Hai lần chạy cùng cấu hình (16 mẫu) của project từng lệch nhau 0,6 điểm chỉ do ngẫu nhiên. Cần lặp lại với seed khác để chắc chắn.
- **So với bài báo không kiểm định được**, vì bài báo không công bố đáp án từng câu. Phép so có ý nghĩa thống kê là so với mốc 64 mẫu do project tự chạy (p = 0,029 với trọng số 2; p = 0,070 với trọng số 1).

---

## 6. Những thứ đã thử nhưng không giúp

Ghi lại để người đọc không mất công thử lại, và để thấy kết quả ở mục 5 không phải may mắn sau rất nhiều lần thử. Tất cả đều trên BIRD dev, model SLM-SQL-1.5B.

| Thử nghiệm | Ý tưởng | Kết quả |
|---|---|---|
| Model trọng tài sau CAV-3 | Thêm bước CSC của bài báo sau khi đã lọc bằng CAV-3 | 67,34, chỉ hơn 4 câu (p = 0,22) |
| Judge bằng chính model 1,5B | Cho model tự chấm hai nhóm đứng đầu | Chỉ có ích một chút trên 200 câu, không ổn định |
| Re-ranker học máy | Học cách chấm điểm mẫu từ nhiều đặc trưng | Hơn CAV-3 tối đa 0,1 điểm; bản thêm đặc trưng còn kém 0,15 |
| Truy xuất giá trị ví dụ tốt hơn | Cho model thấy đúng giá trị cần dùng (`'0040'` thay vì `40`) | Giá trị đúng xuất hiện trong prompt từ 95,5% lên 98,1%, nhưng EX không tăng (66,07 → 65,45, p = 0,28): model vốn đã dùng đúng giá trị |
| Thêm luật kiểm tra | Phép chia số nguyên, đối chiếu với gợi ý (evidence) | Tối đa +0,06 điểm; luật evidence còn làm giảm 0,5 đến 1,8 |
| Hạ temperature | Sinh ở 0,5 thay vì 0,8 | 32 mẫu giảm 1,8 điểm; trộn với 0,8 cũng không hơn |
| Trộn hai kiểu prompt giá trị | 48 mẫu prompt gốc + 16 mẫu prompt giá trị mới | +0,07 đến +0,15 điểm, không có ý nghĩa |
| Trộn với model 1,3B cùng họ | 48 mẫu 1,5B + 16 mẫu SLM-SQL-1.3B | **Chưa kết luận được**: lần chạy đầu hỏng 30% mẫu do lỗi bộ nhớ của vLLM (đã sửa trong code), chưa chạy lại. Đo sơ bộ trên phần không hỏng cho thấy 1,3B yếu hơn và hầu như không bổ sung câu đúng mới |

Bài học chung: với model 1,5B, khoảng 259 / 1.534 câu không có mẫu nào đúng trong 64 mẫu, nên không cách chọn nào cứu được. Phần còn lại phần lớn là lỗi suy luận đa dạng mà các quy tắc và model nhỏ đều không phân biệt được. Cải tiến 3 có tác dụng vì nó làm **chính các mẫu** tốt lên, chứ không chỉ chọn khéo hơn.

---

## 7. Điều kiện thí nghiệm

| Hạng mục | Thiết lập |
|---|---|
| Dữ liệu | BIRD dev, 1.534 câu, có gợi ý (evidence) |
| Model | `cycloneboy/SLM-SQL-1.5B`, không huấn luyện lại |
| Prompt | Theo Phụ lục E.1 của bài báo, định dạng schema của OmniSQL/CSC-SQL |
| Sinh | temperature 0,8, top-p 1,0, tối đa 1.024 token, như bài báo |
| Phần cứng | Kaggle 2 × T4, vLLM 0.8.5, FP16 (bài báo dùng BF16) |
| Thước đo | EX theo cách tính chính thức của BIRD (so sánh tập kết quả) |
| Thống kê | Khoảng tin cậy 95% bằng bootstrap theo câu hỏi; McNemar exact cho so sánh ghép cặp |
| Chống "học thuộc" | 200 câu `bird_dev200` dùng để thiết kế và chọn tham số; 1.334 câu còn lại dùng để kiểm tra |

## 8. Chạy lại

```powershell
# Cải tiến 1: CAV-3 trên pool 64 mẫu
python -m evaluation.selection_study results/bird-dev-vllm-64 --metric set --output results/selection-bird-dev-vllm-64

# Cải tiến 3, bước rút gọn schema từ 32 mẫu đầu (không cần GPU)
python -m evaluation.schema_keep results/bird-dev-vllm-64/pool.jsonl data/benchmarks/bird_dev.json --samples 32 --output data/benchmarks/bird_dev_keep32.json

# Cải tiến 3, vòng 2: chạy notebooks/kaggle_vllm_bird.ipynb với KEEP_SCHEMA = "data/benchmarks/bird_dev_keep32.json"

# Cải tiến 3, đánh giá trộn hai vòng
python -m evaluation.ensemble_study results/bird-dev-vllm-64 results/bird-dev-prune32/results/bird-dev-prune32 --flags results/selection-bird-dev-vllm-64/candidate_flags.json --tune data/benchmarks/bird_dev200.json --extra 16 32 --output results/ensemble-prune32
```

Bảng kết quả gốc: [CAV-3, 64 mẫu](../results/selection-bird-dev-vllm-64/tables.md), [CSC chạy lại](../results/merge-study-bird-dev/tables.md), [hai vòng schema rút gọn](../results/ensemble-prune32/tables.md).
