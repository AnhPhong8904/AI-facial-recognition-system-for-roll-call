import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QDateEdit, QMessageBox, QFrame, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

class StudentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin Sinh viên và Đăng ký")
        self.setGeometry(100, 100, 1300, 800) # Cho cửa sổ lớn hơn
        self.setStyleSheet("background-color: white; font-family: Arial;")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.header_ui())
        
        # === SPLITTER CHIA ĐÔI MÀN HÌNH ===
        splitter = QSplitter(Qt.Horizontal)
        
        # --- BÊN TRÁI: Form Thông tin Sinh viên ---
        splitter.addWidget(self.create_student_form_panel())
        
        # --- BÊN PHẢI: Bảng (Sinh viên + Đăng ký) ---
        splitter.addWidget(self.create_student_tables_panel())

        # Set tỷ lệ ban đầu (Bên trái 1 phần, Bên phải 2 phần)
        splitter.setSizes([450, 850]) 
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Cập nhật thời gian
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

    # ---------------- Header ----------------
    def header_ui(self):
        header = QFrame()
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header.setFixedHeight(80)
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

        title_label = QLabel("Quản lý Sinh viên và Đăng ký Lớp học")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label, stretch=1)

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

    # ---------------- Panel 1: Form Sinh viên (Bên trái) ----------------
    def create_student_form_panel(self):
        info_group = QGroupBox("Thông tin Sinh viên")
        info_group.setFont(QFont("Arial", 10, QFont.Bold))
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)

        # === Các trường thông tin ===
        labels = [
            "Mã sinh viên:", "Họ tên:", "Giới tính:", "Ngày sinh:",
            "Email:", "Số điện thoại:", "Ngành học:", "Năm học:",
            "Lớp hành chính:", "Trạng thái:"
        ]
        
        self.inputs = {} # Dictionary để lưu trữ các QWidget nhập liệu

        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            input_field = None
            
            if label_text == "Giới tính:":
                input_field = QComboBox()
                input_field.addItems(["", "Nam", "Nữ", "Khác"])
            elif label_text == "Ngày sinh:":
                input_field = QDateEdit()
                input_field.setDisplayFormat("dd-MM-yyyy")
                input_field.setCalendarPopup(True)
                input_field.setDate(QDate(2000, 1, 1))
            elif label_text == "Trạng thái:":
                input_field = QComboBox()
                input_field.addItems(["Đang học", "Đã tốt nghiệp", "Bị đình chỉ"])
                # Lưu ý: Controller sẽ chuyển 'Đang học' thành 1, còn lại là 0
            else:
                input_field = QLineEdit()
                if label_text == "Mã sinh viên:":
                    input_field.setToolTip("Ví dụ: SV001. Mã này phải là duy nhất.")
            
            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(input_field, i, 1)
            self.inputs[label_text] = input_field

        # === Nút chức năng (Thêm/Sửa/Xóa SV) ===
        btn_layout = QHBoxLayout()
        self.btn_add_student = QPushButton("Thêm SV")
        self.btn_update_student = QPushButton("Cập nhật SV")
        self.btn_delete_student = QPushButton("Xoá SV")
        self.btn_refresh_student = QPushButton("Làm mới")

        for btn in [self.btn_add_student, self.btn_update_student, self.btn_delete_student, self.btn_refresh_student]:
            btn.setStyleSheet("background-color: #1e40af; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;")
            btn_layout.addWidget(btn)

        form_layout.addLayout(btn_layout, len(labels), 0, 1, 2)
        
        # === Nút Nhận diện (Huấn luyện) ===
        training_layout = QGridLayout()
        self.btn_take_photo = QPushButton("1. Lấy ảnh Nhận diện")
        self.btn_train = QPushButton("2. Huấn luyện Model")
        
        for btn in [self.btn_take_photo, self.btn_train]:
            btn.setStyleSheet("background-color: #006400; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;")
        
        training_layout.addWidget(self.btn_take_photo, 0, 0)
        training_layout.addWidget(self.btn_train, 0, 1)
        
        form_layout.addLayout(training_layout, len(labels)+1, 0, 1, 2)
        
        info_group.setLayout(form_layout)
        return info_group

    # ---------------- Panel 2: Bảng (Bên phải) ----------------
    def create_student_tables_panel(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # === Nửa trên: Bảng Sinh viên (Master) ===
        student_group = QGroupBox("Danh sách Sinh viên")
        student_group.setFont(QFont("Arial", 10, QFont.Bold))
        student_layout = QVBoxLayout(student_group)
        
        search_layout = QHBoxLayout()
        self.search_by = QComboBox()
        self.search_by.addItems(["Mã sinh viên", "Tên sinh viên", "Email", "SĐT", "Lớp hành chính"])
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa...")
        self.btn_search = QPushButton("Tìm kiếm")
        self.btn_all = QPushButton("Xem tất cả")

        for btn in [self.btn_search, self.btn_all]:
            btn.setStyleSheet("background-color: #1e40af; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;")

        search_layout.addWidget(QLabel("Tìm kiếm theo:"))
        search_layout.addWidget(self.search_by)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_all)

        self.table_student = QTableWidget()
        self.table_student.setColumnCount(10) # Đủ 10 cột
        self.table_student.setHorizontalHeaderLabels([
            "Mã SV", "Họ tên", "Giới tính", "Ngày sinh", 
            "Email", "SĐT", "Ngành", "Năm học", "Lớp HC", "Trạng thái"
        ])
        self.table_student.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_student.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_student.setEditTriggers(QTableWidget.NoEditTriggers)

        student_layout.addLayout(search_layout)
        student_layout.addWidget(self.table_student)
        
        # === Nửa dưới: Bảng Đăng ký (Detail) ===
        self.registration_group = QGroupBox("Đăng ký Lớp học (Vui lòng chọn 1 sinh viên)")
        self.registration_group.setFont(QFont("Arial", 10, QFont.Bold))
        registration_layout = QVBoxLayout(self.registration_group)

        # Hàng 1: Thêm Đăng ký
        add_reg_layout = QHBoxLayout()
        add_reg_layout.addWidget(QLabel("Đăng ký Lớp học mới:"))
        self.combo_lophoc = QComboBox() # ComboBox để chọn Lớp học
        self.combo_lophoc.setToolTip("Danh sách các lớp học sinh viên CHƯA đăng ký")
        self.btn_add_registration = QPushButton("Đăng ký")
        self.btn_add_registration.setStyleSheet("background-color: #006400; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;")
        
        add_reg_layout.addWidget(self.combo_lophoc, 1)
        add_reg_layout.addWidget(self.btn_add_registration)
        
        # Hàng 2: Bảng Lớp học đã đăng ký
        self.table_registration = QTableWidget()
        self.table_registration.setColumnCount(5)
        self.table_registration.setHorizontalHeaderLabels([
            "ID Đăng ký", "Mã Lớp", "Tên Lớp học", "Tên Môn học", "Hủy"
        ])
        self.table_registration.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_registration.setEditTriggers(QTableWidget.NoEditTriggers)

        registration_layout.addLayout(add_reg_layout)
        registration_layout.addWidget(self.table_registration)
        
        # Mặc định tắt group này
        self.registration_group.setEnabled(False)

        # Gộp 2 nửa (Trên và Dưới)
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(student_group)
        splitter.addWidget(self.registration_group)
        splitter.setSizes([300, 300]) # Tỷ lệ ban đầu

        main_layout.addWidget(splitter)
        return main_widget

    # ---------------- Update Time ----------------
    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\ndd-MM-yyyy"))

    # ==========================================================
    # HÀM TIỆN ÍCH (HELPER FUNCTIONS)
    # Controller sẽ gọi các hàm này
    # ==========================================================

    def show_message(self, title, message, level="info"):
        """Hiển thị hộp thoại thông báo"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if level == "info":
            msg_box.setIcon(QMessageBox.Information)
        elif level == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif level == "error":
            msg_box.setIcon(QMessageBox.Critical)
        elif level == "question":
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            return msg_box.exec_()

        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    # --- Tiện ích cho Sinh viên (Bên trái & Bảng trên) ---

    def get_student_form_data(self):
        """Lấy dữ liệu từ form Sinh viên"""
        trang_thai_text = self.inputs["Trạng thái:"].currentText()
        trang_thai_bit = 1 if trang_thai_text == "Đang học" else 0
        
        ngay_sinh_qdate = self.inputs["Ngày sinh:"].date()
        # Xử lý ngày sinh: Nếu là ngày mặc định, lưu NULL
        ngay_sinh_sql = None
        if ngay_sinh_qdate != QDate(2000, 1, 1):
            ngay_sinh_sql = ngay_sinh_qdate.toString("yyyy-MM-dd")

        data = {
            "ma_sv": self.inputs["Mã sinh viên:"].text(),
            "ho_ten": self.inputs["Họ tên:"].text(),
            "gioi_tinh": self.inputs["Giới tính:"].currentText(),
            "ngay_sinh": ngay_sinh_sql,
            "email": self.inputs["Email:"].text(),
            "sdt": self.inputs["Số điện thoại:"].text(),
            "nganh": self.inputs["Ngành học:"].text(),
            "nam_hoc": self.inputs["Năm học:"].text(),
            "lop_hoc": self.inputs["Lớp hành chính:"].text(),
            "trang_thai": trang_thai_bit
        }
        return data

    def set_student_form_data(self, data):
        """Điền dữ liệu (từ bảng) vào form Sinh viên"""
        self.inputs["Mã sinh viên:"].setText(data.get("ma_sv", ""))
        self.inputs["Họ tên:"].setText(data.get("ho_ten", ""))
        self.inputs["Giới tính:"].setCurrentText(data.get("gioi_tinh", ""))
        
        ngay_sinh_str = data.get("ngay_sinh", "")
        if ngay_sinh_str:
            self.inputs["Ngày sinh:"].setDate(QDate.fromString(ngay_sinh_str, "yyyy-MM-dd"))
        else:
            self.inputs["Ngày sinh:"].setDate(QDate(2000, 1, 1))

        self.inputs["Email:"].setText(data.get("email", ""))
        self.inputs["Số điện thoại:"].setText(data.get("sdt", ""))
        self.inputs["Ngành học:"].setText(data.get("nganh", ""))
        self.inputs["Năm học:"].setText(data.get("nam_hoc", ""))
        self.inputs["Lớp hành chính:"].setText(data.get("lop_hoc", ""))
        
        trang_thai_str = "Đang học" if data.get("trang_thai", 1) == 1 else "Đã tốt nghiệp"
        self.inputs["Trạng thái:"].setCurrentText(trang_thai_str)

    def clear_student_form(self):
        """Xóa trắng form Sinh viên"""
        self.inputs["Mã sinh viên:"].clear()
        self.inputs["Họ tên:"].clear()
        self.inputs["Giới tính:"].setCurrentIndex(0) 
        self.inputs["Ngày sinh:"].setDate(QDate(2000, 1, 1))
        self.inputs["Email:"].clear()
        self.inputs["Số điện thoại:"].clear()
        self.inputs["Ngành học:"].clear()
        self.inputs["Năm học:"].clear()
        self.inputs["Lớp hành chính:"].clear()
        self.inputs["Trạng thái:"].setCurrentIndex(0)
        
        self.inputs["Mã sinh viên:"].setEnabled(True)
        self.table_student.clearSelection()

    def populate_student_table(self, data):
        """Điền dữ liệu (list of tuples) vào bảng Sinh viên"""
        self.table_student.setRowCount(0)
        if not data:
            return
            
        self.table_student.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            # Cột cuối (Trạng thái)
            trang_thai_bit = row_data[9]
            trang_thai_str = "Đang học" if trang_thai_bit == 1 else "Nghỉ học"
            
            for col_index, item in enumerate(row_data[:-1]): # Lấy 9 cột đầu
                item_str = str(item) if item is not None else ""
                cell_item = QTableWidgetItem(item_str)
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable) 
                self.table_student.setItem(row_index, col_index, cell_item)
            
            # Set cột Trạng thái (cuối cùng)
            cell_item_trang_thai = QTableWidgetItem(trang_thai_str)
            cell_item_trang_thai.setFlags(cell_item_trang_thai.flags() & ~Qt.ItemIsEditable) 
            self.table_student.setItem(row_index, 9, cell_item_trang_thai)
        
        self.table_student.resizeColumnsToContents()

    def get_search_data(self):
        """Lấy thông tin tìm kiếm Sinh viên"""
        return {
            "search_by": self.search_by.currentText(),
            "keyword": self.search_input.text()
        }

    def get_selected_ma_sv(self):
        """Lấy MA_SV của hàng đang được chọn"""
        selected_rows = self.table_student.selectionModel().selectedRows()
        if not selected_rows:
            return None
        
        selected_row = selected_rows[0].row()
        ma_sv_item = self.table_student.item(selected_row, 0)
        return ma_sv_item.text() if ma_sv_item else None

    # --- Tiện ích cho Đăng ký (Bảng dưới) ---
    
    def set_registration_panel_enabled(self, enabled, student_name=""):
        """Bật/Tắt group Đăng ký Lớp học"""
        self.registration_group.setEnabled(enabled)
        if enabled:
            self.registration_group.setTitle(f"Đăng ký Lớp học cho: {student_name}")
        else:
            self.registration_group.setTitle("Đăng ký Lớp học (Vui lòng chọn 1 sinh viên)")

    def populate_lophoc_combo(self, classes_data):
        """Điền ComboBox Lớp học (Chưa đăng ký)"""
        self.combo_lophoc.clear()
        self.combo_lophoc.addItem("--- Chọn Lớp học để đăng ký ---", None)
        if classes_data:
            for id_lop, ma_lop, ten_lop in classes_data:
                self.combo_lophoc.addItem(f"{ma_lop} - {ten_lop}", id_lop)

    def populate_registration_table(self, data):
        """Điền Bảng Lớp học (Đã đăng ký)"""
        self.table_registration.setRowCount(0)
        if not data:
            return
            
        self.table_registration.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            # (ID_DK, MA_LOP, TEN_LOP, TEN_MON)
            id_dk, ma_lop, ten_lop, ten_mon = row_data
            
            self.table_registration.setItem(row_index, 0, QTableWidgetItem(str(id_dk)))
            self.table_registration.setItem(row_index, 1, QTableWidgetItem(ma_lop))
            self.table_registration.setItem(row_index, 2, QTableWidgetItem(ten_lop))
            self.table_registration.setItem(row_index, 3, QTableWidgetItem(ten_mon))
            
            # Tạo nút Hủy
            delete_btn = QPushButton("Hủy")
            delete_btn.setStyleSheet("background-color: #DC2626; color: white; padding: 3px 5px; border-radius: 4px; font-weight: bold;")
            delete_btn.setCursor(Qt.PointingHandCursor)
            # Lưu ID_DK (ID Đăng ký) vào nút để Controller biết xóa cái nào
            delete_btn.setProperty("id_dk", id_dk) 
            
            self.table_registration.setCellWidget(row_index, 4, delete_btn)
        
        self.table_registration.resizeColumnsToContents()