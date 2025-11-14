# AI_model/main_webcam.py

import cv2
import numpy as np

# --- Import các module của bạn ---
from Detection.face_detector import FaceDetector 
from Recognition.embedding_extractor import EmbeddingExtractor 
# [SỬA] Import class KNNRecognizer
from Recognition.torch_recognizer import TorchRecognizer

# --- Cấu hình ---
# [SỬA] Quay lại 2 file model
MODEL_PATH = r"E:\AI-facial-recognition-system-for-roll-call\AI_model\models\face_prototypes.pth"


# [SỬA] Đây là NGƯỠNG KHOẢNG CÁCH
# Với L2/FaceNet, ngưỡng này thường quanh 0.9 - 1.0. 
# 0.9 là một điểm khởi đầu tốt (chặt chẽ hơn)
SIMILARITY_THRESHOLD = 0.6

# 1. Tải model YOLO
print("Đang tải model YOLO (Detection)...")
yolo_detector = FaceDetector() 

# 2. Tải model Embedding (PyTorch)
print("Đang tải model Embedding (PyTorch FaceNet)...")
extractor = EmbeddingExtractor(model_name='vggface2')

# 3. Tải model Recognition (KNN)
print("Đang tải model Recognition (PyTorch Prototypes)...")
recognizer = TorchRecognizer()
try:
    recognizer.load(MODEL_PATH)
    print("Tải model (prototypes) thành công.")
except FileNotFoundError:
    print(f"LỖI: Không tìm thấy file model tại '{MODEL_PATH}'.")
    exit()

print("[INFO] Đã tải xong model. Bắt đầu chạy webcam/video...")

# video_path = r"D:\AI-facial-recognition-system-for-roll-call\video\theanh.mp4"
cap = cv2.VideoCapture(0) # Dùng webcam
# cap = cv2.VideoCapture(r"D:\AI-facial-recognition-system-for-roll-call\video\haiduong.mp4") # Dùng video

if not cap.isOpened():
    print("Lỗi: Không thể mở webcam/video.")
    exit()

cv2.namedWindow("Face Recognition (KNN + Distance)", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kết thúc video hoặc lỗi đọc frame.")
        break
    
    if isinstance(cap.get(cv2.CAP_PROP_AUTOFOCUS), float): 
        frame = cv2.flip(frame, 1)

    detections = yolo_detector.detect_faces(frame)

    for box in detections:
        (x1, y1, x2, y2) = box
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        
        if x1 >= x2 or y1 >= y2:
            continue
            
        cropped_face = frame[y1:y2, x1:x2]
        embedding = extractor.get_embedding(cropped_face) # Lấy embedding (numpy)
        # --- Bước 3: Nhận diện (KNN + Distance) ---
        if embedding is not None:
            # [SỬA] Hàm predict giờ trả về (tên, độ_tương_đồng)
            name, similarity = recognizer.predict(embedding, similarity_threshold=SIMILARITY_THRESHOLD)
            
            # --- Bước 4: Hiển thị kết quả ---
            # Hiển thị khoảng cách (distance)
            text = f"{name} (Sim: {similarity:.2f})"
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            
            # (Phần code vẽ vời giữ nguyên)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x1, y1 - text_h - 15), (x1 + text_w, y1 - 10), color, -1)
            cv2.putText(frame, text, (x1, y1 - 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
    cv2.imshow("Face Recognition (PyTorch Cosine-Sim)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()