import sys
import os  # Thêm import 'os'
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QComboBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize  # Thêm 'QSize'
from PyQt5.QtGui import QFont, QPixmap, QIcon  # Thêm 'QPixmap' và 'QIcon'


class AttendanceManagerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Quản lý thông tin điểm danh")
        self.setGeometry(200, 100, 1000, 700)
        self.setStyleSheet("background-color: white; font-family: Arial;")

        # ===================== THANH TIÊU ĐỀ =====================
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(25, 10, 25, 10)

        # ===== THÊM ICON ĐỒNG HỒ =====
        clock_icon = QLabel()
        clock_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\clock.png"
        
        if os.path.exists(clock_icon_path):
            clock_pixmap = QPixmap(clock_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
            clock_icon.setStyleSheet("margin-right: 5px;")
        else:
            print(f"Không tìm thấy icon đồng hồ tại: {clock_icon_path}")
        
        # Nhóm icon và nhãn thời gian
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.addWidget(clock_icon)
        # ================================

        # Thời gian
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: white; font-size: 14px;")
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        
        time_layout.addWidget(self.time_label) # Thêm nhãn thời gian vào nhóm

        # Tiêu đề
        title_label = QLabel("Quản lý thông tin điểm danh")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 17px;")

        # ===== THÊM ICON NÚT QUAY LẠI =====
        # Nút quay lại (bỏ mũi tên '⬅')
        back_btn = QPushButton(" Quay lại")
        
        back_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\back.png"
        if os.path.exists(back_icon_path):
            back_btn.setIcon(QIcon(back_icon_path))
            back_btn.setIconSize(QSize(20, 20))
        else:
            print(f"Không tìm thấy icon 'back' tại: {back_icon_path}")

        # SỬA: Đổi style button để đồng bộ với các file khác
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

        header_layout.addLayout(time_layout) # Thêm nhóm (icon + time)
        header_layout.addStretch(1)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(back_btn)
        header.setLayout(header_layout)

        # ===================== KHUNG CẬP NHẬT BÊN TRÁI =====================
        left_group = QGroupBox("Cập nhật điểm danh")
        left_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 15px;
                color: #0B3D91;
                border: 2px solid #0B3D91;
                border-radius: 8px;
                margin-top: 8px;
            }
        """)

        grid = QGridLayout()
        labels = [
            "ID điểm danh", "ID sinh viên", "Tên sinh viên", "Lớp học",
            "Giờ vào", "Giờ ra", "Ngày", "Điểm danh", "ID bài học"
        ]
        self.inputs = {}

        for i, text in enumerate(labels):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
            line_edit = QLineEdit()
            line_edit.setFixedWidth(180)
            self.inputs[text] = line_edit
            grid.addWidget(lbl, i, 0)
            grid.addWidget(line_edit, i, 1)

        # Hàng nút
        btn_import = QPushButton("Nhập file csv")
        btn_export = QPushButton("Xuất file csv")
        btn_update = QPushButton("Cập nhật")
        btn_reset = QPushButton("Làm mới")
        btn_view = QPushButton("Xem ảnh")
        btn_delete = QPushButton("Xoá")

        for btn in [btn_import, btn_export, btn_update, btn_reset, btn_view, btn_delete]:
            btn.setFixedWidth(150)
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B3D91;
                    color: white;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover { background-color: #1E5CC5; }
            """)

        grid.addWidget(btn_import, 9, 0)
        grid.addWidget(btn_export, 9, 1)
        grid.addWidget(btn_update, 10, 0)
        grid.addWidget(btn_reset, 10, 1)
        grid.addWidget(btn_view, 11, 0)
        grid.addWidget(btn_delete, 11, 1)

        left_group.setLayout(grid)

        # ===================== KHUNG TÌM KIẾM VÀ BẢNG =====================
        right_group = QGroupBox()
        right_layout = QVBoxLayout()

        # Thanh tìm kiếm
        search_layout = QHBoxLayout()
        search_label = QLabel("Tìm kiếm theo")
        search_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        search_combo = QComboBox()
        search_combo.addItems(["ID sinh viên", "Tên sinh viên", "Lớp học", "Ngày", "ID bài học"])
        search_input = QLineEdit()
        search_input.setPlaceholderText("Nhập từ khoá tìm kiếm...")

        search_btn = QPushButton("Tìm kiếm")
        today_btn = QPushButton("Hôm nay")
        all_btn = QPushButton("Xem tất cả")

        for btn in [search_btn, today_btn, all_btn]:
            btn.setFixedWidth(100)
            btn.setFixedHeight(35)  # SỬA: Đổi từ 32 thành 35
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B3D91;
                    color: white;
                    font-weight: bold;
                    border-radius: 5px;  # SỬA: Đổi từ 6px thành 5px
                }
                QPushButton:hover { background-color: #1E5CC5; }
            """)

        search_layout.addWidget(search_label)
        search_layout.addWidget(search_combo)
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(today_btn)
        search_layout.addWidget(all_btn)

        # Bảng dữ liệu
        table = QTableWidget()
        # Sửa lỗi: Thiếu 1 cột "Điểm danh" trong header
        table.setColumnCount(9) 
        table.setHorizontalHeaderLabels([
            "AttendanceID", "ID sinh viên", "Tên sinh viên",
            "Lớp học", "Giờ vào", "Giờ ra", "Ngày", "ID bài học", "Điểm danh"
        ])
        table.setStyleSheet("""
    QHeaderView::section {
        background-color: white;
        color: #0B3D91;
        border: 1px solid #0B3D91;
        padding: 6px;
        font-weight: bold;
    }
    QTableWidget {
        border: 1px solid #0B3D91;
        gridline-color: #0B3D91;
        font-size: 13px;
        background-color: white;
        selection-background-color: #E0ECFF;
        selection-color: black;
    }
""")

        right_layout.addLayout(search_layout)
        right_layout.addWidget(table)
        right_group.setLayout(right_layout)

        # ===================== BỐ CỤC CHÍNH =====================
        main_layout = QVBoxLayout()
        main_layout.addWidget(header)
        content_layout = QHBoxLayout()
        
        # SỬA LỖI: Chuyển 1 và 2.5 thành 2 và 5 (số nguyên)
        content_layout.addWidget(left_group, 2)
        content_layout.addWidget(right_group, 5)
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\n dd-MM-yyyy"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttendanceManagerUI()
    window.show()
    sys.exit(app.exec_())