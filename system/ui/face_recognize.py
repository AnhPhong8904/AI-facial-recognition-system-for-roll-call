import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QHBoxLayout,
    QVBoxLayout, QGroupBox, QFrame, QGridLayout, QLineEdit, QListWidget
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSize
from PyQt5.QtGui import QFont, QImage, QPixmap, QIcon

# [SỬA] Đổi tên class
class FaceRecognizeWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.cap = None 
        self.timer_camera = QTimer()
        # [SỬA] Xóa logic connect
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Điểm danh khuôn mặt")
        self.setGeometry(300, 100, 1200, 750)
        self.setStyleSheet("background-color: white; font-family: Arial;")

        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1e40af; color: white; border-radius: 8px;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(25, 10, 25, 10)

        clock_icon = QLabel()
        clock_icon_path = r"system/img/clock.png" 
        
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

        self.back_btn = QPushButton(" Quay lại") 
        back_icon_path = r"system/img/back.png"
        
        if os.path.exists(back_icon_path):
            self.back_btn.setIcon(QIcon(back_icon_path))
            self.back_btn.setIconSize(QSize(20, 20))
        else:
            print(f"Không tìm thấy icon 'back' tại: {back_icon_path}")
            
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2); color: white;
                font-weight: bold; border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px; font-size: 14px; padding: 8px 15px;
            }
            QPushButton:hover { 
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)

        header_layout.addLayout(time_layout)
        header_layout.addStretch(1)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.back_btn)
        header.setLayout(header_layout)

        group_left = QGroupBox("Màn hình nhận diện")
        group_left.setStyleSheet("""
            QGroupBox {
                font-weight: bold; font-size: 15px; color: #0B3D91;
                border: 2px solid #0B3D91; border-radius: 10px;
                margin-top: 15px; padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; subcontrol-position: top center;
                padding: 0 10px; background-color: white;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        top_select_layout = QHBoxLayout()
        lbl_subject = QLabel("Chọn Lớp học phần (Buổi học):")
        lbl_subject.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.subject_cb = QComboBox() 
        self.subject_cb.setPlaceholderText("Vui lòng chọn buổi học...")
        
        top_select_layout.addWidget(lbl_subject)
        top_select_layout.addWidget(self.subject_cb, 1)
        left_layout.addLayout(top_select_layout)

        self.camera_frame = QLabel()
        self.camera_frame.setFixedSize(640, 480)
        self.camera_frame.setStyleSheet("background-color: #333; border: 2px solid #0B3D91; border-radius: 6px;")
        self.camera_frame.setAlignment(Qt.AlignCenter)
        self.camera_frame.setText("<font color='white'>CAMERA TẮT</font>")
        left_layout.addWidget(self.camera_frame, alignment=Qt.AlignCenter)

        self.notice_label = QLabel("Vui lòng chọn Lớp học phần và Mở Camera.")
        self.notice_label.setWordWrap(True)
        self.notice_label.setStyleSheet("color: #D97706; font-weight: bold; font-size: 13px; border-top: 2px solid #0B3D91; padding-top: 5px; min-height: 40px;")
        self.notice_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.notice_label)

        btn_layout = QHBoxLayout()
        self.open_btn = QPushButton("Mở Camera")
        self.close_btn = QPushButton("Đóng Camera")
        
        # ==========================================================
        # [MỚI] THÊM NÚT CHỐT SỔ
        # ==========================================================
        self.finalize_btn = QPushButton("Chốt sổ (Ghi Vắng)")
        self.finalize_btn.setStyleSheet("""
            QPushButton {
                background-color: #B91C1C; color: white;
                font-weight: bold; border-radius: 6px;
            }
            QPushButton:hover { background-color: #DC2626; }
            QPushButton:disabled { background-color: #999; }
        """)
        
        # Cập nhật style cho các nút Mở/Đóng
        for btn in [self.open_btn, self.close_btn, self.finalize_btn]:
            btn.setFixedWidth(150)
            btn.setFixedHeight(35)
            
            # Chỉ áp dụng style xanh cho nút Mở/Đóng
            if btn != self.finalize_btn:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0B3D91; color: white;
                        font-weight: bold; border-radius: 6px;
                    }
                    QPushButton:hover { background-color: #1E5CC5; }
                    QPushButton:disabled { background-color: #999; }
                """)
        
        self.close_btn.setEnabled(False)
        self.open_btn.setEnabled(False) 
        # Nút Chốt sổ cũng bị vô hiệu hóa lúc đầu
        self.finalize_btn.setEnabled(False) 

        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addWidget(self.finalize_btn) # <<< THÊM NÚT VÀO LAYOUT
        left_layout.addLayout(btn_layout)
        group_left.setLayout(left_layout)

        group_right_layout = QVBoxLayout()

        success_box = QGroupBox("Điểm danh thành công (Gần nhất)")
        success_box.setStyleSheet(group_left.styleSheet())
        success_layout = QGridLayout()
        success_layout.setColumnStretch(2, 1)

        self.face_img_label = QLabel()
        self.face_img_label.setFixedSize(130, 130)
        self.face_img_label.setStyleSheet("border: 2px solid #aaa; border-radius: 8px; background-color: #eee;")
        self.face_img_label.setText("Ảnh\nnhận diện")
        self.face_img_label.setAlignment(Qt.AlignCenter)

        self.id_le = QLineEdit()
        self.name_le = QLineEdit()
        self.time_le = QLineEdit()
        
        for le in [self.id_le, self.name_le, self.time_le]:
            le.setReadOnly(True)
            le.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; padding: 5px; font-weight: bold;")

        success_layout.addWidget(self.face_img_label, 0, 0, 3, 1)
        success_layout.addWidget(QLabel("Mã sinh viên:"), 0, 1)
        success_layout.addWidget(self.id_le, 0, 2)
        success_layout.addWidget(QLabel("Tên sinh viên:"), 1, 1)
        success_layout.addWidget(self.name_le, 1, 2)
        success_layout.addWidget(QLabel("Thời gian:"), 2, 1)
        success_layout.addWidget(self.time_le, 2, 2)
        success_box.setLayout(success_layout)

        info_box = QGroupBox("Thông tin buổi học")
        info_box.setStyleSheet(group_left.styleSheet())
        info_layout = QGridLayout()
        info_layout.setColumnStretch(1, 1)

        self.class_name_label = QLabel("<font color='#C2410C'>Vui lòng chọn buổi học</font>")
        self.subject_name_label = QLabel("<font color='#C2410C'>...</font>")
        self.class_time_label = QLabel("<font color='#C2410C'>...</font>")
        self.teacher_name_label = QLabel("<font color='#C2410C'>...</font>") 
        self.class_room_label = QLabel("<font color='#C2410C'>...</font>") 

        info_layout.addWidget(QLabel("Lớp tín chỉ:"), 0, 0)
        info_layout.addWidget(self.class_name_label, 0, 1)
        info_layout.addWidget(QLabel("Tên môn học:"), 1, 0)
        info_layout.addWidget(self.subject_name_label, 1, 1)
        info_layout.addWidget(QLabel("Thời gian:"), 2, 0)
        info_layout.addWidget(self.class_time_label, 2, 1)
        info_layout.addWidget(QLabel("Giảng viên:"), 3, 0) 
        info_layout.addWidget(self.teacher_name_label, 3, 1) 
        info_layout.addWidget(QLabel("Phòng học:"), 4, 0) 
        info_layout.addWidget(self.class_room_label, 4, 1)
        
        info_box.setLayout(info_layout)
        
        attendance_box = QGroupBox("Danh sách Sinh viên")
        attendance_box.setStyleSheet(group_left.styleSheet())
        attendance_layout = QVBoxLayout()
        
        self.attendance_label = QLabel("Đã điểm danh: 0 | Vắng: 0 | Tổng: 0")
        self.attendance_label.setStyleSheet("font-weight: bold; font-size: 13px; margin-bottom: 5px;")
        
        list_layout = QHBoxLayout()
        
        self.present_list_widget = QListWidget()
        self.present_list_widget.setStyleSheet("border: 1px solid green; background-color: #f0fff0; padding: 5px;")
        list_layout.addWidget(self.present_list_widget, 1)

        self.absent_list_widget = QListWidget()
        self.absent_list_widget.setStyleSheet("border: 1px solid red; background-color: #fff0f0; padding: 5px;")
        list_layout.addWidget(self.absent_list_widget, 1)
        
        attendance_layout.addWidget(self.attendance_label)
        attendance_layout.addLayout(list_layout)
        attendance_box.setLayout(attendance_layout)

        group_right_layout.addWidget(success_box)
        group_right_layout.addWidget(info_box)
        group_right_layout.addWidget(attendance_box, 1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(header)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        content_layout.addWidget(group_left, 1)
        content_layout.addLayout(group_right_layout, 1)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    # [SỬA] Xóa logic, chỉ để lại hàm
    
    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP\n dd-MM-yyyy"))

    # ==========================================================
    # HÀM TIỆN ÍCH (HELPER FUNCTIONS)
    # ==========================================================
    
    def update_frame_on_ui(self, q_image):
        """Dùng để controller cập nhật khung hình camera."""
        if q_image:
            pixmap = QPixmap.fromImage(q_image).scaled(
                self.camera_frame.width(), self.camera_frame.height(), Qt.KeepAspectRatio
            )
            self.camera_frame.setPixmap(pixmap)
        else:
            self.camera_frame.clear()
            self.camera_frame.setText("<font color='white'>CAMERA TẮT</font>")

    def update_notice(self, text, level="info"):
        """Cập nhật thông báo (label dưới camera)."""
        self.notice_label.setText(text)
        if level == "info":
            self.notice_label.setStyleSheet("color: #0B3D91; font-weight: bold; font-size: 13px; border-top: 2px solid #0B3D91; padding-top: 5px; min-height: 40px;")
        elif level == "success":
            self.notice_label.setStyleSheet("color: #166534; font-weight: bold; font-size: 13px; border-top: 2px solid #166534; padding-top: 5px; min-height: 40px;")
        elif level == "warning":
            self.notice_label.setStyleSheet("color: #D97706; font-weight: bold; font-size: 13px; border-top: 2px solid #D97706; padding-top: 5px; min-height: 40px;")
        elif level == "error":
            self.notice_label.setStyleSheet("color: #DC2626; font-weight: bold; font-size: 13px; border-top: 2px solid #DC2626; padding-top: 5px; min-height: 40px;")

    def update_last_person_info(self, ma_sv, ho_ten, timestamp, face_q_image):
        """Cập nhật box 'Điểm danh thành công (Gần nhất)'."""
        self.id_le.setText(ma_sv)
        self.name_le.setText(ho_ten)
        self.time_le.setText(timestamp)
        
        if face_q_image:
            pixmap = QPixmap.fromImage(face_q_image).scaled(
                self.face_img_label.width(), self.face_img_label.height(), Qt.KeepAspectRatio
            )
            self.face_img_label.setPixmap(pixmap)

    def clear_last_person_info(self):
        """Xóa thông tin người điểm danh gần nhất."""
        self.id_le.clear()
        self.name_le.clear()
        self.time_le.clear()
        self.face_img_label.clear()
        self.face_img_label.setText("Ảnh\nnhận diện")

    def update_class_info(self, class_name, subject_name, time_str, teacher_name, room):
        """Cập nhật box 'Thông tin buổi học'."""
        self.class_name_label.setText(f"<font color='#1e40af'>{class_name}</font>")
        self.subject_name_label.setText(f"<font color='#1e40af'>{subject_name}</font>")
        self.class_time_label.setText(f"<font color='#1e40af'>{time_str}</font>")
        self.teacher_name_label.setText(f"<font color='#1e40af'>{teacher_name}</font>")
        self.class_room_label.setText(f"<font color='#1e40af'>{room}</font>")

    def clear_class_info(self):
        """Xóa thông tin buổi học khi không chọn môn nào."""
        self.class_name_label.setText("<font color='#C2410C'>Vui lòng chọn buổi học</font>")
        self.subject_name_label.setText("<font color='#C2410C'>...</font>")
        self.class_time_label.setText("<font color='#C2410C'>...</font>")
        self.teacher_name_label.setText("<font color='#C2410C'>...</font>")
        self.class_room_label.setText("<font color='#C2410C'>...</font>")
    
    def set_camera_buttons_state(self, is_running):
        """Bật/tắt nút Mở/Đóng camera."""
        self.open_btn.setEnabled(not is_running)
        self.close_btn.setEnabled(is_running)
        self.subject_cb.setEnabled(not is_running)
        
        # [MỚI] Nút chốt sổ chỉ bật khi đã chọn lớp VÀ camera đang tắt
        if self.subject_cb.currentIndex() > 0 and not is_running:
            self.finalize_btn.setEnabled(True)
        else:
            self.finalize_btn.setEnabled(False)