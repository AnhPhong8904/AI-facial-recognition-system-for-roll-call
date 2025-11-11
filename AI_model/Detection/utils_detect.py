# utils_detect.py
import cv2

def draw_warning_text(frame, text, color=(0, 0, 255)):
    h, w = frame.shape[:2]
    cv2.putText(frame, text, (w // 10, h - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)
    return frame




