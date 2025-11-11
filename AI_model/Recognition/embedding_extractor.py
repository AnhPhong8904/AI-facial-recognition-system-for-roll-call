# AI_model/Recognition/embedding_extractor.py

import torch
from facenet_pytorch import InceptionResnetV1
import cv2
import numpy as np
from torchvision import transforms

class EmbeddingExtractor:
    def __init__(self, model_name='vggface2'):
        """
        Tải model pre-trained của FaceNet (InceptionResnetV1) bằng PyTorch.
        """
        print(f"Đang tải model FaceNet (PyTorch) pre-trained trên {model_name}...")
        
        # 1. Thiết lập device (GPU nếu có)
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        print(f'Đang chạy trên device: {self.device}')

        # 2. Tải model
        # .eval() để chuyển model sang chế độ dự đoán (tắt dropout, v.v.)
        self.model = InceptionResnetV1(pretrained=model_name).eval().to(self.device)

        # 3. Chuẩn bị phép biến đổi (transform)
        # Model này yêu cầu ảnh 160x160 và đã được chuẩn hóa
        self.transform = transforms.Compose([
            transforms.ToPILImage(), # Chuyển đổi numpy array (từ OpenCV) sang PIL Image
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            # Phép chuẩn hóa này là tiêu chuẩn cho InceptionResnetV1
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

    def get_embedding(self, face_image_numpy):
        """
        Trích xuất vector đặc trưng 512-d từ một ảnh khuôn mặt đã được crop.
        
        Args:
            face_image_numpy (numpy.ndarray): Ảnh khuôn mặt (đã crop) từ OpenCV (BGR).
        
        Returns:
            numpy.ndarray: Vector đặc trưng (embedding) 512-d.
        """
        if face_image_numpy is None or face_image_numpy.size == 0:
            return None
            
        try:
            # 1. Chuyển BGR (OpenCV) sang RGB
            face_rgb = cv2.cvtColor(face_image_numpy, cv2.COLOR_BGR2RGB)
            
            # 2. Áp dụng transform (Resize, ToTensor, Normalize)
            face_tensor = self.transform(face_rgb).to(self.device)
            
            # 3. Thêm chiều batch (model yêu cầu [Batch_size, C, H, W])
            # face_tensor.unsqueeze(0) sẽ biến [3, 160, 160] -> [1, 3, 160, 160]
            
            # 4. Tắt tính toán gradient
            with torch.no_grad():
                # Chạy model
                embedding = self.model(face_tensor.unsqueeze(0))
            
            # 5. Chuyển kết quả về CPU, sang numpy array và trả về vector [512,]
            return embedding.cpu().numpy()[0]

        except Exception as e:
            print(f"Lỗi khi trích xuất embedding (PyTorch): {e}")
            return None