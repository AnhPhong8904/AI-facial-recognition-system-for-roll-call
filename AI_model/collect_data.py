# AI_model/collect_data.py
# (ĐÃ CẬP NHẬT: Tự động chụp khi phát hiện 1 khuôn mặt)

import os
import cv2
import time
import sys

# --- Import module của bạn ---
try:
    from Detection.face_detector import FaceDetector 
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Detection.face_detector import FaceDetector 

# --- Cấu hình ---
DATASET_PATH = r"E:\AI-facial-recognition-system-for-roll-call\dataset"
TARGET_IMAGES = 50 # Số lượng ảnh cần thu thập
DELAY_BETWEEN_SHOTS = 0.2 # 0.2 giây (200ms)

# --- 1. Lấy thông tin người mới TỪ THAM SỐ DÒNG LỆNH ---
if len(sys.argv) != 2:
    print("Loi: Can cung cap chinh xac 1 ten (hoac ID) lam tham so.")
    print("Vi du su dung (go trong terminal): python AI_model/collect_data.py SV003")
    exit()
    
person_name = sys.argv[1]

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

print("\n--- BAT DAU THU THAP DU LIEU (TU DONG) ---")
print(f"Doi tuong: {person_name}")
print(f"[HUONG DAN] Dua khuon mat vao trung tam.")
print(f"[HUONG DAN] Script se tu dong chup khi thay 1 mat.")
print(f"[HUONG DAN] Nhan 'q' de thoat.")

image_count = 0
cv2.namedWindow(f"Thu Thap Du Lieu: {person_name}", cv2.WINDOW_NORMAL)

# --- [MỚI] Đếm ngược 5 giây để chuẩn bị ---
print("\nChuan bi trong 5 giay...")
for i in range(5, 0, -1):
    print(f"{i}...")
    
    # Hiển thị frame trong lúc đếm ngược
    ret, frame = cap.read()
    if not ret: continue
    if isinstance(cap.get(cv2.CAP_PROP_AUTOFOCUS), float): 
        frame = cv2.flip(frame, 1)
        
    cv2.putText(frame, f"Bat dau trong: {i}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow(f"Thu Thap Du Lieu: {person_name}", frame)
    cv2.waitKey(1000) # Chờ 1 giây

print("Bat dau chup!")
last_shot_time = time.time() # Theo dõi thời gian

# --- 5. Vòng lặp chính ---
while image_count < TARGET_IMAGES:
    ret, frame = cap.read()
    if not ret:
        print("Loi doc frame.")
        break
        
    if isinstance(cap.get(cv2.CAP_PROP_AUTOFOCUS), float): 
        frame = cv2.flip(frame, 1)

    frame_display = frame.copy()
    detections = yolo_detector.detect_faces(frame)
    
    current_time = time.time()
    can_take_shot = (current_time - last_shot_time) > DELAY_BETWEEN_SHOTS
    
    # --- 6. [MỚI] Logic Tự động chụp ---
    if len(detections) == 1 and can_take_shot:
        box = detections[0]
        (x1, y1, x2, y2) = [int(coord) for coord in box[:4]]
        
        # Cắt khuôn mặt từ frame GỐC
        cropped_face = frame[y1:y2, x1:x2]
        
        # Tạo tên file
        filename = f"{person_name}_{int(time.time() * 1000)}_{image_count + 1}.jpg"
        save_path = os.path.join(person_dir, filename)
        
        # Lưu ảnh
        cv2.imwrite(save_path, cropped_face)
        print(f"Da luu ({image_count + 1}/{TARGET_IMAGES}): {save_path}")
        
        image_count += 1
        last_shot_time = time.time() # Cập nhật thời gian vừa chụp
        
        # Hiệu ứng "chớp" và thông báo
        cv2.rectangle(frame_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        text = f"DA CHUP: {image_count}/{TARGET_IMAGES}"
        cv2.putText(frame_display, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        frame_display[y1:y2, x1:x2] = cv2.bitwise_not(frame_display[y1:y2, x1:x2])

    elif len(detections) > 1:
        cv2.putText(frame_display, "NHIEU KHUON MAT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        cv2.putText(frame_display, "DUA MAT VAO KHUNG HINH", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

    cv2.imshow(f"Thu Thap Du Lieu: {person_name}", frame_display)
    
    # Vẫn cho phép nhấn 'q' để thoát
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Da thoat boi nguoi dung.")
        break

# --- 7. Dọn dẹp ---
cap.release()
cv2.destroyAllWindows()
print("\n--- HOAN TAT ---")
print(f"Da luu tong cong {image_count} anh cho {person_name} tai:")
print(f"{person_dir}")
print("\nBuoc tiep theo: Chay 'Huấn luyện Model' de cap nhat.")