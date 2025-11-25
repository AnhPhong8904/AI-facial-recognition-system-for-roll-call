from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import QProcess, Qt
import os
import sys

class TrainingMonitorDialog(QDialog):
    def __init__(self, script_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Đang huấn luyện AI...")
        self.resize(600, 400)
        
        # Layout
        layout = QVBoxLayout()
        
        # Label thông báo
        self.lbl_status = QLabel("Đang khởi tạo tiến trình...")
        layout.addWidget(self.lbl_status)
        
        # Khung hiển thị log (Màn hình đen, chữ xanh)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background-color: black; color: #00FF00; font-family: Consolas;")
        layout.addWidget(self.txt_log)
        
        # Nút đóng (ban đầu ẩn hoặc disable)
        self.btn_close = QPushButton("Đóng")
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.setEnabled(False)
        layout.addWidget(self.btn_close)
        
        self.setLayout(layout)
        
        # Cấu hình QProcess để chạy script
        self.process = QProcess()
        self.process.setProgram(sys.executable) # Dùng chính python đang chạy app
        
        # Quan trọng: Thêm tham số "-u" để python không buffer (in ra ngay lập tức)
        self.process.setArguments(["-u", script_path])
        
        # Thiết lập thư mục làm việc (tránh lỗi không tìm thấy file ảnh)
        work_dir = os.path.dirname(script_path)
        self.process.setWorkingDirectory(work_dir)
        
        # Kết nối tín hiệu
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        
        # Bắt đầu chạy
        self.start_training()

    def start_training(self):
        self.lbl_status.setText("Đang chạy script training...")
        self.process.start()

    def handle_stdout(self):
        """Hứng output thông thường (print)"""
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf8")
        self.txt_log.append(text)
        # Tự động cuộn xuống dưới cùng
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())

    def handle_stderr(self):
        """Hứng lỗi (nếu có)"""
        data = self.process.readAllStandardError()
        text = bytes(data).decode("utf8")
        # In lỗi bằng màu đỏ (dùng HTML)
        self.txt_log.append(f"<span style='color:red'>{text}</span>")

    def handle_finished(self):
        self.lbl_status.setText("Huấn luyện hoàn tất!")
        self.btn_close.setEnabled(True)
        self.btn_close.setText("Đóng (Hoàn thành)")
        QMessageBox.information(self, "Xong", "Quá trình huấn luyện đã kết thúc.")

    def closeEvent(self, event):
        # Nếu đang chạy mà bấm X thì kill process
        if self.process.state() == QProcess.Running:
            self.process.kill()
        event.accept()