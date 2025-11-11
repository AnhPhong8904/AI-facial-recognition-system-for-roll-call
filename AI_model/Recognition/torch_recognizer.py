# AI_model/Recognition/torch_recognizer.py

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
        self.prototypes = {}

    def train(self, embeddings, labels):
        """
        Huấn luyện model bằng cách tính "prototype" (centroid) 
        cho mỗi người và chuyển sang Tensor.
        
        Args:
            embeddings (list or np.array): Danh sách tất cả vector đặc trưng.
            labels (list of str): Danh sách các nhãn (tên) tương ứng.
        """
        print("Đang tính toán prototypes (PyTorch)...")
        self.prototypes = {}
        unique_labels = set(labels)
        
        for name in unique_labels:
            # 1. Lấy tất cả embedding của người này
            # (Chúng ta cần chuyển embeddings sang Tensor để tính toán)
            
            # Tạo list các tensor
            embeddings_for_person = [
                torch.tensor(e) for e, lbl in zip(embeddings, labels) if lbl == name
            ]
            
            # 2. Xếp chồng các tensor thành 1 tensor [N, 512]
            embeddings_stack = torch.stack(embeddings_for_person).to(self.device)
            
            # 3. Tính trung bình cộng (prototype)
            # dim=0 -> tính trung bình theo cột
            prototype = torch.mean(embeddings_stack, dim=0)
            
            # 4. Lưu lại
            self.prototypes[name] = prototype
            print(f"-> Đã tính xong prototype cho: {name}")

        print("Huấn luyện (tính prototype) hoàn tất.")

    def predict(self, embedding, similarity_threshold=0.6):
        """
        Dự đoán tên từ một vector đặc trưng (PyTorch Tensor)
        dựa trên Cosine Similarity.
        
        Args:
            embedding (np.array): Vector đặc trưng (từ extractor).
            similarity_threshold (float): Ngưỡng tương đồng. 
                                          Nếu độ tương đồng cao nhất VẪN < ngưỡng,
                                          coi là "Unknown".
        
        Returns:
            tuple: (tên_dự_đoán, độ_tương_đồng_cao_nhất)
        """
        if embedding is None or not self.prototypes:
            return "Unknown", 0.0

        max_similarity = -1.0
        identity = "Unknown"
        
        # Chuyển embedding (numpy) sang tensor
        current_embedding = torch.tensor(embedding, dtype=torch.float32).to(self.device)

        # So sánh với tất cả các prototypes đã lưu
        for name, proto in self.prototypes.items():
            
            # Tính Cosine Similarity
            # Cần .unsqueeze(0) để biến [512] -> [1, 512] cho hàm F.cosine_similarity
            similarity = F.cosine_similarity(current_embedding.unsqueeze(0), 
                                             proto.unsqueeze(0))
            
            similarity = similarity.item() # Lấy giá trị float từ tensor
            
            if similarity > max_similarity:
                max_similarity = similarity
                identity = name
        
        # Đây là bước quan trọng:
        # Nếu độ giống cao nhất VẪN thấp hơn ngưỡng
        if max_similarity < similarity_threshold:
            identity = "Unknown"
            
        return identity, max_similarity

    def save(self, model_path):
        """Lưu prototypes (dict) ra file."""
        print(f"Đang lưu prototypes (PyTorch) tới {model_path}")
        # Dùng torch.save để lưu
        torch.save(self.prototypes, model_path)

    def load(self, model_path):
        """Tải prototypes (dict) từ file."""
        print(f"Đang tải prototypes (PyTorch) từ {model_path}")
        # Dùng torch.load và map về device
        self.prototypes = torch.load(model_path, map_location=self.device)
        print("Tải model hoàn tất.")