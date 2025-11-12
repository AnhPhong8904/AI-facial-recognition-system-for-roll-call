# AI_model/train_recognizer.py

import os
import cv2
import glob
import numpy as np

# --- Import các module của bạn ---
from Detection.face_detector import FaceDetector 
from Recognition.embedding_extractor import EmbeddingExtractor
# [SỬA] Import class KNNRecognizer
from Recognition.torch_recognizer import TorchRecognizer

# --- Cấu hình ---
DATASET_PATH = r"E:\AI-facial-recognition-system-for-roll-call\dataset"
# [SỬA] Quay lại 2 file model
MODEL_PATH = "models/face_prototypes.pth"

# -----------------

# 1. Khởi tạo model YOLO
try:
    yolo_detector = FaceDetector()
    print("Tải model YOLO (Detection) thành công.")
except Exception as e:
    print(f"Lỗi khi tải FaceDetector: {e}")
    exit()

# 2. Khởi tạo model Embedding (PyTorch FaceNet)
extractor = EmbeddingExtractor(model_name='vggface2')

# 3. Khởi tạo model Recognition (KNN)
# [SỬA] Dùng class KNNRecognizer, n_neighbors=5 (hoặc 1, 3 tùy bạn)
recognizer = TorchRecognizer()

# (Phần code trích xuất embedding từ dataset giữ nguyên... 
# ...từ dòng "Chuẩn bị dữ liệu" đến "print(f'-> Đã xử lý {image_count} ảnh cho {person_name}.')")
# ...
known_embeddings = []
known_names = []

print("Bắt đầu trích xuất đặc trưng từ dataset...")

for person_name in os.listdir(DATASET_PATH):
    person_dir = os.path.join(DATASET_PATH, person_name)
    if not os.path.isdir(person_dir):
        continue
        
    print(f"[INFO] Đang xử lý: {person_name}")
    
    image_paths = glob.glob(os.path.join(person_dir, "*.*")) # Lấy mọi file ảnh
    
    image_count = 0
    for image_path in image_paths:
        try:
            image = cv2.imread(image_path)
            if image is None:
                print(f"Không thể đọc: {image_path}")
                continue
            
            detections = yolo_detector.detect_faces(image)
            
            if len(detections) != 1:
                print(f"Cảnh báo: {image_path} - Tìm thấy {len(detections)} khuôn mặt. Bỏ qua.")
                continue

            box = detections[0] 
            (x1, y1, x2, y2) = [int(coord) for coord in box[:4]] 
            
            cropped_face = image[y1:y2, x1:x2]
            
            embedding = extractor.get_embedding(cropped_face)
            
            if embedding is not None:
                known_embeddings.append(embedding)
                known_names.append(person_name)
                image_count += 1
            
        except Exception as e:
            print(f"Lỗi xử lý ảnh {image_path}: {e}")

    print(f"-> Đã xử lý {image_count} ảnh cho {person_name}.")

# (Phần code huấn luyện và lưu model)
if len(known_embeddings) == 0:
    print("Không có dữ liệu nào được trích xuất. Dừng chương trình.")
else:
    print(f"Tổng cộng trích xuất được {len(known_embeddings)} đặc trưng.")
    
    # Huấn luyện KNN
    recognizer.train(np.array(known_embeddings), known_names)
    
    if not os.path.exists("models"):
        os.makedirs("models")
        
    # Lưu model
    # [SỬA] Lưu 2 file
    recognizer.save(MODEL_PATH)
    
    print("\n--- HOÀN TẤT HUẤN LUYỆN ---")
    print(f"Đã lưu prototypes (PyTorch) tại: {MODEL_PATH}")