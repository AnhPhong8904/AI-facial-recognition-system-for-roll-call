import os
import sys
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QDate, QTime, QDateTime
from PyQt5.QtGui import QPixmap
# Sửa tên file import
from ui.checkin_info import CheckinWindow 
# Chúng ta sẽ cần file service mới
from model import checkin_service 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CheckinController:
    def __init__(self, on_close_callback):
        """
        Khởi tạo controller
        :param on_close_callback: Hàm để gọi khi cửa sổ này đóng (để quay lại Home)
        """
        self.view = CheckinWindow()
        self.on_close_callback = on_close_callback
        # Ảnh vào và ảnh ra tách riêng
        self.selected_image_in_path = None
        self.selected_image_out_path = None
        
        # Kết nối các nút và sự kiện
        self.connect_signals()
        
        # Tải danh sách điểm danh khi mở
        self.load_all_checkins()

    def connect_signals(self):
        """Kết nối tất cả các nút bấm từ View với các hàm xử lý trong Controller"""
        # Nút chức năng (Form)
        self.view.btn_update.clicked.connect(self.handle_update_checkin)
        self.view.btn_delete.clicked.connect(self.handle_delete_checkin)
        self.view.btn_reset.clicked.connect(self.clear_form)
        # Nút xem ảnh vào / ảnh ra (nếu UI đã tạo)
        if hasattr(self.view, "btn_view_image_in"):
            self.view.btn_view_image_in.clicked.connect(self.handle_view_image_in)
        if hasattr(self.view, "btn_view_image_out"):
            self.view.btn_view_image_out.clicked.connect(self.handle_view_image_out)
        # Giữ tương thích: nếu vẫn chỉ có một nút cũ thì xem ảnh vào
        if hasattr(self.view, "btn_view_image") and not hasattr(self.view, "btn_view_image_in"):
            self.view.btn_view_image.clicked.connect(self.handle_view_image_in)
        
        # Nút chức năng (Tìm kiếm)
        self.view.btn_search.clicked.connect(self.handle_search_checkin)
        self.view.btn_today.clicked.connect(self.handle_today_checkins)
        self.view.btn_all.clicked.connect(self.load_all_checkins)
        
        # Nút Quay lại (Header)
        self.view.back_btn.clicked.connect(self.handle_close)
        
        # Sự kiện click vào bảng (Table)
        self.view.table.itemSelectionChanged.connect(self.handle_table_click)
        
        # (Các nút Import, Export, View Image sẽ được thêm sau)
        # self.view.btn_view_image.clicked.connect(self.handle_view_image)

    def show(self):
        """Hiển thị cửa sổ"""
        self.view.show()

    def handle_close(self):
        """Đóng cửa sổ hiện tại và gọi callback để hiển thị lại cửa sổ Home"""
        print("Đóng cửa sổ Quản lý Điểm danh.")
        self.view.close()
        self.on_close_callback()

    # ==========================================================
    # HÀM TẢI VÀ HIỂN THỊ DỮ LIỆU
    # ==========================================================
    
    def load_all_checkins(self):
        """Tải và hiển thị tất cả dữ liệu điểm danh lên bảng"""
        print("Đang tải danh sách điểm danh...")
        data = checkin_service.get_all_checkins()
        self.view.populate_table(data)
        self.view.search_input.clear() # Xóa ô tìm kiếm
        self.clear_form()

    def handle_table_click(self):
        """Khi nhấn vào một dòng trên bảng, điền thông tin vào form"""
        selected_rows = self.view.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        selected_row = selected_rows[0].row()
        
        # Lấy dữ liệu từ bảng
        # "ID Điểm danh", "ID Buổi", "Mã SV", "Tên Sinh viên", 
        # "Mã Lớp", "Thời gian vào", "Trạng thái", "Ghi chú",
        # "Ảnh vào", "Thời gian ra", "Ảnh ra"
        id_diemdanh = self.view.table.item(selected_row, 0).text()
        id_buoi = self.view.table.item(selected_row, 1).text()
        ma_sv = self.view.table.item(selected_row, 2).text()
        ten_sv = self.view.table.item(selected_row, 3).text()
        ma_lop = self.view.table.item(selected_row, 4).text()
        thoi_gian_str = self.view.table.item(selected_row, 5).text()
        trang_thai = self.view.table.item(selected_row, 6).text()
        ghi_chu = self.view.table.item(selected_row, 7).text()
        self.selected_image_in_path = self.view.table.item(selected_row, 8).text() if self.view.table.columnCount() > 8 and self.view.table.item(selected_row, 8) else ""
        # Cột 9 là thời gian ra, cột 10 (nếu có) là ảnh ra
        self.selected_image_out_path = ""
        if self.view.table.columnCount() > 10:
            item_out = self.view.table.item(selected_row, 10)
            if item_out:
                self.selected_image_out_path = item_out.text()
        
        # Điền vào form
        self.view.inputs["ID điểm danh:"].setText(id_diemdanh)
        self.view.inputs["ID Buổi học:"].setText(id_buoi)
        self.view.inputs["Mã Lớp:"].setText(ma_lop)
        self.view.inputs["Mã Sinh viên:"].setText(ma_sv)
        self.view.inputs["Tên Sinh viên:"].setText(ten_sv)
        self.view.inputs["Trạng thái:"].setCurrentText(trang_thai)
        self.view.inputs["Ghi chú:"].setText(ghi_chu)
        
        # Chuyển đổi chuỗi thời gian
        thoi_gian_dt = QDateTime.fromString(thoi_gian_str, "dd-MM-yyyy HH:mm:ss")
        self.view.inputs["Thời gian:"].setDateTime(thoi_gian_dt)
        
        # Không cho sửa Mã SV và ID Buổi học khi đã chọn (vì đây là khóa chính)
        self.view.inputs["ID Buổi học:"].setEnabled(False)
        self.view.inputs["Mã Sinh viên:"].setEnabled(False)

    def clear_form(self):
        """Làm mới (xóa) tất cả các trường trong form"""
        self.view.clear_form()
        self.selected_image_in_path = None
        self.selected_image_out_path = None

    def _show_image(self, raw_path, title):
        """Hiển thị hộp thoại xem ảnh với đường dẫn và tiêu đề truyền vào."""
        if not raw_path:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một dòng có ảnh để xem.", level="warning")
            return

        raw_path = raw_path.strip()
        if not raw_path:
            self.view.show_message("Không có ảnh", "Bản ghi này không lưu đường dẫn ảnh.", level="info")
            return

        image_path = raw_path
        if not os.path.isabs(image_path):
            image_path = os.path.normpath(os.path.join(BASE_DIR, image_path))

        if not os.path.exists(image_path):
            self.view.show_message("Không tìm thấy", f"Không tìm thấy ảnh tại:\n{image_path}", level="error")
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.view.show_message("Lỗi ảnh", "Không thể đọc file ảnh (định dạng không hợp lệ).", level="error")
            return

        dialog = QDialog(self.view)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        scaled_pixmap = pixmap.scaled(480, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)

        path_label = QLabel(image_path)
        path_label.setWordWrap(True)
        path_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(image_label)
        layout.addWidget(path_label)
        dialog.setLayout(layout)
        dialog.exec_()

    def handle_view_image_in(self):
        """Xem ảnh điểm danh đầu giờ."""
        self._show_image(self.selected_image_in_path or "", "Ảnh điểm danh vào")

    def handle_view_image_out(self):
        """Xem ảnh điểm danh cuối giờ."""
        self._show_image(self.selected_image_out_path or "", "Ảnh điểm danh ra")

    # ==========================================================
    # HÀM XỬ LÝ CRUD (CHỈ CẬP NHẬT, XÓA - KHÔNG THÊM)
    # ==========================================================

    def handle_update_checkin(self):
        """Xử lý Cập nhật điểm danh"""
        # 1. Lấy dữ liệu từ Form
        data = self.view.get_form_data()

        # 2. Kiểm tra
        if not data["id_diemdanh"]:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một mục điểm danh từ bảng để cập nhật.", level="warning")
            return
            
        if not data["trang_thai"]:
            self.view.show_message("Thiếu thông tin", "Trạng thái (Có mặt/Vắng/Đi muộn) là bắt buộc.", level="warning")
            return

        # 3. Gọi Service
        success, message = checkin_service.update_checkin(data)
        
        # 4. Hiển thị kết quả và tải lại
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_checkins()
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_delete_checkin(self):
        """Xử lý Xóa điểm danh"""
        # 1. Lấy ID Điểm danh
        id_diemdanh = self.view.inputs["ID điểm danh:"].text()
        
        if not id_diemdanh:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một mục điểm danh từ bảng để xóa.", level="warning")
            return

        # 2. Hộp thoại XÁC NHẬN
        confirm = self.view.show_message("Xác nhận xóa", 
                                         f"Bạn có chắc chắn muốn xóa mục điểm danh (ID: {id_diemdanh}) không?",
                                         level="question")
        
        if confirm != QMessageBox.Yes:
            return

        # 3. Gọi Service
        success, message = checkin_service.delete_checkin(int(id_diemdanh))
        
        # 4. Hiển thị kết quả và tải lại
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_checkins()
        else:
            self.view.show_message("Thất bại", message, level="error")

    # ==========================================================
    # HÀM XỬ LÝ TÌM KIẾM
    # ==========================================================

    def handle_search_checkin(self):
        """Xử lý Tìm kiếm điểm danh"""
        data = self.view.get_search_data()
        search_by = data["search_by"]
        keyword = data["keyword"]

        if not keyword:
            self.view.show_message("Thiếu thông tin", "Vui lòng nhập từ khóa tìm kiếm.", level="warning")
            return
            
        print(f"Đang tìm kiếm điểm danh: {search_by} - {keyword}")
        result_data = checkin_service.search_checkins(search_by, keyword)
        
        if result_data is None:
            self.view.show_message("Lỗi", "Lỗi khi tìm kiếm CSDL.", level="error")
        elif not result_data:
            self.view.show_message("Thông báo", "Không tìm thấy kết quả nào.", level="info")
        
        self.view.populate_table(result_data)

    def handle_today_checkins(self):
        """Tải dữ liệu điểm danh của ngày hôm nay"""
        print("Đang tải danh sách điểm danh hôm nay...")
        data = checkin_service.get_today_checkins()
        
        if data is None:
            self.view.show_message("Lỗi", "Lỗi khi tải dữ liệu CSDL.", level="error")
        elif not data:
            self.view.show_message("Thông báo", "Không có dữ liệu điểm danh hôm nay.", level="info")

        self.view.populate_table(data)
        self.view.search_input.clear()
        self.clear_form()