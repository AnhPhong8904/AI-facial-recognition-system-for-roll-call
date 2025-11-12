import sys
import os  # SỬA: Thêm import 'os'
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QTableWidget, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize  # SỬA: Thêm 'QSize'
from PyQt5.QtGui import QFont, QIcon, QPixmap  # SỬA: Thêm 'QPixmap'


class SubjectInfoUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin môn học")
        self.resize(1200, 820)
        self.setStyleSheet("background-color: #f5f5ff;")
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(10)

        # ===== HEADER =====
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # SỬA: Clock icon (từ file) + time/date
        clock_icon = QLabel()
        # Dùng đường dẫn giống các file quản lý khác
        clock_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\clock.png"
        
        if os.path.exists(clock_icon_path):
            clock_pixmap = QPixmap(clock_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
        else:
            print(f"Không tìm thấy icon đồng hồ tại: {clock_icon_path}")
            
        clock_icon.setStyleSheet("margin-right: 10px;")

        self.time_label = QLabel("00:00:00 PM")
        self.date_label = QLabel("01-01-2025")
        for lbl in [self.time_label, self.date_label]:
            lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        time_box = QVBoxLayout()
        time_box.addWidget(self.time_label)
        time_box.addWidget(self.date_label)

        title_label = QLabel("Quản lý thông tin môn học")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 20px;")
        title_label.setAlignment(Qt.AlignCenter)

        # SỬA: Nút quay lại (icon từ file + style mờ)
        back_btn = QPushButton(" Quay lại")
        
        back_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\back.png"
        if os.path.exists(back_icon_path):
            back_btn.setIcon(QIcon(back_icon_path))
            back_btn.setIconSize(QSize(20, 20))
        else:
            print(f"Không tìm thấy icon 'back' tại: {back_icon_path}")

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

        header_layout.addWidget(clock_icon) # SỬA: Thêm icon
        header_layout.addLayout(time_box)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(back_btn)

        # ===== GROUP 1: THÔNG TIN MÔN HỌC =====
        info_group = QGroupBox("Thông tin môn học")
        info_group.setFont(QFont("Arial", 11, QFont.Bold))
        info_group.setStyleSheet("""
            QGroupBox {
                background-color: #F8F8F8;
                border: 3px solid #1E40AF;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #1E40AF;
            }
        """)
        info_layout = QGridLayout(info_group)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setHorizontalSpacing(12)
        info_layout.setVerticalSpacing(10)

        # Form fields
        info_layout.addWidget(QLabel("ID môn học:"), 0, 0)
        self.id_monhoc = QLineEdit()
        info_layout.addWidget(self.id_monhoc, 0, 1)

        info_layout.addWidget(QLabel("Tên môn học:"), 1, 0)
        self.ten_monhoc = QLineEdit()
        info_layout.addWidget(self.ten_monhoc, 1, 1)

        info_layout.addWidget(QLabel("Lớp tín chỉ:"), 2, 0)
        self.lop_tinchi = QLineEdit()
        info_layout.addWidget(self.lop_tinchi, 2, 1)

        # Search
        info_layout.addWidget(QLabel("Tìm kiếm theo:"), 0, 2)
        self.search_type = QComboBox()
        self.search_type.addItems(["ID môn học", "Tên môn học"])
        info_layout.addWidget(self.search_type, 0, 3)
        self.search_input = QLineEdit()
        info_layout.addWidget(self.search_input, 0, 4)

        btn_search = QPushButton("Tìm kiếm")
        btn_all = QPushButton("Xem tất cả")
        for b in [btn_search, btn_all]:
            b.setStyleSheet("""
                QPushButton {
                    background-color: #1E40AF;
                    color: white;
                    border-radius: 4px;
                    padding: 5px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #123072; }
            """)
        info_layout.addWidget(btn_search, 0, 5)
        info_layout.addWidget(btn_all, 0, 6)

        # Table
        self.table_subject = QTableWidget(0, 3)
        self.table_subject.setHorizontalHeaderLabels(["ID môn học", "Tên môn học", "Lớp tín chỉ"])
        self.table_subject.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #1E40AF;
            }
        """)
        info_layout.addWidget(self.table_subject, 3, 0, 1, 7)

        # Buttons
        btn_add = QPushButton("Thêm mới")
        btn_del = QPushButton("Xoá")
        btn_update = QPushButton("Cập nhật")
        btn_clear = QPushButton("Làm mới")
        for b in [btn_add, btn_del, btn_update, btn_clear]:
            b.setFixedHeight(34)
            b.setStyleSheet("""
                QPushButton {
                    background-color: #1E40AF;
                    color: white;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #123072; }
            """)
        info_layout.addWidget(btn_add, 4, 0)
        info_layout.addWidget(btn_del, 4, 1)
        info_layout.addWidget(btn_update, 4, 2)
        info_layout.addWidget(btn_clear, 4, 3)

        # ===== GROUP 2 + 3: MÔN HỌC GIẢNG VIÊN / SINH VIÊN =====
        bottom_layout = QHBoxLayout()

        def create_subgroup(title, labels, headers):
            group = QGroupBox(title)
            group.setFont(QFont("Arial", 11, QFont.Bold))
            group.setStyleSheet(info_group.styleSheet())
            layout = QGridLayout(group)

            layout.addWidget(QLabel("Tìm kiếm theo:"), 0, 0)
            cb = QComboBox()
            cb.addItems(["ID", "ID môn học"])
            layout.addWidget(cb, 0, 1)
            txt = QLineEdit()
            layout.addWidget(txt, 0, 2)
            btn_s = QPushButton("Tìm kiếm")
            btn_v = QPushButton("Xem tất cả")
            for b in [btn_s, btn_v]:
                b.setStyleSheet("""
                    QPushButton {
                        background-color: #1E40AF;
                        color: white;
                        border-radius: 4px;
                        font-weight: bold;
                        padding: 4px 10px;
                    }
                    QPushButton:hover { background-color: #123072; }
                """)
            layout.addWidget(btn_s, 0, 3)
            layout.addWidget(btn_v, 0, 4)

            for i, text in enumerate(labels):
                layout.addWidget(QLabel(text), i + 1, 0)
                layout.addWidget(QLineEdit(), i + 1, 1)

            table = QTableWidget(0, len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #1E40AF;
                }
            """)
            layout.addWidget(table, 0, 5, 5, 1)

            add = QPushButton("Thêm mới")
            delete = QPushButton("Xoá")
            update = QPushButton("Cập nhật")
            for b in [add, delete, update]:
                b.setStyleSheet("""
                    QPushButton {
                        background-color: #1E40AF; color: white;
                        border-radius: 4px; font-weight: bold;
                        padding: 5px 10px;
                    }
                    QPushButton:hover { background-color: #123072; }
                """)
            layout.addWidget(add, 5, 0)
            layout.addWidget(delete, 5, 1)
            layout.addWidget(update, 5, 2)

            return group

        teacher_group = create_subgroup(
            "Môn học của giảng viên",
            ["ID giảng viên:", "ID môn học:", "Tên giảng viên:", "Tên môn học:"],
            ["ID giảng viên", "ID môn học"]
        )

        student_group = create_subgroup(
            "Môn học của sinh viên",
            ["ID sinh viên:", "ID môn học:", "Tên sinh viên:", "Tên môn học:"],
            ["ID sinh viên", "ID môn học"]
        )

        bottom_layout.addWidget(teacher_group)
        bottom_layout.addWidget(student_group)

        # ===== FINAL LAYOUT =====
        main_layout.addWidget(header)
        main_layout.addWidget(info_group)
        main_layout.addLayout(bottom_layout)

        # Timer for clock
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP"))
        self.date_label.setText(now.toString("dd-MM-yyyy"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = SubjectInfoUI()
    ui.show()
    sys.exit(app.exec_())