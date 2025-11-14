# AI_model/collect_data.py

import os
import cv2
import time
import sys  # <--- BẮT BUỘC import sys

# --- Import module của bạn ---
# (Đảm bảo đường dẫn import này đúng khi chạy file từ thư mục gốc)
try:
    from Detection.face_detector import FaceDetector 
except ImportError:
    # Xử lý trường hợp chạy file này trực tiếp (để test)
    # Thêm thư mục gốc vào Python Path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Detection.face_detector import FaceDetector 

# --- Cấu hình ---
# [QUAN TRỌNG] Đảm bảo đường dẫn này GIỐNG HỆT với file train_recognizer.py
DATASET_PATH = r"E:\AI-facial-recognition-system-for-roll-call\dataset"
TARGET_IMAGES = 50 # Số lượng ảnh cần thu thập

# --- 1. Lấy thông tin người mới TỪ THAM SỐ DÒNG LỆNH ---
if len(sys.argv) != 2:
    print("Loi: Can cung cap chinh xac 1 ten (hoac ID) lam tham so.")
    print("Vi du su dung (go trong terminal): python AI_model/collect_data.py SV003")
    exit()
    
person_name = sys.argv[1] # Lấy tham số được truyền vào (ví dụ: 'SV003')

if not person_name:
    print("Ten (ma_sv) khong duoc de trong. Thoat chuong trinh.")
    exit()

# --- 2. Tạo thư mục lưu trữ ---
person_dir = os.path.join(DATASET_PATH, person_name)
if not os.path.exists(person_dir):
    os.makedirs(person_dir)
    print(f"Da tao thu muc: {person_dir}")
else:
    print(f"Thu muc da ton tai: {person_dir}")
    print("Anh moi se duoc them vao thu muc nay.")

# --- 3. Khởi tạo model YOLO ---
try:
    yolo_detector = FaceDetector()
    print("Tai model YOLO (Detection) thanh cong.")
except Exception as e:
    print(f"Loi khi tai FaceDetector: {e}")
    exit()

# --- 4. Khởi tạo webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Loi: Khong the mo webcam.")
    exit()

print("\n--- BAT DAU THU THAP DU LIEU ---")
print(f"Doi tuong: {person_name}")
print(f"[HUONG DAN] Nhan 'k' de chup anh.")
print(f"[HUONG DAN] Nhan 'q' de thoat.")

image_count = 0
cv2.namedWindow(f"Thu Thap Du Lieu: {person_name}", cv2.WINDOW_NORMAL)

# --- 5. Vòng lặp chính ---
while image_count < TARGET_IMAGES:
    ret, frame = cap.read()
    if not ret:
        print("Loi doc frame.")
        break
        
    if isinstance(cap.get(cv2.CAP_PROP_AUTOFOCUS), float): 
        frame = cv2.flip(frame, 1) # Lật camera nếu là webcam laptop

    # Tạo một bản sao để vẽ, giữ lại frame gốc để cắt ảnh
    frame_display = frame.copy()
    
    detections = yolo_detector.detect_faces(frame)
    
    # Chỉ xử lý nếu phát hiện ĐÚNG 1 khuôn mặt
    if len(detections) == 1:
        box = detections[0]
        (x1, y1, x2, y2) = [int(coord) for coord in box[:4]]
        
        # Vẽ hộp xung quanh khuôn mặt
        cv2.rectangle(frame_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Hiển thị thông báo
        text = f"Nhan 'k' de chup ({image_count}/{TARGET_IMAGES})"
        cv2.putText(frame_display, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    elif len(detections) > 1:
        cv2.putText(frame_display, "NHIEU KHUON MAT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        cv2.putText(frame_display, "KHONG TIM THAY KHUON MAT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow(f"Thu Thap Du Lieu: {person_name}", frame_display)
    
    key = cv2.waitKey(1) & 0xFF
    
    # --- 6. Xử lý phím bấm ---
    
    # Nhấn 'q' để thoát
    if key == ord('q'):
        print("Da thoat boi nguoi dung.")
        break
        
    # Nhấn 'k' để chụp VÀ chỉ khi có 1 khuôn mặt
    if key == ord('k') and len(detections) == 1:
        # Cắt khuôn mặt từ frame GỐC (không bị vẽ đè)
        cropped_face = frame[y1:y2, x1:x2]
        
        # Tạo tên file duy nhất (ví dụ: SV003_168934572.jpg)
        filename = f"{person_name}_{int(time.time() * 1000)}_{image_count + 1}.jpg"
        save_path = os.path.join(person_dir, filename)
        
        # Lưu ảnh
        cv2.imwrite(save_path, cropped_face)
        print(f"Da luu: {save_path}")
        
        image_count += 1
        
        # Thêm hiệu ứng "chớp" để báo đã chụp
        frame_display[y1:y2, x1:x2] = cv2.bitwise_not(frame_display[y1:y2, x1:x2])
        cv2.imshow(f"Thu Thap Du Lieu: {person_name}", frame_display)
        cv2.waitKey(100) # Đợi 100ms

# --- 7. Dọn dẹp ---
cap.release()
cv2.destroyAllWindows()
print("\n--- HOAN TAT ---")
print(f"Da luu tong cong {image_count} anh cho {person_name} tai:")
print(f"{person_dir}")
print("\nBuoc tiep theo: Chay file 'train_recognizer.py' de cap nhat model.")