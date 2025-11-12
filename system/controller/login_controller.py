from ui.login import LoginWindow
from model import auth_service
from controller.home_controller import HomeController

class LoginController:
    def __init__(self):
        self.view = LoginWindow()
        self.home_controller = None # Để giữ tham chiếu đến cửa sổ home
        
        # Kết nối tín hiệu (signal) từ nút 'login_btn' trong View
        # với hàm (slot) 'handle_login' trong Controller
        self.view.login_btn.clicked.connect(self.handle_login)

    def show(self):
        """Hiển thị cửa sổ login"""
        self.view.show()

    def handle_login(self):
        """
        Hàm này được gọi khi người dùng nhấn nút Đăng nhập.
        Đây là phần "xử lý" bạn cần.
        """
        
        # 1. Lấy dữ liệu từ Giao diện (View)
        username = self.view.username_input.text()
        password = self.view.password_input.text()
        is_admin = self.view.remember_check.isChecked()

        # 2. Kiểm tra đầu vào cơ bản
        if not username or not password:
            self.view.show_error_message("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        # 3. Gọi Logic nghiệp vụ (Model)
        try:
            is_valid, message_or_role = auth_service.check_credentials(
                username, 
                password, 
                is_admin
            )
            
            # 4. Cập nhật lại Giao diện (View) dựa trên kết quả
            if is_valid:
                print(f"Đăng nhập thành công với vai trò: {message_or_role}")
                
                # SỬA Ở ĐÂY:
                # Truyền cả 'role' và hàm 'on_logout'
                self.home_controller = HomeController(
                    role=message_or_role,
                    on_logout=self.show_login_again # <--- Thêm tham số này
                )
                self.home_controller.show()
                
                # Đóng cửa sổ đăng nhập
                self.view.close()
                
            else:
                # Hiển thị lỗi
                self.view.show_error_message(message_or_role)
                
        except Exception as e:
            print(f"Lỗi nghiêm trọng khi xử lý đăng nhập: {e}")
            self.view.show_error_message(f"Lỗi hệ thống: {e}")

    # THÊM HÀM NÀY VÀO CUỐI CLASS:
    def show_login_again(self):
        """
        Đây là hàm callback được gọi bởi HomeController khi người dùng đăng xuất.
        Nó sẽ hiển thị lại cửa sổ đăng nhập.
        """
        print("Hiển thị lại cửa sổ đăng nhập...")
        self.view.show()
        # Xóa nội dung ô nhập khi hiển thị lại
        self.view.clear_inputs()