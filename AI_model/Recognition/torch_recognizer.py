# AI_model/Recognition/torch_recognizer.py
# (Đã sửa: xóa 1 dòng trong hàm train)

import torch
import torch.nn.functional as F

class TorchRecognizer:
    def __init__(self):
        """
        Khởi tạo bộ nhận diện 100% PyTorch
        """
        # Thiết lập device
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        
        # self.prototypes sẽ lưu các vector trung tâm (centroids)
        # Dạng: { 'ten_nguoi': tensor_trung_tam }
        self.prototypes = {} # <-- Dòng này ở đây là ĐÚNG

    def train(self, embeddings, labels):
        """
        Huấn luyện model bằng cách tính "prototype" (centroid) 
        CHO CÁC NHÃN MỚI và THÊM vào dictionary.
        
        Args:
            embeddings (list or np.array): Danh sách tất cả vector đặc trưng (CỦA NGƯỜI MỚI).
            labels (list of str): Danh sách các nhãn (tên) tương ứng (CỦA NGƯỜI MỚI).
        """
        print("Đang tính toán prototypes (PyTorch)...")
        # self.prototypes = {} # <-- DÒNG NÀY ĐÃ BỊ XÓA
        
        unique_labels = set(labels)
        
        for name in unique_labels:
            # 1. Lấy tất cả embedding của người này
            embeddings_for_person = [
                torch.tensor(e) for e, lbl in zip(embeddings, labels) if lbl == name
            ]
            
            # 2. Xếp chồng các tensor thành 1 tensor [N, 512]
            embeddings_stack = torch.stack(embeddings_for_person).to(self.device)
            
            # 3. Tính trung bình cộng (prototype)
            prototype = torch.mean(embeddings_stack, dim=0)
            
            # 4. Lưu lại (hoặc GHI ĐÈ nếu tên đã tồn tại)
            self.prototypes[name] = prototype
            print(f"-> Đã tính/cập nhật xong prototype cho: {name}")

        print("Huấn luyện (tính prototype) hoàn tất.")

    def predict(self, embedding, similarity_threshold=0.6):
        """
        Dự đoán tên từ một vector đặc trưng (PyTorch Tensor)
        dựa trên Cosine Similarity.
        
        (Hàm này giữ nguyên, không thay đổi)
        """
        if embedding is None or not self.prototypes:
            return "Unknown", 0.0

        max_similarity = -1.0
        identity = "Unknown"
        
        current_embedding = torch.tensor(embedding, dtype=torch.float32).to(self.device)

        for name, proto in self.prototypes.items():
            similarity = F.cosine_similarity(current_embedding.unsqueeze(0), 
                                             proto.unsqueeze(0))
            similarity = similarity.item()
            
            if similarity > max_similarity:
                max_similarity = similarity
                identity = name
        
        if max_similarity < similarity_threshold:
            identity = "Unknown"
            
        return identity, max_similarity

    def save(self, model_path):
        """Lưu prototypes (dict) ra file. (Giữ nguyên)"""
        print(f"Đang lưu prototypes (PyTorch) tới {model_path}")
        torch.save(self.prototypes, model_path)

    def load(self, model_path):
        """Tải prototypes (dict) từ file. (Giữ nguyên)"""
        print(f"Đang tải prototypes (PyTorch) từ {model_path}")
        self.prototypes = torch.load(model_path, map_location=self.device)
        print(f"Tải model hoàn tất. (Đã tải {len(self.prototypes)} người)")