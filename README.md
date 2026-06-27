# Đồ án cuối kỳ - Trí Tuệ Nhân Tạo: 18 Thuật Toán Tìm Kiếm Giải Sudoku 9x9

Dự án này là tập hợp 18 thuật toán trí tuệ nhân tạo chia làm 6 nhóm khác nhau để giải quyết bài toán Sudoku 9x9 và biến thể Sudoku Battle. Toàn bộ mã nguồn đã được tái cấu trúc dưới dạng một Dashboard quản lý chung.

## Cấu trúc thư mục mới

Dự án được phân chia rõ ràng thành 2 phần cốt lõi: Giao diện và Thuật toán.

```text
Final-Project-AI/
│
├── main.py                           # Giao diện Dashboard quản lý toàn bộ 18 thuật toán
├── base_gui.py                       # Các thành phần giao diện dùng chung (BaseSudokuApp)
├── sudoku_utils.py                   # Tiện ích xử lý Sudoku (sinh đề, validate, tính toán...)
├── README.md                         # Tài liệu hướng dẫn (File bạn đang đọc)
│
├── GiaoDien/                         # Chứa 18 file mã nguồn giao diện (Tkinter)
│   ├── Nhom1_UninformedSearch/       # 01_IDS, 07_BFS, 08_DFS
│   ├── Nhom2_InformedSearch/         # 02_IDAstar, 09_Greedy, 10_AStar
│   ├── Nhom3_LocalSearch/            # 03_SimulatedAnnealing, 11_HillClimbing, 12_LocalBeam
│   ├── Nhom4_ComplexSearch/          # 04_PartiallyObservable, 13_AndOr, 14_Sensorless
│   ├── Nhom5_CSP/                    # 05_ForwardChecking, 15_Backtracking, 16_MinConflicts
│   └── Nhom6_AdversarialSearch/      # 06_Minimax, 17_AlphaBeta, 18_Expectimax
│
└── ThuatToan/                        # Chứa 18 file mã nguồn logic thuật toán cốt lõi
    ├── Nhom1_UninformedSearch/       # ids, bfs, dfs
    ├── Nhom2_InformedSearch/         # idastar, greedy, astar
    ├── Nhom3_LocalSearch/            # sa, hill_climbing, local_beam
    ├── Nhom4_ComplexSearch/          # partial_observable, and_or, sensorless
    ├── Nhom5_CSP/                    # forward_checking, backtracking, min_conflicts
    └── Nhom6_AdversarialSearch/      # minimax, alpha_beta, expectimax
```

## Yêu cầu cài đặt

- Python 3.8 trở lên.
- Thư viện `tkinter` — đã có sẵn trên Windows/macOS. Trên Ubuntu/Debian, nếu thiếu, cài bằng lệnh:
  ```bash
  sudo apt install python3-tk
  ```

Không cần cài thêm bất kỳ thư viện ngoài nào khác (dự án chỉ sử dụng các thư viện chuẩn của Python).

## Cách sử dụng

Chỉ cần khởi chạy giao diện Dashboard ở thư mục gốc:

```bash
python main.py
```

Từ bảng điều khiển chính, bạn có thể:
1. Xem tổng quan 6 nhóm thuật toán AI.
2. Rê chuột để xem thông tin chi tiết các biến thể thuật toán.
3. Click trực tiếp vào một thuật toán bất kỳ để mở ứng dụng giải Sudoku tương ứng.

Mỗi ứng dụng (từ Nhóm 1 đến Nhóm 5) sẽ tự sinh ra một đề Sudoku ngẫu nhiên, hiển thị giao diện trực quan với các tính năng:
- **Giải (chạy ngầm)**: Agent tự động giải bằng thuật toán tương ứng ở luồng riêng (không gây treo giao diện).
- **Phát lại từng bước**: Trực quan hóa lại quá trình thuật toán đã chạy, có thanh chỉnh tốc độ (nhanh/chậm).
- **Nhảy đến kết quả**: Bỏ qua phần hoạt ảnh phát lại, hiển thị ngay bảng Sudoku đã được giải xong.
- **Đề mới**: Sinh một đề Sudoku ngẫu nhiên khác để thử lại.

Riêng các ứng dụng thuộc **Nhóm 6 (Adversarial Search)** là chương trình **tương tác đối kháng trực tiếp 2 người chơi (Sudoku Battle)**:
- Người chơi click chọn ô trống + nhập số từ bàn phím.
- Ngay sau đó, Agent (sử dụng thuật toán Minimax, Alpha-Beta Pruning, hoặc Expectimax) sẽ tự động suy luận để chọn nước đi tiếp theo phản hồi lại.

## Tài liệu

Toàn bộ lý thuyết, mã giả, cấu trúc môi trường trò chơi (PEAS), số liệu thực nghiệm và đánh giá so sánh hiệu năng được trình bày chi tiết trong báo cáo đồ án của nhóm.
