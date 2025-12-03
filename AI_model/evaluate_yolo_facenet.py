import os
import sys
import time
import argparse
import csv
from datetime import datetime
from typing import Tuple, List, Dict

import cv2
import numpy as np

# Thư viện vẽ đồ thị
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    print("[WARN] Thiếu thư viện 'matplotlib' hoặc 'seaborn'.")
    sys.exit(1)

def resolve_base_dir() -> str:
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if base_dir not in sys.path:
        sys.path.append(base_dir)
    return base_dir

BASE_DIR = resolve_base_dir()

# Import Detector & Recognizer
from AI_model.Detection.face_detector import FaceDetector
from AI_model.Recognition.embedding_extractor import EmbeddingExtractor
from AI_model.Recognition.torch_recognizer import TorchRecognizer

def iter_image_files(dataset_root: str) -> List[Tuple[str, str]]:
    samples = []
    if not os.path.exists(dataset_root):
        return samples
    for person_name in os.listdir(dataset_root):
        person_dir = os.path.join(dataset_root, person_name)
        if not os.path.isdir(person_dir):
            continue
        for fname in os.listdir(person_dir):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                samples.append((os.path.join(person_dir, fname), person_name))
    return samples

def plot_confusion_matrix(cm_data, labels, output_path, title="Confusion Matrix"):
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm_data, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.xlabel('Dự đoán (Predicted)')
    plt.ylabel('Thực tế (Ground Truth)')
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def calculate_metrics(tp, fp, fn, total_samples):
    """Hàm phụ trợ tính toán các chỉ số"""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    # Accuracy trong ngữ cảnh nhận diện thường là tỷ lệ đoán đúng trên tổng số mẫu thực hiện
    # Ở đây dùng (TP / Total) cho đơn giản và trực quan
    accuracy = tp / total_samples if total_samples > 0 else 0.0
    return precision, recall, f1, accuracy

def evaluate_separate(
    dataset_root: str,
    model_path: str,
    similarity_threshold: float = 0.6,
    max_samples: int = 0,
    output_csv_det: str = "eval_detection.csv",
    output_csv_rec: str = "eval_recognition.csv",
    cm_image: str = "confusion_matrix_rec.png"
) -> None:
    
    if not os.path.exists(dataset_root) or not os.path.exists(model_path):
        print("[ERROR] Sai đường dẫn dataset hoặc model.")
        return

    print("=== CHẠY ĐÁNH GIÁ TÁCH BIỆT (DETECTION vs RECOGNITION) ===")
    
    # 1. Load Data
    samples = iter_image_files(dataset_root)
    if not samples: return
    if max_samples > 0: samples = samples[:max_samples]
    print(f"- Tổng số ảnh: {len(samples)}")

    # 2. Load Models
    print("\n[Init] Đang tải models...")
    detector = FaceDetector()
    extractor = EmbeddingExtractor(model_name="vggface2")
    recognizer = TorchRecognizer()
    recognizer.load(model_path)
    print("Models loaded.\n")

    # --- BIẾN THỐNG KÊ CHO DETECTION (YOLO) ---
    det_total_images = 0
    det_tp = 0              # Tìm thấy mặt (Faces Found)
    det_fn = 0              # Không tìm thấy mặt (No Face)
    det_fp = 0              # Tìm thấy nhưng không phải mặt (Giả định = 0 do không có label box)
    det_times = []          # List thời gian detect

    # --- BIẾN THỐNG KÊ CHO RECOGNITION (FACENET) ---
    rec_processed = 0       # Số khuôn mặt được đưa vào nhận diện
    rec_tp = 0              # Đúng người
    rec_fp = 0              # Nhầm người (A thành B)
    rec_fn = 0              # Nhận thành Unknown hoặc sai ngưỡng
    rec_times = []          # List thời gian extract + predict

    # Confusion Matrix cho Recognition
    gt_labels_set = sorted({label for _, label in samples})
    labels_axis = gt_labels_set + ["Unknown"]
    confusion_dict = {gt: {pred: 0 for pred in labels_axis} for gt in labels_axis}

    print(f"[Run] Bắt đầu xử lý...")

    for idx, (img_path, gt_label) in enumerate(samples, start=1):
        img = cv2.imread(img_path)
        if img is None: continue

        # =================================================
        # PHẦN 1: ĐÁNH GIÁ YOLO (DETECTION)
        # =================================================
        det_total_images += 1
        
        t0_det = time.time()
        detections = detector.detect_faces(img)
        t1_det = time.time()
        
        det_times.append((t1_det - t0_det) * 1000) # ms

        # Logic chọn khuôn mặt tốt nhất
        best_face_crop = None
        
        if len(detections) > 0:
            det_tp += 1 # Coi như là TP vì tìm thấy mặt trong ảnh có mặt
            
            # Tìm box to nhất
            boxes = []
            for det in detections:
                x1, y1, x2, y2 = int(det[0]), int(det[1]), int(det[2]), int(det[3])
                boxes.append((x1, y1, x2, y2))
            
            areas = [max(0, x2 - x1) * max(0, y2 - y1) for (x1, y1, x2, y2) in boxes]
            best_idx = int(np.argmax(areas))
            bx1, by1, bx2, by2 = boxes[best_idx]

            if bx1 < bx2 and by1 < by2:
                best_face_crop = img[by1:by2, bx1:bx2]
        else:
            det_fn += 1 # FN vì có mặt mà không tìm thấy

        # =================================================
        # PHẦN 2: ĐÁNH GIÁ FACENET (RECOGNITION)
        # =================================================
        # Chỉ chạy nếu YOLO đã tìm thấy mặt
        if best_face_crop is not None:
            rec_processed += 1
            
            t0_rec = time.time()
            embedding = extractor.get_embedding(best_face_crop)
            
            predicted_label = "Unknown"
            if embedding is not None:
                pred, sim = recognizer.predict(embedding, similarity_threshold)
                predicted_label = pred
            t1_rec = time.time()
            
            rec_times.append((t1_rec - t0_rec) * 1000) # ms

            # So khớp kết quả
            # Case 1: Đúng người
            if predicted_label == gt_label:
                rec_tp += 1
            # Case 2: Sai người hoặc Unknown
            else:
                if predicted_label == "Unknown":
                    rec_fn += 1 # Đáng lẽ là A nhưng máy bảo không biết (False Negative về mặt nhận dạng ID)
                else:
                    rec_fp += 1 # Đáng lẽ là A nhưng máy bảo là B (False Positive/Misidentification)

            # Update Matrix
            pred_key = predicted_label if predicted_label in labels_axis else "Unknown"
            if gt_label in confusion_dict:
                confusion_dict[gt_label][pred_key] += 1

        if idx % 50 == 0:
            print(f"  > Đã xử lý {idx}/{len(samples)} ảnh...")

    # =================================================
    # TỔNG HỢP VÀ BÁO CÁO
    # =================================================
    
    # --- REPORT 1: YOLO DETECTOR ---
    avg_det_time = np.mean(det_times) if det_times else 0
    det_fps = 1000.0 / avg_det_time if avg_det_time > 0 else 0.0

    # Tính metrics cho Detection
    # Lưu ý: FP=0 là giả định vì không có background image check
    det_p, det_r, det_f1, det_acc = calculate_metrics(det_tp, det_fp, det_fn, det_total_images)
    
    print("\n" + "="*40)
    print(" KẾT QUẢ 1: ĐÁNH GIÁ YOLOv8n-face (Detection)")
    print("="*40)
    print(f"1. Tổng số ảnh đầu vào : {det_total_images}")
    print(f"2. Faces Found (TP)    : {det_tp}")
    print(f"3. Missed Faces (FN)   : {det_fn}")
    print(f"----------------------------------------")
    print(f"4. Precision (Detection): {det_p:.4f} (Giả định FP=0)")
    print(f"5. Recall (Detection)   : {det_r:.4f}")
    print(f"6. F1-Score (Detection) : {det_f1:.4f}")
    print(f"7. Accuracy (Detection) : {det_acc:.4f}")
    print(f"----------------------------------------")
    print(f"8. Tốc độ Detect trung bình: {avg_det_time:.2f} ms/ảnh ({det_fps:.2f} FPS)")
    
    # Lưu CSV Detection
    with open(output_csv_det, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Timestamp", "Total", "TP", "FN", "Precision", "Recall", "F1", "Accuracy", "Avg_Time_ms", "FPS"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            det_total_images, det_tp, det_fn,
            f"{det_p:.4f}".replace('.',','), 
            f"{det_r:.4f}".replace('.',','),
            f"{det_f1:.4f}".replace('.',','),
            f"{det_acc:.4f}".replace('.',','),
            f"{avg_det_time:.2f}".replace('.',','),
            f"{det_fps:.2f}".replace('.',',')
        ])
        print(f"[Saved] Detection log saved to {output_csv_det}")


    # --- REPORT 2: FACENET RECOGNIZER ---
    avg_rec_time = np.mean(rec_times) if rec_times else 0
    rec_fps = 1000.0 / avg_rec_time if avg_rec_time > 0 else 0.0

    # Tính metrics cho Recognition
    rec_p, rec_r, rec_f1, rec_acc = calculate_metrics(rec_tp, rec_fp, rec_fn, rec_processed)
    
    print("\n" + "="*40)
    print(" KẾT QUẢ 2: ĐÁNH GIÁ FACENET (Recognition)")
    print("="*40)
    print(f"(Chỉ đánh giá trên {rec_processed} khuôn mặt đã được YOLO cắt ra)")
    print(f"1. Đúng người (TP)       : {rec_tp}")
    print(f"2. Nhầm người (FP)       : {rec_fp}")
    print(f"3. Không nhận ra (FN)    : {rec_fn}")
    print(f"----------------------------------------")
    print(f"4. Precision (Recog)     : {rec_p:.4f}")
    print(f"5. Recall (Recog)        : {rec_r:.4f}")
    print(f"6. F1-Score (Recog)      : {rec_f1:.4f}")
    print(f"7. Accuracy (Recog)      : {rec_acc:.4f}")
    print(f"----------------------------------------")
    print(f"8. Tốc độ Recog trung bình: {avg_rec_time:.2f} ms/mặt ({rec_fps:.2f} FPS)")

    # Lưu CSV Recognition
    with open(output_csv_rec, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Timestamp", "Processed", "TP", "FP", "FN", "Precision", "Recall", "F1", "Accuracy", "Avg_Time_ms", "FPS"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            rec_processed, rec_tp, rec_fp, rec_fn,
            f"{rec_p:.4f}".replace('.',','),
            f"{rec_r:.4f}".replace('.',','),
            f"{rec_f1:.4f}".replace('.',','),
            f"{rec_acc:.4f}".replace('.',','),
            f"{avg_rec_time:.2f}".replace('.',','),
            f"{rec_fps:.2f}".replace('.',',')
        ])
        print(f"[Saved] Recognition log saved to {output_csv_rec}")

    # Vẽ Confusion Matrix cho Recognition
    if cm_image:
        matrix_data = []
        for gt in labels_axis:
            row = [confusion_dict[gt][pred] for pred in labels_axis]
            matrix_data.append(row)
        plot_confusion_matrix(matrix_data, labels_axis, cm_image, title=f"FaceNet Matrix (Thresh={similarity_threshold})")
        print(f"[Saved] Confusion Matrix saved to {cm_image}")

def main():
    default_dataset = os.path.join(BASE_DIR, "dataset")
    default_model = os.path.join(BASE_DIR, "system", "models", "face_prototypes.pth")
    
    parser = argparse.ArgumentParser(description="Đánh giá riêng biệt YOLO và FaceNet")
    parser.add_argument("--dataset", type=str, default=default_dataset)
    parser.add_argument("--model", type=str, default=default_model)
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument("--max-samples", type=int, default=0)
    
    args = parser.parse_args()
    
    evaluate_separate(
        dataset_root=args.dataset,
        model_path=args.model,
        similarity_threshold=args.threshold,
        max_samples=args.max_samples
    )

if __name__ == "__main__":
    main()