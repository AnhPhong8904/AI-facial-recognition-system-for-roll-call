import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QFrame, QMessageBox, QHeaderView, QTabWidget # Thêm QTabWidget
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor

# Import matplotlib để vẽ biểu đồ
import matplotlib
matplotlib.use('Qt5Agg')  # Backend cho PyQt5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


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

        # ===== MAIN CONTENT AREA (Tab: Biểu đồ và Bảng) =====
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 3px solid #1E40AF;
                border-radius: 10px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E5E7EB;
                color: #1E40AF;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #1E40AF;
                color: white;
            }
        """)

        # Tab 1: Biểu đồ
        charts_tab = QWidget()
        charts_layout = QVBoxLayout(charts_tab)
        charts_layout.setContentsMargins(15, 15, 15, 15)
        charts_layout.setSpacing(15)

        # Tạo 3 biểu đồ
        charts_grid = QGridLayout()
        charts_grid.setSpacing(15)

        # Biểu đồ 1: Phân bố trạng thái (Pie Chart)
        self.chart_pie = self.create_chart_widget("Phân bố trạng thái điểm danh")
        charts_grid.addWidget(self.chart_pie, 0, 0)

        # Biểu đồ 2: Điểm danh theo ngày (Line Chart)
        self.chart_line = self.create_chart_widget("Điểm danh theo ngày (7 ngày gần nhất)")
        charts_grid.addWidget(self.chart_line, 0, 1)

        # Biểu đồ 3: Điểm danh theo lớp (Bar Chart)
        self.chart_bar = self.create_chart_widget("Điểm danh theo lớp")
        charts_grid.addWidget(self.chart_bar, 1, 0, 1, 2)

        charts_layout.addLayout(charts_grid)
        tab_widget.addTab(charts_tab, "📊 Biểu đồ")

        # Tab 2: Bảng dữ liệu
        tables_tab = QFrame()
        tables_tab.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        tables_layout = QGridLayout(tables_tab)
        tables_layout.setContentsMargins(15, 15, 15, 15)
        tables_layout.setSpacing(10)

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

        tables_layout.addWidget(group_late, 0, 0)
        tables_layout.addWidget(group_absent, 0, 1)

        tab_widget.addTab(tables_tab, "📋 Bảng dữ liệu")
        
        # Tab 3: Thống kê điểm danh theo sinh viên
        stats_tab = QFrame()
        stats_tab.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        stats_layout = QHBoxLayout(stats_tab)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        stats_layout.setSpacing(15)
        
        # Bên trái: Danh sách lớp học
        left_panel = QGroupBox("Danh sách lớp học")
        left_panel.setFont(QFont("Arial", 11, QFont.Bold))
        left_panel.setStyleSheet("""
            QGroupBox {
                border: 2px solid #D1D5DB;
                background-color: #F9FAFB;
                border-radius: 5px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                color: #1E40AF;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tìm kiếm lớp học
        search_class_layout = QHBoxLayout()
        self.search_class_input = QLineEdit()
        self.search_class_input.setPlaceholderText("Tìm kiếm lớp học...")
        self.search_class_input.setStyleSheet("padding: 5px; border: 1px solid #D1D5DB; border-radius: 4px;")
        search_class_layout.addWidget(self.search_class_input)
        left_layout.addLayout(search_class_layout)
        
        # Danh sách lớp học
        self.list_classes = QTableWidget()
        self.list_classes.setColumnCount(4)
        self.list_classes.setHorizontalHeaderLabels(["Mã Lớp", "Tên Lớp", "Tổng SV", "Cấm thi"])
        self.list_classes.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #9CA3AF;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #333333;
                border: 1px solid #D1D5DB;
                padding: 5px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #C0DFFD;
                color: black;
            }
        """)
        self.list_classes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.list_classes.setSelectionBehavior(QTableWidget.SelectRows)
        self.list_classes.setEditTriggers(QTableWidget.NoEditTriggers)
        self.list_classes.setMaximumWidth(400)
        left_layout.addWidget(self.list_classes)
        
        # Bên phải: Danh sách sinh viên của lớp đã chọn
        right_panel = QGroupBox("Danh sách sinh viên")
        right_panel.setFont(QFont("Arial", 11, QFont.Bold))
        right_panel.setStyleSheet("""
            QGroupBox {
                border: 2px solid #D1D5DB;
                background-color: #F9FAFB;
                border-radius: 5px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                color: #1E40AF;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Label hiển thị lớp đang chọn
        self.selected_class_label = QLabel("Vui lòng chọn một lớp học")
        self.selected_class_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #1E40AF; padding: 5px;")
        right_layout.addWidget(self.selected_class_label)
        
        # Bảng sinh viên
        self.table_students = QTableWidget()
        self.table_students.setColumnCount(8)
        self.table_students.setHorizontalHeaderLabels(["Mã SV", "Tên SV", "Tổng buổi", "Vắng", "Tổng tiết", "Tiết vắng", "Tỷ lệ vắng", "Trạng thái"])
        self.table_students.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #9CA3AF;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #333333;
                border: 1px solid #D1D5DB;
                padding: 5px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #C0DFFD;
                color: black;
            }
        """)
        self.table_students.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_students.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_students.setEditTriggers(QTableWidget.NoEditTriggers)
        right_layout.addWidget(self.table_students)
        
        # Nút xuất CSV
        btn_export_layout = QHBoxLayout()
        self.btn_export_students = QPushButton("Xuất CSV")
        self.btn_export_students.setStyleSheet("""
            QPushButton {
                background-color: #1E40AF;
                color: white;
                border-radius: 4px;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover { background-color: #123072; }
        """)
        btn_export_layout.addStretch()
        btn_export_layout.addWidget(self.btn_export_students)
        right_layout.addLayout(btn_export_layout)
        
        stats_layout.addWidget(left_panel, 1)
        stats_layout.addWidget(right_panel, 2)
        tab_widget.addTab(stats_tab, "📊 Thống kê điểm danh")

        # ===== FINAL LAYOUT =====
        main_layout.addWidget(header)
        main_layout.addLayout(stats_layout)
        main_layout.addWidget(tab_widget, 1) # Cho tab chiếm phần lớn

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
    
    def populate_classes_list(self, data):
        """Hiển thị danh sách lớp học"""
        self.list_classes.setRowCount(0)
        if not data:
            return
            
        self.list_classes.setRowCount(len(data))
        for row_index, row_dict in enumerate(data):
            row_data = [
                row_dict.get("ma_lop", ""),
                row_dict.get("ten_lop", ""),
                str(row_dict.get("tong_sv", 0)),
                f"{row_dict.get('so_sv_cam_thi', 0)}/{row_dict.get('tong_sv', 0)}"
            ]
            
            for col_index, item_str in enumerate(row_data):
                cell_item = QTableWidgetItem(str(item_str))
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable)
                self.list_classes.setItem(row_index, col_index, cell_item)
        
        self.list_classes.resizeColumnsToContents()
    
    def populate_students_table(self, data, class_info=None):
        """Hiển thị danh sách sinh viên với màu sắc (đỏ = cấm thi, xanh = đủ điều kiện)"""
        self.table_students.setRowCount(0)
        
        if class_info:
            self.selected_class_label.setText(
                f"Lớp: {class_info.get('ma_lop', '')} - {class_info.get('ten_lop', '')} | "
                f"Môn: {class_info.get('ten_mon', '')} ({class_info.get('so_tin_chi', 0)} tín chỉ)"
            )
        else:
            self.selected_class_label.setText("Vui lòng chọn một lớp học")
        
        if not data:
            return
            
        self.table_students.setRowCount(len(data))
        for row_index, row_dict in enumerate(data):
            # Tạo danh sách giá trị theo thứ tự cột
            row_data = [
                row_dict.get("ma_sv", ""),
                row_dict.get("ho_ten", ""),
                str(row_dict.get("tong_buoi", 0)),
                str(row_dict.get("so_buoi_vang", 0)),
                str(row_dict.get("tong_tiet", 0)),
                str(row_dict.get("so_tiet_vang", 0)),
                f"{row_dict.get('ti_le_vang', 0) * 100:.1f}%",
                row_dict.get("trang_thai", "")
            ]
            
            # Xác định màu nền dựa trên trạng thái cấm thi
            cam_thi = row_dict.get("cam_thi", False)
            bg_color = "#FCA5A5" if cam_thi else "#86EFAC"  # Đỏ nếu cấm thi, xanh nếu đủ điều kiện
            
            for col_index, item_str in enumerate(row_data):
                cell_item = QTableWidgetItem(str(item_str))
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable)
                cell_item.setBackground(QColor(bg_color))
                self.table_students.setItem(row_index, col_index, cell_item)
        
        self.table_students.resizeColumnsToContents()

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

    def create_chart_widget(self, title):
        """Tạo widget chứa biểu đồ matplotlib"""
        group = QGroupBox(title)
        group.setFont(QFont("Arial", 11, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #D1D5DB;
                background-color: #F9FAFB;
                border-radius: 5px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                color: #1E40AF;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tạo Figure và Canvas
        figure = Figure(figsize=(6, 4), facecolor='white')
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        
        # Lưu reference để cập nhật sau
        group.figure = figure
        group.canvas = canvas
        
        return group

    def update_pie_chart(self, data):
        """Cập nhật biểu đồ tròn (Phân bố trạng thái)"""
        figure = self.chart_pie.figure
        figure.clear()
        ax = figure.add_subplot(111)
        
        labels = ['Có mặt', 'Đi muộn', 'Vắng']
        sizes = [data.get('co_mat', 0), data.get('di_muon', 0), data.get('vang', 0)]
        colors = ['#86EFAC', '#E9D5FF', '#FCA5A5']
        explode = (0.05, 0.05, 0.05)  # Tách nhẹ các phần
        
        # Chỉ vẽ nếu có dữ liệu
        if sum(sizes) > 0:
            ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                   shadow=True, startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
            ax.set_title('Phân bố trạng thái điểm danh', fontsize=12, fontweight='bold', pad=10)
        else:
            ax.text(0.5, 0.5, 'Chưa có dữ liệu', ha='center', va='center', 
                   fontsize=14, transform=ax.transAxes)
        
        self.chart_pie.canvas.draw()

    def update_line_chart(self, data):
        """Cập nhật biểu đồ đường (Điểm danh theo ngày)"""
        figure = self.chart_line.figure
        figure.clear()
        ax = figure.add_subplot(111)
        
        if not data or len(data) == 0:
            ax.text(0.5, 0.5, 'Chưa có dữ liệu', ha='center', va='center', 
                   fontsize=14, transform=ax.transAxes)
            self.chart_line.canvas.draw()
            return
        
        dates = [row[0] for row in data]
        co_mat = [row[1] for row in data]
        di_muon = [row[2] for row in data]
        vang = [row[3] for row in data]
        
        x = np.arange(len(dates))
        width = 0.25
        
        ax.bar(x - width, co_mat, width, label='Có mặt', color='#86EFAC')
        ax.bar(x, di_muon, width, label='Đi muộn', color='#E9D5FF')
        ax.bar(x + width, vang, width, label='Vắng', color='#FCA5A5')
        
        ax.set_xlabel('Ngày', fontsize=10, fontweight='bold')
        ax.set_ylabel('Số lượng', fontsize=10, fontweight='bold')
        ax.set_title('Điểm danh theo ngày (7 ngày gần nhất)', fontsize=12, fontweight='bold', pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        figure.tight_layout()
        self.chart_line.canvas.draw()

    def update_bar_chart(self, data):
        """Cập nhật biểu đồ cột (Điểm danh theo lớp)"""
        figure = self.chart_bar.figure
        figure.clear()
        ax = figure.add_subplot(111)
        
        if not data or len(data) == 0:
            ax.text(0.5, 0.5, 'Chưa có dữ liệu', ha='center', va='center', 
                   fontsize=14, transform=ax.transAxes)
            self.chart_bar.canvas.draw()
            return
        
        # Chỉ lấy top 10 lớp có nhiều điểm danh nhất
        top_data = sorted(data, key=lambda x: x[4], reverse=True)[:10]
        
        classes = [row[0][:15] + '...' if len(row[0]) > 15 else row[0] for row in top_data]
        co_mat = [row[1] for row in top_data]
        di_muon = [row[2] for row in top_data]
        vang = [row[3] for row in top_data]
        
        x = np.arange(len(classes))
        width = 0.25
        
        ax.bar(x - width, co_mat, width, label='Có mặt', color='#86EFAC')
        ax.bar(x, di_muon, width, label='Đi muộn', color='#E9D5FF')
        ax.bar(x + width, vang, width, label='Vắng', color='#FCA5A5')
        
        ax.set_xlabel('Lớp học', fontsize=10, fontweight='bold')
        ax.set_ylabel('Số lượng', fontsize=10, fontweight='bold')
        ax.set_title('Điểm danh theo lớp', fontsize=12, fontweight='bold', pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(classes, rotation=45, ha='right', fontsize=8)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        figure.tight_layout()
        self.chart_bar.canvas.draw()