import sys
import os 
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QComboBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QGroupBox, QFrame, QMessageBox, QDateTimeEdit, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon

class CheckinWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thông tin điểm danh")
        self.setGeometry(200, 100, 1200, 700) # Cho rộng hơn 1 chút
        self.setStyleSheet("background-color: white; font-family: Arial;")
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.header_ui())
        
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.left_panel_ui(), 2) # Tỷ lệ 2
        content_layout.addWidget(self.right_panel_ui(), 5) # Tỷ lệ 5
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)

    # ---------------- Header ----------------
    def header_ui(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 10, 25, 10)

        # Icon Đồng hồ
        clock_icon = QLabel()
        clock_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\clock.png"
        
        if os.path.exists(clock_icon_path):
            clock_pixmap = QPixmap(clock_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
            clock_icon.setStyleSheet("margin-right: 5px;")
        
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.addWidget(clock_icon)

        # Thời gian
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: white; font-size: 14px;")
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        
        time_layout.addWidget(self.time_label)

        # Tiêu đề
        title_label = QLabel("Quản lý thông tin điểm danh")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 17px;")

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
        header_layout.addStretch(1)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.back_btn)
        return header

    # ---------------- Left Panel (Form) ----------------
    def left_panel_ui(self):
        left_group = QGroupBox("Cập nhật điểm danh")
        left_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold; font-size: 15px; color: #0B3D91;
                border: 2px solid #0B3D91; border-radius: 8px;
                margin-top: 8px;
            }
        """)

        grid = QGridLayout()
        
        # === SỬA ĐỔI CÁC TRƯỜNG CHO KHỚP CSDL ===
        labels = [
            "ID điểm danh:", "ID Buổi học:", "Mã Lớp:",
            "Mã Sinh viên:", "Tên Sinh viên:", "Thời gian:",
            "Trạng thái:", "Ghi chú:"
        ]
        self.inputs = {}

        for i, text in enumerate(labels):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
            input_widget = None
            
            if text == "Trạng thái:":
                input_widget = QComboBox()
                input_widget.addItems(["", "Có mặt", "Vắng", "Đi muộn"])
            elif text == "Thời gian:":
                input_widget = QDateTimeEdit()
                input_widget.setDisplayFormat("dd-MM-yyyy HH:mm:ss")
                input_widget.setCalendarPopup(True)
            else:
                input_widget = QLineEdit()
                # Các trường này chỉ để xem, không cho sửa
                if text in ["ID điểm danh:", "Mã Lớp:", "Tên Sinh viên:"]:
                    input_widget.setReadOnly(True)
                    input_widget.setStyleSheet("background-color: #f0f0f0;")

            self.inputs[text] = input_widget
            grid.addWidget(lbl, i, 0)
            grid.addWidget(input_widget, i, 1)

        # Hàng nút
        btn_layout = QGridLayout() # Dùng GridLayout cho dễ chia
        self.btn_update = QPushButton("Cập nhật")
        self.btn_reset = QPushButton("Làm mới")
        self.btn_view_image = QPushButton("Xem ảnh")
        self.btn_delete = QPushButton("Xoá")
        
        # Tạm thời vô hiệu hóa Import/Export (chức năng phức tạp)
        self.btn_import = QPushButton("Nhập CSV")
        self.btn_export = QPushButton("Xuất CSV")
        self.btn_import.setEnabled(False)
        self.btn_export.setEnabled(False)

        buttons = [
            self.btn_update, self.btn_reset, self.btn_view_image, 
            self.btn_delete, self.btn_import, self.btn_export
        ]

        for i, btn in enumerate(buttons):
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B3D91; color: white;
                    font-weight: bold; border-radius: 5px;
                }
                QPushButton:hover { background-color: #1E5CC5; }
                QPushButton:disabled { background-color: #D3D3D3; }
            """)
            btn_layout.addWidget(btn, i // 2, i % 2) # Thêm vào 2 cột

        grid.addLayout(btn_layout, len(labels), 0, 1, 2)
        left_group.setLayout(grid)
        return left_group

    # ---------------- Right Panel (Table) ----------------
    def right_panel_ui(self):
        right_group = QGroupBox()
        right_layout = QVBoxLayout()

        # Thanh tìm kiếm
        search_layout = QHBoxLayout()
        search_label = QLabel("Tìm kiếm theo")
        search_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.search_by = QComboBox()
        # Sửa lại tiêu chí tìm kiếm
        self.search_by.addItems(["Mã Sinh viên", "Tên Sinh viên", "Mã Lớp", "Ngày (yyyy-MM-dd)"])
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khoá tìm kiếm...")

        self.btn_search = QPushButton("Tìm kiếm")
        self.btn_today = QPushButton("Hôm nay")
        self.btn_all = QPushButton("Xem tất cả")

        for btn in [self.btn_search, self.btn_today, self.btn_all]:
            btn.setFixedWidth(100)
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B3D91; color: white;
                    font-weight: bold; border-radius: 5px;
                }
                QPushButton:hover { background-color: #1E5CC5; }
            """)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_by)
        search_layout.addWidget(self.search_input, 1) # Cho ô tìm kiếm dài ra
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_today)
        search_layout.addWidget(self.btn_all)

        # Bảng dữ liệu
        self.table = QTableWidget()
        
        # === SỬA ĐỔI CỘT CHO KHỚP CSDL ===
        self.table.setColumnCount(8) 
        self.table.setHorizontalHeaderLabels([
            "ID Điểm danh", "ID Buổi", "Mã SV", "Tên Sinh viên", 
            "Mã Lớp", "Thời gian", "Trạng thái", "Ghi chú"
            # Bỏ "Giờ ra", bỏ "Ngày" (vì đã gộp vào Thời gian)
        ])
        
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: white; color: #0B3D91;
                border: 1px solid #0B3D91; padding: 6px;
                font-weight: bold;
            }
            QTableWidget {
                border: 1px solid #0B3D91; gridline-color: #0B3D91;
                font-size: 13px; background-color: white;
                selection-background-color: #E0ECFF; selection-color: black;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        right_layout.addLayout(search_layout)
        right_layout.addWidget(self.table)
        right_group.setLayout(right_layout)
        return right_group

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\n dd-MM-yyyy"))
        
    # ==========================================================
    # HÀM TIỆN ÍCH (HELPER FUNCTIONS)
    # ==========================================================
    
    def get_form_data(self):
        """Lấy dữ liệu từ form trả về một dictionary"""
        data = {
            "id_diemdanh": self.inputs["ID điểm danh:"].text(),
            "id_buoi": self.inputs["ID Buổi học:"].text(),
            "id_sv": self.inputs["Mã Sinh viên:"].text(),
            # "thoi_gian": self.inputs["Thời gian:"].dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "thoi_gian": self.inputs["Thời gian:"].text(), # Sửa: DateTimeEdit dùng text()
            "trang_thai": self.inputs["Trạng thái:"].currentText(),
            "ghi_chu": self.inputs["Ghi chú:"].text()
        }
        return data

    def clear_form(self):
        """Xóa trắng các ô nhập liệu về trạng thái mặc định"""
        self.inputs["ID điểm danh:"].clear()
        self.inputs["ID Buổi học:"].clear()
        self.inputs["Mã Lớp:"].clear()
        self.inputs["Mã Sinh viên:"].clear()
        self.inputs["Tên Sinh viên:"].clear()
        self.inputs["Thời gian:"].setDateTime(QDateTime.currentDateTime())
        self.inputs["Trạng thái:"].setCurrentIndex(0)
        self.inputs["Ghi chú:"].clear()
        
        # Cho phép nhập liệu
        self.inputs["ID Buổi học:"].setEnabled(True)
        self.inputs["Mã Sinh viên:"].setEnabled(True)
        
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
                
                # Định dạng lại thời gian
                if col_index == 5 and isinstance(item, QDateTime):
                    item_str = item.toString("dd-MM-yyyy HH:mm:ss")
                
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