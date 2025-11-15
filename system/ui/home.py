import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QToolButton, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize, QPropertyAnimation, QRect
from PyQt5.QtCore import pyqtSignal

# Đổi tên class thành HomeView cho nhất quán
class HomeWindow(QWidget): 
    # Tín hiệu này sẽ được gửi đến main_app để xử lý logout
    logout_signal = pyqtSignal()

    def __init__(self, role):
        super().__init__()
        self.user_role = role 
        self.buttons = {} # Để lưu trữ tham chiếu đến các nút
        self.initUI()
        
        # Gọi hàm phân quyền sau khi UI đã được vẽ
        self.set_permissions(role)
        self.set_user_role(role)

    def initUI(self):
        self.setWindowTitle("Hệ thống điểm danh bằng nhận diện khuôn mặt")
        self.setStyleSheet("background-color: white; font-family: Arial;")
        self.resize(1000, 700)

        # ===== LAYOUT CHÍNH =====
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 10, 25, 10)
        main_layout.setSpacing(15)

        # ===== THANH NGANG TRÊN CÙNG =====
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
        # [SỬA ĐƯỜNG DẪN] Giả định icon nằm trong system/img
        clock_icon_path = r"system/img/clock.png"
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
        # [SỬA ĐƯỜNG DẪN]
        admin_icon_path = r"system/img/user.png" 
        if os.path.exists(admin_icon_path):
            admin_pixmap = QPixmap(admin_icon_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            admin_icon.setPixmap(admin_pixmap)
        
        self.admin_text = QLabel("ADMIN") 
        self.admin_text.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        admin_layout.addWidget(admin_icon)
        admin_layout.addWidget(self.admin_text)

        self.logout_button = QPushButton(" Đăng xuất")
        self.logout_button.setCursor(Qt.PointingHandCursor)
        self.logout_button.setFixedHeight(35)
        
        # [SỬA ĐƯỜNG DẪN]
        logout_icon_path = r"system/img/logout.png"
        if os.path.exists(logout_icon_path):
            self.logout_button.setIcon(QIcon(logout_icon_path))
            self.logout_button.setIconSize(QSize(20, 20))
        
        self.logout_button.setStyleSheet("""
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
        self.logout_button.clicked.connect(self.logout_clicked)

        top_layout.addWidget(clock_widget)
        top_layout.addStretch(1)
        top_layout.addWidget(title_label)
        top_layout.addStretch(1)
        top_layout.addWidget(admin_widget)
        top_layout.addWidget(self.logout_button)

        # ===== CONTAINER CHO ẢNH NỀN & NỘI DUNG =====
        content_container = QWidget()
        content_container.setStyleSheet("background-color: transparent; border-radius: 15px;")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # ===== ẢNH NỀN =====
        self.background = QLabel(content_container)
        # [SỬA ĐƯỜNG DẪN]
        self.bg_path = r"system/img/logo2.jpg" 
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

        # Vẽ tất cả 8 nút
        buttons_data = [
            ("Sinh viên", r"system/img/female-graduate-student.png"),
            ("Nhận diện", r"system/img/electronic-id.png"),
            ("Điểm danh", r"system/img/checkmark.png"),
            ("Môn học", r"system/img/book.png"),
            ("Thống kê", r"system/img/dashboard.png"),
            ("Giảng viên", r"system/img/teacher.png"),
            ("Lịch học", r"system/img/training.png"),
            ("Xem ảnh", r"system/img/image.png"),
        ]

        positions = [(i, j) for i in range(2) for j in range(4)]
        
        for position, (text, icon_path) in zip(positions, buttons_data):
            btn = QToolButton()
            btn.setText(text)
            btn.setFixedSize(180, 150)
            
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
            else:
                print(f"Khong tim thay icon: {icon_path}")
                
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
                QToolButton:disabled {
                    background-color: #f0f0f0;
                    color: #a0a0a0;
                }
            """)
            self.add_hover_animation(btn)
            grid.addWidget(btn, *position)
            
            # Lưu tham chiếu nút bằng tên
            self.buttons[text] = btn

        # ===== THÊM CÁC THÀNH PHẦN VÀO LAYOUT =====
        main_layout.addWidget(top_bar)
        main_layout.addWidget(content_container)

        buttons_widget.raise_()

        self.setLayout(main_layout)
        self.content_container = content_container
        self.buttons_widget = buttons_widget

    # ===== CẬP NHẬT ẢNH NỀN & OVERLAY KHI PHÓNG TO =====
    def resizeEvent(self, event):
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
            if btn.isEnabled():
                btn.original_geometry = btn.geometry()
                anim = QPropertyAnimation(btn, b"geometry")
                anim.setDuration(120)
                x, y, w, h = btn.original_geometry.getRect()
                anim.setStartValue(QRect(x, y, w, h))
                anim.setEndValue(QRect(x - 3, y - 3, w + 6, h + 6))
                anim.start()
                btn.anim = anim

        def on_leave():
            if hasattr(btn, "original_geometry") and btn.isEnabled():
                anim = QPropertyAnimation(btn, b"geometry")
                anim.setDuration(120)
                anim.setStartValue(btn.geometry())
                anim.setEndValue(btn.original_geometry)
                anim.start()
                btn.anim = anim

        btn.enterEvent = lambda e: on_enter()
        btn.leaveEvent = lambda e: on_leave()

    def logout_clicked(self):
        print("Tín hiệu đăng xuất được gửi đi...")
        self.logout_signal.emit()

    def set_user_role(self, role):
        if role == 'GiangVien':
            self.admin_text.setText("GIẢNG VIÊN")
        else:
            self.admin_text.setText("ADMIN")
            
    def set_permissions(self, role):
        """
        Làm mờ các nút dựa trên vai trò
        """
        if role == 'GiangVien':
            # Giảng viên bị mờ các nút Quản lý
            buttons_to_disable = ["Môn học", "Giảng viên", "Lịch học"]
            for btn_name in buttons_to_disable:
                if btn_name in self.buttons:
                    self.buttons[btn_name].setEnabled(False)
                    self.buttons[btn_name].setToolTip("Bạn không có quyền truy cập mục này")
        
        if role == 'Admin':
            # Admin (ví dụ) không cần điểm danh
            buttons_to_disable = ["Điểm danh"]
            for btn_name in buttons_to_disable:
                if btn_name in self.buttons:
                    self.buttons[btn_name].setEnabled(False)
                    self.buttons[btn_name].setToolTip("Chức năng này dành cho Giảng viên")