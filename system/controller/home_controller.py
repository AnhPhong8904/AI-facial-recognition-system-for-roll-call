import sys
import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal

# -------------------------------------------------------------------
# [QUAN TRỌNG] Thêm thư mục gốc vào sys.path
# -------------------------------------------------------------------
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
# [SỬA] Import View cho đúng
from ui.home import HomeWindow

# [SỬA] ĐÃ XÓA TẤT CẢ IMPORT CONTROLLER CON KHỎI ĐÂY
# (Để tránh lỗi Import vòng lặp)

class HomeController:
    logout_requested = pyqtSignal()
    
    def __init__(self, role, on_logout):
        """
        Khởi tạo controller
        :param role: Vai trò ('Admin' hoặc 'GiangVien')
        :param on_logout: Hàm callback để gọi khi đăng xuất
        """
        self.view = HomeWindow(role) # [SỬA] Dùng HomeView
        self.on_logout_callback = on_logout
        self.user_role = role 
        
        # Giữ tham chiếu đến các controller con
        self.student_controller = None
        self.face_recognize_controller = None   # Cho nút "Nhận diện"
        self.checkin_controller = None          # Cho nút "Điểm danh"
        self.teacher_controller = None
        self.subject_controller = None
        self.schedule_controller = None 
        self.report_controller = None

        self.view.logout_signal.connect(self.handle_logout) 
        self.connect_navigation_signals()
        
    def connect_navigation_signals(self):
        """Kết nối các nút điều hướng"""
        
        # === Nút Giảng viên (Chỉ Admin) ===
        if self.user_role == 'Admin':
            giangvien_btn = self.view.buttons.get("Giảng viên")
            if giangvien_btn:
                giangvien_btn.clicked.connect(self.open_teacher_management)
        
        # === Nút Môn học ===
        monhoc_btn = self.view.buttons.get("Môn học")
        if monhoc_btn:
            monhoc_btn.clicked.connect(self.open_subject_management)
            
        # === Nút Lịch học ===
        buoihoc_btn = self.view.buttons.get("Lịch học")
        if buoihoc_btn:
            buoihoc_btn.clicked.connect(self.open_schedule_management)

        # === Nút Sinh viên ===
        sinhvien_btn = self.view.buttons.get("Sinh viên")
        if sinhvien_btn:
            sinhvien_btn.clicked.connect(self.open_student_management)

        # === Nút Thống kê ===
        stats_btn = self.view.buttons.get("Thống kê")
        if stats_btn:
            stats_btn.clicked.connect(self.open_report_management) 

        # === Nút "Điểm danh" (Xem danh sách) ===
        checkin_btn = self.view.buttons.get("Điểm danh")
        if checkin_btn:
            checkin_btn.clicked.connect(self.open_checkin_list_management)

        # === Nút "Nhận diện" (Mở camera) ===
        nhandien_btn = self.view.buttons.get("Nhận diện")
        if nhandien_btn:
            nhandien_btn.clicked.connect(self.open_face_recognize_management)
            
        # (Các nút "Xem ảnh" chưa kết nối)

    def show(self):
        self.view.show()
    
    def handle_logout(self):
        """Đóng cửa sổ Home và gọi callback để hiển thị lại Login"""
        print("Controller nhận được tín hiệu đăng xuất. Đóng cửa sổ Home.")
        self.view.close() 
        self.on_logout_callback() 

    # ==========================================================
    # HÀM MỞ CÁC CỬA SỔ CON
    # ==========================================================

    def show_home_again(self):
        """Hiển thị lại cửa sổ Home (được gọi từ các controller con)"""
        print("Quay lại cửa sổ Home...")
        self.view.show()
        # Xóa tham chiếu đến các controller con
        self.student_controller = None
        self.face_recognize_controller = None
        self.checkin_controller = None 
        self.teacher_controller = None
        self.subject_controller = None
        self.schedule_controller = None
        self.report_controller = None

    def open_student_management(self):
       """Mở cửa sổ Quản lý Sinh viên và ẩn Home"""
       print("Mở cửa sổ Quản lý thông tin Sinh viên...")
       try:
           # [SỬA] Import tại đây
           from controller.student_controller import StudentController
           self.student_controller = StudentController(
               on_close_callback=self.show_home_again
           )
           self.student_controller.show()
           self.view.hide()
       except Exception as e:
           QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Sinh viên.\nLỗi: {e}")
           print(f"Lỗi chi tiết (open_student_management): {e}")

    def open_face_recognize_management(self):
        """Mở cửa sổ Nhận diện (Camera) và ẩn Home"""
        print("Mở cửa sổ Nhận diện (Camera)...")
        try:
            # [SỬA] Import tại đây
            from controller.face_recognize_controller import FaceRecognizeController
            self.face_recognize_controller = FaceRecognizeController(
                on_close_callback=self.show_home_again
            )
            self.face_recognize_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Nhận diện.\nLỗi: {e}")
            print(f"Lỗi chi tiết (open_face_recognize_management): {e}")

    def open_checkin_list_management(self):
        """Mở cửa sổ xem danh sách Điểm danh và ẩn Home"""
        print("Mở cửa sổ Danh sách Điểm danh...")
        try:
            # [SỬA] Import tại đây
            from controller.checkin_controller import CheckinController
            self.checkin_controller = CheckinController(
                on_close_callback=self.show_home_again
            )
            self.checkin_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Danh sách Điểm danh.\nLỗi: {e}")
            print(f"Lỗi chi tiết (open_checkin_list_management): {e}")

    def open_teacher_management(self):
        print("Mở cửa sổ Quản lý Giảng viên...")
        try:
            # [SỬA] Import tại đây
            from controller.teacher_info_controller import TeacherController
            self.teacher_controller = TeacherController(
                on_close_callback=self.show_home_again
            )
            self.teacher_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Giảng viên.\nLỗi: {e}")

    def open_subject_management(self):
        print("Mở cửa sổ Quản lý thông tin Môn học...")
        try:
            # [SỬA] Import tại đây
            from controller.subject_controller import SubjectController
            self.subject_controller = SubjectController(
                role=self.user_role, 
                on_close_callback=self.show_home_again
            )
            self.subject_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Môn học.\nLỗi: {e}")
            
    def open_schedule_management(self):
        print("MVở cửa sổ Quản lý thông tin Lịch học...")
        try:
            # [SỬA] Import tại đây
            from controller.schedule_controller import ScheduleController
            self.schedule_controller = ScheduleController(
                on_close_callback=self.show_home_again
            )
            self.schedule_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Lịch học.\nLỗi: {e}")

    def open_report_management(self):
        print("Mở cửa sổ Quản lý thông tin Báo cáo...")
        try:
            # [SỬA] Import tại đây
            from controller.report_controller import ReportController
            self.report_controller = ReportController(
                on_close_callback=self.show_home_again
            )
            self.report_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Báo cáo.\nLỗi: {e}")