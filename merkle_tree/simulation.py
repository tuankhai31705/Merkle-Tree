import sys
import os
import hashlib
from colorama import init, Fore, Back, Style

# Bổ sung đường dẫn hiện tại vào sys.path để import các module nội bộ
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thiết lập encoding UTF-8 cho stdout trên Windows để in ký tự tiếng Việt có dấu
if sys.platform.startswith('win'):
    import io
    sys.stdout.reconfigure(encoding='utf-8')

from merkle_tree.note import Note
from merkle_tree.tree import MerkleTree

# Khởi tạo colorama để hiển thị màu sắc trên Windows Terminal
init(autoreset=True)

def print_header(title: str):
    """In tiêu đề nổi bật với màu sắc."""
    print("\n" + "=" * 80)
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(80)}")
    print("=" * 80)

def print_tree_recursive(tree: MerkleTree, level: int, index: int, prefix: str = "", is_left: bool = True, is_root: bool = False):
    """Vẽ cây Merkle đệ quy dạng sơ đồ cây ASCII có màu sắc."""
    node_val = tree.tree[level][index]
    
    # Định dạng hiển thị nút băm
    if node_val == tree.EMPTY_LEAF:
        node_str = f"{Fore.LIGHTBLACK_EX}[Empty Leaf]"
    else:
        node_str = f"{Fore.YELLOW}[{node_val[:8]}...{node_val[-8:]}]"
        
    if is_root:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}Root ── {node_str}")
    else:
        connector = f"{Fore.BLUE}├── " if is_left else f"{Fore.BLUE}└── "
        direction_label = f"{Fore.WHITE}L" if is_left else f"{Fore.WHITE}R"
        print(f"{prefix}{connector}{direction_label}: {node_str}")
        prefix += f"{Fore.BLUE}│   " if is_left else "    "
        
    if level > 0:
        # Đệ quy xuống các nút con
        print_tree_recursive(tree, level - 1, 2 * index, prefix, is_left=True)
        print_tree_recursive(tree, level - 1, 2 * index + 1, prefix, is_left=False)

def show_tree(tree: MerkleTree):
    """Hiển thị sơ đồ cây Merkle hiện tại."""
    print(f"\n{Fore.GREEN}{Style.BRIGHT}--- Sơ đồ Cây Merkle (Độ sâu: {tree.depth}) ---")
    print_tree_recursive(tree, tree.depth, 0, is_root=True)
    print(f"Tổng số lá đã chèn: {Fore.YELLOW}{tree.next_index}/{tree.max_leaves}")
    print(f"Gốc Merkle hiện tại: {Fore.YELLOW}{tree.get_root()}\n")

def run_scripted_demo():
    """Chạy kịch bản mô phỏng tự động từng bước."""
    print_header("MÔ PHỎNG HỆ THỐNG CAM KẾT COIN & CÂY MERKLE ZEROCASH")
    
    # 1. Khởi tạo cây Merkle độ sâu 3 (tối đa 8 lá)
    print(f"{Fore.GREEN}[Bước 1] Khởi tạo cây Merkle độ sâu d=3 (chứa tối đa 8 Note Commitments)")
    tree = MerkleTree(depth=3)
    show_tree(tree)
    
    # 2. Tạo các note ngẫu nhiên đại diện cho các giao dịch coin
    print(f"{Fore.GREEN}[Bước 2] Sinh các Note coin ngẫu nhiên và tính cam kết (Note Commitments)")
    users = ["Alice", "Bob", "Charlie", "David"]
    values = [50, 100, 25, 80]
    notes = []
    commitments = []
    
    for user, val in zip(users, values):
        note = Note.generate_random(owner_pk=f"pk_{user.lower()}", value=val)
        notes.append(note)
        cm = note.compute_commitment()
        commitments.append(cm)
        print(f"\n* {Fore.MAGENTA}{user} gửi {val} coin:")
        print(f"  - Note: {note}")
        print(f"  - Commitment (cm): {Fore.YELLOW}{cm}")
        
    # 3. Chèn các commitments vào Cây Merkle
    print(f"\n{Fore.GREEN}[Bước 3] Chèn các Note Commitments vào cây Merkle...")
    for idx, cm in enumerate(commitments):
        tree.insert(cm)
        print(f"  - Đã chèn commitment {idx} (của {users[idx]}) vào lá thứ {idx}")
        
    show_tree(tree)
    
    # 4. Tạo chứng minh đường dẫn Merkle (Membership Proof) cho Bob (index 1)
    target_idx = 1
    target_user = users[target_idx]
    target_note = notes[target_idx]
    target_cm = commitments[target_idx]
    
    print(f"{Fore.GREEN}[Bước 4] Tạo chứng minh đường dẫn (Merkle Path/Membership Proof) cho {target_user}")
    proof = tree.get_proof(target_idx)
    
    print(f"\nChứng minh Merkle cho lá thứ {target_idx} (của {target_user}):")
    for i, step in enumerate(proof):
        print(f"  - Tầng {i}: Anh em bên {Fore.CYAN}{step['direction']:<5} {Fore.YELLOW}{step['hash'][:16]}...")
        
    # 5. Xác thực chứng minh thành viên cho Bob
    print(f"\n{Fore.GREEN}[Bước 5] Xác minh chứng minh thành viên (Membership Verification)")
    current_root = tree.get_root()
    is_valid = MerkleTree.verify_proof(target_cm, proof, current_root)
    
    print(f"  - Coin commitment cần xác minh: {Fore.YELLOW}{target_cm}")
    print(f"  - Gốc Merkle Root kỳ vọng:     {Fore.YELLOW}{current_root}")
    if is_valid:
        print(f"  - Kết quả: {Fore.GREEN}{Style.BRIGHT}XÁC MINH THÀNH CÔNG! Coin này thuộc về tập ẩn danh (Anonymity Set).")
    else:
        print(f"  - Kết quả: {Fore.RED}{Style.BRIGHT}XÁC MINH THẤT BẠI!")
        
    # 6. Thử nghiệm giả mạo hoặc thay đổi dữ liệu
    print(f"\n{Fore.GREEN}[Bước 6] Thử nghiệm tấn công / Giả mạo dữ liệu")
    
    # Kịch bản A: Bob thay đổi mệnh giá Note của mình lên 1000 coin trước khi tạo proof
    print(f"\n{Fore.RED}Kịch bản A: Bob sửa đổi Note từ {values[target_idx]} coin thành 1000 coin và tự tính commitment giả mạo:")
    fake_note = Note(owner_pk=target_note.owner_pk, value=1000, rho=target_note.rho, r=target_note.r)
    fake_cm = fake_note.compute_commitment()
    print(f"  - Note giả: {fake_note}")
    print(f"  - Commitment giả: {Fore.YELLOW}{fake_cm}")
    
    is_fake_valid = MerkleTree.verify_proof(fake_cm, proof, current_root)
    if is_fake_valid:
        print(f"  - Kết quả: {Fore.RED}{Style.BRIGHT}NGUY HIỂM! Chấp nhận note giả mạo.")
    else:
        print(f"  - Kết quả: {Fore.GREEN}{Style.BRIGHT}TỪ CHỐI THÀNH CÔNG! Note giả mạo bị phát hiện do mã băm commitment không khớp.")
        
    # Kịch bản B: Sử dụng một proof bị sửa đổi mã băm
    print(f"\n{Fore.RED}Kịch bản B: Kẻ tấn công sửa đổi một mã băm trung gian trong Merkle Proof:")
    tampered_proof = [step.copy() for step in proof]
    tampered_proof[0]['hash'] = hashlib.sha256(b"tampered_data").hexdigest()
    
    is_tampered_valid = MerkleTree.verify_proof(target_cm, tampered_proof, current_root)
    if is_tampered_valid:
        print(f"  - Kết quả: {Fore.RED}{Style.BRIGHT}NGUY HIỂM! Chấp nhận proof bị sửa đổi.")
    else:
        print(f"  - Kết quả: {Fore.GREEN}{Style.BRIGHT}TỪ CHỐI THÀNH CÔNG! Proof bị sửa đổi không thể dẫn tới gốc Merkle Root chính xác.")
        
    return tree

def run_interactive_simulation(tree: MerkleTree):
    """Vào chế độ CLI tương tác để người dùng tự do khám phá."""
    notes_list = []
    
    while True:
        print_header("MENU TƯƠNG TÁC CÂY MERKLE")
        print("1. Tạo Coin Note mới và chèn vào cây")
        print("2. Xem sơ đồ cây Merkle hiện tại")
        print("3. Tạo và xác minh Membership Proof cho một index")
        print("4. Chạy lại kịch bản mô phỏng tự động ban đầu")
        print("5. Thoát")
        
        choice = input(f"\n{Fore.CYAN}Nhập lựa chọn của bạn (1-5): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            if tree.next_index >= tree.max_leaves:
                print(f"{Fore.RED}Lỗi: Cây Merkle đã đầy ({tree.max_leaves}/{tree.max_leaves} lá)!")
                continue
                
            owner = input("Nhập tên người sở hữu (ví dụ: Alice): ").strip()
            if not owner:
                owner = "Anonymous"
            try:
                val_str = input("Nhập giá trị coin (số nguyên dương): ").strip()
                val = int(val_str)
                if val < 0:
                    print(f"{Fore.RED}Lỗi: Giá trị coin phải là số nguyên dương.")
                    continue
            except ValueError:
                print(f"{Fore.RED}Lỗi: Vui lòng nhập số nguyên hợp lệ.")
                continue
                
            note = Note.generate_random(owner_pk=f"pk_{owner.lower()}", value=val)
            cm = note.compute_commitment()
            
            try:
                idx = tree.insert(cm)
                notes_list.append((idx, note, cm))
                print(f"\n{Fore.GREEN}Đã chèn thành công!")
                print(f"  - Chỉ số lá (Index): {Fore.YELLOW}{idx}")
                print(f"  - Note tạo ra: {note}")
                print(f"  - Commitment (cm): {Fore.YELLOW}{cm}")
            except Exception as e:
                print(f"{Fore.RED}Lỗi chèn vào cây: {e}")
                
        elif choice == '2':
            show_tree(tree)
            
        elif choice == '3':
            try:
                idx_str = input(f"Nhập chỉ số lá cần kiểm tra (0-{tree.max_leaves-1}): ").strip()
                idx = int(idx_str)
                if idx < 0 or idx >= tree.max_leaves:
                    print(f"{Fore.RED}Lỗi: Vui lòng nhập chỉ số trong khoảng [0, {tree.max_leaves-1}].")
                    continue
            except ValueError:
                print(f"{Fore.RED}Lỗi: Vui lòng nhập số nguyên hợp lệ.")
                continue
                
            # Tạo proof
            try:
                proof = tree.get_proof(idx)
                leaf_hash = tree.tree[0][idx]
                root = tree.get_root()
                
                print(f"\n{Fore.CYAN}--- Membership Proof cho Lá thứ {idx} ---")
                print(f"Mã băm lá: {Fore.YELLOW}{leaf_hash}")
                for i, step in enumerate(proof):
                    print(f"  Tầng {i}: Anh em bên {Fore.MAGENTA}{step['direction']:<5} {Fore.YELLOW}{step['hash']}")
                
                print(f"\n{Fore.CYAN}--- Thực hiện Xác minh ---")
                is_valid = MerkleTree.verify_proof(leaf_hash, proof, root)
                print(f"Gốc Merkle Root hiện tại: {Fore.YELLOW}{root}")
                if is_valid:
                    if leaf_hash == MerkleTree.EMPTY_LEAF:
                        print(f"Kết quả: {Fore.GREEN}{Style.BRIGHT}XÁC MINH HỢP LỆ (Lá trống - EMPTY).")
                    else:
                        print(f"Kết quả: {Fore.GREEN}{Style.BRIGHT}XÁC MINH THÀNH CÔNG! Coin thuộc về cây.")
                else:
                    print(f"Kết quả: {Fore.RED}{Style.BRIGHT}XÁC MINH THẤT BẠI!")
                    
                # Cho phép người dùng thử phá hoại
                tamper = input(f"\n{Fore.YELLOW}Bạn muốn thử giả mạo mã băm lá này để kiểm tra hệ thống bảo mật không? (y/n): ").strip().lower()
                if tamper == 'y':
                    fake_hash = hashlib.sha256(b"fake_coin").hexdigest()
                    is_fake_valid = MerkleTree.verify_proof(fake_hash, proof, root)
                    print(f"Mã băm giả: {Fore.YELLOW}{fake_hash}")
                    if is_fake_valid:
                        print(f"Kết quả: {Fore.RED}{Style.BRIGHT}LỖI HỆ THỐNG! Đã chấp nhận coin giả.")
                    else:
                        print(f"Kết quả: {Fore.GREEN}{Style.BRIGHT}TỪ CHỐI THÀNH CÔNG! Coin giả đã bị phát hiện.")
            except Exception as e:
                print(f"{Fore.RED}Lỗi trong quá trình tạo/xác minh proof: {e}")
                
        elif choice == '4':
            tree = run_scripted_demo()
            
        elif choice == '5':
            print(f"\n{Fore.GREEN}Cảm ơn bạn đã trải nghiệm mô phỏng Cây Merkle Zerocash. Tạm biệt!")
            break
        else:
            print(f"{Fore.RED}Lựa chọn không hợp lệ, vui lòng thử lại.")

if __name__ == "__main__":
    # Chạy demo tự động trước
    tree = run_scripted_demo()
    
    # Cho phép người dùng tiếp tục khám phá thủ công qua giao diện CLI tương tác
    input(f"\n{Fore.CYAN}Nhấn Enter để chuyển sang chế độ CLI tương tác...")
    run_interactive_simulation(tree)
