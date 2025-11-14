# SỬA IMPORT: Đảm bảo tên file view là chính xác
from ui.home import HomeWindow
from PyQt5.QtWidgets import QMessageBox

# Import các controller con
try:
    # Sửa tên file import (nếu cần)
    from controller.teacher_info_controller import TeacherController
except ImportError:
    print("Cảnh báo: Không thể import TeacherController.")
    # Class giả để code chạy mà không crash
    class TeacherController: 
        def __init__(self, on_close_callback): pass
        def show(self): pass

try:
    from controller.subject_controller import SubjectController
except ImportError:
    print("Cảnh báo: Không thể import SubjectController.")
    class SubjectController: 
        def __init__(self, role, on_close_callback): pass
        def show(self): pass

try:
    from controller.schedule_controller import ScheduleController
except ImportError:
    print("Cảnh báo: Không thể import ScheduleController.")
    class ScheduleController: 
        def __init__(self, on_close_callback): pass
        def show(self): pass

try:
    from controller.checkin_controller import CheckinController
except ImportError:
    print("Cảnh báo: Không thể import CheckinController.")
    class CheckinController: 
        def __init__(self, on_close_callback): pass
        def show(self): pass

try:
    # Đã đổi tên thành report_controller
    from controller.report_controller import ReportController
except ImportError:
    print("Cảnh báo: Không thể import ReportController.")
    class ReportController: 
        def __init__(self, on_close_callback): pass
        def show(self): pass

# === SỬA IMPORT ===
# Đảm bảo import StudentController
try:
    from controller.student_controller import StudentController
except ImportError:
    print("Cảnh báo: Không thể import StudentController.")
    class StudentController: 
        def __init__(self, on_close_callback): pass
        def show(self): pass


class HomeController:
    def __init__(self, role, on_logout):
        """
        Khởi tạo controller
        :param role: Vai trò ('Admin' hoặc 'GiangVien')
        :param on_logout: Hàm callback để gọi khi đăng xuất
        """
        self.view = HomeWindow(role) 
        self.on_logout_callback = on_logout
        self.user_role = role # Lưu vai trò lại
        
        # Giữ tham chiếu đến các controller con
        self.teacher_controller = None
        self.subject_controller = None
        self.schedule_controller = None 
        self.checkin_controller = None
        self.report_controller = None
        self.student_controller = None # THÊM DÒNG NÀY

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
        
        # === Nút Môn học ===
        monhoc_btn = self.view.buttons.get("Môn học")
        if monhoc_btn:
            monhoc_btn.clicked.connect(self.open_subject_management)
            
        # === Nút Lịch học ===
        buoihoc_btn = self.view.buttons.get("Lịch học")
        if buoihoc_btn:
            buoihoc_btn.clicked.connect(self.open_schedule_management)
        else:
             print("Cảnh báo: Không tìm thấy nút 'Lịch học'.") 

        # === Nút Điểm danh ===
        checkin_btn = self.view.buttons.get("Điểm danh")
        if checkin_btn:
            checkin_btn.clicked.connect(self.open_checkin_management)

        # === Nút Thống kê ===
        stats_btn = self.view.buttons.get("Thống kê")
        if stats_btn:
            stats_btn.clicked.connect(self.open_report_management) 

        # === Nút Sinh viên ===
        sinhvien_btn = self.view.buttons.get("Sinh viên")
        if sinhvien_btn:
            sinhvien_btn.clicked.connect(self.open_student_management)

        # (Các nút "Nhận diện", "Xem ảnh" chưa kết nối)

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
        
        try:
            self.teacher_controller = TeacherController(
                on_close_callback=self.show_home_again
            )
            self.teacher_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Giảng viên.\nLỗi: {e}")

    def open_subject_management(self):
        """Mở cửa sổ Quản lý thông tin Môn học và ẩn Home"""
        print("Mở cửa sổ Quản lý thông tin Môn học...")
        
        try:
            self.subject_controller = SubjectController(
                role=self.user_role, # Truyền role (phân quyền)
                on_close_callback=self.show_home_again
            )
            self.subject_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Môn học.\nLỗi: {e}")
            
    def open_schedule_management(self):
        """Mở cửa sổ Quản lý Lịch học (Lịch học) và ẩn Home"""
        print("Mở cửa sổ Quản lý thông tin Lịch học...")
        
        try:
            self.schedule_controller = ScheduleController(
                on_close_callback=self.show_home_again
            )
            self.schedule_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Lịch học.\nLỗi: {e}")

    def open_checkin_management(self):
        """Mở cửa sổ Quản lý Điểm danh và ẩn Home"""
        print("Mở cửa sổ Quản lý thông tin Điểm danh...")
        
        try:
            self.checkin_controller = CheckinController(
                on_close_callback=self.show_home_again
            )
            self.checkin_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Điểm danh.\nLỗi: {e}")

    def open_report_management(self):
        """Mở cửa sổ Quản lý Báo cáo (Thống kê) và ẩn Home"""
        print("Mở cửa sổ Quản lý thông tin Báo cáo...")
        
        try:
            # Đã đổi tên thành ReportController
            self.report_controller = ReportController(
                on_close_callback=self.show_home_again
            )
            self.report_controller.show()
            self.view.hide()
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Báo cáo.\nLỗi: {e}")

    # === SỬA HÀM NÀY ===
    def open_student_management(self):
       """MỞI: Mở cửa sổ Quản lý Sinh viên và ẩn Home"""
       print("Mở cửa sổ Quản lý thông tin Sinh viên...")
       
       try:
           # SỬA LỖI: Truyền tham số on_close_callback
           self.student_controller = StudentController(
               on_close_callback=self.show_home_again
           )
           self.student_controller.show()
           self.view.hide()
       except Exception as e:
            QMessageBox.critical(self.view, "Lỗi", f"Không thể mở Quản lý Sinh viên.\nLỗi: {e}")
            print(f"Lỗi chi tiết (open_student_management): {e}") # Thêm log chi tiết


    def show_home_again(self):
        """Hiển thị lại cửa sổ Home (được gọi từ các controller con)"""
        print("Quay lại cửa sổ Home...")
        self.view.show()
        # Xóa tham chiếu đến các controller con
        self.teacher_controller = None
        self.subject_controller = None
        self.schedule_controller = None
        self.checkin_controller = None
        self.report_controller = None
        self.student_controller = None # THÊM DÒNG NÀY