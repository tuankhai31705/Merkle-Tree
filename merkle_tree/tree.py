import hashlib

def hash_pair(left_hex: str, right_hex: str) -> str:
    """
    Tính mã băm SHA-256 từ cặp mã băm con (trái và phải).
    Chuyển đổi chuỗi hex sang bytes trước khi băm để đảm bảo tính chuẩn hóa.
    """
    left_bytes = bytes.fromhex(left_hex)
    right_bytes = bytes.fromhex(right_hex)
    return hashlib.sha256(left_bytes + right_bytes).hexdigest()

class MerkleTree:
    """
    Cây Merkle nhị phân hoàn hảo có độ sâu cố định (depth).
    Hỗ trợ chèn lá tăng dần, tạo và xác minh Membership Proof.
    """
    # Giá trị băm mặc định cho lá trống: SHA-256("empty_leaf")
    EMPTY_LEAF = hashlib.sha256(b"empty_leaf").hexdigest()

    def __init__(self, depth: int = 4):
        if depth <= 0:
            raise ValueError("Độ sâu (depth) của cây phải lớn hơn 0.")
        self.depth = depth
        self.max_leaves = 2 ** depth
        self.next_index = 0
        
        # Cấu trúc lưu trữ: self.tree[level][index]
        # level 0 là tầng lá (leaves), level depth là gốc (root)
        self.tree = [[] for _ in range(depth + 1)]
        
        # Khởi tạo cây với tất cả các lá trống
        self.tree[0] = [self.EMPTY_LEAF] * self.max_leaves
        
        # Tính toán giá trị băm cho các tầng cha
        self._rebuild_tree()

    def _rebuild_tree(self):
        """Tính toán toàn bộ các nút cha từ tầng lá lên đến gốc."""
        for level in range(1, self.depth + 1):
            parent_level = []
            prev_level = self.tree[level - 1]
            for i in range(0, len(prev_level), 2):
                parent_level.append(hash_pair(prev_level[i], prev_level[i + 1]))
            self.tree[level] = parent_level

    def insert(self, commitment: str) -> int:
        """
        Chèn một note commitment mới vào lá trống tiếp theo.
        Trả về vị trí index vừa được chèn.
        """
        if self.next_index >= self.max_leaves:
            raise IndexError("Cây Merkle đã đầy, không thể chèn thêm coin commitment.")
        
        # Kiểm tra tính hợp lệ của mã băm hex nhập vào
        try:
            bytes.fromhex(commitment)
        except ValueError:
            raise ValueError("Commitment phải là chuỗi hex 64 ký tự hợp lệ.")
            
        if len(commitment) != 64:
            raise ValueError("Commitment phải là chuỗi hex SHA-256 có độ dài 64 ký tự.")

        idx = self.next_index
        self.tree[0][idx] = commitment
        
        # Cập nhật đường dẫn từ lá lên gốc
        self._update_path(idx)
        
        self.next_index += 1
        return idx

    def _update_path(self, leaf_index: int):
        """Cập nhật các nút cha dọc theo đường dẫn từ lá lên đến gốc."""
        idx = leaf_index
        for level in range(self.depth):
            # Tìm chỉ số nút anh em (sibling)
            left_idx = idx if idx % 2 == 0 else idx - 1
            right_idx = idx + 1 if idx % 2 == 0 else idx
            
            parent_hash = hash_pair(self.tree[level][left_idx], self.tree[level][right_idx])
            
            # Di chuyển lên tầng tiếp theo
            idx = idx // 2
            self.tree[level + 1][idx] = parent_hash

    def get_root(self) -> str:
        """Trả về mã băm gốc (Merkle Root) hiện tại."""
        return self.tree[self.depth][0]

    def get_proof(self, index: int) -> list:
        """
        Tạo chứng minh đường dẫn Merkle (Merkle proof) cho lá tại vị trí index.
        Chứng minh là danh sách các dict chứa:
        - 'hash': mã băm của nút anh em (sibling) ở tầng tương ứng.
        - 'direction': hướng của nút anh em ('left' hoặc 'right').
        """
        if index < 0 or index >= self.max_leaves:
            raise IndexError("Chỉ số lá (index) nằm ngoài phạm vi cây.")
            
        proof = []
        idx = index
        for level in range(self.depth):
            is_right_sibling = (idx % 2 == 0)
            sibling_idx = idx + 1 if is_right_sibling else idx - 1
            
            sibling_hash = self.tree[level][sibling_idx]
            direction = 'right' if is_right_sibling else 'left'
            
            proof.append({
                'hash': sibling_hash,
                'direction': direction
            })
            idx = idx // 2
            
        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: list, expected_root: str) -> bool:
        """
        Xác minh chứng minh thành viên (membership proof) cho leaf_hash.
        Trả về True nếu băm ngược lên khớp với gốc dự kiến (expected_root), ngược lại False.
        """
        try:
            current_hash = leaf_hash
            for step in proof:
                sibling_hash = step['hash']
                direction = step['direction']
                
                if direction == 'right':
                    current_hash = hash_pair(current_hash, sibling_hash)
                elif direction == 'left':
                    current_hash = hash_pair(sibling_hash, current_hash)
                else:
                    raise ValueError(f"Hướng không hợp lệ trong proof: {direction}")
            return current_hash == expected_root
        except Exception:
            return False
