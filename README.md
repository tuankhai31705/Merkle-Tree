# Mô phỏng Cây Merkle cho Tập Cam kết Coin (Zerocash Anonymity Set)

Dự án này triển khai cấu trúc **Cây Merkle nhị phân** lưu trữ các **Note Commitments** bằng ngôn ngữ Python. Đây là nền tảng toán học và kỹ thuật cốt lõi giúp xây dựng **tập ẩn danh (anonymity set)** trong các hệ thống tiền mã hóa riêng tư như **Zerocash** (và sau này là **Zcash**).

---

## 🚀 HƯỚNG DẪN NHANH (QUICK START)


### Bước 1: Cài đặt thư viện phụ thuộc
Đảm bảo máy tính đã cài đặt Python 3.8+. Mở terminal tại thư mục dự án và chạy:
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy kịch bản mô phỏng trực quan & tương tác
Chạy lệnh sau để bắt đầu xem cách cây Merkle hoạt động:
```bash
python merkle_tree/simulation.py
```
*   **Giai đoạn 1 (Tự động):** Chương trình sẽ tự động sinh coin, tạo cây Merkle độ sâu 3 (tối đa 8 lá), chèn coin của Alice, Bob, Charlie, David vào cây, tạo Membership Proof cho Bob và xác thực nó. Tiếp theo, chương trình tự động chạy thử kịch bản giả mạo để chứng minh hệ thống từ chối thành công.
*   **Giai đoạn 2 (Tương tác):** Nhấn **Enter** khi được nhắc để vào menu CLI tương tác. Tại đây bạn có thể tự nhập coin của riêng mình (ví dụ chèn coin của chính bạn) và xem cây Merkle được vẽ trực quan thay đổi thế nào.

### Bước 3: Chạy bộ kiểm thử tự động (Unit Tests)
Để xác minh tính đúng đắn toán học của tất cả các hàm trong hệ thống, hãy chạy:
```bash
python -m pytest -v
```

---



---

## Các chức năng đã triển khai

1. **Sinh Note và Commitment:** Lớp `Note` sinh ngẫu nhiên note mật mã hoặc khởi tạo tùy chọn, tính mã băm SHA-256 chuẩn hóa cho các giá trị byte.
2. **Cập nhật Cây Merkle Tăng dần (Incremental Update):** Lớp `MerkleTree` chèn các coin commitments mới vào cây và tự động cập nhật đường dẫn lên gốc một cách hiệu quả.
3. **Sinh Chứng minh Thành viên (Membership Proof):** Trích xuất đường dẫn Merkle (danh sách các nút anh em kèm theo hướng Trái/Phải).
4. **Xác thực Chứng minh:** Thuật toán băm ngược từ lá kết hợp với proof để đối chiếu gốc Merkle Root, phát hiện tức thì bất kỳ hành vi sửa đổi dữ liệu hay giả mạo cấu trúc cây.
5. **Giao diện Trực quan hóa CLI:** Vẽ cấu trúc cây Merkle bằng ký tự ASCII có màu sắc bắt mắt và kịch bản mô phỏng tương tác sinh động.

---

## Cấu trúc thư mục dự án

```text
Merkle-Tree/
├── merkle_tree/
│   ├── __init__.py
│   ├── note.py          # Lớp định nghĩa Note và tính toán commitment
│   ├── tree.py          # Lớp MerkleTree, thuật toán băm cặp và xác thực proof
│   └── simulation.py    # Kịch bản mô phỏng trực quan hóa trên terminal
├── tests/
│   ├── __init__.py
│   └── test_merkle.py   # Các ca kiểm thử tự động với pytest
├── requirements.txt      # Khai báo thư viện phụ thuộc (colorama, pytest)
├── .gitignore            # Cấu hình bỏ qua các tệp không cần thiết khi git commit
└── README.md             # Tài liệu hướng dẫn sử dụng này
```

---

