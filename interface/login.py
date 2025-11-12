import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QVBoxLayout, QCheckBox, QFrame
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống điểm danh bằng nhận diện khuôn mặt")
        self.setGeometry(300, 100, 900, 500)
        self.setStyleSheet("background-color: white; font-family: Arial;")

        # Layout chính chia 2 phần: trái (ảnh) và phải (form)
        main_layout = QHBoxLayout(self)

        # ==== PHẦN TRÁI ====
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #2b4fc2; border-radius: 5px;")
        left_layout = QVBoxLayout(left_frame)

        title = QLabel("Hệ thống điểm danh\nbằng nhận diện khuôn mặt")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        image = QLabel()
        pixmap = QPixmap(r"E:\AI-facial-recognition-system-for-roll-call\interface\img\logo.jpg")  # ảnh minh họa
        pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignCenter)

        left_layout.addStretch()
        left_layout.addWidget(title)
        left_layout.addWidget(image)
        left_layout.addStretch()

        # ==== PHẦN PHẢI ====
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(50, 40, 50, 40)

        # Logo
        logo = QLabel()
        logo_pix = QPixmap(r"E:\AI-facial-recognition-system-for-roll-call\interface\img\LogoEaut.png")
        logo_pix = logo_pix.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(logo_pix)
        logo.setAlignment(Qt.AlignCenter)

        # Ô nhập
        username_label = QLabel("Tên đăng nhập")
        username_label.setFont(QFont("Arial", 11))
        username_input = QLineEdit()
        username_input.setPlaceholderText("Nhập tên đăng nhập")
        username_input.setStyleSheet("padding: 8px; border-radius: 10px; border: 1px solid #ccc;")

        password_label = QLabel("Mật khẩu")
        password_label.setFont(QFont("Arial", 11))
        password_input = QLineEdit()
        password_input.setPlaceholderText("Nhập mật khẩu")
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet("padding: 8px; border-radius: 10px; border: 1px solid #ccc;")

        remember_check = QCheckBox("Đăng nhập bằng tài khoản admin")
        remember_check.setFont(QFont("Arial", 10))

        login_btn = QPushButton("Đăng nhập")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b4fc2;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1e3d9f;
            }
        """)

        right_layout.addWidget(logo)
        right_layout.addSpacing(10)
        right_layout.addWidget(username_label)
        right_layout.addWidget(username_input)
        right_layout.addWidget(password_label)
        right_layout.addWidget(password_input)
        right_layout.addWidget(remember_check)
        right_layout.addSpacing(10)
        right_layout.addWidget(login_btn)
        right_layout.addStretch()

        # Ghép 2 phần lại
        main_layout.addWidget(left_frame, 2)
        main_layout.addWidget(right_frame, 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
