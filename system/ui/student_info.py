import sys
import os  # SỬA: Thêm import
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit,
    QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize  # SỬA: Thêm QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon  # SỬA: Thêm QPixmap, QIcon


class StudentInfoUI(QWidget):
    def __init__(self):
        super().__init__()

        # Dữ liệu mẫu
        self.class_data = [
            {"code": "CNTT101", "name": "Lập trình Python", "teacher": "Nguyễn A"},
            {"code": "CNTT102", "name": "Cấu trúc dữ liệu", "teacher": "Trần B"},
            {"code": "CNTT201", "name": "Mạng máy tính", "teacher": "Lê C"},
            {"code": "CNTT202", "name": "Cơ sở dữ liệu", "teacher": "Phạm D"},
            {"code": "KT101", "name": "Toán rời rạc", "teacher": "Võ E"},
        ]

        self.student_data = [
            {"id": "SV001", "name": "Nguyễn Văn A", "class": "CNTT101", "phone": "0901111001"},
            {"id": "SV002", "name": "Trần Thị B", "class": "CNTT102", "phone": "0901111002"},
            {"id": "SV003", "name": "Lê Văn C", "class": "CNTT201", "phone": "0901111003"},
            {"id": "SV004", "name": "Phạm Thị D", "class": "CNTT202", "phone": "0901111004"},
            {"id": "SV005", "name": "Võ Văn E", "class": "KT101", "phone": "0901111005"},
        ]

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Quản lý thông tin sinh viên")
        self.setGeometry(150, 50, 1200, 750)
        self.setStyleSheet("background-color: white; font-family: Arial;")

        # ======== HEADER ========
        header = QFrame()
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header.setFixedHeight(80)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(25, 10, 25, 10)  # SỬA: Thêm lề đồng bộ

        # SỬA: ===== THÊM ICON ĐỒNG HỒ =====
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

        # Đồng hồ
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: white; font-size: 14px;")
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        
        time_layout.addWidget(self.time_label) # Thêm nhãn thời gian vào nhóm

        title_label = QLabel("Quản lý thông tin sinh viên") # SỬA: Đổi tiêu đề
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 18px;")

        # SỬA: ===== THÊM ICON NÚT QUAY LẠI =====
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

        header_layout.addLayout(time_layout) # SỬA: Thêm nhóm layout
        header_layout.addStretch(1)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(back_btn)
        header.setLayout(header_layout)

        # ======== THÔNG TIN SINH VIÊN ========
        group_sv = QGroupBox("Thông tin sinh viên")
        group_sv.setStyleSheet("""
            QGroupBox {
                color: #0B3D91;
                font-weight: bold;
                font-size: 18px;
                border: 3px solid #0B3D91;
                border-radius: 10px;
                margin-top: 20px;
                padding-top: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                background-color: white;
            }
        """)

        group_layout = QVBoxLayout()

        # --- Hàng 1: Thông tin khóa học + Tìm kiếm ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)

        # ----- Thông tin khóa học -----
        course_box = QGroupBox("Thông tin khóa học")
        course_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #0B3D91;
                border: 2px solid #0B3D91;
                border-radius: 8px;
                margin-top: 18px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: white;
            }
        """)
        course_layout = QGridLayout()
        course_layout.addWidget(QLabel("Chuyên ngành:"), 0, 0)
        major_cb = QComboBox()
        major_cb.addItems(["CNTT", "KT", "NN"])
        course_layout.addWidget(major_cb, 0, 1)
        course_layout.addWidget(QLabel("Hệ đào tạo:"), 0, 2)
        degree_cb = QComboBox()
        degree_cb.addItems(["Chính quy", "Tại chức"])
        course_layout.addWidget(degree_cb, 0, 3)
        course_layout.addWidget(QLabel("Năm học:"), 1, 0)
        course_layout.addWidget(QLineEdit(), 1, 1)
        course_layout.addWidget(QLabel("Học kì:"), 1, 2)
        course_layout.addWidget(QLineEdit(), 1, 3)
        course_box.setLayout(course_layout)

        # ----- Tìm kiếm -----
        search_box = QGroupBox("Tìm kiếm")
        search_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #0B3D91;
                border: 2px solid #0B3D91;
                border-radius: 8px;
                margin-top: 18px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: white;
            }
        """)
        search_layout = QGridLayout()
        search_layout.addWidget(QLabel("Tìm theo:"), 0, 0)
        self.search_field_cb = QComboBox()
        self.search_field_cb.addItems(["ID", "Tên", "Lớp", "SĐT"])
        search_layout.addWidget(self.search_field_cb, 0, 1)
        search_layout.addWidget(QLabel("Từ khoá:"), 0, 2)
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input, 0, 3)

        self.search_btn = QPushButton("Tìm kiếm")
        self.search_btn.setFixedWidth(100)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B3D91;
                color: white;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1E5CC5; }
        """)
        self.search_btn.clicked.connect(self.search_student)
        search_layout.addWidget(self.search_btn, 0, 4)

        self.view_all_students_btn = QPushButton("Xem tất cả")
        self.view_all_students_btn.setFixedWidth(100)
        self.view_all_students_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B3D91;
                color: white;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1E5CC5; }
        """)
        self.view_all_students_btn.clicked.connect(self.view_all_students)
        search_layout.addWidget(self.view_all_students_btn, 0, 5)

        self.student_table = QTableWidget(0, 4)
        self.student_table.setHorizontalHeaderLabels(["ID sinh viên", "Tên sinh viên", "Lớp học", "Số điện thoại"])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        search_layout.addWidget(self.student_table, 1, 0, 1, 6)
        search_box.setLayout(search_layout)

        top_layout.addWidget(course_box, 1)
        top_layout.addWidget(search_box, 2)

        # ----- Thông tin lớp học -----
        class_box = QGroupBox("Thông tin lớp học")
        class_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #0B3D91;
                border: 2px solid #0B3D91;
                border-radius: 8px;
                margin-top: 18px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: white;
            }
        """)
        class_layout = QGridLayout()
        class_layout.addWidget(QLabel("ID sinh viên:"), 0, 0)
        class_layout.addWidget(QLineEdit(), 0, 1)
        class_layout.addWidget(QLabel("Tên sinh viên:"), 0, 2)
        class_layout.addWidget(QLineEdit(), 0, 3)
        class_layout.addWidget(QLabel("Lớp học:"), 1, 0)
        class_layout.addWidget(QComboBox(), 1, 1)
        class_layout.addWidget(QLabel("Số điện thoại:"), 1, 2)
        class_layout.addWidget(QLineEdit(), 1, 3)
        class_layout.addWidget(QLabel("Giới tính:"), 2, 0)
        class_layout.addWidget(QComboBox(), 2, 1)
        class_layout.addWidget(QLabel("Ngày sinh:"), 2, 2)
        class_layout.addWidget(QLineEdit(), 2, 3)
        class_box.setLayout(class_layout)

        # ----- Nút -----
        btn_layout = QHBoxLayout()
        for text in ["Lưu", "Sửa", "Xoá", "Làm mới"]:
            btn = QPushButton(text)
            btn.setFixedWidth(100)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B3D91;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 6px;
                }
                QPushButton:hover { background-color: #1E5CC5; }
            """)
            btn_layout.addWidget(btn)

        special_layout = QHBoxLayout()
        for text in ["Lấy danh sinh viên", "Huấn luyện mô hình"]:
            btn = QPushButton(text)
            btn.setFixedWidth(180)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B3D91;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 6px;
                }
                QPushButton:hover { background-color: #1E5CC5; }
            """)
            special_layout.addWidget(btn)

        # Gộp vào layout
        group_layout.addLayout(top_layout)
        group_layout.addWidget(class_box)
        group_layout.addLayout(btn_layout)
        group_layout.addLayout(special_layout)
        group_sv.setLayout(group_layout)

        # ======== QUẢN LÝ LỚP HỌC ========
        group_class = QGroupBox("Quản lý lớp học")
        group_class.setStyleSheet("""
            QGroupBox {
                color: #0B3D91;
                font-weight: bold;
                font-size: 18px;
                border: 3px solid #0B3D91;
                border-radius: 10px;
                margin-top: 18px;
                padding-top: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                background-color: white;
            }
        """)

        layout_class = QGridLayout()
        layout_class.addWidget(QLabel("Tìm kiếm theo:"), 0, 0)
        self.class_search_combo = QComboBox()
        self.class_search_combo.addItems(["Mã lớp", "Tên lớp"])
        layout_class.addWidget(self.class_search_combo, 0, 1)
        layout_class.addWidget(QLabel("Từ khóa:"), 0, 2)
        self.class_search_input = QLineEdit()
        layout_class.addWidget(self.class_search_input, 0, 3)

        self.class_search_btn = QPushButton("Tìm kiếm")
        self.class_search_btn.setFixedWidth(120)
        self.class_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B3D91;
                color: white;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1E5CC5; }
        """)
        self.class_search_btn.clicked.connect(self.search_class)
        layout_class.addWidget(self.class_search_btn, 0, 4)

        self.class_view_all_btn = QPushButton("Xem tất cả")
        self.class_view_all_btn.setFixedWidth(120)
        self.class_view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B3D91;
                color: white;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1E5CC5; }
        """)
        self.class_view_all_btn.clicked.connect(self.view_all_classes)
        layout_class.addWidget(self.class_view_all_btn, 0, 5)

        # Nút thao tác lớp
        btn_layout2 = QHBoxLayout()
        for text in ["Thêm mới", "Xoá", "Cập nhật"]:
            btn = QPushButton(text)
            btn.setFixedWidth(120)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B3D91;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 6px;
                }
                QPushButton:hover { background-color: #1E5CC5; }
            """)
            btn_layout2.addWidget(btn)
        layout_class.addLayout(btn_layout2, 1, 0, 1, 6)

        # Bảng lớp
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Mã lớp", "Tên lớp", "Giảng viên"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_class.addWidget(self.table, 2, 0, 1, 6)
        group_class.setLayout(layout_class)

        # ======== TỔNG ========
        main_layout = QVBoxLayout()
        main_layout.addWidget(header)
        main_layout.addSpacing(10)
        main_layout.addWidget(group_sv)
        main_layout.addWidget(group_class)
        self.setLayout(main_layout)

        # Populate
        self.populate_class_table(self.class_data)
        self.populate_student_table(self.student_data)

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\n dd-MM-yyyy"))

    # ---------- Students ----------
    def populate_student_table(self, data):
        self.student_table.setRowCount(0)
        for i, s in enumerate(data):
            self.student_table.insertRow(i)
            self.student_table.setItem(i, 0, QTableWidgetItem(s["id"]))
            self.student_table.setItem(i, 1, QTableWidgetItem(s["name"]))
            self.student_table.setItem(i, 2, QTableWidgetItem(s["class"]))
            self.student_table.setItem(i, 3, QTableWidgetItem(s["phone"]))

    def search_student(self):
        field_map = {"ID": "id", "Tên": "name", "Lớp": "class", "SĐT": "phone"}
        field = field_map[self.search_field_cb.currentText()]
        keyword = self.search_input.text().strip().lower()
        if not keyword:
            self.populate_student_table(self.student_data)
            return
        filtered = [s for s in self.student_data if keyword in s[field].lower()]
        self.populate_student_table(filtered)

    def view_all_students(self):
        self.search_input.clear()
        self.populate_student_table(self.student_data)

    # ---------- Classes ----------
    def populate_class_table(self, data):
        self.table.setRowCount(0)
        for i, c in enumerate(data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(c["code"]))
            self.table.setItem(i, 1, QTableWidgetItem(c["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(c["teacher"]))

    def search_class(self):
        keyword = self.class_search_input.text().strip().lower()
        if not keyword:
            self.populate_class_table(self.class_data)
            return
        if self.class_search_combo.currentText() == "Mã lớp":
            filtered = [c for c in self.class_data if keyword in c["code"].lower()]
        else:
            filtered = [c for c in self.class_data if keyword in c["name"].lower()]
        self.populate_class_table(filtered)

    def view_all_classes(self):
        self.class_search_input.clear()
        self.populate_class_table(self.class_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentInfoUI()
    window.show()
    sys.exit(app.exec_())