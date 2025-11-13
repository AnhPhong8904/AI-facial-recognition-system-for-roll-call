import sys
import os 
# MỚI: Thêm QDateEdit, QDate
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QDateEdit
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize, QDate
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QIcon

class TeacherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin giảng viên")
        # MỚI: Tăng kích thước cửa sổ để chứa thêm trường
        self.setGeometry(100, 100, 1200, 700) 
        self.setStyleSheet("background-color: white; font-family: Arial;")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.header_ui())
        main_layout.addWidget(self.content_ui())
        self.setLayout(main_layout)

        # Cập nhật thời gian
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

    # ---------------- Header ----------------
    def header_ui(self):
        header = QWidget()
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        layout = QHBoxLayout()
        layout.setContentsMargins(25, 10, 25, 10)

        # Icon Đồng hồ
        clock_icon = QLabel()
        clock_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\clock.png"
        
        if os.path.exists(clock_icon_path):
            clock_pixmap = QPixmap(clock_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
            clock_icon.setStyleSheet("margin-right: 5px;")

        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0,0,0,0)
        time_layout.addWidget(clock_icon)

        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 10, QFont.Bold))
        time_layout.addWidget(self.time_label)
        
        layout.addLayout(time_layout)

        title = QLabel("Quản lý thông tin giảng viên")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, stretch=1)

        # Nút Quay lại
        self.back_btn = QPushButton(" Quay lại") 
        
        back_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\back.png"
        if os.path.exists(back_icon_path):
            self.back_btn.setIcon(QIcon(back_icon_path))
            self.back_btn.setIconSize(QSize(20, 20))
            
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2); color: white;
                font-weight: bold; border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px; font-size: 14px; padding: 8px 15px;
            }
            QPushButton:hover { 
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        
        layout.addWidget(self.back_btn)
        header.setLayout(layout)
        return header

    # ---------------- Content ----------------
    def content_ui(self):
        content = QWidget()
        content_layout = QHBoxLayout()

        # Left panel - Thông tin giảng viên
        info_group = QGroupBox("Thông tin giảng viên")
        info_group.setFont(QFont("Arial", 10, QFont.Bold))
        form_layout = QGridLayout()
        # MỚI: Thêm giãn cách dọc
        form_layout.setVerticalSpacing(12) 

        # MỚI: Cập nhật danh sách labels
        labels = [
            "Mã giảng viên:", "Họ tên:", "Số điện thoại:", "Email:", 
            "Tên đăng nhập:", "Mật khẩu:", "Giới tính:", "Ngày sinh:", "Địa chỉ:"
        ]
        
        self.inputs = {} 

        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            form_layout.addWidget(label, i, 0) # Thêm label vào cột 0
            
            # MỚI: Xử lý các trường đặc biệt
            if label_text == "Giới tính:":
                widget = QComboBox()
                widget.addItems(["", "Nam", "Nữ", "Khác"])
                form_layout.addWidget(widget, i, 1) # Thêm widget vào cột 1
                
            elif label_text == "Ngày sinh:":
                widget = QDateEdit()
                widget.setDisplayFormat("dd/MM/yyyy")
                widget.setCalendarPopup(True) # <-- Nhấn vào ra lịch
                widget.setDate(QDate(2000, 1, 1)) # Ngày mặc định
                form_layout.addWidget(widget, i, 1)
                
            else: # Các trường còn lại là QLineEdit
                widget = QLineEdit()
                if label_text == "Mật khẩu:":
                    widget.setEchoMode(QLineEdit.Password)
                    widget.setPlaceholderText("Nhập nếu muốn thay đổi")
                
                form_layout.addWidget(widget, i, 1)
            
            # Lưu trữ tất cả widgets (bao gồm QLineEdit, QComboBox, QDateEdit)
            self.inputs[label_text] = widget

        # Nút chức năng
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Thêm mới")
        self.btn_update = QPushButton("Cập nhật")
        self.btn_delete = QPushButton("Xoá")
        self.btn_refresh = QPushButton("Làm mới")

        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_refresh]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e40af; color: white; 
                    padding: 8px 12px; border-radius: 6px; font-weight: bold;
                }
                QPushButton:hover { background-color: #2b4fc2; }
            """)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)

        form_layout.addLayout(btn_layout, len(labels), 0, 1, 2)
        info_group.setLayout(form_layout)

        # Right panel - Bảng dữ liệu và tìm kiếm
        right_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_by = QComboBox()
        self.search_by.addItems(["Mã giảng viên", "Tên giảng viên", "Email", "SĐT"])
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập thông tin tìm kiếm...")
        
        self.btn_search = QPushButton("Tìm kiếm")
        self.btn_all = QPushButton("Xem tất cả")

        for btn in [self.btn_search, self.btn_all]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e40af; color: white; 
                    padding: 8px 12px; border-radius: 6px; font-weight: bold;
                }
                QPushButton:hover { background-color: #2b4fc2; }
            """)

        search_layout.addWidget(QLabel("Tìm kiếm theo:"))
        search_layout.addWidget(self.search_by)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_all)

        # MỚI: Cập nhật Bảng
        self.table = QTableWidget()
        self.table.setColumnCount(10) # 10 cột (bao gồm 2 cột ẩn)
        self.table.setHorizontalHeaderLabels([
            "ID TK", "ID GV", "Mã GV", "Họ tên", 
            "Giới tính", "Ngày sinh", "Địa chỉ", 
            "SĐT", "Email", "Tên đăng nhập"
        ])
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: white;")
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Ẩn 2 cột ID
        self.table.setColumnHidden(0, True) # ID_TAIKHOAN
        self.table.setColumnHidden(1, True) # ID_GV

        right_layout.addLayout(search_layout)
        right_layout.addWidget(self.table)

        # MỚI: Cập nhật tỉ lệ
        content_layout.addWidget(info_group, 4) # Tăng tỉ lệ form
        content_layout.addLayout(right_layout, 6) # Giảm tỉ lệ bảng
        content.setLayout(content_layout)

        return content

    # ---------------- Update Time ----------------
    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\ndd-MM-yyyy"))
