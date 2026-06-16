import hashlib
import secrets

class Note:
    """
    Đại diện cho một Coin/Note trong hệ thống mô phỏng Zerocash.
    Mỗi Note gồm có:
    - owner_pk: Khóa công khai của người sở hữu (dạng chuỗi văn bản hoặc hex)
    - value: Giá trị coin (số nguyên dương)
    - rho: Số sê-ri duy nhất (serial number) dùng để định danh note, tránh double-spending
    - r: Số ngẫu nhiên bí mật (commitment trapdoor) giúp ẩn giấu thông tin note
    """
    def __init__(self, owner_pk: str, value: int, rho: str = None, r: str = None):
        if value < 0:
            raise ValueError("Giá trị coin (value) không thể âm.")
        self.owner_pk = owner_pk
        self.value = value
        # Nếu không truyền vào, tự động sinh chuỗi ngẫu nhiên bảo mật 256-bit (32 bytes hex)
        self.rho = rho if rho is not None else secrets.token_hex(32)
        self.r = r if r is not None else secrets.token_hex(32)

    def compute_commitment(self) -> str:
        """
        Tính toán Note Commitment (cm) của note hiện tại:
        cm = SHA-256(owner_pk || value || rho || r)
        Trả về chuỗi hex biểu diễn mã băm 256-bit.
        """
        hasher = hashlib.sha256()
        
        # Băm owner_pk (chuỗi UTF-8)
        hasher.update(self.owner_pk.encode('utf-8'))
        
        # Băm value (số nguyên 8 bytes big-endian)
        hasher.update(self.value.to_bytes(8, byteorder='big'))
        
        # Băm rho (nếu là hex thì đổi ra bytes, ngược lại thì encode UTF-8)
        try:
            hasher.update(bytes.fromhex(self.rho))
        except ValueError:
            hasher.update(self.rho.encode('utf-8'))
            
        # Băm r (nếu là hex thì đổi ra bytes, ngược lại thì encode UTF-8)
        try:
            hasher.update(bytes.fromhex(self.r))
        except ValueError:
            hasher.update(self.r.encode('utf-8'))
            
        return hasher.hexdigest()

    @classmethod
    def generate_random(cls, owner_pk: str, value: int) -> 'Note':
        """
        Sinh ngẫu nhiên một Note cho người sở hữu owner_pk với mệnh giá value.
        """
        return cls(owner_pk=owner_pk, value=value)

    def __repr__(self) -> str:
        return (f"Note(owner_pk='{self.owner_pk[:10]}...', "
                f"value={self.value}, "
                f"rho='{self.rho[:8]}...', "
                f"r='{self.r[:8]}...')")
