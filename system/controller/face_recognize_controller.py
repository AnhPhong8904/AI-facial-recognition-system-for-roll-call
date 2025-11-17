import sys
import os
import cv2
import numpy as np
from datetime import datetime, timedelta # [SỬA] Thêm import datetime
from PyQt5.QtWidgets import QListWidgetItem, QMessageBox # [MỚI] Thêm QMessageBox
from PyQt5.QtCore import Qt, QDateTime, QTimer
from PyQt5.QtGui import QImage, QPixmap, QColor # [SỬA] Thêm import QColor

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
    get_available_sessions, get_session_info, get_roster, mark_present,
    finalize_attendance  # [MỚI] Import hàm chốt sổ
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
        self.student_roster = {} # Dict lưu trạng thái (Vắng/Có mặt/Đi muộn)
        
        # [SỬA] Thêm biến lưu trữ thời gian
        self.session_start_time = None
        self.session_end_time = None
        self.session_finalized = False

        # [MỚI] Thêm độ trễ điểm danh để giảm nhận nhầm
        self.attendance_delay_seconds = 5
        self.pending_recognitions = {}
        self.auto_finalize_timer = QTimer()
        self.auto_finalize_timer.setInterval(60_000)  # kiểm tra mỗi phút
        self.auto_finalize_timer.timeout.connect(self.check_auto_finalize)
        
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
        
        # [MỚI] KẾT NỐI NÚT CHỐT SỔ
        # Bạn *phải* thêm một nút tên là 'finalize_btn' (hoặc tên khác) 
        # vào file ui/face_recognize.py
        # Sau đó bỏ comment dòng dưới đây:
        self.view.finalize_btn.clicked.connect(self.handle_finalize_session)

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

    # [SỬA LẠI HÀM NÀY]

    def handle_session_selected(self, index):
        """Khi người dùng chọn một buổi học từ ComboBox."""
        self.current_session_id = self.view.subject_cb.itemData(index)
        
        if self.current_session_id is None:
            self.view.clear_class_info()
            self.view.open_btn.setEnabled(False)
            self.student_roster = {}
            self.populate_roster_lists() 
            # [SỬA] Reset thời gian
            self.session_start_time = None
            self.session_end_time = None
            self.session_finalized = False
            self.pending_recognitions.clear()
            self.auto_finalize_timer.stop()
        else:
            try:
                # 1. Cập nhật thông tin buổi học
                session_details = get_session_info(self.current_session_id)
                if session_details:
                    # [SỬA] Nhận 7 giá trị từ service
                    (ten_lop, ten_mon, thoi_gian, giang_vien, phong, 
                     start_time_val, end_time_val) = session_details
                    
                    self.view.update_class_info(ten_lop, ten_mon, thoi_gian, giang_vien, phong)
                    
                    # ---------------------------------------------------------
                    # [SỬA LỖI] Chuyển đổi sang datetime.time
                    # Bất kể CSDL trả về str hay time, chúng ta sẽ xử lý
                    # ---------------------------------------------------------
                    if isinstance(start_time_val, str):
                        # Nếu là string (ví dụ: '07:00:00' hoặc '07:00:00.000000')
                        # Cắt bỏ phần milisecond nếu có
                        time_str = start_time_val.split('.')[0]
                        self.session_start_time = datetime.strptime(time_str, '%H:%M:%S').time()
                    else:
                        # Nếu đã là datetime.time (trường hợp lý tưởng)
                        self.session_start_time = start_time_val
                        
                    if isinstance(end_time_val, str):
                        time_str = end_time_val.split('.')[0]
                        self.session_end_time = datetime.strptime(time_str, '%H:%M:%S').time()
                    else:
                        self.session_end_time = end_time_val
                    # ---------------------------------------------------------
                    
                else:
                    # [SỬA] Reset thời gian nếu không tìm thấy
                    self.session_start_time = None
                    self.session_end_time = None
                
                # 2. Lấy danh sách sinh viên
                self.student_roster = get_roster(self.current_session_id)
                
                # 3. Cập nhật danh sách "Có mặt" / "Vắng"
                self.populate_roster_lists()
                self.pending_recognitions.clear()
                
                # 4. Cho phép mở camera
                if self.recognizer: # Chỉ cho mở nếu AI đã tải thành công
                    self.view.open_btn.setEnabled(True)
                
            except Exception as e:
                self.view.update_notice(f"Lỗi khi tải danh sách lớp: {e}", "error")
            else:
                self.session_finalized = False
                self.restart_auto_finalize_timer()

    def restart_auto_finalize_timer(self):
        """Khởi động/ dừng timer auto chốt dựa trên dữ liệu hiện tại."""
        self.auto_finalize_timer.stop()
        if self.session_end_time and self.current_session_id is not None:
            self.auto_finalize_timer.start()

    def check_auto_finalize(self):
        """Tự động chốt sổ nếu đã quá 15 phút sau giờ kết thúc."""
        if (
            self.session_finalized
            or self.current_session_id is None
            or self.session_end_time is None
        ):
            return
        
        today = datetime.today().date()
        buffer_end = datetime.combine(today, self.session_end_time) + timedelta(minutes=15)
        if datetime.now() >= buffer_end:
            self.trigger_finalize(auto=True)

    def populate_roster_lists(self):
        """
        Cập nhật 2 danh sách Vắng/Có mặt từ self.student_roster.
        [SỬA] Thêm logic hiển thị 'Đi muộn'
        """
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
                    # [SỬA] Phân biệt 'Có mặt' và 'Đi muộn'
                    if student['status'] == 'Đi muộn':
                        item.setText(f"{item_text} (Đi muộn)")
                        item.setForeground(QColor("#C05000")) # Màu cam đậm
                    else: # 'Có mặt'
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
        self.pending_recognitions.clear()
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
                    ready, remaining = self.check_attendance_delay(ma_sv)
                    if ready:
                        self.mark_student_present(ma_sv, cropped_face_img)
                        color = (0, 255, 0) # Xanh lá
                        text = f"{ma_sv} (Đang ghi...)"
                    else:
                        color = (0, 165, 255) # Cam
                        text = f"{ma_sv} (Waiting {remaining:.1f}s)"
                else:
                    # Đã điểm danh rồi
                    color = (0, 255, 0) # Xanh lá
                    text = f"{ma_sv} (Check-in Successfull)"
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
        """
        Hàm quan trọng: Kiểm tra thời gian, Cập nhật CSDL, State, và UI.
        [SỬA] Toàn bộ hàm này được viết lại để xử lý logic thời gian.
        """
        # Đảm bảo xóa trạng thái chờ
        self.pending_recognitions.pop(ma_sv, None)
        # 1. Kiểm tra điều kiện đầu vào
        if self.current_session_id is None or self.session_start_time is None:
            self.view.update_notice("Lỗi: Chưa chọn buổi học hoặc thiếu thông tin giờ.", "error")
            return
            
        student_data = self.student_roster[ma_sv]
        student_id = student_data["id"]
        
        # 2. Xử lý logic thời gian
        today = datetime.today().date()
        now = datetime.now()
        
        # Tạo đối tượng datetime đầy đủ
        start_datetime = datetime.combine(today, self.session_start_time)
        grace_end_datetime = start_datetime + timedelta(minutes=15)
        end_datetime = datetime.combine(today, self.session_end_time)
        
        status_to_set = None
        notice_message = ""
        notice_level = "info"

        if now > end_datetime:
            notice_message = f"❌ Đã hết giờ điểm danh (Kết thúc lúc {self.session_end_time.strftime('%H:%M')})."
            notice_level = "error"
        elif now >= start_datetime and now <= grace_end_datetime:
            status_to_set = "Có mặt"
        elif now > grace_end_datetime and now <= end_datetime:
            status_to_set = "Đi muộn"
        else: # now < start_datetime
            notice_message = f"ℹ️ Chưa đến giờ điểm danh (Bắt đầu {self.session_start_time.strftime('%H:%M')})."
            notice_level = "warning"

        # 3. Nếu không hợp lệ (quá sớm/quá muộn), chỉ thông báo và dừng
        if status_to_set is None:
            self.view.update_notice(notice_message, notice_level)
            return

        # 4. Nếu hợp lệ -> Ghi vào CSDL
        success, message = mark_present(
            self.current_session_id, student_id, ma_sv, status_to_set
        )
        
        if success:
            # 5. Cập nhật State (Bộ nhớ)
            self.student_roster[ma_sv]["status"] = status_to_set
            
            # 6. Cập nhật UI
            notice_suffix = f" ({status_to_set})"
            self.view.update_notice(f"✅ {student_data['name']} ({ma_sv}) đã điểm danh!{notice_suffix}", "success")
            
            # Cập nhật box "Gần nhất"
            timestamp = now.strftime("%H:%M:%S")
            
            # Chuyển ảnh crop (OpenCV) sang QImage
            face_rgb = cv2.cvtColor(cropped_face_img, cv2.COLOR_BGR2RGB)
            h, w, ch = face_rgb.shape
            q_face_img = QImage(face_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            
            self.view.update_last_person_info(ma_sv, student_data['name'], timestamp, q_face_img)
            
            # 7. Cập nhật danh sách (chuyển từ Vắng -> Có mặt/Đi muộn)
            self.populate_roster_lists()
        else:
            self.view.update_notice(f"❌ Lỗi khi ghi danh {ma_sv}: {message}", "error")

    def check_attendance_delay(self, ma_sv):
        """
        Đảm bảo nhận diện ổn định một vài giây trước khi điểm danh.
        Trả về (ready: bool, remaining_seconds: float)
        """
        now = datetime.now()
        first_seen = self.pending_recognitions.get(ma_sv)

        if first_seen is None:
            self.pending_recognitions[ma_sv] = now
            return False, float(self.attendance_delay_seconds)

        elapsed = (now - first_seen).total_seconds()
        if elapsed >= self.attendance_delay_seconds:
            self.pending_recognitions.pop(ma_sv, None)
            return True, 0.0

        remaining = self.attendance_delay_seconds - elapsed
        return False, max(0.0, remaining)

    # ==========================================================
    # [MỚI] HÀM XỬ LÝ CHỐT SỔ (GHI VẮNG)
    # ==========================================================
    
    def handle_finalize_session(self):
        """Người dùng chủ động nhấn nút chốt sổ."""
        self.trigger_finalize(auto=False)

    def trigger_finalize(self, auto=False):
        """
        Thực thi logic chốt sổ (thủ công hoặc tự động).
        auto=True sẽ bỏ qua hộp thoại xác nhận và chạy khi đủ điều kiện.
        """
        
        # 1. Kiểm tra đã chọn buổi học chưa
        if self.current_session_id is None:
            if not auto:
                self.view.update_notice("Vui lòng chọn buổi học trước khi chốt sổ.", "error")
                QMessageBox.warning(self.view, "Lỗi", "Vui lòng chọn buổi học trước khi chốt sổ.")
            return

        # 2. Đảm bảo camera đã tắt
        if self.cap and self.cap.isOpened():
            if auto:
                self.handle_close_camera()
            else:
                self.view.update_notice("Vui lòng tắt camera trước khi chốt sổ.", "warning")
                QMessageBox.warning(self.view, "Cảnh báo", "Vui lòng tắt camera trước khi chốt sổ.")
                return
        
        if self.session_finalized:
            if not auto:
                self.view.update_notice("Buổi học này đã được chốt trước đó.", "info")
            return

        # 3. Hỏi xác nhận người dùng
        if not auto:
            confirm_reply = QMessageBox.question(
                self.view,
                "Xác nhận Chốt sổ",
                "Bạn có chắc chắn muốn chốt sổ buổi học này không?\n\n"
                "Thao tác này sẽ tự động ghi 'Vắng' cho tất cả sinh viên "
                "chưa được điểm danh (có mặt/đi muộn).\n\n"
                "Bạn chỉ nên thực hiện việc này khi buổi học đã kết thúc.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if confirm_reply == QMessageBox.No:
                self.view.update_notice("Thao tác chốt sổ đã bị hủy.", "info")
                return
        else:
            self.view.update_notice("Tự động chốt sổ: Đã quá 15 phút sau giờ kết thúc.", "warning")

        # 4. Nếu người dùng đồng ý -> Gọi service
        try:
            progress_msg = "Đang chốt sổ, vui lòng chờ..."
            if auto:
                progress_msg = "Hệ thống đang tự động chốt sổ..."
            self.view.update_notice(progress_msg, "warning")
            
            success, message, count = finalize_attendance(self.current_session_id)
            
            if success:
                self.session_finalized = True
                self.auto_finalize_timer.stop()
                success_notice = f"✅ {message}"
                self.view.update_notice(success_notice, "success")
                if auto:
                    # Với auto, hiển thị thông báo nhỏ để GV biết
                    self.view.update_notice(
                        f"Tự động chốt sổ thành công. Đã ghi vắng cho {count} sinh viên.",
                        "success"
                    )
                else:
                    QMessageBox.information(
                        self.view,
                        "Hoàn tất",
                        f"Chốt sổ thành công.\nĐã ghi vắng cho {count} sinh viên."
                    )
                
                # Cập nhật lại danh sách (dù không ảnh hưởng UI, nhưng cho đúng)
                # self.student_roster = get_roster(self.current_session_id)
                # self.populate_roster_lists()
            else:
                self.view.update_notice(f"❌ Lỗi khi chốt sổ: {message}", "error")
                QMessageBox.critical(self.view, "Lỗi", f"Không thể chốt sổ.\nLỗi: {message}")
        
        except Exception as e:
            self.view.update_notice(f"❌ Lỗi nghiêm trọng khi chốt sổ: {e}", "error")
            QMessageBox.critical(self.view, "Lỗi nghiêm trọng", f"Đã xảy ra lỗi: {e}")