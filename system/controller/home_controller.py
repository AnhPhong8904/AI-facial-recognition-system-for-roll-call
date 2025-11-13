# SỬA IMPORT: Đảm bảo tên file view là chính xác
from ui.home import HomeWindow
from PyQt5.QtWidgets import QMessageBox

# Import các controller con
try:
    from controller.teacher_info_controller import TeacherController
except ImportError:
    print("Cảnh báo: Không thể import TeacherController.")
    class TeacherController: pass 

try:
    from controller.subject_controller import SubjectController
except ImportError:
    print("Cảnh báo: Không thể import SubjectController.")
    class SubjectController: pass 

try:
    from controller.schedule_controller import ScheduleController
except ImportError:
    print("Cảnh báo: Không thể import ScheduleController.")
    class ScheduleController: pass 

try:
    from controller.checkin_controller import CheckinController
except ImportError:
    print("Cảnh báo: Không thể import CheckinController.")
    class CheckinController: pass 

# MỚI: Import StatisticsController
try:
    from controller.report_controller import ReportController
except ImportError:
    print("Cảnh báo: Không thể import ReportController.")
    class ReportController: pass 


class HomeController:
    def __init__(self, role, on_logout):
        """
        Khởi tạo controller
        :param role: Vai trò ('Admin' hoặc 'GiangVien')
        :param on_logout: Hàm callback để gọi khi đăng xuất
        """
        self.view = HomeWindow(role) 
        self.on_logout_callback = on_logout
        self.user_role = role # MỚI: Lưu vai trò lại
        
        # Giữ tham chiếu đến các controller con
        self.teacher_controller = None
        self.subject_controller = None
        self.schedule_controller = None 
        self.checkin_controller = None
        self.report_controller = None # MỚI

        # Lắng nghe tín hiệu 'logout_signal' từ View
        self.view.logout_signal.connect(self.handle_logout) 
        
        # Kết nối các nút chức năng
        self.connect_navigation_signals()
        
    def connect_navigation_signals(self):
        """Kết nối các nút điều hướng (Giảng viên, Môn học...)"""
        
        # === Nút Giảng viên (Chỉ Admin) ===
        if self.user_role == 'Admin':
            giangvien_btn = self.view.buttons.get("Giảng viên")
            if giangvien_btn:
                giangvien_btn.clicked.connect(self.open_teacher_management)
        
        # === Nút Môn học (Mọi người) ===
        monhoc_btn = self.view.buttons.get("Môn học")
        if monhoc_btn:
            monhoc_btn.clicked.connect(self.open_subject_management)
            
        # === Nút Buổi học (Mọi người) ===
        # SỬA: Tên nút là "Buổi học" trong ui/home_view.py
        buoihoc_btn = self.view.buttons.get("Buổi học")
        if buoihoc_btn:
            buoihoc_btn.clicked.connect(self.open_schedule_management)
        else:
             print("Cảnh báo: Không tìm thấy nút 'Buổi học'.") # Thêm kiểm tra lỗi

        # === Nút Điểm danh ===
        checkin_btn = self.view.buttons.get("Điểm danh")
        if checkin_btn:
            checkin_btn.clicked.connect(self.open_checkin_management)

        # === Nút Thống kê (MỚI) ===
        stats_btn = self.view.buttons.get("Thống kê")
        if stats_btn:
            stats_btn.clicked.connect(self.open_report_management)

        # (Kết nối các nút khác ở đây nếu cần...)
        sinhvien_btn = self.view.buttons.get("Sinh viên")
        if sinhvien_btn:
            sinhvien_btn.clicked.connect(self.open_student_management)

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

    def open_teacher_management(self):
        """Mở cửa sổ Quản lý Giảng viên và ẩn Home"""
        print("Mở cửa sổ Quản lý Giảng viên...")
        
        self.teacher_controller = TeacherController(
            on_close_callback=self.show_home_again
        )
        self.teacher_controller.show()
        self.view.hide()

    def open_subject_management(self):
        """Mở cửa sổ Quản lý thông tin Môn học và ẩn Home"""
        print("Mở cửa sổ Quản lý thông tin Môn học...")
        
        self.subject_controller = SubjectController(
            role=self.user_role, # Truyền role (phân quyền)
            on_close_callback=self.show_home_again
        )
        self.subject_controller.show()
        self.view.hide()
        
    def open_schedule_management(self):
        """Mở cửa sổ Quản lý Lịch học (Buổi học) và ẩn Home"""
        print("Mở cửa sổ Quản lý thông tin Lịch học...")
        
        self.schedule_controller = ScheduleController(
            on_close_callback=self.show_home_again
        )
        self.schedule_controller.show()
        self.view.hide()

    def open_checkin_management(self):
        """Mở cửa sổ Quản lý Điểm danh và ẩn Home"""
        print("Mở cửa sổ Quản lý thông tin Điểm danh...")
        
        self.checkin_controller = CheckinController(
            on_close_callback=self.show_home_again
        )
        self.checkin_controller.show()
        self.view.hide()

    # MỚI: Hàm mở Thống kê
    def open_report_management(self):
        """Mở cửa sổ Quản lý Thống kê và ẩn Home"""
        print("Mở cửa sổ Quản lý thông tin Thống kê...")
        
        self.report_controller = ReportController(
            on_close_callback=self.show_home_again
        )
        self.report_controller.show()
        self.view.hide()

    def open_student_management(self):
       """Hàm chờ: Mở Quản lý Sinh viên"""
       print("Chức năng 'Sinh viên' chưa được cài đặt.")
       # Sử dụng self.view (cửa sổ Home) làm parent cho QMessageBox
       QMessageBox.information(self.view, "Thông báo", "Chức năng 'Quản lý Sinh viên' đang được phát triển.")


    def show_home_again(self):
        """Hiển thị lại cửa sổ Home (được gọi từ các controller con)"""
        print("Quay lại cửa sổ Home...")
        self.view.show()
        # Xóa tham chiếu đến các controller con
        self.teacher_controller = None
        self.subject_controller = None
        self.schedule_controller = None
        self.checkin_controller = None
        self.report_controller = None # MỚI