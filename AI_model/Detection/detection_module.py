
import cv2
from .face_detector import FaceDetector

class DetectionModule:
    def __init__(self):
        self.detector = FaceDetector()

    def process_frame(self, frame):
        detections = self.detector.detect_faces(frame)

        if len(detections) == 0:
            cv2.putText(frame, "Khong phat hien khuon mat!.", 
                        (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            for (x1, y1, x2, y2) in detections:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        return frame
