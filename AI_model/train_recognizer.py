# AI_model/train_recognizer.py
# (Đã cập nhật logic để huấn luyện "thêm" - incremental VÀ THÊM LOG)

import os
import cv2
import glob
import numpy as np
import sys

# --- Import các module của bạn ---
try:
    from Recognition.torch_recognizer import TorchRecognizer
    from Recognition.embedding_extractor import EmbeddingExtractor 
    from utils.data_augmentor import augment_image 
except ImportError as e:
    print(f"Lỗi import: {e}. Đảm bảo các file (torch_recognizer, embedding_extractor, data_augmentor) tồn tại.")
    exit()

# --- Cấu hình ---
DATASET_PATH = r"E:\AI-facial-recognition-system-for-roll-call\dataset"
MODEL_PATH = "models/face_prototypes.pth"

# -----------------

# 1. Khởi tạo model Embedding (FaceNet)
extractor = EmbeddingExtractor(model_name='vggface2')
print("Tải model Embedding (PyTorch FaceNet) thành công.")

# 2. Khởi tạo model Recognition (Torch Prototypes)
recognizer = TorchRecognizer()

# 3. TẢI MODEL CŨ (NẾU CÓ)
if os.path.exists(MODEL_PATH):
    try:
        recognizer.load(MODEL_PATH)
    except Exception as e:
        print(f"Lỗi khi tải model cũ '{MODEL_PATH}': {e}. Sẽ huấn luyện lại từ đầu.")
else:
    print("Không tìm thấy model cũ. Sẽ tạo model mới.")


# --- Chuẩn bị dữ liệu (CHỈ CHO NGƯỜI MỚI) ---
new_embeddings = [] 
new_names = []      

print("Bắt đầu quét dataset (có Data Augmentation)...")

total_original_images = 0

for person_name in os.listdir(DATASET_PATH):
    person_dir = os.path.join(DATASET_PATH, person_name)
    if not os.path.isdir(person_dir):
        continue
        
    # 4. KIỂM TRA XEM NGƯỜI NÀY ĐÃ CÓ TRONG MODEL CHƯA
    if person_name in recognizer.prototypes:
        print(f"[INFO] Bỏ qua: {person_name} (đã được huấn luyện).")
        continue
        
    print(f"[INFO] Đang xử lý NGƯỜI MỚI: {person_name}")
    
    image_paths = glob.glob(os.path.join(person_dir, "*.*"))
    
    # [LOGGING] Lấy tổng số ảnh để đếm
    total_images_for_person = len(image_paths)
    if total_images_for_person == 0:
        print(f"-> Không tìm thấy ảnh nào cho {person_name}. Bỏ qua.")
        continue

    image_count_for_person = 0 
    original_image_count = 0   
    
    for image_path in image_paths:
        try:
            original_cropped_face = cv2.imread(image_path)
            if original_cropped_face is None:
                print(f"\n   -> [LỖI] Không thể đọc: {os.path.basename(image_path)}") # Thêm \n
                continue
            
            original_image_count += 1
            
            # 5. [MỚI] DÒNG LOG CHI TIẾT
            # 'end="\r"' giúp dòng này tự cập nhật tại chỗ
            print(f"   -> [Ảnh {original_image_count}/{total_images_for_person}] Đang augment & trích xuất: {os.path.basename(image_path)}     ", end="\r")

            augmented_face_list = augment_image(original_cropped_face, brightness_value=50)

            for face_version in augmented_face_list:
                embedding = extractor.get_embedding(face_version)
                
                if embedding is not None:
                
                    # ===============================================
                    # [MỚI] PRINT EMBEDDING (CHỈ CHẠY 1 LẦN)
                    if original_image_count == 1:
                        print(f"\n   -> [DEBUG] Kieu du lieu embedding: {type(embedding)}")
                        print(f"   -> [DEBUG] Kich thuoc (shape): {embedding.shape}")
                        
                        # [SỬA] Bỏ comment dòng này để in đầy đủ
                        print(f"   -> [DEBUG] FULL EMBEDDING (512 GIA TRI): \n{embedding}\n")
                    new_embeddings.append(embedding)
                    new_names.append(person_name)
                    image_count_for_person += 1
            
        except Exception as e:
            # Thêm \n để ngắt dòng log \r ở trên
            print(f"\n   -> [LỖI] Xử lý ảnh {image_path}: {e}") 

    # [LOGGING] Thêm một dòng print() trống để ngắt dòng \r
    print() 
    print(f"-> Đã xử lý {original_image_count} ảnh gốc, tạo ra {image_count_for_person} đặc trưng cho {person_name}.")
    total_original_images += original_image_count

# 6. HUẤN LUYỆN (NẾU CÓ NGƯỜI MỚI) VÀ LƯU LẠI
if len(new_embeddings) == 0:
    print("\nKhông có người mới nào để huấn luyện. Model đã được cập nhật.")
else:
    print(f"\nTổng cộng xử lý {total_original_images} ảnh gốc (từ người mới).")
    print(f"Tổng cộng trích xuất được {len(new_embeddings)} đặc trưng mới (do augmentation).")
    
    recognizer.train(np.array(new_embeddings), new_names)
    
    print("\n--- HOÀN TẤT HUẤN LUYỆN (THÊM) ---")

if not os.path.exists("models"):
    os.makedirs("models")
    
# 7. LƯU LẠI TOÀN BỘ MODEL (CŨ + MỚI)
try:
    recognizer.save(MODEL_PATH)
    print(f"Đã lưu prototypes (PyTorch) tại: {MODEL_PATH}")
    print(f"Tổng số người trong model: {len(recognizer.prototypes)}")
except Exception as e:
    print(f"LỖI NGHIÊM TRỌNG KHI LƯU MODEL: {e}")