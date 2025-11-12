import sys
import cv2
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QHBoxLayout,
    QVBoxLayout, QGroupBox, QFrame, QGridLayout, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize
from PyQt5.QtGui import QFont, QImage, QPixmap, QIcon


class FaceRecognitionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.cap = None
        self.timer_camera = QTimer()
        self.timer_camera.timeout.connect(self.update_camera_frame)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Điểm danh khuôn mặt")
        self.setGeometry(300, 100, 1100, 700)
        self.setStyleSheet("background-color: white; font-family: Arial;")

        # ===================== THANH TIÊU ĐỀ =====================
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(25, 10, 25, 10)

        clock_icon = QLabel()
        clock_icon_path = r"E:\AI-facial-recognition-system-for-roll-call\interface\img\clock.png"
        
        if os.path.exists(clock_icon_path):
            clock_pixmap = QPixmap(clock_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            clock_icon.setPixmap(clock_pixmap)
            clock_icon.setStyleSheet("margin-right: 5px;")
        else:
            print(f"Không tìm thấy icon đồng hồ tại: {clock_icon_path}")
        
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.addWidget(clock_icon)

        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: white; font-size: 13px;")
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        
        time_layout.addWidget(self.time_label)

        title_label = QLabel("Điểm danh khuôn mặt")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 17px;")

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

        header_layout.addLayout(time_layout)
        header_layout.addStretch(1)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(back_btn)
        header.setLayout(header_layout)

        # ===================== KHUNG TRÁI: CAMERA =====================
        group_left = QGroupBox("Màn hình nhận diện")
        group_left.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 15px;
                color: #0B3D91;
                border: 2px solid #0B3D91;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: white;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        # Dòng chọn môn và hệ đào tạo
        top_select_layout = QHBoxLayout()
        lbl_subject = QLabel("Chọn môn/ID buổi học:")
        lbl_subject.setStyleSheet("font-weight: bold; font-size: 13px;")
        subject_cb = QComboBox()
        subject_cb.addItems(["Xử lý ảnh & Thị giác máy tính", "AI cơ bản", "Lập trình Python"])

        lbl_degree = QLabel("Hệ đào tạo:")
        lbl_degree.setStyleSheet("font-weight: bold; font-size: 13px;")
        degree_cb = QComboBox()
        degree_cb.addItems(["Chính quy", "Tại chức"])

        top_select_layout.addWidget(lbl_subject)
        top_select_layout.addWidget(subject_cb)
        top_select_layout.addSpacing(10)
        top_select_layout.addWidget(lbl_degree)
        top_select_layout.addWidget(degree_cb)
        left_layout.addLayout(top_select_layout)

        # Camera hiển thị
        self.camera_frame = QLabel()
        self.camera_frame.setFixedSize(400, 280)
        self.camera_frame.setStyleSheet("background-color: #dcdcdc; border: 2px solid #0B3D91; border-radius: 6px;")
        self.camera_frame.setAlignment(Qt.AlignCenter)
        self.camera_frame.setText("Camera Preview\n(ảnh demo)")
        left_layout.addWidget(self.camera_frame, alignment=Qt.AlignCenter)

        # Thông báo
        self.notice_label = QLabel(
            "Thông báo: Sinh viên Bắc Văn Giang đã điểm danh thành công môn học 'Xử lý ảnh & thị giác máy tính'"
        )
        self.notice_label.setWordWrap(True)
        self.notice_label.setStyleSheet("color: green; font-weight: bold; font-size: 13px; border-top: 2px solid #0B3D91; padding-top: 5px;")
        left_layout.addWidget(self.notice_label)

        # Nút mở / đóng camera
        btn_layout = QHBoxLayout()
        self.open_btn = QPushButton("Mở Camera")
        self.close_btn = QPushButton("Đóng Camera")
        self.open_btn.clicked.connect(self.start_camera)
        self.close_btn.clicked.connect(self.stop_camera)

        for btn in [self.open_btn, self.close_btn]:
            btn.setFixedWidth(150)
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B3D91;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover { background-color: #1E5CC5; }
            """)

        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.close_btn)
        left_layout.addLayout(btn_layout)
        group_left.setLayout(left_layout)

        # ===================== KHUNG PHẢI: THÔNG TIN SINH VIÊN =====================
        group_right = QVBoxLayout()

        success_box = QGroupBox("Điểm danh thành công")
        success_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #0B3D91;
                font-size: 15px;
                border: 2px solid #0B3D91;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: white;
            }
        """)
        success_layout = QGridLayout()

        face_img = QLabel()
        face_img.setFixedSize(130, 130)
        face_img.setStyleSheet("border: 2px solid #aaa; border-radius: 8px;")
        face_img.setText("Ảnh\nnhận diện")
        face_img.setAlignment(Qt.AlignCenter)

        success_layout.addWidget(face_img, 0, 0, 3, 1)
        success_layout.addWidget(QLabel("ID sinh viên:"), 0, 1)
        id_le = QLineEdit("20221871")
        success_layout.addWidget(id_le, 0, 2)
        success_layout.addWidget(QLabel("Tên sinh viên:"), 1, 1)
        name_le = QLineEdit("Bắc Văn Giang")
        success_layout.addWidget(name_le, 1, 2)
        success_layout.addWidget(QLabel("Thời gian:"), 2, 1)
        time_le = QLineEdit("18:36:36")
        success_layout.addWidget(time_le, 2, 2)
        success_box.setLayout(success_layout)

        info_box = QGroupBox("Thông tin buổi học")
        info_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #0B3D91;
                font-size: 15px;
                border: 2px solid #0B3D91;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: white;
            }
        """)
        info_layout = QGridLayout()
        info_layout.addWidget(QLabel("Lớp tín chỉ:"), 0, 0)
        info_layout.addWidget(QLabel("<font color='red'>Lớp tín chỉ</font>"), 0, 1)
        info_layout.addWidget(QLabel("Tên môn học / ID buổi học:"), 1, 0)
        info_layout.addWidget(QLabel("<font color='red'>Xử lý ảnh và thị giác máy tính</font>"), 1, 1)
        info_layout.addWidget(QLabel("Thời gian:"), 2, 0)
        info_layout.addWidget(QLabel("<font color='red'>18:30:00 - 20:30:00</font>"), 2, 1)
        info_box.setLayout(info_layout)

        group_right.addWidget(success_box)
        group_right.addWidget(info_box)

        # ===================== BỐ CỤC CHÍNH =====================
        main_layout = QVBoxLayout()
        main_layout.addWidget(header)
        content_layout = QHBoxLayout()
        content_layout.addWidget(group_left, 1.5)
        content_layout.addLayout(group_right, 2)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    # ===================== HÀM XỬ LÝ CAMERA =====================
    def start_camera(self):
        """Bật camera thật"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.notice_label.setText("❌ Không thể mở camera. Vui lòng kiểm tra thiết bị!")
            self.notice_label.setStyleSheet("color: red; font-weight: bold;")
            return

        self.notice_label.setText("✅ Camera đã mở. Đang hiển thị hình ảnh...")
        self.notice_label.setStyleSheet("color: green; font-weight: bold;")
        self.timer_camera.start(30)

    def update_camera_frame(self):
        """Hiển thị khung hình từ camera"""
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.camera_frame.width(), self.camera_frame.height(), Qt.KeepAspectRatio
        )
        self.camera_frame.setPixmap(pixmap)

    def stop_camera(self):
        """Tắt camera"""
        if self.timer_camera.isActive():
            self.timer_camera.stop()
        if self.cap:
            self.cap.release()
        self.camera_frame.clear()
        self.camera_frame.setText("Camera Preview\n(ảnh demo)")
        self.notice_label.setText("Camera đã tắt.")
        self.notice_label.setStyleSheet("color: orange; font-weight: bold;")

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\n dd-MM-yyyy"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionUI()
    window.show()
    sys.exit(app.exec_())