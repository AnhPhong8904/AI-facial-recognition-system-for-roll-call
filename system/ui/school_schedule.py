import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QDateEdit, QTimeEdit, QFrame, QMessageBox
)
# Cần import QTime
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize, QDate, QTime 
from PyQt5.QtGui import QFont, QPixmap, QIcon

class ScheduleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin Lịch học")
        self.setGeometry(100, 100, 1200, 700) # Cho cửa sổ rộng hơn
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
        header = QFrame()
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header.setFixedHeight(80)
        layout = QHBoxLayout()
        layout.setContentsMargins(25, 10, 25, 10)

        # Icon Đồng hồ
        clock_icon = QLabel()
        clock_icon_path = r"D:\AI-facial-recognition-system-for-roll-call\system\img\clock.png" 
        
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

        title = QLabel("Quản lý thông tin Lịch học") # Đổi tiêu đề
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, stretch=1)

        # Nút Quay lại
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
        
        layout.addWidget(self.back_btn)
        header.setLayout(layout)
        return header

    # ---------------- Content ----------------
    def content_ui(self):
        content = QWidget()
        content_layout = QHBoxLayout()

        # Left panel - Thông tin lịch học (ĐÃ THIẾT KẾ LẠI)
        info_group = QGroupBox("Thông tin lịch học")
        info_group.setFont(QFont("Arial", 10, QFont.Bold))
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)

        # Dùng một QLineEdit ẩn để lưu ID_BUOI khi chọn từ bảng
        self.hidden_id_buoi = QLineEdit()
        
        # Hàng 0: Chọn Lớp học
        form_layout.addWidget(QLabel("Chọn Lớp học:"), 0, 0)
        self.combo_lophoc = QComboBox()
        self.combo_lophoc.setToolTip("Chọn Lớp học (Lớp tín chỉ) từ danh sách")
        form_layout.addWidget(self.combo_lophoc, 0, 1)

        # Hàng 1: Tên Môn học (Chỉ xem)
        form_layout.addWidget(QLabel("Tên Môn học:"), 1, 0)
        self.line_ten_mon = QLineEdit()
        self.line_ten_mon.setReadOnly(True)
        self.line_ten_mon.setStyleSheet("background-color: #f0f0f0;")
        form_layout.addWidget(self.line_ten_mon, 1, 1)

        # Hàng 2: Tên Giảng viên (Chỉ xem)
        form_layout.addWidget(QLabel("Tên Giảng viên:"), 2, 0)
        self.line_ten_gv = QLineEdit()
        self.line_ten_gv.setReadOnly(True)
        self.line_ten_gv.setStyleSheet("background-color: #f0f0f0;")
        form_layout.addWidget(self.line_ten_gv, 2, 1)

        # Hàng 3: Ngày học
        form_layout.addWidget(QLabel("Ngày học:"), 3, 0)
        self.date_ngay_hoc = QDateEdit()
        self.date_ngay_hoc.setDisplayFormat("dd-MM-yyyy")
        self.date_ngay_hoc.setCalendarPopup(True)
        self.date_ngay_hoc.setDate(QDate.currentDate())
        form_layout.addWidget(self.date_ngay_hoc, 3, 1)

        # Hàng 4: Giờ bắt đầu
        form_layout.addWidget(QLabel("Giờ bắt đầu:"), 4, 0)
        self.time_bat_dau = QTimeEdit()
        self.time_bat_dau.setDisplayFormat("HH:mm")
        form_layout.addWidget(self.time_bat_dau, 4, 1)
        
        # Hàng 5: Giờ kết thúc
        form_layout.addWidget(QLabel("Giờ kết thúc:"), 5, 0)
        self.time_ket_thuc = QTimeEdit()
        self.time_ket_thuc.setDisplayFormat("HH:mm")
        form_layout.addWidget(self.time_ket_thuc, 5, 1)
        
        # Hàng 6: Phòng học
        form_layout.addWidget(QLabel("Phòng học:"), 6, 0)
        self.line_phong_hoc = QLineEdit()
        form_layout.addWidget(self.line_phong_hoc, 6, 1)
        
        # Hàng 7: Ghi chú
        form_layout.addWidget(QLabel("Ghi chú:"), 7, 0)
        self.line_ghi_chu = QLineEdit()
        form_layout.addWidget(self.line_ghi_chu, 7, 1)

        # Nút chức năng
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Thêm lịch học")
        self.btn_update = QPushButton("Cập nhật")
        self.btn_delete = QPushButton("Xoá")
        self.btn_refresh = QPushButton("Làm mới")

        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_refresh]:
            btn.setStyleSheet("background-color: #1e40af; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)

        form_layout.addLayout(btn_layout, 8, 0, 1, 2)
        info_group.setLayout(form_layout)

        # Right panel - Bảng dữ liệu và tìm kiếm
        right_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_by = QComboBox()
        self.search_by.addItems(["Mã lớp", "Tên môn", "Tên giảng viên"]) # Sửa tiêu chí
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

        self.table = QTableWidget()
        # Sửa đổi cột cho khớp
        self.table.setColumnCount(7) 
        self.table.setHorizontalHeaderLabels([
            "ID Buổi", "Ngày học", "Giờ BĐ", "Giờ KT", 
            "Phòng học", "Mã Lớp", "Ghi chú"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: white;")
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        right_layout.addLayout(search_layout)
        right_layout.addWidget(self.table)

        # Add panels to content
        content_layout.addWidget(info_group, 3)
        content_layout.addLayout(right_layout, 5)
        content.setLayout(content_layout)

        return content

    # ---------------- Update Time ----------------
    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\ndd-MM-yyyy"))
        
    # ==========================================================
    # HÀM TIỆN ÍCH (HELPER FUNCTIONS)
    # Controller sẽ gọi các hàm này
    # ==========================================================

    def populate_lophoc_combo(self, classes_data):
        """
        Điền danh sách Lớp học vào ComboBox.
        classes_data: list of tuples (ID_LOP, MA_LOP, TEN_LOP)
        """
        self.combo_lophoc.clear()
        self.combo_lophoc.addItem("--- Chọn Lớp học ---", None) # Mục rỗng
        if classes_data:
            for id_lop, ma_lop, ten_lop in classes_data:
                self.combo_lophoc.addItem(f"{ma_lop} - {ten_lop}", id_lop)
    
    def set_class_details(self, details):
        """
        Điền chi tiết (Tên môn, Tên GV, Giờ BĐ, Giờ KT)
        """
        if details:
            # [SỬA] Nhận 4 giá trị
            ten_mon, ten_gv, gio_bd, gio_kt = details
            
            self.line_ten_mon.setText(ten_mon if ten_mon else "N/A")
            self.line_ten_gv.setText(ten_gv if ten_gv else "N/A")
            
            # [MỚI] Tự động điền giờ
            if gio_bd:
                # Chuyển đổi (ví dụ: datetime.time(7, 0)) sang QTime
                if isinstance(gio_bd, str):
                     # Xử lý trường hợp CSDL trả về string '07:00:00'
                    time_str = gio_bd.split('.')[0] # Bỏ milisecond
                    self.time_bat_dau.setTime(QTime.fromString(time_str, "HH:mm:ss"))
                elif hasattr(gio_bd, 'strftime'): # Xử lý datetime.time
                    self.time_bat_dau.setTime(QTime(gio_bd.hour, gio_bd.minute))
                
            if gio_kt:
                if isinstance(gio_kt, str):
                    time_str = gio_kt.split('.')[0]
                    self.time_ket_thuc.setTime(QTime.fromString(time_str, "HH:mm:ss"))
                elif hasattr(gio_kt, 'strftime'):
                    self.time_ket_thuc.setTime(QTime(gio_kt.hour, gio_kt.minute))
                
        else:
            self.line_ten_mon.clear()
            self.line_ten_gv.clear()
            # [MỚI] Reset lại giờ khi xóa chọn
            self.time_bat_dau.setTime(QTime(7, 0))
            self.time_ket_thuc.setTime(QTime(9, 0))

    def get_form_data(self):
        """Lấy dữ liệu từ form trả về một dictionary"""
        data = {
            "id_buoi": self.hidden_id_buoi.text(), # Lấy ID ẩn
            "id_lop": self.combo_lophoc.currentData(), # Lấy ID_LOP từ ComboBox
            "ngay_hoc": self.date_ngay_hoc.date().toString("yyyy-MM-dd"),
            "gio_bd": self.time_bat_dau.time().toString("HH:mm"),
            "gio_kt": self.time_ket_thuc.time().toString("HH:mm"),
            "phong_hoc": self.line_phong_hoc.text(),
            "ghi_chu": self.line_ghi_chu.text()
        }
        return data

    def clear_form(self):
        """Xóa trắng các ô nhập liệu về trạng thái mặc định"""
        self.hidden_id_buoi.clear()
        self.combo_lophoc.setCurrentIndex(0) # Về mục "Chọn Lớp học"
        self.line_ten_mon.clear()
        self.line_ten_gv.clear()
        self.date_ngay_hoc.setDate(QDate.currentDate())
        self.time_bat_dau.setTime(QTime(7, 0)) # Set giờ mặc định
        self.time_ket_thuc.setTime(QTime(9, 0))
        self.line_phong_hoc.clear()
        self.line_ghi_chu.clear()
        
        # Bật lại ComboBox nếu nó bị tắt (khi Cập nhật)
        self.combo_lophoc.setEnabled(True)
        self.table.clearSelection()

    def populate_table(self, data):
        """Hiển thị dữ liệu (list of tuples) lên bảng"""
        self.table.setRowCount(0)
        if not data:
            return
            
        self.table.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for col_index, item in enumerate(row_data):
                item_str = str(item) if item is not None else ""
                
                # Định dạng lại ngày sinh
                if col_index == 1 and isinstance(item, QDate):
                    item_str = item.toString("dd-MM-yyyy")
                
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