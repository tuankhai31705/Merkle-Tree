# Mô phỏng Cây Merkle cho Tập Cam kết Coin (Zerocash Anonymity Set)

Dự án này triển khai cấu trúc **Cây Merkle nhị phân** lưu trữ các **Note Commitments** bằng ngôn ngữ Python. Đây là nền tảng toán học và kỹ thuật cốt lõi giúp xây dựng **tập ẩn danh (anonymity set)** trong các hệ thống tiền mã hóa riêng tư như **Zerocash** (và sau này là **Zcash**).

---

## 1. Cơ sở lý thuyết

### Note và Note Commitment
Trong hệ thống Zerocash, mỗi coin (được gọi là **Note**) được đại diện bởi bộ giá trị:
$$N = (a_{pk}, v, \rho, r)$$
Trong đó:
* $a_{pk}$ (Address Public Key): Khóa công khai của người nhận/sở hữu coin.
* $v$ (Value): Mệnh giá/giá trị của coin.
* $\rho$ (Serial Number): Số sê-ri duy nhất của coin. Khi coin được tiêu thụ, $\rho$ được dùng để tạo ra **nullifier** (dấu vết tiêu hủy) công khai nhằm ngăn chặn tiêu chi kép (double-spending).
* $r$ (Commitment Trapdoor): Số ngẫu nhiên bí mật dùng để đảm bảo tính che giấu (hiding property) của cam kết.

**Note Commitment ($cm$)** là một hàm băm mật mã một chiều ẩn giấu các thông tin của Note:
$$cm = \text{SHA-256}(a_{pk} \parallel v \parallel \rho \parallel r)$$

### Cây Merkle và Tập Ẩn Danh (Anonymity Set)
* Tất cả các coin commitments hợp lệ được phát hành trên mạng lưới sẽ được chèn làm các lá của **Cây Merkle**.
* **Gốc Merkle (Merkle Root - $R$)** đại diện cho trạng thái hiện tại của toàn bộ tập hợp coin đang tồn tại.
* **Tập ẩn danh (Anonymity Set):** Khi người sở hữu muốn tiêu một coin, thay vì công khai chỉ ra coin nào của họ ở trên blockchain, họ sử dụng công nghệ **Zero-Knowledge Proofs (ZKP)** để chứng minh rằng: *"Tôi biết các tham số bí mật của một Note $N$ có mã băm commitment là $cm$, và tôi có một chứng minh đường dẫn Merkle (Merkle Path / Membership Proof) chứng tỏ $cm$ nằm trong cây Merkle có gốc là $R$."*
* Bằng cách này, người kiểm chứng chỉ biết coin đó hợp lệ và nằm đâu đó trong cây (tập ẩn danh), nhưng không biết chính xác đó là coin nào.

---

## 2. Các chức năng đã triển khai

1. **Sinh Note và Commitment:** Sinh ngẫu nhiên note mật mã hoặc khởi tạo tùy chọn, tính mã băm SHA-256 chuẩn hóa cho các giá trị byte.
2. **Cập nhật Cây Merkle Tăng dần (Incremental Update):** Chèn các coin commitments mới vào cây và tự động cập nhật đường dẫn lên gốc một cách hiệu quả.
3. **Sinh Chứng minh Thành viên (Membership Proof):** Trích xuất đường dẫn Merkle (danh sách các nút anh em kèm theo hướng Trái/Phải).
4. **Xác thực Chứng minh:** Thuật toán băm ngược từ lá kết hợp với proof để đối chiếu gốc Merkle Root, phát hiện tức thì bất kỳ hành vi sửa đổi dữ liệu hay giả mạo cấu trúc cây.
5. **Giao diện Trực quan hóa CLI:** Vẽ cấu trúc cây Merkle bằng ký tự ASCII có màu sắc bắt mắt và kịch bản mô phỏng tương tác sinh động.

---

## 3. Cấu trúc thư mục

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

## 4. Hướng dẫn cài đặt và sử dụng

### Bước 1: Cài đặt thư viện phụ thuộc
Đảm bảo bạn đã cài đặt Python 3.8 trở lên. Run lệnh sau để cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy chương trình mô phỏng
Bạn có thể chạy file mô phỏng để xem hoạt động trực quan:
```bash
python merkle_tree/simulation.py
```
*Chương trình sẽ tự động thực thi kịch bản minh họa sinh coin, tạo cây Merkle, sinh proof và kiểm thử các kịch bản tấn công giả mạo. Sau đó, nó cung cấp một **Menu tương tác** cho phép bạn tự nhập tên người dùng, mệnh giá coin, tự tạo và xác minh proof.*

### Bước 3: Chạy bộ kiểm thử tự động
Để chạy các ca kiểm thử đơn vị (unit tests) nhằm kiểm chứng tính chính xác của thuật toán:
```bash
pytest tests/
```
hoặc chạy kiểm thử kèm chi tiết đầu ra:
```bash
pytest -v
```
