# config_detect.py
DETECTION_CONFIG = {
    "model_type": "yolo",                  # "yolo"
    "model_path": "AI_model/weights/yolov8n-face.pt",    # đường dẫn model
    "conf_threshold": 0.6,                 # ngưỡng phát hiện
    "img_size": 640,                       # kích thước resize ảnh
    "max_faces": 30,                        # giới hạn số khuôn mặt
    "stable_frames": 5                     # số frame cần ổn định
}
