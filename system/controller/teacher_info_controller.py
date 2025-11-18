from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QLineEdit, QComboBox, QDateEdit
from PyQt5.QtCore import Qt, QDate
import datetime
from ui.teacher_info import TeacherWindow
from model import teacher_service

class TeacherController:
    def __init__(self, on_close_callback):
        """
        Khởi tạo controller
        :param on_close_callback: Hàm để gọi khi cửa sổ này đóng (để quay lại Home)
        """
        self.view = TeacherWindow()
        self.on_close_callback = on_close_callback
        
        # Biến để lưu ID khi chọn từ bảng
        self.current_teacher_id_gv = None
        self.current_teacher_id_taikhoan = None
        
        # Kết nối các nút và sự kiện
        self.connect_signals()
        
        # Tải danh sách giảng viên khi mở
        self.load_all_teachers()

    def connect_signals(self):
        """Kết nối tất cả các nút bấm từ View với các hàm xử lý trong Controller"""
        self.view.btn_add.clicked.connect(self.add_teacher)
        self.view.btn_update.clicked.connect(self.update_teacher)
        self.view.btn_delete.clicked.connect(self.delete_teacher)
        self.view.btn_refresh.clicked.connect(self.clear_form)
        
        self.view.btn_search.clicked.connect(self.search_teachers)
        self.view.btn_all.clicked.connect(self.load_all_teachers)
        
        self.view.back_btn.clicked.connect(self.handle_close)
        
        # Sự kiện click vào bảng (Table)
        self.view.table.itemSelectionChanged.connect(self.on_table_row_clicked)

    def show(self):
        """Hiển thị cửa sổ"""
        self.view.show()

    def handle_close(self):
        """Đóng cửa sổ hiện tại và gọi callback để hiển thị lại cửa sổ Home"""
        print("Đóng cửa sổ Giảng viên.")
        self.view.close()
        self.on_close_callback()

    # ==========================================================
    # HÀM TẢI VÀ HIỂN THỊ DỮ LIỆU
    # ==========================================================
    
    def load_all_teachers(self):
        """Tải và hiển thị tất cả giảng viên lên bảng"""
        print("Đang tải danh sách giảng viên...")
        try:
            data = teacher_service.get_all_teachers()
            self.populate_table(data)
        except Exception as e:
            self.show_message("Lỗi", f"Không thể tải danh sách giảng viên: {e}", level="error")
        
        self.view.search_input.clear()
        self.clear_form()

    def populate_table(self, data):
        """Hiển thị dữ liệu (data) lên QTableWidget (self.view.table)"""
        self.view.table.setRowCount(0) # Xóa dữ liệu cũ
        if not data:
            print("Không có dữ liệu giảng viên.")
            return

        self.view.table.setRowCount(len(data))
        
        for row_index, row_data in enumerate(data):
            # Cột 0 (ID_TAIKHOAN) và 1 (ID_GV) đã bị ẩn trong UI
            # (ID_TAIKHOAN, ID_GV, MA_GV, HO_TEN, GIOI_TINH, NGAY_SINH, DIA_CHI, SDT, EMAIL, TEN_DANG_NHAP)
            
            for col_index, item in enumerate(row_data):
                cell_value = ""
                if isinstance(item, (datetime.date, datetime.datetime)):
                    # Định dạng ngày sinh (service đã format sẵn, nhưng vẫn xử lý nếu có)
                    cell_value = item.strftime("%d/%m/%Y")
                else:
                    # Service đã format ngày sinh thành string, dùng trực tiếp
                    cell_value = str(item) if item is not None else ""
                
                cell_item = QTableWidgetItem(cell_value)
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable) 
                
                self.view.table.setItem(row_index, col_index, cell_item)
                
        self.view.table.resizeColumnsToContents()

    def on_table_row_clicked(self):
        """Khi nhấn vào một dòng trên bảng, điền thông tin vào form"""
        selected_rows = self.view.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        selected_row = selected_rows[0].row()
        
        try:
            # Lấy dữ liệu từ bảng (dựa trên thứ tự cột đã định nghĩa)
            id_tk = self.view.table.item(selected_row, 0).text()
            id_gv = self.view.table.item(selected_row, 1).text()
            ma_gv = self.view.table.item(selected_row, 2).text()
            ho_ten = self.view.table.item(selected_row, 3).text()
            gioi_tinh = self.view.table.item(selected_row, 4).text()
            ngay_sinh_str = self.view.table.item(selected_row, 5).text()
            dia_chi = self.view.table.item(selected_row, 6).text()
            sdt = self.view.table.item(selected_row, 7).text()
            email = self.view.table.item(selected_row, 8).text()
            ten_dang_nhap = self.view.table.item(selected_row, 9).text()

            # Lưu ID lại để dùng cho Sửa/Xóa
            self.current_teacher_id_gv = int(id_gv)
            self.current_teacher_id_taikhoan = int(id_tk)

            # --- Điền vào form ---
            self.view.inputs["Mã giảng viên:"].setText(ma_gv)
            self.view.inputs["Họ tên:"].setText(ho_ten)
            self.view.inputs["Số điện thoại:"].setText(sdt)
            self.view.inputs["Email:"].setText(email)
            self.view.inputs["Tên đăng nhập:"].setText(ten_dang_nhap)
            self.view.inputs["Địa chỉ:"].setText(dia_chi)
            
            # Xử lý ComboBox Giới tính
            index = self.view.inputs["Giới tính:"].findText(gioi_tinh, Qt.MatchFixedString)
            if index >= 0:
                self.view.inputs["Giới tính:"].setCurrentIndex(index)
            else:
                self.view.inputs["Giới tính:"].setCurrentIndex(0) # Về rỗng

            # Xử lý QDateEdit Ngày sinh với nhiều format fallback
            if ngay_sinh_str:
                ngay_sinh_qdate = QDate.fromString(ngay_sinh_str, "dd/MM/yyyy")
                if not ngay_sinh_qdate.isValid():
                    ngay_sinh_qdate = QDate.fromString(ngay_sinh_str, "dd-MM-yyyy")
                if not ngay_sinh_qdate.isValid():
                    ngay_sinh_qdate = QDate.fromString(ngay_sinh_str, "yyyy-MM-dd")
                if not ngay_sinh_qdate.isValid():
                    ngay_sinh_qdate = QDate.fromString(ngay_sinh_str, Qt.ISODate)
                
                if ngay_sinh_qdate.isValid():
                    self.view.inputs["Ngày sinh:"].setDate(ngay_sinh_qdate)
                else:
                    self.view.inputs["Ngày sinh:"].setDate(QDate(2000, 1, 1))
            else:
                self.view.inputs["Ngày sinh:"].setDate(QDate(2000, 1, 1))
            
            self.view.inputs["Mật khẩu:"].setText("")
            
            # Không cho sửa Mã GV và Tên đăng nhập khi đã chọn
            self.view.inputs["Mã giảng viên:"].setEnabled(False)
            self.view.inputs["Tên đăng nhập:"].setEnabled(False)

        except Exception as e:
            print(f"Lỗi khi đọc dữ liệu từ bảng: {e}")
            self.clear_form()


    def clear_form(self):
        """Làm mới (xóa) tất cả các trường trong form"""
        for widget in self.view.inputs.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate(2000, 1, 1))
        
        # Cho phép nhập Mã GV và Tên đăng nhập trở lại
        self.view.inputs["Mã giảng viên:"].setEnabled(True)
        self.view.inputs["Tên đăng nhập:"].setEnabled(True)
        
        # Bỏ chọn trên bảng
        self.view.table.clearSelection()
        
        # Xóa ID đã lưu
        self.current_teacher_id_gv = None
        self.current_teacher_id_taikhoan = None

    # ==========================================================
    # HÀM XỬ LÝ CRUD (THÊM, SỬA, XÓA)
    # ==========================================================
    
    def get_data_from_form(self):
        """Hàm tiện ích lấy dữ liệu từ các widget trong form"""
        data = {}
        data['ma_gv'] = self.view.inputs["Mã giảng viên:"].text().strip()
        data['ho_ten'] = self.view.inputs["Họ tên:"].text().strip()
        data['sdt'] = self.view.inputs["Số điện thoại:"].text().strip()
        data['email'] = self.view.inputs["Email:"].text().strip()
        data['ten_dang_nhap'] = self.view.inputs["Tên đăng nhập:"].text().strip()
        data['mat_khau'] = self.view.inputs["Mật khẩu:"].text() # Không strip mật khẩu
        
        # Lấy từ ComboBox
        data['gioi_tinh'] = self.view.inputs["Giới tính:"].currentText()
        if data['gioi_tinh'] == "": # Nếu là chuỗi rỗng
            data['gioi_tinh'] = None
            
        # Lấy từ QDateEdit
        date = self.view.inputs["Ngày sinh:"].date()
        # Nếu là ngày mặc định, coi như không nhập
        if date == QDate(2000, 1, 1):
             data['ngay_sinh'] = None
        else:
             data['ngay_sinh'] = date.toString("yyyy-MM-dd") # Format CSDL
             
        data['dia_chi'] = self.view.inputs["Địa chỉ:"].text().strip()
        if data['dia_chi'] == "":
            data['dia_chi'] = None
            
        return data

    def add_teacher(self):
        """Xử lý Thêm mới giảng viên"""
        data = self.get_data_from_form()

        if not data['ma_gv'] or not data['ho_ten'] or not data['ten_dang_nhap'] or not data['mat_khau']:
            self.show_message("Thiếu thông tin", "Mã giảng viên, Họ tên, Tên đăng nhập và Mật khẩu là bắt buộc.", level="warning")
            return
            
        try:
            success, message = teacher_service.add_teacher(data)
            if success:
                self.show_message("Thành công", message, level="info")
                self.load_all_teachers()
            else:
                self.show_message("Thất bại", message, level="error")
        except Exception as e:
             self.show_message("Lỗi", f"Đã xảy ra lỗi khi thêm: {e}", level="error")


    def update_teacher(self):
        """Xử lý Cập nhật giảng viên"""
        if self.current_teacher_id_gv is None or self.current_teacher_id_taikhoan is None:
            self.show_message("Chưa chọn", "Vui lòng chọn một giảng viên từ bảng để cập nhật.", level="warning")
            return

        data = self.get_data_from_form()
        
        if not data['ma_gv'] or not data['ho_ten']:
            self.show_message("Thiếu thông tin", "Mã giảng viên và Họ tên là bắt buộc.", level="warning")
            return
            
        # Nếu không nhập mật khẩu mới, gửi None
        if not data['mat_khau']:
            data['mat_khau'] = None 
            
        try:
            success, message = teacher_service.update_teacher(
                self.current_teacher_id_gv, 
                self.current_teacher_id_taikhoan, 
                data
            )
            
            if success:
                self.show_message("Thành công", message, level="info")
                self.load_all_teachers()
            else:
                self.show_message("Thất bại", message, level="error")
        except Exception as e:
             self.show_message("Lỗi", f"Đã xảy ra lỗi khi cập nhật: {e}", level="error")

    def delete_teacher(self):
        """Xử lý Xóa giảng viên"""
        if self.current_teacher_id_gv is None or self.current_teacher_id_taikhoan is None:
            self.show_message("Chưa chọn", "Vui lòng chọn một giảng viên từ bảng để xóa.", level="warning")
            return
            
        ma_gv = self.view.inputs["Mã giảng viên:"].text()

        confirm = self.show_message("Xác nhận xóa", 
                                  f"Bạn có chắc chắn muốn xóa giảng viên '{ma_gv}' không?\n"
                                  "Hành động này sẽ xóa cả tài khoản liên quan.",
                                  level="question")
        
        if confirm != QMessageBox.Yes:
            return
            
        try:
            success, message = teacher_service.delete_teacher(
                self.current_teacher_id_gv, 
                self.current_teacher_id_taikhoan
            )
            
            if success:
                self.show_message("Thành công", message, level="info")
                self.load_all_teachers()
            else:
                self.show_message("Thất bại", message, level="error")
        except Exception as e:
             self.show_message("Lỗi", f"Đã xảy ra lỗi khi xóa: {e}", level="error")

    # ==========================================================
    # HÀM XỬ LÝ TÌM KIẾM
    # ==========================================================

    def search_teachers(self):
        """Xử lý Tìm kiếm giảng viên"""
        criteria_vi = self.view.search_by.currentText()
        keyword = self.view.search_input.text().strip()

        if not keyword:
            self.show_message("Thiếu thông tin", "Vui lòng nhập từ khóa tìm kiếm.", level="warning")
            return
            
        # Map từ Tiếng Việt (UI) sang tên cột (CSDL)
        criteria_map = {
            "Mã giảng viên": "MA_GV",
            "Tên giảng viên": "HO_TEN",
            "Email": "EMAIL",
            "SĐT": "SDT"
        }
        
        criteria_db = criteria_map.get(criteria_vi)
        if not criteria_db:
             self.show_message("Lỗi", "Tiêu chí tìm kiếm không hợp lệ.", level="error")
             return
             
        print(f"Đang tìm kiếm: {criteria_db} - {keyword}")
        
        try:
            data = teacher_service.search_teachers(criteria_db, keyword)
            self.populate_table(data)
            if not data:
                self.show_message("Thông báo", "Không tìm thấy kết quả nào.", level="info")
        except Exception as e:
            self.show_message("Lỗi", f"Lỗi khi tìm kiếm CSDL: {e}", level="error")
            
    # ==========================================================
    # HÀM TIỆN ÍCH
    # ==========================================================

    def show_message(self, title, message, level="info"):
        """
        Hiển thị hộp thoại thông báo.
        level: 'info', 'warning', 'error', 'question'
        """
        if level == "info":
            QMessageBox.information(self.view, title, message)
        elif level == "warning":
            QMessageBox.warning(self.view, title, message)
        elif level == "error":
            QMessageBox.critical(self.view, title, message)
        elif level == "question":
            return QMessageBox.question(self.view, title, message, 
                                        QMessageBox.Yes | QMessageBox.No, 
                                        QMessageBox.No)