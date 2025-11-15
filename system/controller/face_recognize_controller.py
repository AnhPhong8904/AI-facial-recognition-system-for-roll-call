import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QImage, QPixmap

# -------------------------------------------------------------------
# [QUAN TRỌNG] Thêm thư mục gốc vào sys.path
# -------------------------------------------------------------------
# Giả định file này ở system/controller/face_recognize_controller.py
# Cần lùi 3 cấp để về thư mục gốc (AI-FACIAL-RECOGNITION-SYSTEM-FOR-ROLL-CALL)
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)
except NameError:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)

# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
# Import View
# [SỬA] Sửa lại tên file và tên class cho đúng
from ui.face_recognize import FaceRecognizeWindow

# Import các model AI (từ thư mục AI_model)
from AI_model.Detection.face_detector import FaceDetector
from AI_model.Recognition.embedding_extractor import EmbeddingExtractor
from AI_model.Recognition.torch_recognizer import TorchRecognizer

# [SỬA] Import các hàm service thật (tên file bạn đã cung cấp)
from model.face_recognize_service import (
    get_available_sessions, get_session_info, get_roster, mark_present
)

# Tên class FaceRecognizeController đã đúng
class FaceRecognizeController:
    def __init__(self, on_close_callback):
        # [SỬA] Sửa lại tên class View
        self.view = FaceRecognizeWindow()
        self.on_close_callback = on_close_callback

        # Biến trạng thái
        self.cap = None
        self.current_session_id = None
        self.student_roster = {} # Dict lưu trạng thái (Vắng/Có mặt)
        
        # Ngưỡng nhận diện (cần tinh chỉnh)
        self.similarity_threshold = 0.6 

        # Tải AI Models (Nặng)
        self.load_ai_models()

        # Kết nối tín hiệu
        self.connect_signals()
        
        # Tải dữ liệu CSDL (Nhẹ)
        self.load_available_sessions()

    def load_ai_models(self):
        """Tải các model AI một lần khi khởi động."""
        self.view.update_notice("Đang tải model AI, vui lòng chờ...", "warning")
        try:
            # 1. Tải model YOLO (Detection)
            print("Đang tải model YOLO (Detection)...")
            self.detector = FaceDetector() 

            # 2. Tải model Embedding (PyTorch FaceNet)
            print("Đang tải model Embedding (PyTorch FaceNet)...")
            self.extractor = EmbeddingExtractor(model_name='vggface2')

            # 3. Tải model Recognition (Torch Prototypes)
            print("Đang tải model Recognition (PyTorch Prototypes)...")
            self.recognizer = TorchRecognizer()
            
            # [QUAN TRỌNG] Đường dẫn này phải trỏ đến file .pth đã huấn luyện
            MODEL_PATH = os.path.join(BASE_DIR, "system", "models", "face_prototypes.pth")
            
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Không tìm thấy file model tại: {MODEL_PATH}\n"
                                        "Vui lòng chạy 'Huấn luyện Model' trong cửa sổ Quản lý Sinh viên.")
            
            self.recognizer.load(MODEL_PATH)
            print(f"Đã tải {len(self.recognizer.prototypes)} khuôn mặt từ model.")
            
            self.view.update_notice("Tải model AI thành công.", "success")
        
        except Exception as e:
            self.detector = None
            self.recognizer = None
            self.extractor = None
            print(f"Lỗi nghiêm trọng khi tải model AI: {e}")
            self.view.update_notice(f"Lỗi nghiêm trọng khi tải model AI:\n{e}", "error")

    def connect_signals(self):
        """Kết nối các nút bấm và sự kiện."""
        self.view.back_btn.clicked.connect(self.handle_close_window)
        self.view.subject_cb.currentIndexChanged.connect(self.handle_session_selected)
        self.view.open_btn.clicked.connect(self.handle_open_camera)
        self.view.close_btn.clicked.connect(self.handle_close_camera)
        
        # Kết nối timer (tạo trong View) với hàm update_frame
        self.view.timer_camera.timeout.connect(self.update_frame)

    def show(self):
        """Hiển thị cửa sổ và tải lại danh sách buổi học (có thể có buổi mới)."""
        self.load_available_sessions()
        self.view.show()

    def load_available_sessions(self):
        """Tải các buổi học hôm nay vào ComboBox."""
        try:
            # Gọi hàm service trực tiếp
            sessions = get_available_sessions()
            self.view.subject_cb.clear()
            self.view.subject_cb.addItem("--- Vui lòng chọn buổi học ---", None)
            for (session_id, session_text) in sessions:
                self.view.subject_cb.addItem(session_text, session_id)
        except Exception as e:
            self.view.update_notice(f"Lỗi khi tải danh sách buổi học: {e}", "error")

    def handle_session_selected(self, index):
        """Khi người dùng chọn một buổi học từ ComboBox."""
        self.current_session_id = self.view.subject_cb.itemData(index)
        
        if self.current_session_id is None:
            self.view.clear_class_info()
            self.view.open_btn.setEnabled(False)
            self.student_roster = {}
            self.populate_roster_lists() 
        else:
            try:
                # 1. Cập nhật thông tin buổi học
                session_details = get_session_info(self.current_session_id)
                if session_details:
                    (ten_lop, ten_mon, thoi_gian, giang_vien, phong) = session_details
                    self.view.update_class_info(ten_lop, ten_mon, thoi_gian, giang_vien, phong)
                
                # 2. Lấy danh sách sinh viên
                self.student_roster = get_roster(self.current_session_id)
                
                # 3. Cập nhật danh sách "Có mặt" / "Vắng"
                self.populate_roster_lists()
                
                # 4. Cho phép mở camera
                if self.recognizer: # Chỉ cho mở nếu AI đã tải thành công
                    self.view.open_btn.setEnabled(True)
                
            except Exception as e:
                self.view.update_notice(f"Lỗi khi tải danh sách lớp: {e}", "error")

    def populate_roster_lists(self):
        """Cập nhật 2 danh sách Vắng/Có mặt từ self.student_roster."""
        self.view.present_list_widget.clear()
        self.view.absent_list_widget.clear()
        
        present_count = 0
        absent_count = 0
        
        if not self.student_roster:
            total = 0
        else:
            total = len(self.student_roster)
            # (Sắp xếp theo MA_SV để danh sách ổn định)
            sorted_ma_sv = sorted(self.student_roster.keys())
            
            for ma_sv in sorted_ma_sv:
                student = self.student_roster[ma_sv]
                item_text = f"{ma_sv} - {student['name']}"
                item = QListWidgetItem(item_text)
                
                if student['status'] == 'Vắng':
                    self.view.absent_list_widget.addItem(item)
                    absent_count += 1
                else:
                    item.setForeground(Qt.darkGreen)
                    self.view.present_list_widget.addItem(item)
                    present_count += 1
                
        self.view.attendance_label.setText(
            f"Đã điểm danh: {present_count} | Vắng: {absent_count} | Tổng: {total}"
        )

    # -------------------------------------------------------------------
    # HÀM XỬ LÝ CAMERA VÀ AI
    # -------------------------------------------------------------------

    def handle_open_camera(self):
        """Bật camera và khởi động QTimer."""
        try:
            self.cap = cv2.VideoCapture(0) # Thử webcam 0
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(1) # Thử webcam 1
                
            if not self.cap.isOpened():
                raise IOError("Không thể mở webcam (đã thử 0 và 1).")
            
            self.view.timer_camera.start(30) # 30ms ~ 33 FPS
            self.view.set_camera_buttons_state(is_running=True)
            self.view.update_notice("Camera đã mở. Bắt đầu nhận diện...", "info")
            self.view.clear_last_person_info()
            
        except Exception as e:
            self.view.update_notice(f"Lỗi camera: {e}", "error")

    def handle_close_camera(self):
        """Tắt camera và QTimer."""
        self.view.timer_camera.stop()
        if self.cap:
            self.cap.release()
        self.cap = None
        self.view.update_frame_on_ui(None) # Hiển thị "CAMERA TẮT"
        self.view.set_camera_buttons_state(is_running=False)
        self.view.update_notice("Camera đã tắt.", "warning")

    def handle_close_window(self):
        """Dọn dẹp trước khi đóng cửa sổ."""
        self.handle_close_camera()
        self.view.close()
        self.on_close_callback()

    def update_frame(self):
        """Vòng lặp chính: Lấy frame -> Nhận diện -> Hiển thị."""
        if not self.cap or not self.recognizer:
            return

        ret, frame = self.cap.read()
        if not ret:
            print("Lỗi đọc frame.")
            return

        # Lật ảnh (webcam thường bị ngược)
        if isinstance(self.cap.get(cv2.CAP_PROP_AUTOFOCUS), float): 
            frame = cv2.flip(frame, 1)

        # 1. Phát hiện (Detect)
        detections = self.detector.detect_faces(frame)
        
        display_frame = frame.copy()
        
        # 2. Trích xuất (Extract) & Nhận diện (Recognize)
        for box in detections:
            (x1, y1, x2, y2) = [int(coord) for coord in box[:4]]
            
            # Đảm bảo box hợp lệ
            if x1 >= x2 or y1 >= y2:
                continue
                
            cropped_face = frame[y1:y2, x1:x2]
            
            embedding = self.extractor.get_embedding(cropped_face)
            
            if embedding is not None:
                ma_sv, similarity = self.recognizer.predict(embedding, self.similarity_threshold)
                
                # Xử lý logic điểm danh và vẽ
                self.process_recognition(ma_sv, similarity, cropped_face, (x1, y1, x2, y2), display_frame)

        # 3. Hiển thị (Display)
        # Chuyển đổi BGR (OpenCV) sang RGB (QImage)
        frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        self.view.update_frame_on_ui(q_image)

    def process_recognition(self, ma_sv, similarity, cropped_face_img, box, display_frame):
        """
        Xử lý logic điểm danh và vẽ lên 'display_frame'.
        """
        (x1, y1, x2, y2) = box
        color = (0, 0, 255) # Đỏ (Mặc định là Unknown/Lỗi)
        text = f"Unknown (Sim: {similarity:.2f})"

        if ma_sv != "Unknown":
            # Kiểm tra xem SV này có trong danh sách lớp không
            if ma_sv in self.student_roster:
                student_data = self.student_roster[ma_sv]
                
                # [QUAN TRỌNG] Kiểm tra xem SV đã điểm danh CHƯA
                if student_data["status"] == "Vắng":
                    # --- ĐIỂM DANH THÀNH CÔNG ---
                    # (Hàm này sẽ cập nhật CSDL, UI, và state)
                    self.mark_student_present(ma_sv, cropped_face_img)
                    color = (0, 255, 0) # Xanh lá
                    text = f"{ma_sv} (OK)"
                else:
                    # Đã điểm danh rồi
                    color = (0, 255, 0) # Xanh lá
                    text = f"{ma_sv} (Da check-in)"
            else:
                # Nhận diện được, nhưng không có trong lớp
                color = (0, 255, 255) # Vàng
                text = f"{ma_sv} (KHONG TRONG LOP)"
        
        # Vẽ box
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        # Vẽ text
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(display_frame, (x1, y1 - text_h - 15), (x1 + text_w, y1 - 10), color, -1)
        cv2.putText(display_frame, text, (x1, y1 - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    def mark_student_present(self, ma_sv, cropped_face_img):
        """Hàm quan trọng: Cập nhật CSDL, State, và UI."""
        if self.current_session_id is None:
            return # Không điểm danh nếu chưa chọn buổi
            
        student_data = self.student_roster[ma_sv]
        student_id = student_data["id"]
        
        # 1. Cập nhật CSDL
        # Gọi hàm service trực tiếp
        success, message = mark_present(self.current_session_id, student_id, ma_sv)
        
        if success:
            # 2. Cập nhật State (Bộ nhớ)
            self.student_roster[ma_sv]["status"] = "Có mặt"
            
            # 3. Cập nhật UI
            self.view.update_notice(f"✅ {student_data['name']} ({ma_sv}) đã điểm danh!", "success")
            
            # Cập nhật box "Gần nhất"
            now = QDateTime.currentDateTime()
            timestamp = now.toString("hh:mm:ss")
            
            # Chuyển ảnh crop (OpenCV) sang QImage
            face_rgb = cv2.cvtColor(cropped_face_img, cv2.COLOR_BGR2RGB)
            h, w, ch = face_rgb.shape
            q_face_img = QImage(face_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            
            self.view.update_last_person_info(ma_sv, student_data['name'], timestamp, q_face_img)
            
            # 4. Cập nhật danh sách (chuyển từ Vắng -> Có mặt)
            self.populate_roster_lists()
        else:
            self.view.update_notice(f"❌ Lỗi khi ghi danh {ma_sv}: {message}", "error")