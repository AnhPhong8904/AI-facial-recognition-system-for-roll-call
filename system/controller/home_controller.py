# SỬA IMPORT: Đảm bảo tên file view là chính xác
from ui.home import HomeWindow

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
            
        # === Nút Lịch học (Mọi người) ===
        buoihoc_btn = self.view.buttons.get("Lịch học")
        if buoihoc_btn:
            buoihoc_btn.clicked.connect(self.open_schedule_management)

        # (Kết nối các nút khác ở đây nếu cần...)
        # Vd:
        # sinhvien_btn = self.view.buttons.get("Sinh viên")
        # if sinhvien_btn:
        #     sinhvien_btn.clicked.connect(self.open_student_management)

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
        
        # SỬA LỖI: Truyền `role` (phân quyền) vào SubjectController
        self.subject_controller = SubjectController(
            role=self.user_role, # <--- Fix lỗi TypeError
            on_close_callback=self.show_home_again
        )
        self.subject_controller.show()
        self.view.hide()
        
    def open_schedule_management(self):
        """Mở cửa sổ Quản lý Lịch học (Lịch học) và ẩn Home"""
        print("Mở cửa sổ Quản lý thông tin Lịch học...")
        
        self.schedule_controller = ScheduleController(
            on_close_callback=self.show_home_again
        )
        self.schedule_controller.show()
        self.view.hide()

    # (Thêm các hàm open_... khác ở đây)
    # def open_student_management(self):
    #    print("Chức năng 'Sinh viên' chưa được cài đặt.")
    #    QMessageBox.information(self.view, "Thông báo", "Chức năng 'Quản lý Sinh viên' đang được phát triển.")


    def show_home_again(self):
        """Hiển thị lại cửa sổ Home (được gọi từ các controller con)"""
        print("Quay lại cửa sổ Home...")
        self.view.show()
        # Xóa tham chiếu đến các controller con
        self.teacher_controller = None
        self.subject_controller = None
        self.schedule_controller = None