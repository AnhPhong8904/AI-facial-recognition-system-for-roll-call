import sys
from PyQt5.QtWidgets import QApplication
# Sửa ở đây: 'controllers' -> 'controller'
from controller.login_controller import LoginController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Khởi tạo và hiển thị controller đăng nhập
    login_controller = LoginController()
    login_controller.show()
    
    sys.exit(app.exec_())