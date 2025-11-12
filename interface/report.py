import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon


class StatisticsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thống kê hệ thống")
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

        # ===== PHẦN BẠN HỎI: ICON ĐỒNG HỒ =====
        # Đồng hồ với icon từ đường dẫn
        clock_icon = QLabel()
        # Đây là đường dẫn đến icon đồng hồ của bạn
        clock_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\clock.png"
        
        # Kiểm tra xem file có tồn tại không
        if os.path.exists(clock_icon_path):
            # Tải hình ảnh, thay đổi kích thước và đặt vào QLabel
            clock_pixmap = QPixmap(clock_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
        else:
            print(f"Không tìm thấy icon đồng hồ tại: {clock_icon_path}")
            
        clock_icon.setStyleSheet("margin-right: 10px;")
        # ==========================================

        self.time_label = QLabel()
        self.date_label = QLabel()
        for lbl in [self.time_label, self.date_label]:
            lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        time_box = QVBoxLayout()
        time_box.addWidget(self.time_label)
        time_box.addWidget(self.date_label)

        title_label = QLabel("Thống kê hệ thống")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 20px;")
        title_label.setAlignment(Qt.AlignCenter)

        # ===== PHẦN BẠN HỎI: ICON NÚT QUAY LẠI =====
        # Nút quay lại với icon từ đường dẫn
        back_btn = QPushButton(" Quay lại")
        # Đây là đường dẫn đến icon 'back' của bạn
        back_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\back.png"
        
        # Kiểm tra xem file có tồn tại không
        if os.path.exists(back_icon_path):
            # Tạo QIcon từ đường dẫn và đặt làm icon cho nút
            back_btn.setIcon(QIcon(back_icon_path))
            back_btn.setIconSize(QSize(20, 20)) # Đặt kích thước cho icon
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
        # =============================================

        # Thêm các widget vào header_layout
        # Icon đồng hồ được thêm vào đầu tiên
        header_layout.addWidget(clock_icon)
        header_layout.addLayout(time_box)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        # Nút 'Quay lại' được thêm vào cuối
        header_layout.addWidget(back_btn)

        # ===== TOP STAT CARDS =====
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        def create_stat_card(color, icon, title, value):
            frame = QFrame()
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                }}
                QLabel {{
                    color: black;
                    font-weight: bold;
                }}
            """)
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(15, 10, 15, 10)
            layout.setSpacing(5)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 32px;")
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 11, QFont.Bold))
            value_label = QLabel(str(value))
            value_label.setFont(QFont("Arial", 18, QFont.Bold))

            layout.addWidget(icon_label)
            layout.addWidget(title_label)
            layout.addWidget(value_label)
            return frame

        stats_layout.addWidget(create_stat_card("#93C5FD", "🎓", "Số sinh viên", 36))
        stats_layout.addWidget(create_stat_card("#86EFAC", "📝", "Số bản điểm danh", 36))
        stats_layout.addWidget(create_stat_card("#E9D5FF", "🏃", "Số lần đi muộn", 36))
        stats_layout.addWidget(create_stat_card("#FCA5A5", "💺", "Số lần vắng", 36))

        # ===== MAIN CONTENT AREA =====
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

        # --- Helper: Create section ---
        def create_table_section(title, headers, color=None):
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

            cb = QComboBox()
            cb.addItems(["ID sinh viên", "Tên sinh viên", "Môn học"])
            txt = QLineEdit()
            btn_search = QPushButton("Tìm kiếm")
            btn_all = QPushButton("Xem tất cả")
            btn_csv = QPushButton("Xuất CSV")

            for b in [btn_search, btn_all, btn_csv]:
                b.setStyleSheet("""
                    QPushButton {
                        background-color: #1E40AF;
                        color: white;
                        border-radius: 4px;
                        font-weight: bold;
                        padding: 4px 8px;
                    }
                    QPushButton:hover { background-color: #123072; }
                """)

            layout.addWidget(cb, 0, 0)
            layout.addWidget(txt, 0, 1)
            layout.addWidget(btn_search, 0, 2)
            layout.addWidget(btn_all, 0, 3)
            layout.addWidget(btn_csv, 0, 4)

            table = QTableWidget(0, len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #9CA3AF;
                }
            """)
            layout.addWidget(table, 1, 0, 1, 5)
            return group

        # Create all 3 sections
        late_students = create_table_section(
            "Sinh viên đi muộn",
            ["ID sinh viên", "Tên sinh viên", "Ngày", "Môn học", "ID buổi học", "Trạng thái"]
        )
        no_attendance = create_table_section(
            "Sinh viên không điểm danh",
            ["ID sinh viên", "Tên sinh viên", "Ngày", "Môn học", "ID buổi học", "Trạng thái"],
            color="#DC2626"
        )
        absent_students = create_table_section(
            "Sinh viên vắng",
            ["ID sinh viên", "Tên sinh viên", "Ngày", "Môn học", "ID buổi học", "Trạng thái"]
        )

        content_layout.addWidget(late_students, 0, 0)
        content_layout.addWidget(no_attendance, 0, 1)
        content_layout.addWidget(absent_students, 1, 0, 1, 2)

        # ===== MAIN LAYOUT =====
        main_layout.addWidget(header)
        main_layout.addLayout(stats_layout)
        main_layout.addWidget(content_frame)

        # Timer update clock
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
    ui = StatisticsUI()
    ui.show()
    sys.exit(app.exec_())