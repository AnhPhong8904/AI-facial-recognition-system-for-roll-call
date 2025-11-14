# AI_model/train_recognizer.py
# (Đã cập nhật logic để huấn luyện "thêm" - incremental)

import os
import cv2
import glob
import numpy as np
import sys

# --- Import các module của bạn ---
try:
    # [QUAN TRỌNG] Đảm bảo bạn đang import TorchRecognizer
    from Recognition.torch_recognizer import TorchRecognizer
    from Recognition.embedding_extractor import EmbeddingExtractor 
    from utils.data_augmentor import augment_image 
except ImportError as e:
    print(f"Lỗi import: {e}. Đảm bảo các file (torch_recognizer, embedding_extractor, data_augmentor) tồn tại.")
    exit()

# --- Cấu hình ---
DATASET_PATH = r"E:\AI-facial-recognition-system-for-roll-call\dataset"
MODEL_PATH = "models/face_prototypes.pth" # <-- File lưu của TorchRecognizer

# -----------------

# 1. Khởi tạo model Embedding (FaceNet)
extractor = EmbeddingExtractor(model_name='vggface2')
print("Tải model Embedding (PyTorch FaceNet) thành công.")

# 2. Khởi tạo model Recognition (Torch Prototypes)
recognizer = TorchRecognizer()

# 3. [MỚI] TẢI MODEL CŨ (NẾU CÓ)
# recognizer.prototypes (là 1 dict) sẽ được điền dữ liệu cũ vào
if os.path.exists(MODEL_PATH):
    try:
        recognizer.load(MODEL_PATH)
    except Exception as e:
        print(f"Lỗi khi tải model cũ '{MODEL_PATH}': {e}. Sẽ huấn luyện lại từ đầu.")
        # Nếu file bị hỏng, cứ để recognizer.prototypes là dict rỗng
else:
    print("Không tìm thấy model cũ. Sẽ tạo model mới.")


# --- Chuẩn bị dữ liệu (CHỈ CHO NGƯỜI MỚI) ---
new_embeddings = [] # Chỉ lưu embedding của người mới
new_names = []      # Chỉ lưu tên của người mới

print("Bắt đầu quét dataset (có Data Augmentation)...")

total_original_images = 0 # Đếm tổng số ảnh gốc (của người mới)

for person_name in os.listdir(DATASET_PATH):
    person_dir = os.path.join(DATASET_PATH, person_name)
    if not os.path.isdir(person_dir):
        continue
        
    # 4. [MỚI] KIỂM TRA XEM NGƯỜI NÀY ĐÃ CÓ TRONG MODEL CHƯA
    if person_name in recognizer.prototypes:
        print(f"[INFO] Bỏ qua: {person_name} (đã được huấn luyện).")
        continue
        
    # Nếu không, đây là người mới:
    print(f"[INFO] Đang xử lý NGƯỜI MỚI: {person_name}")
    
    image_paths = glob.glob(os.path.join(person_dir, "*.*"))
    
    image_count_for_person = 0 # Đếm tổng số đặc trưng (đã augment)
    original_image_count = 0   # Đếm số ảnh gốc
    
    for image_path in image_paths:
        try:
            original_cropped_face = cv2.imread(image_path)
            if original_cropped_face is None:
                print(f"Không thể đọc: {image_path}")
                continue
            
            original_image_count += 1
            
            # Chạy Augmentation
            augmented_face_list = augment_image(original_cropped_face, brightness_value=50)

            for face_version in augmented_face_list:
                embedding = extractor.get_embedding(face_version)
                
                if embedding is not None:
                    # THÊM VÀO DANH SÁCH "MỚI"
                    new_embeddings.append(embedding)
                    new_names.append(person_name)
                    image_count_for_person += 1
            
        except Exception as e:
            print(f"Lỗi xử lý ảnh {image_path}: {e}")

    print(f"-> Đã xử lý {original_image_count} ảnh gốc, tạo ra {image_count_for_person} đặc trưng cho {person_name}.")
    total_original_images += original_image_count

# 5. [MỚI] HUẤN LUYỆN (NẾU CÓ NGƯỜI MỚI) VÀ LƯU LẠI
if len(new_embeddings) == 0:
    print("\nKhông có người mới nào để huấn luyện. Model đã được cập nhật.")
else:
    print(f"\nTổng cộng xử lý {total_original_images} ảnh gốc (từ người mới).")
    print(f"Tổng cộng trích xuất được {len(new_embeddings)} đặc trưng mới (do augmentation).")
    
    # [QUAN TRỌNG] Hàm train bây giờ sẽ THÊM vào self.prototypes
    recognizer.train(np.array(new_embeddings), new_names)
    
    print("\n--- HOÀN TẤT HUẤN LUYỆN (THÊM) ---")

if not os.path.exists("models"):
    os.makedirs("models")
    
# 6. [MỚI] LƯU LẠI TOÀN BỘ MODEL (CŨ + MỚI)
# (Ngay cả khi không có gì mới, việc lưu lại đảm bảo file không bị lỗi)
try:
    recognizer.save(MODEL_PATH)
    print(f"Đã lưu prototypes (PyTorch) tại: {MODEL_PATH}")
    print(f"Tổng số người trong model: {len(recognizer.prototypes)}")
except Exception as e:
    print(f"LỖI NGHIÊM TRỌNG KHI LƯU MODEL: {e}")