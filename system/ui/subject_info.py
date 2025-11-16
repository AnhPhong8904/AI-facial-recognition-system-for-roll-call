import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, 
    QGroupBox, QFrame, QMessageBox, QSpinBox, QTimeEdit, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize, QDate, QTime
from PyQt5.QtGui import QFont, QIcon, QPixmap

class SubjectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý Môn học và Lớp học")
        self.setGeometry(100, 100, 1300, 800) # Cho cửa sổ lớn hơn
        self.setStyleSheet("background-color: white; font-family: Arial;")
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 10, 25, 10)
        main_layout.setSpacing(15)

        # ===== HEADER =====
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 10, 25, 10)

        # Đồng hồ
        clock_icon = QLabel()
        clock_icon_path = r"D:\AI-facial-recognition-system-for-roll-call\system\img\clock.png"
        
        if os.path.exists(clock_icon_path):
            clock_pixmap = QPixmap(clock_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
        clock_icon.setStyleSheet("margin-right: 5px;")

        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0,0,0,0)
        time_layout.addWidget(clock_icon)
        time_layout.addWidget(self.time_label)

        title_label = QLabel("Quản lý Môn học và Lớp học")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 20px;")
        title_label.setAlignment(Qt.AlignCenter)

        # Nút quay lại
        self.back_btn = QPushButton(" Quay lại")
        back_icon_path = r"D:\AI-facial-recognition-system-for-roll-call\system\img\back.png"
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

        header_layout.addLayout(time_layout)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.back_btn)
        
        main_layout.addWidget(header)

        # ===== SPLITTER (CHIA ĐÔI MÀN HÌNH) =====
        # QSplitter cho phép người dùng kéo chia
        splitter = QSplitter(Qt.Vertical)
        
        # --- Phần 1 (Trên): Quản lý Môn học (Master) ---
        subject_group = self.create_subject_group()
        
        # --- Phần 2 (Dưới): Quản lý Lớp học (Detail) ---
        class_group = self.create_class_group()

        splitter.addWidget(subject_group)
        splitter.addWidget(class_group)
        splitter.setSizes([350, 450]) # Tỷ lệ ban đầu

        main_layout.addWidget(splitter)
        
        # Timer for clock
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

    # ==========================================================
    # --- GROUP 1: QUẢN LÝ MÔN HỌC (MASTER) ---
    # ==========================================================
    def create_subject_group(self):
        group = QGroupBox("Quản lý Môn học")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QHBoxLayout(group)
        
        # Form (Bên trái)
        form_widget = QFrame()
        form_layout = QGridLayout(form_widget)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)
        
        self.subject_inputs = {} # Lưu trữ các input

        labels = ["Mã môn học:", "Tên môn học:", "Số tín chỉ:", "Giảng viên phụ trách:"]
        
        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            input_field = None
            
            if label_text == "Số tín chỉ:":
                input_field = QSpinBox()
                input_field.setRange(1, 10)
            elif label_text == "Giảng viên phụ trách:":
                input_field = QComboBox()
            else:
                input_field = QLineEdit()
            
            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(input_field, i, 1)
            self.subject_inputs[label_text] = input_field

        # Buttons
        btn_layout = QHBoxLayout()
        self.subject_btn_add = QPushButton("Thêm")
        self.subject_btn_update = QPushButton("Cập nhật")
        self.subject_btn_delete = QPushButton("Xoá")
        self.subject_btn_refresh = QPushButton("Làm mới")
        
        self.subject_admin_buttons = [self.subject_btn_add, self.subject_btn_update, self.subject_btn_delete]
        
        for btn in [self.subject_btn_add, self.subject_btn_update, self.subject_btn_delete, self.subject_btn_refresh]:
            btn.setStyleSheet("background-color: #1e40af; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;")
            btn_layout.addWidget(btn)

        form_layout.addLayout(btn_layout, len(labels), 0, 1, 2)
        
        # Bảng (Bên phải)
        table_panel = QWidget()
        table_layout = QVBoxLayout(table_panel)
        
        search_layout = QHBoxLayout()
        self.subject_search_by = QComboBox()
        self.subject_search_by.addItems(["Mã môn học", "Tên môn học"])
        self.subject_search_input = QLineEdit()
        self.subject_search_input.setPlaceholderText("Nhập từ khóa...")
        self.subject_btn_search = QPushButton("Tìm kiếm")
        self.subject_btn_all = QPushButton("Xem tất cả")
        
        for btn in [self.subject_btn_search, self.subject_btn_all]:
            btn.setStyleSheet("background-color: #1e40af; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;")

        search_layout.addWidget(QLabel("Tìm kiếm:"), 0)
        search_layout.addWidget(self.subject_search_by, 1)
        search_layout.addWidget(self.subject_search_input, 2)
        search_layout.addWidget(self.subject_btn_search, 0)
        search_layout.addWidget(self.subject_btn_all, 0)

        self.table_subject = QTableWidget()
        self.table_subject.setColumnCount(4)
        self.table_subject.setHorizontalHeaderLabels(["Mã môn", "Tên môn học", "Số tín chỉ", "Giảng viên"])
        self.table_subject.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_subject.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_subject.setEditTriggers(QTableWidget.NoEditTriggers)

        table_layout.addLayout(search_layout)
        table_layout.addWidget(self.table_subject)
        
        layout.addWidget(form_widget, 2) # 2/5
        layout.addWidget(table_panel, 3) # 3/5
        return group

    # ==========================================================
    # --- GROUP 2: QUẢN LÝ LỚP HỌC (DETAIL) ---
    # ==========================================================
    def create_class_group(self):
        group = QGroupBox("Quản lý Lớp học (Vui lòng chọn một môn học ở trên)")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QHBoxLayout(group)
        
        self.class_group_box = group # Lưu tham chiếu để đổi tiêu đề
        
        # Form (Bên trái)
        form_widget = QFrame()
        form_layout = QGridLayout(form_widget)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)
        
        self.class_inputs = {} # Lưu trữ các input
        
        # Dùng một QLineEdit ẩn để lưu ID_LOP khi chọn từ bảng
        self.hidden_id_lop = QLineEdit()

        labels = ["Mã Lớp:", "Tên Lớp:", "Năm học:", "Học kỳ:", "Thứ học:", "Giờ bắt đầu:", "Giờ kết thúc:", "Phòng học:"]
        
        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            input_field = None
            
            if label_text == "Giờ bắt đầu:" or label_text == "Giờ kết thúc:":
                input_field = QTimeEdit()
                input_field.setDisplayFormat("HH:mm")
            elif label_text == "Thứ học:":
                input_field = QComboBox()
                input_field.addItems(["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"])
            else:
                input_field = QLineEdit()
            
            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(input_field, i, 1)
            self.class_inputs[label_text] = input_field

        # Buttons
        btn_layout = QHBoxLayout()
        self.class_btn_add = QPushButton("Thêm Lớp")
        self.class_btn_update = QPushButton("Cập nhật Lớp")
        self.class_btn_delete = QPushButton("Xoá Lớp")
        self.class_btn_refresh = QPushButton("Làm mới")
        
        self.class_admin_buttons = [self.class_btn_add, self.class_btn_update, self.class_btn_delete]
        
        for btn in [self.class_btn_add, self.class_btn_update, self.class_btn_delete, self.class_btn_refresh]:
            btn.setStyleSheet("background-color: #006400; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;")
            btn_layout.addWidget(btn)

        form_layout.addLayout(btn_layout, len(labels), 0, 1, 2)
        
        # Bảng (Bên phải)
        table_panel = QWidget()
        table_layout = QVBoxLayout(table_panel)
        
        # Bảng Lớp học
        self.table_class = QTableWidget()
        self.table_class.setColumnCount(9)
        self.table_class.setHorizontalHeaderLabels(["ID Lớp", "Mã Lớp", "Tên Lớp", "Năm học", "Học kỳ", "Thứ", "Giờ BĐ", "Giờ KT", "Phòng học"])
        self.table_class.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_class.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_class.setEditTriggers(QTableWidget.NoEditTriggers)

        table_layout.addWidget(self.table_class)
        
        layout.addWidget(form_widget, 2) # 2/5
        layout.addWidget(table_panel, 3) # 3/5
        
        # Mặc định tắt group này đi
        group.setEnabled(False)
        return group


    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\ndd-MM-yyyy"))

    # ==========================================================
    # HÀM TIỆN ÍCH (HELPER FUNCTIONS)
    # Controller sẽ gọi các hàm này
    # ==========================================================
    
    def show_message(self, title, message, level="info"):
        """Hiển thị hộp thoại thông báo"""
        if level == "info":
            QMessageBox.information(self, title, message)
        elif level == "warning":
            QMessageBox.warning(self, title, message)
        elif level == "error":
            QMessageBox.critical(self, title, message)
        elif level == "question":
            return QMessageBox.question(self, title, message, 
                                        QMessageBox.Yes | QMessageBox.No, 
                                        QMessageBox.No)
                                        
    # --- Tiện ích cho Môn học (Master) ---

    def populate_gv_combo(self, teachers_data):
        combo = self.subject_inputs["Giảng viên phụ trách:"]
        combo.clear()
        combo.addItem("--- Không có ---", None)
        if teachers_data:
            for id_gv, ho_ten in teachers_data:
                combo.addItem(f"{ho_ten} (ID: {id_gv})", id_gv) 

    def populate_subject_table(self, data):
        self.table_subject.setRowCount(0)
        if not data:
            return
        self.table_subject.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for col_index, item in enumerate(row_data):
                item_str = str(item) if item is not None else ""
                cell_item = QTableWidgetItem(item_str)
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable) 
                self.table_subject.setItem(row_index, col_index, cell_item)
        self.table_subject.resizeColumnsToContents()

    def get_subject_form_data(self):
        return {
            "ma_mon": self.subject_inputs["Mã môn học:"].text(),
            "ten_mon": self.subject_inputs["Tên môn học:"].text(),
            "so_tin_chi": self.subject_inputs["Số tín chỉ:"].value(),
            "id_gv": self.subject_inputs["Giảng viên phụ trách:"].currentData()
        }
        
    def get_selected_ma_mon(self):
        selected_rows = self.table_subject.selectionModel().selectedRows()
        if not selected_rows:
            return None
        selected_row = selected_rows[0].row()
        ma_mon_item = self.table_subject.item(selected_row, 0)
        return ma_mon_item.text() if ma_mon_item else None
        
    def clear_subject_form(self):
        self.subject_inputs["Mã môn học:"].clear()
        self.subject_inputs["Tên môn học:"].clear()
        self.subject_inputs["Số tín chỉ:"].setValue(1)
        self.subject_inputs["Giảng viên phụ trách:"].setCurrentIndex(0)
        self.subject_inputs["Mã môn học:"].setEnabled(True)
        self.table_subject.clearSelection()

    # --- Tiện ích cho Lớp học (Detail) ---
    
    def set_selected_subject(self, ma_mon, ten_mon):
        """Kích hoạt Group Lớp học và đặt tiêu đề"""
        self.class_group_box.setEnabled(True)
        self.class_group_box.setTitle(f"Quản lý Lớp học cho môn: {ten_mon} ({ma_mon})")

    def disable_class_group(self):
        """Tắt Group Lớp học (khi không có Môn học nào được chọn)"""
        self.class_group_box.setEnabled(False)
        self.class_group_box.setTitle("Quản lý Lớp học (Vui lòng chọn một môn học ở trên)")
        
    def populate_class_table(self, data):
        self.table_class.setRowCount(0)
        if not data:
            return
        self.table_class.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for col_index, item in enumerate(row_data):
                item_str = str(item) if item is not None else ""
                cell_item = QTableWidgetItem(item_str)
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable) 
                self.table_class.setItem(row_index, col_index, cell_item)
        self.table_class.resizeColumnsToContents()

    def get_class_form_data(self):
        return {
            "id_lop": self.hidden_id_lop.text(),
            "ma_lop": self.class_inputs["Mã Lớp:"].text(),
            "ten_lop": self.class_inputs["Tên Lớp:"].text(),
            "nam_hoc": self.class_inputs["Năm học:"].text(),
            "hoc_ky": self.class_inputs["Học kỳ:"].text(),
            "thu_hoc": self.class_inputs["Thứ học:"].currentText(),
            "gio_bd": self.class_inputs["Giờ bắt đầu:"].time().toString("HH:mm"),
            "gio_kt": self.class_inputs["Giờ kết thúc:"].time().toString("HH:mm"),
            "phong_hoc": self.class_inputs["Phòng học:"].text()
        }

    def clear_class_form(self):
        self.hidden_id_lop.clear()
        self.class_inputs["Mã Lớp:"].clear()
        self.class_inputs["Tên Lớp:"].clear()
        self.class_inputs["Năm học:"].clear()
        self.class_inputs["Học kỳ:"].clear()
        self.class_inputs["Thứ học:"].setCurrentIndex(0)
        self.class_inputs["Giờ bắt đầu:"].setTime(QTime(7, 0))
        self.class_inputs["Giờ kết thúc:"].setTime(QTime(9, 0))
        self.class_inputs["Phòng học:"].clear()
        self.class_inputs["Mã Lớp:"].setEnabled(True)
        self.table_class.clearSelection()

    def set_admin_mode(self, is_admin):
        """Phân quyền cho cả 2 group"""
        # Phân quyền Môn học
        for btn in self.subject_admin_buttons:
            btn.setEnabled(is_admin)
        for widget in [self.subject_inputs["Mã môn học:"], 
                       self.subject_inputs["Tên môn học:"],
                       self.subject_inputs["Số tín chỉ:"], 
                       self.subject_inputs["Giảng viên phụ trách:"]]:
            widget.setEnabled(is_admin)
            
        # Phân quyền Lớp học
        for btn in self.class_admin_buttons:
            btn.setEnabled(is_admin)
        for widget in self.class_inputs.values():
            widget.setEnabled(is_admin)
            
        # Nút "Làm mới" luôn bật
        self.subject_btn_refresh.setEnabled(True)
        self.class_btn_refresh.setEnabled(True)