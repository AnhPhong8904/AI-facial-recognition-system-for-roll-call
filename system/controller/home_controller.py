from ui.home import HomeWindow

try:
    from controller.teacher_info_controller import TeacherController
except ImportError as e:
    print(f"Lỗi import: Không tìm thấy TeacherController. {e}")
    # Tạo class giả để tránh crash nếu file chưa tồn tại
    class TeacherController:
        def __init__(self, on_close_callback):
            print("LỖI: Class TeacherController chưa được import")
        def show(self):
            pass


class HomeController:
    def __init__(self, role, on_logout):
        """
        Khởi tạo controller
        :param role: Vai trò ('Admin' hoặc 'GiangVien')
        :param on_logout: Hàm callback để gọi khi đăng xuất
        """
        self.view = HomeWindow(role) 
        self.on_logout_callback = on_logout
        self.teacher_controller = None # MỚI: Để giữ tham chiếu

        # Lắng nghe tín hiệu 'logout_signal' từ View
        self.view.logout_signal.connect(self.handle_logout)
        
        # MỚI: Kết nối nút "Giảng viên" (nếu tồn tại)
        if role == 'Admin':
            # Tìm nút "Giảng viên" mà View đã tạo
            giangvien_btn = self.view.buttons.get("Giảng viên")
            if giangvien_btn:
                giangvien_btn.clicked.connect(self.open_teacher_management)
            else:
                print("Cảnh báo: Không tìm thấy nút 'Giảng viên' trong view.")
        
    def show(self):
        self.view.show()
    
    def handle_logout(self):
        """
        Được gọi khi View gửi tín hiệu logout_signal
        """
        print("Controller nhận được tín hiệu đăng xuất. Đóng cửa sổ Home.")
        self.view.close() 
        self.on_logout_callback() 

    # MỚI: Hàm để mở cửa sổ Quản lý Giảng viên
    def open_teacher_management(self):
        """Mở cửa sổ Giảng viên và ẩn cửa sổ Home"""
        print("Mở cửa sổ Quản lý Giảng viên...")
        
        # Tạo controller Giảng viên và truyền hàm callback
        self.teacher_controller = TeacherController(
            on_close_callback=self.show_home_again
        )
        self.teacher_controller.show()
        
        # Ẩn cửa sổ Home
        self.view.hide()

    # MỚI: Hàm callback để hiển thị lại Home
    def show_home_again(self):
        """Hiển thị lại cửa sổ Home (được gọi từ TeacherController)"""
        print("Quay lại cửa sổ Home...")
        self.view.show()
        self.teacher_controller = None # Xóa tham chiếu