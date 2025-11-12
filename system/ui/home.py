import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QToolButton, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import (
    Qt, QTimer, QDateTime, QSize, 
    QPropertyAnimation, QRect, pyqtSignal # Thêm pyqtSignal
)

# Đổi tên class để nhất quán, bạn có thể giữ tên cũ
# nhưng nếu giữ tên cũ thì phải sửa ở home_controller.py
class HomeWindow(QWidget): 
    
    # 1. Thêm tín hiệu (signal)
    logout_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Hệ thống điểm danh bằng nhận diện khuôn mặt")
        self.setStyleSheet("background-color: white; font-family: Arial;")
        self.resize(1000, 700)

        # ===== LAYOUT CHÍNH =====
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 10, 25, 10)
        main_layout.setSpacing(15)

        # ===== THANH NGANG TRÊN CÙNG (KHÔNG CÓ OVERLAY) =====
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        top_bar.setFixedHeight(80)

        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(30, 0, 30, 0)

        # Đồng hồ
        clock_widget = QWidget()
        clock_layout = QHBoxLayout(clock_widget)
        clock_layout.setContentsMargins(0, 0, 0, 0)
        clock_layout.setSpacing(10)
        
        clock_icon = QLabel()
        clock_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\system\img\clock.png"
        if os.path.exists(clock_icon_path):
            clock_pixmap = QPixmap(clock_icon_path).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
        
        self.time_label = QLabel()
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.time_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        clock_layout.addWidget(clock_icon)
        clock_layout.addWidget(self.time_label)

        # Tiêu đề
        title_label = QLabel("Hệ thống điểm danh\nbằng nhận diện khuôn mặt")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

        # Admin + Logout
        admin_widget = QWidget()
        admin_layout = QHBoxLayout(admin_widget)
        admin_layout.setContentsMargins(0, 0, 0, 0)
        admin_layout.setSpacing(8)
        
        admin_icon = QLabel()
        admin_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\system\img\user.png"
        if os.path.exists(admin_icon_path):
            admin_pixmap = QPixmap(admin_icon_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            admin_icon.setPixmap(admin_pixmap)
        
        # 2. Thay đổi ở đây:
        self.admin_text = QLabel("ADMIN") # Đổi tên thành self.admin_text
        self.admin_text.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        admin_layout.addWidget(admin_icon)
        admin_layout.addWidget(self.admin_text)

        logout_button = QPushButton(" Đăng xuất")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.setFixedHeight(35)
        
        logout_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\system\img\logout.png"
        if os.path.exists(logout_icon_path):
            logout_button.setIcon(QIcon(logout_icon_path))
            logout_button.setIconSize(QSize(20, 20))
        
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        # 3. Thay đổi ở đây:
        logout_button.clicked.connect(self.logout_clicked) # Giữ nguyên

        top_layout.addWidget(clock_widget)
        top_layout.addStretch(1)
        top_layout.addWidget(title_label)
        top_layout.addStretch(1)
        top_layout.addWidget(admin_widget)
        top_layout.addWidget(logout_button)

        # ===== CONTAINER CHO ẢNH NỀN & NỘI DUNG =====
        content_container = QWidget()
        content_container.setStyleSheet("background-color: transparent; border-radius: 15px;")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # ===== ẢNH NỀN =====
        self.background = QLabel(content_container)
        self.bg_path = r"E:\AI-facial-recognition-system-for-roll-call\system\img\logo2.jpg"
        if os.path.exists(self.bg_path):
            self.pixmap = QPixmap(self.bg_path)
            self.background.setPixmap(self.pixmap)
        else:
            print(f"⚠️ Không tìm thấy ảnh nền: {self.bg_path}")
        self.background.setScaledContents(True)

        # ===== LỚP PHỦ MÀU XANH TRONG SUỐT =====
        self.overlay = QLabel(content_container)
        self.overlay.setStyleSheet("background-color: rgba(0, 80, 200, 120); border-radius: 15px;")

        # ===== CÁC NÚT CHỨC NĂNG =====
        buttons_widget = QWidget(content_container)
        buttons_widget.setAttribute(Qt.WA_TranslucentBackground)
        
        grid = QGridLayout(buttons_widget)
        grid.setSpacing(40)
        grid.setContentsMargins(50, 50, 50, 50)

        buttons = [
            ("Sinh viên", r"E:\AI-facial-recognition-system-for-roll-call\system\img\female-graduate-student.png"),
            ("Nhận diện", r"E:\AI-facial-recognition-system-for-roll-call\system\img\electronic-id.png"),
            ("Điểm danh", r"E:\AI-facial-recognition-system-for-roll-call\system\img\checkmark.png"),
            ("Môn học", r"E:\AI-facial-recognition-system-for-roll-call\system\img\book.png"),
            ("Thống kê", r"E:\AI-facial-recognition-system-for-roll-call\system\img\dashboard.png"),
            ("Giảng viên", r"E:\AI-facial-recognition-system-for-roll-call\system\img\teacher.png"),
            ("Buổi học", r"E:\AI-facial-recognition-system-for-roll-call\system\img\training.png"),
            ("Xem ảnh", r"E:\AI-facial-recognition-system-for-roll-call\system\img\image.png"),
        ]

        positions = [(i, j) for i in range(2) for j in range(4)]
        for position, (text, icon_path) in zip(positions, buttons):
            btn = QToolButton()
            btn.setText(text)
            btn.setFixedSize(180, 150)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(64, 64))
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setStyleSheet("""
                QToolButton {
                    background-color: white;
                    color: black;
                    font-size: 15px;
                    font-weight: bold;
                    border-radius: 15px;
                    border: none;
                    padding-top: 8px;
                }
                QToolButton:hover {
                    background-color: #e6f0ff;
                }
            """)
            self.add_hover_animation(btn)
            grid.addWidget(btn, *position)

        # ===== THÊM CÁC THÀNH PHẦN VÀO LAYOUT =====
        main_layout.addWidget(top_bar)
        main_layout.addWidget(content_container)

        # Đặt buttons_widget lên trên overlay
        buttons_widget.raise_()

        self.setLayout(main_layout)
        self.content_container = content_container
        self.buttons_widget = buttons_widget

    # ===== CẬP NHẬT ẢNH NỀN & OVERLAY KHI PHÓNG TO =====
    def resizeEvent(self, event):
        """Cập nhật kích thước background & overlay khi thay đổi kích thước cửa sổ"""
        if hasattr(self, 'content_container'):
            w = self.content_container.width()
            h = self.content_container.height()
            self.background.setGeometry(0, 0, w, h)
            self.overlay.setGeometry(0, 0, w, h)
            self.buttons_widget.setGeometry(0, 0, w, h)
        super().resizeEvent(event)

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\ndd-MM-yyyy"))

    def add_hover_animation(self, btn):
        def on_enter():
            btn.original_geometry = btn.geometry()
            anim = QPropertyAnimation(btn, b"geometry")
            anim.setDuration(120)
            x, y, w, h = btn.original_geometry.getRect()
            anim.setStartValue(QRect(x, y, w, h))
            anim.setEndValue(QRect(x - 3, y - 3, w + 6, h + 6))
            anim.start()
            btn.anim = anim

        def on_leave():
            if hasattr(btn, "original_geometry"):
                anim = QPropertyAnimation(btn, b"geometry")
                anim.setDuration(120)
                anim.setStartValue(btn.geometry())
                anim.setEndValue(btn.original_geometry)
                anim.start()
                btn.anim = anim

        btn.enterEvent = lambda e: on_enter()
        btn.leaveEvent = lambda e: on_leave()

    # 4. Thay đổi ở đây:
    def logout_clicked(self):
        print("Gửi tín hiệu đăng xuất...")
        self.logout_signal.emit() # Gửi tín hiệu thay vì chỉ in
    
    # 5. Thêm hàm mới:
    def set_user_role(self, role_name):
        """Hàm này được controller gọi để set tên vai trò trên UI"""
        self.admin_text.setText(role_name.upper())

# 6. Bỏ khối if __name__ == "__main__":
# (Vì file này sẽ được chạy từ main.py)