from ui.home import HomeWindow # Import class HomeWindow từ file view

class HomeController:
    def __init__(self, role, on_logout):
        """
        Khởi tạo controller.
        - role: Vai trò của người dùng (ví dụ: 'admin') để hiển thị.
        - on_logout: Một hàm (callback) sẽ được gọi khi người dùng đăng xuất.
        """
        self.view = HomeWindow()
        self.view.set_user_role(role) # Gọi hàm trong View để set tên vai trò
        self.on_logout_callback = on_logout # Lưu lại hàm callback
        
        # Kết nối tín hiệu 'logout_signal' từ View (khi nhấn nút)
        # tới hàm 'handle_logout' của controller này.
        self.view.logout_signal.connect(self.handle_logout)
        
    def show(self):
        """Hiển thị cửa sổ Home."""
        self.view.show()
    
    def handle_logout(self):
        """
        Hàm này được gọi khi View phát tín hiệu logout.
        """
        print("Controller nhận được tín hiệu, đóng Home, gọi callback...")
        self.view.close() # Đóng cửa sổ Home
        self.on_logout_callback() # Gọi hàm callback (để mở lại Login)