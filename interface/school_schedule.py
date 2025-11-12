import sys
import os  # Thêm import 'os'
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QDateEdit
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize  # Thêm 'QSize'
from PyQt5.QtGui import QFont, QPixmap, QIcon  # Thêm 'QPixmap' và 'QIcon'


class ScheduleUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin lịch học")
        self.setGeometry(100, 100, 1000, 600)
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
        header.setFixedHeight(80)
        layout = QHBoxLayout()
        # Thêm padding cho header
        layout.setContentsMargins(25, 10, 25, 10) # SỬA: Đổi 15 thành 25
 
        # ===== THÊM ICON ĐỒNG HỒ =====
        clock_icon = QLabel()
        # Sử dụng đường dẫn 'mg' giống như file teacher_info
        clock_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\clock.png" 
        
        if os.path.exists(clock_icon_path):
            clock_pixmap = QPixmap(clock_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
            clock_icon.setStyleSheet("margin-right: 5px;")
        else:
            print(f"Không tìm thấy icon đồng hồ tại: {clock_icon_path}")

        # Nhóm icon và nhãn thời gian
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0,0,0,0)
        time_layout.addWidget(clock_icon)

        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 10, QFont.Bold))
        time_layout.addWidget(self.time_label) # Thêm nhãn thời gian vào nhóm
        
        layout.addLayout(time_layout) # Thêm nhóm (icon + time) vào layout chính
        # ================================

        title = QLabel("Quản lý thông tin lịch học")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, stretch=1)

        # ===== THÊM ICON NÚT QUAY LẠI =====
        back_btn = QPushButton(" Quay lại") # Thêm khoảng trắng
        
        # Sử dụng đường dẫn 'mg'
        back_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\back.png"
        if os.path.exists(back_icon_path):
            back_btn.setIcon(QIcon(back_icon_path))
            back_btn.setIconSize(QSize(20, 20))
        else:
            print(f"Không tìm thấy icon 'back' tại: {back_icon_path}")
            
        # SỬA: Đổi style button để giống 2 file kia
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                font-size: 14px;
                padding: 8px 15px;
            }
            QPushButton:hover { 
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        # ===================================
        
        layout.addWidget(back_btn)

        header.setLayout(layout)
        return header

    # ---------------- Content ----------------
    def content_ui(self):
        content = QWidget()
        content_layout = QHBoxLayout()

        # Left panel - Thông tin buổi học
        info_group = QGroupBox("Thông tin buổi học") # Sửa tiêu đề
        info_group.setFont(QFont("Arial", 10, QFont.Bold))
        form_layout = QGridLayout()

        labels = [
            "ID buổi học:", "Giờ bắt đầu:", "Giờ kết thúc:",
            "Ngày:", "ID giảng viên:", "Tên giảng viên:",
            "ID môn học:", "Tên môn học:"
        ]
        self.inputs = {}

        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            if label_text == "Ngày:":
                input_field = QDateEdit()
                input_field.setDisplayFormat("dd-MM-yyyy")
                input_field.setCalendarPopup(True)
            else:
                input_field = QLineEdit()

            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(input_field, i, 1)
            self.inputs[label_text] = input_field

        # Nút chức năng
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Thêm mới")
        btn_update = QPushButton("Cập nhật")
        btn_delete = QPushButton("Xoá")
        btn_refresh = QPushButton("Làm mới")

        for btn in [btn_add, btn_update, btn_delete, btn_refresh]:
            btn.setStyleSheet("background-color: #1e40af; color: white; padding: 6px 10px; border-radius: 6px;")

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_update)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_refresh)

        form_layout.addLayout(btn_layout, len(labels), 0, 1, 2)
        info_group.setLayout(form_layout)

        # Right panel - Bảng dữ liệu và tìm kiếm
        right_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        search_by = QComboBox()
        search_by.addItems(["ID buổi học", "Tên giảng viên", "Tên môn học"])
        search_input = QLineEdit()
        btn_search = QPushButton("Tìm kiếm")
        btn_all = QPushButton("Xem tất cả")

        for btn in [btn_search, btn_all]:
            btn.setStyleSheet("background-color: #1e40af; color: white; padding: 6px 10px; border-radius: 6px;")

        search_layout.addWidget(QLabel("Tìm kiếm theo:"))
        search_layout.addWidget(search_by)
        search_layout.addWidget(search_input)
        search_layout.addWidget(btn_search)
        search_layout.addWidget(btn_all)

        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "ID buổi học", "Giờ bắt đầu", "Giờ kết thúc", "Ngày",
            "ID giảng viên", "Tên giảng viên", "ID môn học", "Tên môn học"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("background-color: white;")

        right_layout.addLayout(search_layout)
        right_layout.addWidget(table)

        # Add panels to content
        content_layout.addWidget(info_group, 3)
        content_layout.addLayout(right_layout, 5)
        content.setLayout(content_layout)

        return content

    # ---------------- Update Time ----------------
    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\ndd-MM-yyyy"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleUI()
    window.show()
    sys.exit(app.exec_())