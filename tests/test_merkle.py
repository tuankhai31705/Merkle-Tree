import pytest
import hashlib
from merkle_tree.note import Note
from merkle_tree.tree import MerkleTree

def test_note_commitment():
    # Khởi tạo các tham số note cố định
    owner = "pk_test"
    val = 100
    rho = "0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"
    r = "201f1e1d1c1b1a191817161514131211100f0e0d0c0b0a090807060504030201"
    
    note1 = Note(owner, val, rho, r)
    note2 = Note(owner, val, rho, r)
    
    # Hai note có cùng tham số phải có cùng commitment
    assert note1.compute_commitment() == note2.compute_commitment()
    
    # Note khác tham số phải có commitment khác nhau
    note_diff_val = Note(owner, 200, rho, r)
    assert note1.compute_commitment() != note_diff_val.compute_commitment()
    
    note_diff_rho = Note(owner, val, None, r)
    assert note1.compute_commitment() != note_diff_rho.compute_commitment()

def test_note_negative_value():
    with pytest.raises(ValueError):
        Note("owner", -50)

def test_merkle_tree_initialization():
    # Khởi tạo cây độ sâu 2 (tối đa 4 lá)
    tree = MerkleTree(depth=2)
    assert tree.depth == 2
    assert tree.max_leaves == 4
    assert tree.next_index == 0
    
    # Gốc ban đầu của cây rỗng không được trùng với rỗng hoàn toàn hoặc rỗng của cây độ sâu khác
    empty_root = tree.get_root()
    assert len(empty_root) == 64
    
    with pytest.raises(ValueError):
        MerkleTree(depth=0)

def test_merkle_tree_insert_and_proof():
    tree = MerkleTree(depth=3) # max 8 leaves
    
    # Sinh commitments
    cm0 = Note.generate_random("pk_alice", 50).compute_commitment()
    cm1 = Note.generate_random("pk_bob", 100).compute_commitment()
    
    # Chèn lá
    idx0 = tree.insert(cm0)
    idx1 = tree.insert(cm1)
    
    assert idx0 == 0
    assert idx1 == 1
    assert tree.next_index == 2
    
    # Lấy proof và xác minh
    root = tree.get_root()
    
    proof0 = tree.get_proof(0)
    assert len(proof0) == 3 # Độ sâu là 3
    assert MerkleTree.verify_proof(cm0, proof0, root) is True
    
    proof1 = tree.get_proof(1)
    assert MerkleTree.verify_proof(cm1, proof1, root) is True
    
    # Xác minh thất bại nếu dùng sai coin cho proof
    assert MerkleTree.verify_proof(cm0, proof1, root) is False

def test_merkle_tree_tampering():
    tree = MerkleTree(depth=2)
    cm = Note.generate_random("pk_alice", 50).compute_commitment()
    tree.insert(cm)
    
    root = tree.get_root()
    proof = tree.get_proof(0)
    
    # Trường hợp 1: Chỉnh sửa giá trị lá
    fake_cm = hashlib.sha256(b"fake_coin").hexdigest()
    assert MerkleTree.verify_proof(fake_cm, proof, root) is False
    
    # Trường hợp 2: Chỉnh sửa mã băm trung gian trong proof
    tampered_proof = [step.copy() for step in proof]
    tampered_proof[0]['hash'] = hashlib.sha256(b"tampered_data").hexdigest()
    assert MerkleTree.verify_proof(cm, tampered_proof, root) is False
    
    # Trường hợp 3: Thay đổi hướng của nút anh em
    tampered_direction_proof = [step.copy() for step in proof]
    tampered_direction_proof[0]['direction'] = 'left' if proof[0]['direction'] == 'right' else 'right'
    assert MerkleTree.verify_proof(cm, tampered_direction_proof, root) is False

def test_merkle_tree_limits():
    tree = MerkleTree(depth=1) # max 2 leaves
    cm0 = Note.generate_random("pk_a", 10).compute_commitment()
    cm1 = Note.generate_random("pk_b", 20).compute_commitment()
    cm2 = Note.generate_random("pk_c", 30).compute_commitment()
    
    tree.insert(cm0)
    tree.insert(cm1)
    
    # Vượt quá giới hạn lá
    with pytest.raises(IndexError):
        tree.insert(cm2)
        
    # Vị trí lá lấy proof ngoài phạm vi
    with pytest.raises(IndexError):
        tree.get_proof(2)
        
    with pytest.raises(IndexError):
        tree.get_proof(-1)

def test_invalid_insert_commitment():
    tree = MerkleTree(depth=2)
    
    # Băm không phải là hex
    with pytest.raises(ValueError):
        tree.insert("not_a_hex_hash_at_all_1234567890123456789012345678901234567890")
        
    # Băm có độ dài sai
    with pytest.raises(ValueError):
        tree.insert("123456")
