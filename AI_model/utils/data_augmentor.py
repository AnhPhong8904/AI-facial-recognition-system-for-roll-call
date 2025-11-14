# AI_model/utils/data_augmentor.py

import cv2
import numpy as np

def _change_brightness(image, value):
    """
    Thay đổi độ sáng của ảnh một cách an toàn (tránh bị lóa/đen kịt).
    value > 0: Tăng sáng
    value < 0: Giảm sáng
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Chuyển v sang kiểu int để cộng trừ không bị "xoay vòng" (overflow)
    # Sau đó dùng np.clip để giới hạn giá trị trong khoảng 0-255
    v_new = np.clip(v.astype(int) + value, 0, 255).astype(np.uint8)
    
    final_hsv = cv2.merge((h, s, v_new))
    bright_img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return bright_img

def _horizontal_flip(image):
    """Lật ảnh theo chiều ngang."""
    return cv2.flip(image, 1)

def augment_image(image, brightness_value=50):
    """
    Áp dụng một bộ augmentation cơ bản cho ảnh.
    
    Args:
        image (np.array): Ảnh BGR (ảnh gốc đã cắt).
        brightness_value (int): Giá trị để tăng/giảm độ sáng.
        
    Returns:
        list: Một danh sách các ảnh đã được augment,
              bao gồm: [ảnh gốc, ảnh lật, ảnh sáng, ảnh tối].
    """
    augmented_images = []
    
    # 1. Ảnh gốc
    augmented_images.append(image)
    
    # 2. Ảnh lật ngang (mô phỏng góc nhìn khác)
    augmented_images.append(_horizontal_flip(image))
    
    # 3. Ảnh sáng hơn
    augmented_images.append(_change_brightness(image, brightness_value))
    
    # 4. Ảnh tối hơn
    augmented_images.append(_change_brightness(image, -brightness_value))
    
    return augmented_images