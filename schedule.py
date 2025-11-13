import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, 
    QGroupBox, QFrame, QMessageBox, QTimeEdit, QDateEdit
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize, QDate, QTime
from PyQt5.QtGui import QFont, QIcon, QPixmap

class ScheduleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin Lịch học (Buổi học)")
        self.setGeometry(100, 100, 1000, 600)
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
        clock_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\clock.png"
        
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

        title_label = QLabel("Quản lý thông tin Lịch học (Buổi học)")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 20px;")
        title_label.setAlignment(Qt.AlignCenter)

        # Nút quay lại
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

        header_layout.addLayout(time_layout)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.back_btn)
        
        main_layout.addWidget(header)

        # ===== CONTENT (ĐÃ SỬA ĐỔI) =====
        content_layout = QHBoxLayout()
        
        # --- LEFT PANEL ---
        info_group = QGroupBox("Thông tin buổi học")
        info_group.setFont(QFont("Arial", 10, QFont.Bold))
        form_layout = QGridLayout()
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)
        
        self.inputs = {} # Lưu trữ các input

        # === Form fields (Đã sửa đổi cho khớp CSDL) ===
        # 1. ComboBox (Hộp chọn) cho Lớp học
        form_layout.addWidget(QLabel("Chọn Lớp học:"), 0, 0)
        self.combo_lophoc = QComboBox()
        self.combo_lophoc.setToolTip("Chọn lớp học (đã tạo) để thêm buổi học")
        form_layout.addWidget(self.combo_lophoc, 0, 1)
        self.inputs["lophoc"] = self.combo_lophoc
        
        # 2. Các trường chỉ xem (Tên môn, Tên GV)
        form_layout.addWidget(QLabel("Tên môn học:"), 1, 0)
        self.label_ten_mon = QLineEdit("[Tên môn học]")
        self.label_ten_mon.setReadOnly(True)
        form_layout.addWidget(self.label_ten_mon, 1, 1)

        form_layout.addWidget(QLabel("Tên giảng viên:"), 2, 0)
        self.label_ten_gv = QLineEdit("[Tên giảng viên]")
        self.label_ten_gv.setReadOnly(True)
        form_layout.addWidget(self.label_ten_gv, 2, 1)

        # 3. Các trường nhập liệu
        form_layout.addWidget(QLabel("Ngày học:"), 3, 0)
        self.date_ngay_hoc = QDateEdit()
        self.date_ngay_hoc.setDisplayFormat("dd-MM-yyyy")
        self.date_ngay_hoc.setCalendarPopup(True)
        self.date_ngay_hoc.setDate(QDate.currentDate())
        form_layout.addWidget(self.date_ngay_hoc, 3, 1)
        self.inputs["ngay_hoc"] = self.date_ngay_hoc

        form_layout.addWidget(QLabel("Giờ bắt đầu:"), 4, 0)
        self.time_bat_dau = QTimeEdit()
        self.time_bat_dau.setDisplayFormat("HH:mm")
        self.time_bat_dau.setTime(QTime(7, 0)) # Mặc định 7:00 AM
        form_layout.addWidget(self.time_bat_dau, 4, 1)
        self.inputs["gio_bat_dau"] = self.time_bat_dau

        form_layout.addWidget(QLabel("Giờ kết thúc:"), 5, 0)
        self.time_ket_thuc = QTimeEdit()
        self.time_ket_thuc.setDisplayFormat("HH:mm")
        self.time_ket_thuc.setTime(QTime(9, 30)) # Mặc định 9:30 AM
        form_layout.addWidget(self.time_ket_thuc, 5, 1)
        self.inputs["gio_ket_thuc"] = self.time_ket_thuc
        
        form_layout.addWidget(QLabel("Phòng học:"), 6, 0)
        self.line_phong_hoc = QLineEdit()
        self.line_phong_hoc.setPlaceholderText("Ví dụ: P.301")
        form_layout.addWidget(self.line_phong_hoc, 6, 1)
        self.inputs["phong_hoc"] = self.line_phong_hoc
        
        # ID Buổi học (ẩn, chỉ dùng để Cập nhật/Xóa)
        self.hidden_id_buoi = QLineEdit()
        self.hidden_id_buoi.setVisible(False)
        self.inputs["id_buoi"] = self.hidden_id_buoi

        # === Buttons ===
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Thêm mới")
        self.btn_update = QPushButton("Cập nhật")
        self.btn_delete = QPushButton("Xoá")
        self.btn_refresh = QPushButton("Làm mới")
        
        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_refresh]:
            btn.setStyleSheet("background-color: #1e40af; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;")
            btn_layout.addWidget(btn)

        form_layout.addLayout(btn_layout, 7, 0, 1, 2)
        info_group.setLayout(form_layout)
        
        # --- RIGHT PANEL ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        search_layout = QHBoxLayout()
        self.search_by = QComboBox()
        self.search_by.addItems(["Tên môn học", "Tên giảng viên", "Mã lớp"])
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

        # === Table (Đã sửa đổi) ===
        self.table = QTableWidget()
        self.table.setColumnCount(7) # Sửa số cột
        self.table.setHorizontalHeaderLabels([
            "ID Buổi", "Ngày học", "Giờ BĐ", "Giờ KT", 
            "Phòng học", "Mã Lớp", "Tên Môn học"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: white;")
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        right_layout.addLayout(search_layout)
        right_layout.addWidget(self.table)

        # ===== FINAL LAYOUT =====
        content_layout.addWidget(info_group, 3) # Panel trái
        content_layout.addWidget(right_panel, 5) # Panel phải

        main_layout.addLayout(content_layout) 
        
        # Timer for clock
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\ndd-MM-yyyy"))

    # ==========================================================
    # HÀM TIỆN ÍCH (HELPER FUNCTIONS)
    # ==========================================================
    
    def populate_lophoc_combo(self, lophoc_data):
        """
        Điền danh sách Lớp học vào ComboBox.
        lophoc_data: list of tuples (ID_LOP, MA_LOP, TEN_MON)
        """
        combo = self.inputs["lophoc"]
        combo.clear()
        combo.addItem("--- Chọn Lớp học ---", None) # Thêm mục rỗng
        if lophoc_data:
            for id_lop, ma_lop, ten_mon in lophoc_data:
                combo.addItem(f"{ma_lop} ({ten_mon})", id_lop) # Hiển thị Mã Lớp (Tên môn), lưu ID_LOP

    def set_class_details(self, details):
        """Điền chi tiết Lớp học (Tên môn, Tên GV) vào các ô ReadOnly"""
        if details:
            self.label_ten_mon.setText(details.get("ten_mon", "[N/A]"))
            self.label_ten_gv.setText(details.get("ten_gv", "[N/A]"))
        else:
            self.label_ten_mon.setText("[---]")
            self.label_ten_gv.setText("[---]")

    def get_form_data(self):
        """Lấy dữ liệu từ form trả về một dictionary"""
        return {
            "id_lop": self.inputs["lophoc"].currentData(), # Lấy ID_LOP từ ComboBox
            "ngay_hoc": self.inputs["ngay_hoc"].date().toString("yyyy-MM-dd"),
            "gio_bat_dau": self.inputs["gio_bat_dau"].time().toString("HH:mm"),
            "gio_ket_thuc": self.inputs["gio_ket_thuc"].time().toString("HH:mm"),
            "phong_hoc": self.inputs["phong_hoc"].text(),
            "id_buoi": self.inputs["id_buoi"].text() # Lấy ID buổi học (đang ẩn)
        }

    def clear_form(self):
        """Xóa trắng các ô nhập liệu về trạng thái mặc định"""
        self.inputs["lophoc"].setCurrentIndex(0) # Về mục "Chọn Lớp học"
        self.label_ten_mon.setText("[---]")
        self.label_ten_gv.setText("[---]")
        self.inputs["ngay_hoc"].setDate(QDate.currentDate())
        self.inputs["gio_bat_dau"].setTime(QTime(7, 0))
        self.inputs["gio_ket_thuc"].setTime(QTime(9, 30))
        self.inputs["phong_hoc"].clear()
        self.inputs["id_buoi"].clear()
        
        self.inputs["lophoc"].setEnabled(True) # Cho phép chọn lại lớp
        self.table.clearSelection()

    def populate_table(self, data):
        """Hiển thị dữ liệu (list of tuples) lên bảng"""
        self.table.setRowCount(0)
        if not data:
            return
            
        self.table.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for col_index, item in enumerate(row_data):
                # Định dạng đặc biệt cho Ngày và Giờ
                if col_index == 1 and isinstance(item, QDate):
                    item_str = item.toString("dd-MM-yyyy")
                elif (col_index == 2 or col_index == 3) and isinstance(item, QTime):
                    item_str = item.toString("HH:mm")
                else:
                    item_str = str(item) if item is not None else ""
                
                cell_item = QTableWidgetItem(item_str)
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable) 
                self.table.setItem(row_index, col_index, cell_item)
        
        self.table.resizeColumnsToContents()

    def get_search_data(self):
        """Lấy thông tin tìm kiếm"""
        return {
            "search_by": self.search_by.currentText(),
            "keyword": self.search_input.text()
        }

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