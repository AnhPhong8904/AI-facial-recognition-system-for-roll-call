# face_detector.py
import cv2
from ultralytics import YOLO
from .config_detect import DETECTION_CONFIG
from .utils_detect import (
    draw_warning_text
    
)
import time


class FaceDetector:
    def __init__(self):
        cfg = DETECTION_CONFIG
        self.model_type = cfg["model_type"]
        self.conf_threshold = cfg["conf_threshold"]
        self.max_faces = cfg["max_faces"]
        self.stable_frames = cfg["stable_frames"]
        self.model = YOLO(cfg["model_path"])

        # Biến ổn định phát hiện
        self.no_face_frames = 0
        self.last_detect_time = time.time()

    def detect_faces(self, frame):
        results = self.model(frame, verbose=False)
        boxes = []
        for r in results:
            for box in r.boxes:
                if box.conf[0] >= self.conf_threshold:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    boxes.append((x1, y1, x2, y2))
        return boxes[:self.max_faces]

    def process_frame(self, frame):
        boxes = self.detect_faces(frame)

        if len(boxes) == 0:
            self.no_face_frames += 1
            if self.no_face_frames >= self.stable_frames:
                frame = draw_warning_text(frame, "Can not detect face!")
        else:
            self.no_face_frames = 0
            for (x1, y1, x2, y2) in boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
              

        return frame


# if __name__ == "__main__":
#     cap = cv2.VideoCapture(r"E:\AI-facial-recognition-system-for-roll-call\video\bacgiang.mp4")
#     detector = FaceDetector()

#     cv2.namedWindow("Face Detection", cv2.WINDOW_NORMAL)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame = cv2.flip(frame, 1)
#         frame = detector.process_frame(frame)

#         height, width = frame.shape[:2]
#         win_w, win_h = cv2.getWindowImageRect("Face Detection")[2:]
#         scale = min(win_w / width, win_h / height)
#         new_w, new_h = int(width * scale), int(height * scale)
#         resized = cv2.resize(frame, (new_w, new_h))
#         top = (win_h - new_h) // 2
#         bottom = (win_h - new_h + 1) // 2
#         left = (win_w - new_w) // 2
#         right = (win_w - new_w + 1) // 2

#         canvas = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(0, 0, 0))
#         cv2.imshow("Face Detection", canvas)

#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
