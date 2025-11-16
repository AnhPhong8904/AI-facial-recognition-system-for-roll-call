import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QFrame, QMessageBox, QHeaderView # Thêm QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon


class ReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Báo cáo Thống kê hệ thống")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: white; font-family: Arial;")
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(10)

        # ===== HEADER =====
        header = QFrame()
        header.setFixedHeight(85)
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Đồng hồ
        clock_icon = QLabel()
        clock_icon_path = r"D:\AI-facial-recognition-system-for-roll-call\system\img\clock.png"
        
        if os.path.exists(clock_icon_path):
            clock_pixmap = QPixmap(clock_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
        clock_icon.setStyleSheet("margin-right: 10px;")

        self.time_label = QLabel()
        self.date_label = QLabel()
        for lbl in [self.time_label, self.date_label]:
            lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        time_box = QVBoxLayout()
        time_box.addWidget(self.time_label)
        time_box.addWidget(self.date_label)

        title_label = QLabel("Báo cáo Thống kê hệ thống")
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
        
        header_layout.addWidget(clock_icon)
        header_layout.addLayout(time_box)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.back_btn)

        # ===== TOP STAT CARDS (Thẻ Thống kê) =====
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # Hàm helper để tạo thẻ
        def create_stat_card(color, icon, title):
            frame = QFrame()
            frame.setStyleSheet(f"""
                QFrame {{ background-color: {color}; border-radius: 8px; }}
                QLabel {{ color: black; font-weight: bold; }}
            """)
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(15, 10, 15, 10)
            layout.setSpacing(5)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 32px;")
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 11, QFont.Bold))
            
            # Tạo QLabel cho giá trị và lưu tham chiếu
            value_label = QLabel("0") # Giá trị mặc định
            value_label.setFont(QFont("Arial", 18, QFont.Bold))

            layout.addWidget(icon_label)
            layout.addWidget(title_label)
            layout.addWidget(value_label)
            return frame, value_label # Trả về cả label giá trị

        # Tạo và lưu trữ các label giá trị
        card_sv, self.value_sv = create_stat_card("#93C5FD", "🎓", "Số sinh viên")
        card_diemdanh, self.value_diemdanh = create_stat_card("#86EFAC", "📝", "Số bản điểm danh")
        card_dimuon, self.value_dimuon = create_stat_card("#E9D5FF", "🏃", "Số lần đi muộn")
        card_vang, self.value_vang = create_stat_card("#FCA5A5", "💺", "Số lần vắng")

        stats_layout.addWidget(card_sv)
        stats_layout.addWidget(card_diemdanh)
        stats_layout.addWidget(card_dimuon)
        stats_layout.addWidget(card_vang)

        # ===== MAIN CONTENT AREA (Bảng) =====
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 3px solid #1E40AF;
                border-radius: 10px;
            }
        """)
        content_layout = QGridLayout(content_frame)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)

        # --- Tạo 2 bảng (Đi muộn và Vắng) ---
        
        # Bảng 1: Sinh viên Đi muộn
        (group_late, 
         self.table_late, 
         self.search_by_late, 
         self.search_input_late,
         self.btn_search_late, 
         self.btn_all_late, 
         self.btn_csv_late) = self.create_table_section(
            "Sinh viên đi muộn",
            ["Mã SV", "Tên SV", "Mã Lớp", "Tên Lớp", "Thời gian", "Trạng thái"]
        )
        
        # Bảng 2: Sinh viên Vắng
        (group_absent, 
         self.table_absent, 
         self.search_by_absent, 
         self.search_input_absent,
         self.btn_search_absent, 
         self.btn_all_absent, 
         self.btn_csv_absent) = self.create_table_section(
            "Sinh viên vắng",
            ["Mã SV", "Tên SV", "Mã Lớp", "Tên Lớp", "Thời gian", "Trạng thái"],
            color="#DC2626"
        )

        content_layout.addWidget(group_late, 0, 0)
        content_layout.addWidget(group_absent, 0, 1)

        # ===== FINAL LAYOUT =====
        main_layout.addWidget(header)
        main_layout.addLayout(stats_layout)
        main_layout.addWidget(content_frame, 1) # Cho bảng chiếm phần lớn

        # Timer update clock
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

    def create_table_section(self, title, headers, color=None):
        """Hàm helper để tạo một group (bảng + tìm kiếm)"""
        group = QGroupBox(title)
        group.setFont(QFont("Arial", 11, QFont.Bold))
        group.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid #D1D5DB;
                background-color: #F9FAFB;
                border-radius: 5px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                color: {color if color else '#1E40AF'};
            }}
        """)
        layout = QGridLayout(group)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(6)

        # Các widget
        cb = QComboBox()
        cb.addItems(["Mã Sinh viên", "Tên Sinh viên", "Mã Lớp", "Tên Lớp"])
        cb.setStyleSheet("padding: 5px; border: 1px solid #D1D5DB; border-radius: 4px;") # Thêm style cho combobox

        txt = QLineEdit()
        txt.setPlaceholderText("Nhập từ khóa...")
        txt.setStyleSheet("padding: 5px; border: 1px solid #D1D5DB; border-radius: 4px;") # Thêm style cho lineedit

        btn_search = QPushButton("Tìm kiếm")
        btn_all = QPushButton("Xem tất cả")
        btn_csv = QPushButton("Xuất CSV")

        # Đảm bảo các nút có màu xanh
        for b in [btn_search, btn_all, btn_csv]:
            b.setFixedWidth(100) # Giới hạn chiều rộng
            b.setFixedHeight(30) # Giới hạn chiều cao
            b.setStyleSheet("""
                QPushButton {
                    background-color: #1E40AF; /* Màu xanh đậm */
                    color: white;
                    border-radius: 4px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover { background-color: #123072; } /* Đậm hơn khi hover */
            """)
            b.setEnabled(True) # Đảm bảo nút được bật

        layout.addWidget(cb, 0, 0)
        layout.addWidget(txt, 0, 1, 1, 2)
        layout.addWidget(btn_search, 0, 3)
        layout.addWidget(btn_all, 0, 4)
        layout.addWidget(btn_csv, 0, 5)

        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #9CA3AF;
                gridline-color: #E0E0E0; /* Màu đường kẻ ô */
            }
            QHeaderView::section {
                background-color: #F0F0F0; /* Màu nền header */
                color: #333333; /* Màu chữ header */
                border: 1px solid #D1D5DB;
                padding: 5px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #C0DFFD; /* Màu khi chọn hàng */
                color: black;
            }
        """)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(table, 1, 0, 1, 6)
        
        return (group, table, cb, txt, btn_search, btn_all, btn_csv)

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP"))
        self.date_label.setText(now.toString("dd-MM-yyyy"))
        
    # ==========================================================
    # HÀM TIỆN ÍCH (HELPER FUNCTIONS)
    # ==========================================================
    
    def populate_table(self, table_widget, data):
        """Hiển thị dữ liệu (list of tuples) lên bảng"""
        table_widget.setRowCount(0)
        if not data:
            return
            
        table_widget.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for col_index, item in enumerate(row_data):
                item_str = str(item) if item is not None else ""
                
                cell_item = QTableWidgetItem(item_str)
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable) 
                table_widget.setItem(row_index, col_index, cell_item)
        
        table_widget.resizeColumnsToContents()

    def update_stat_cards(self, stats_data):
        """Cập nhật 4 thẻ thống kê"""
        if stats_data:
            self.value_sv.setText(str(stats_data.get("tong_sv", 0)))
            self.value_diemdanh.setText(str(stats_data.get("tong_diemdanh", 0)))
            self.value_dimuon.setText(str(stats_data.get("tong_dimuon", 0)))
            self.value_vang.setText(str(stats_data.get("tong_vang", 0)))

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
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()