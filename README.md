# Đồ án cuối kỳ - Trí Tuệ Nhân Tạo: 6 Thuật Toán Tìm Kiếm Giải Sudoku 9x9

## Cấu trúc thư mục

```
├── sudoku_utils.py                   # Module dùng chung (sinh đề, kiểm tra luật...)
│
├── ids_solver.py                     # Logic thuật toán IDS
├── 01_IDS_sudoku.py                  # App Tkinter — Uninformed Search (IDS)
│
├── idastar_solver.py                 # Logic thuật toán IDA*
├── 02_IDAstar_sudoku.py              # App Tkinter — Informed Search (IDA*)
│
├── sa_solver.py                      # Logic thuật toán Simulated Annealing
├── 03_SimulatedAnnealing_sudoku.py   # App Tkinter — Local Search
│
├── partial_observable_solver.py      # Logic Partially Observable Search
├── 04_PartiallyObservable_sudoku.py  # App Tkinter — Complex Environments
│
├── forward_checking_solver.py        # Logic Backtracking + Forward Checking
├── 05_ForwardChecking_sudoku.py      # App Tkinter — CSP
│
├── minimax_solver.py                 # Logic Minimax (Sudoku Battle)
└── 06_Minimax_SudokuBattle.py        # App Tkinter — Adversarial Search
```

Mỗi nhóm thuật toán gồm 2 file: 1 file **`*_solver.py`** chứa thuật toán thuần (logic, có
thể chạy độc lập bằng `python <ten_file>_solver.py` để test nhanh không cần giao diện),
và 1 file **app Tkinter** (đánh số `01_` đến `06_`) là chương trình chính có giao diện
trực quan — đây là file cần chạy để xem demo.

## Yêu cầu cài đặt

- Python 3.8 trở lên.
- Thư viện `tkinter` — đã có sẵn trên Windows/macOS. Trên Ubuntu/Debian, nếu thiếu, cài bằng:
  ```bash
  sudo apt install python3-tk
  ```

Không cần cài thêm bất kỳ thư viện ngoài nào khác (chỉ dùng thư viện chuẩn của Python).

## Cách chạy

Clone repository, giữ tất cả các file trong cùng 1 thư mục, rồi chạy từng app:

```bash
python 01_IDS_sudoku.py
python 02_IDAstar_sudoku.py
python 03_SimulatedAnnealing_sudoku.py
python 04_PartiallyObservable_sudoku.py
python 05_ForwardChecking_sudoku.py
python 06_Minimax_SudokuBattle.py
```

Mỗi app sẽ tự sinh ra một đề Sudoku ngẫu nhiên, hiển thị giao diện, có các nút:
- **Giải (chạy ngầm)**: chạy thuật toán ở luồng riêng (không treo giao diện).
- **Phát lại từng bước**: trực quan hóa lại quá trình thuật toán đã chạy, có thanh chỉnh tốc độ.
- **Nhảy đến kết quả**: bỏ qua phần phát lại, hiển thị ngay lời giải cuối.
- **Đề mới**: sinh đề khác để thử lại.

Riêng `06_Minimax_SudokuBattle.py` là chương trình **tương tác 2 chiều**: người chơi
click chọn ô + nhập số, sau đó Agent (dùng Minimax) tự động phản hồi.

## Test nhanh logic thuật toán (không cần giao diện)

```bash
python ids_solver.py
python idastar_solver.py
python sa_solver.py
python partial_observable_solver.py
python forward_checking_solver.py
python minimax_solver.py
```

Mỗi file khi chạy trực tiếp sẽ tự sinh 1 đề demo, chạy thuật toán, và in kết quả + số
liệu thống kê (thời gian, số node mở rộng...) ra màn hình console.

## Tài liệu

Toàn bộ lý thuyết, mã giả, PEAS, số liệu thực nghiệm và đánh giá so sánh được trình bày
chi tiết trong file báo cáo: `BaoCao_DoAn_TriTueNhanTao_Sudoku.docx`.
