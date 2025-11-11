# detect_logger.py
import logging

logging.basicConfig(
    filename='logs/detect.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def log_detection(num_faces):
    logging.info(f"Detected {num_faces} faces.")
