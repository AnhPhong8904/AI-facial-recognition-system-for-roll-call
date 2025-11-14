# controller/student_controller.py

import sys
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt, QDate
# Sửa tên file import (nếu cần)
from ui.student_info import StudentWindow
from model import student_service 
from model.ai_service import AIService # <-- Đã import AIService
from datetime import date 

class StudentController:
    def __init__(self, on_close_callback):
        """
        Khởi tạo controller
        :param on_close_callback: Hàm để gọi khi cửa sổ này đóng (để quay lại Home)
        """
        self.view = StudentWindow()
        self.on_close_callback = on_close_callback
        
        # Khởi tạo service AI
        self.ai_service = AIService() # <-- Đã khởi tạo AIService
        
        # Biến lưu trữ Sinh viên đang được chọn
        self.selected_ma_sv = None
        self.selected_id_sv = None # Cần ID_SV để Đăng ký/Tải
        
        # Kết nối các nút và sự kiện
        self.connect_signals()
        
        # Tải danh sách sinh viên khi mở
        self.load_all_students()

    def connect_signals(self):
        """Kết nối tất cả các nút bấm từ View với các hàm xử lý trong Controller"""
        # === Nút Quay lại (Header) ===
        self.view.back_btn.clicked.connect(self.handle_close)
        
        # === Group 1: Quản lý Sinh viên ===
        self.view.btn_add_student.clicked.connect(self.handle_add_student)
        self.view.btn_update_student.clicked.connect(self.handle_update_student)
        self.view.btn_delete_student.clicked.connect(self.handle_delete_student)
        self.view.btn_refresh_student.clicked.connect(self.clear_student_form_and_detail)
        
        # Tìm kiếm Sinh viên
        self.view.btn_search.clicked.connect(self.handle_search_student)
        self.view.btn_all.clicked.connect(self.load_all_students)
        
        # Bảng Sinh viên
        self.view.table_student.itemSelectionChanged.connect(self.handle_student_table_click)
        
        # Nút Nhận diện (ĐÃ KẾT NỐI)
        self.view.btn_take_photo.clicked.connect(self.handle_take_photo)
        self.view.btn_train.clicked.connect(self.handle_train_model)

        # === Group 2: Đăng ký Lớp học ===
        self.view.btn_add_registration.clicked.connect(self.handle_add_registration)
        # Nút Hủy (trong bảng) sẽ được kết nối động trong 'load_registrations_for_student'

    def show(self):
        """Hiển thị cửa sổ"""
        self.view.show()

    def handle_close(self):
        """Đóng cửa sổ hiện tại và gọi callback để hiển thị lại cửa sổ Home"""
        print("Đóng cửa sổ Quản lý Sinh viên.")
        self.view.close()
        self.on_close_callback()

    # ==========================================================
    # HÀM TẢI VÀ HIỂN THỊ DỮ LIỆU (Giữ nguyên)
    # ==========================================================
    
    def load_all_students(self):
        """Tải và hiển thị tất cả sinh viên lên bảng (Nửa trên)"""
        print("Đang tải danh sách sinh viên...")
        data = student_service.get_all_students()
        self.view.populate_student_table(data)
        self.view.search_input.clear() 
        self.clear_student_form_and_detail()

    def handle_student_table_click(self):
        """
        Khi nhấn vào một Sinh viên (Nửa trên):
        1. Điền thông tin vào Form (Bên trái).
        2. Kích hoạt Bảng Đăng ký (Nửa dưới).
        3. Tải các Lớp học Đã đăng ký (Bảng Nửa dưới).
        4. Tải các Lớp học Chưa đăng ký (ComboBox).
        """
        selected_rows = self.view.table_student.selectionModel().selectedRows()
        if not selected_rows:
            self.clear_student_form_and_detail() # Xóa Bảng Đăng ký nếu bỏ chọn
            return
            
        selected_row = selected_rows[0].row()
        
        # 1. Lấy dữ liệu từ bảng Sinh viên
        ma_sv = self.view.table_student.item(selected_row, 0).text()
        ho_ten = self.view.table_student.item(selected_row, 1).text()
        gioi_tinh = self.view.table_student.item(selected_row, 2).text()
        ngay_sinh_str_ddmmyyyy = self.view.table_student.item(selected_row, 3).text() 
        email = self.view.table_student.item(selected_row, 4).text()
        sdt = self.view.table_student.item(selected_row, 5).text()
        nganh = self.view.table_student.item(selected_row, 6).text()
        nam_hoc = self.view.table_student.item(selected_row, 7).text()
        lop_hoc = self.view.table_student.item(selected_row, 8).text()
        trang_thai_str = self.view.table_student.item(selected_row, 9).text()
        
        trang_thai_bit = 1 if trang_thai_str == "Đang học" else 0
        
        # Chuyển đổi ngày sinh (từ dd-MM-yyyy sang yyyy-MM-dd)
        try:
            ngay_sinh_sql = QDate.fromString(ngay_sinh_str_ddmmyyyy, "dd-MM-yyyy").toString("yyyy-MM-dd")
        except:
            ngay_sinh_sql = ""

        # 2. Điền vào Form (Bên trái)
        data = {
            "ma_sv": ma_sv, "ho_ten": ho_ten, "gioi_tinh": gioi_tinh,
            "ngay_sinh": ngay_sinh_sql, "email": email, "sdt": sdt,
            "nganh": nganh, "nam_hoc": nam_hoc, "lop_hoc": lop_hoc,
            "trang_thai": trang_thai_bit
        }
        self.view.set_student_form_data(data)
        self.view.inputs["Mã sinh viên:"].setEnabled(False) # Không cho sửa Mã SV

        # 3. Kích hoạt Bảng Đăng ký (Nửa dưới)
        print(f"Đã chọn SV: {ma_sv}. Đang tải danh sách đăng ký...")
        self.selected_ma_sv = ma_sv
        # Lấy ID_SV (cần cho việc Thêm/Xóa Đăng ký)
        self.selected_id_sv = student_service.get_student_id_by_ma_sv(ma_sv) 
        
        if self.selected_id_sv:
            self.view.set_registration_panel_enabled(True, ho_ten)
            # 4. Tải Lớp học Đã đăng ký (Bảng Nửa dưới)
            self.load_registrations_for_student(self.selected_id_sv)
            # 5. Tải Lớp học Chưa đăng ký (ComboBox)
            self.load_available_classes(self.selected_id_sv)
        else:
            self.view.show_message("Lỗi", f"Không tìm thấy ID_SV cho Mã {ma_sv}", level="error")
            self.clear_student_form_and_detail()

    def clear_student_form_and_detail(self):
        """Làm mới (xóa) Form SV VÀ tắt/xóa Bảng Đăng ký"""
        self.view.clear_student_form()
        self.view.set_registration_panel_enabled(False) # Tắt group Đăng ký
        self.view.populate_registration_table(None)
        self.view.populate_lophoc_combo(None)
        self.selected_ma_sv = None
        self.selected_id_sv = None

    # ==========================================================
    # HÀM XỬ LÝ CRUD SINH VIÊN (Giữ nguyên)
    # ==========================================================

    def handle_add_student(self):
        """Xử lý Thêm mới sinh viên"""
        data = self.view.get_student_form_data()

        if not data["ma_sv"] or not data["ho_ten"]:
            self.view.show_message("Thiếu thông tin", "Mã sinh viên và Họ tên là bắt buộc.", level="warning")
            return
            
        success, message = student_service.add_student(data)
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_students()
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_update_student(self):
        """Xử lý Cập nhật sinh viên"""
        data = self.view.get_student_form_data()

        if not data["ma_sv"]:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một sinh viên từ bảng để cập nhật.", level="warning")
            return

        success, message = student_service.update_student(data)
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_students()
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_delete_student(self):
        """Xử lý Xóa sinh viên (VÀ TẤT CẢ ĐĂNG KÝ/ĐIỂM DANH)"""
        ma_sv = self.view.get_selected_ma_sv()
        
        if not ma_sv:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một sinh viên từ bảng để xóa.", level="warning")
            return

        confirm = self.view.show_message("XÁC NHẬN XÓA (NGHIÊM TÚC)", 
                                         f"Bạn có chắc chắn muốn xóa sinh viên '{ma_sv}' không?\n"
                                         "HÀNH ĐỘNG NÀY SẼ XÓA TẤT CẢ DỮ LIỆU ĐĂNG KÝ, ĐIỂM DANH, THỐNG KÊ, VÀ ẢNH KHUÔN MẶT CỦA SINH VIÊN NÀY.",
                                         level="question")
        
        if confirm != QMessageBox.Yes:
            return

        success, message = student_service.delete_student(ma_sv)
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_students()
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_search_student(self):
        """Xử lý Tìm kiếm sinh viên"""
        data = self.view.get_search_data()
        result_data = student_service.search_students(data["search_by"], data["keyword"])
        
        if result_data is None:
            self.view.show_message("Lỗi", "Lỗi khi tìm kiếm CSDL.", level="error")
        elif not result_data:
            self.view.show_message("Thông báo", "Không tìm thấy kết quả nào.", level="info")
        
        self.view.populate_student_table(result_data)
        self.clear_student_form_and_detail()

    # ==========================================================
    # HÀM XỬ LÝ ĐĂNG KÝ LỚP HỌC (Giữ nguyên)
    # ==========================================================
    
    def load_registrations_for_student(self, id_sv):
        """Tải các lớp SV đã đăng ký (Bảng Nửa dưới)"""
        if id_sv is None: return
        
        data = student_service.get_registrations_for_student(id_sv)
        self.view.populate_registration_table(data)
        
        # QUAN TRỌNG: Kết nối các nút "Hủy" vừa được tạo
        for row in range(self.view.table_registration.rowCount()):
            delete_btn = self.view.table_registration.cellWidget(row, 4)
            if delete_btn:
                try:
                    # Ngắt kết nối cũ trước khi kết nối mới
                    delete_btn.clicked.disconnect() 
                except TypeError:
                    pass # Bỏ qua nếu chưa có kết nối
                delete_btn.clicked.connect(self.handle_delete_registration)

    def load_available_classes(self, id_sv):
        """Tải các lớp SV CHƯA đăng ký (ComboBox)"""
        if id_sv is None: return
        
        data = student_service.get_available_classes_for_student(id_sv)
        self.view.populate_lophoc_combo(data)

    def handle_add_registration(self):
        """Xử lý khi nhấn nút 'Đăng ký' (Bảng dưới)"""
        id_lop = self.view.combo_lophoc.currentData()
        
        if self.selected_id_sv is None:
            self.view.show_message("Lỗi", "Chưa chọn sinh viên.", level="error")
            return
            
        if id_lop is None:
            self.view.show_message("Thiếu thông tin", "Vui lòng chọn một lớp học từ danh sách.", level="warning")
            return
            
        success, message = student_service.add_registration(self.selected_id_sv, id_lop)
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            # Tải lại cả 2: Bảng đăng ký VÀ ComboBox
            self.load_registrations_for_student(self.selected_id_sv)
            self.load_available_classes(self.selected_id_sv)
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_delete_registration(self):
        """Xử lý khi nhấn nút 'Hủy' (trong Bảng dưới)"""
        # Lấy nút đã được nhấn
        sender_button = self.view.sender()
        if not sender_button:
            return
            
        # Lấy ID_DK (ID Đăng ký) đã được lưu trong nút
        id_dk = sender_button.property("id_dk")
        
        if id_dk is None:
            self.view.show_message("Lỗi", "Không thể tìm thấy ID Đăng ký của nút này.", level="error")
            return

        confirm = self.view.show_message("Xác nhận hủy", 
                                         f"Bạn có chắc chắn muốn hủy đăng ký (ID: {id_dk}) này không?",
                                         level="question")
        if confirm != QMessageBox.Yes:
            return

        success, message = student_service.delete_registration(id_dk)

        if success:
            self.view.show_message("Thành công", message, level="info")
            # Tải lại cả 2: Bảng đăng ký VÀ ComboBox
            self.load_registrations_for_student(self.selected_id_sv)
            self.load_available_classes(self.selected_id_sv)
        else:
            self.view.show_message("Thất bại", message, level="error")

    # ==========================================================
    # HÀM XỬ LÝ NHẬN DIỆN (ĐÃ CẬP NHẬT)
    # ==========================================================
    
    def handle_take_photo(self):
        """XHandle_take_photo (ĐÃ CẬP NHẬT)"""
        ma_sv = self.view.get_selected_ma_sv()
        if not ma_sv:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một sinh viên từ bảng.", level="warning")
            return
            
        # Hỏi xác nhận trước khi mở camera
        confirm = self.view.show_message("Xác nhận", 
                                         f"Bạn sắp mở camera để thu thập dữ liệu cho: {ma_sv}\n"
                                         "Vui lòng đảm bảo camera sẵn sàng và làm theo hướng dẫn trên cửa sổ camera (nhấn 'k' để chụp).\n\nNhấn 'Yes' để tiếp tục.",
                                         level="question")
        
        if confirm != QMessageBox.Yes:
            return

        # Hiển thị thông báo chờ (vì script đang chạy)
        self.view.show_message("Đang xử lý", 
                                "Đang khởi động camera...\n"
                                "Vui lòng xem cửa sổ Terminal hoặc cửa sổ Camera bật lên.", 
                                level="info")
        
        # Gọi service để chạy script
        # self.ai_service đã được khởi tạo trong __init__
        success, message = self.ai_service.start_data_collection(ma_sv)
        
        # Hiển thị kết quả
        if success:
            self.view.show_message("Hoàn tất", message, level="info")
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_train_model(self):
        """Xử lý khi nhấn nút Huấn luyện (ĐÃ CẬP NHẬT)"""
        
        # Cảnh báo người dùng về việc đơ giao diện
        confirm = self.view.show_message("Xác nhận Huấn luyện", 
                                         "Bạn có chắc chắn muốn huấn luyện lại model không?\n\n"
                                         "QUAN TRỌNG: Quá trình này có thể mất vài phút và sẽ làm GIAO DIỆN BỊ ĐƠ (FREEZE) cho đến khi hoàn tất.\n"
                                         "Đây là hành động bình thường, vui lòng chờ.",
                                         level="question")
        if confirm != QMessageBox.Yes:
            return

        # Hiển thị thông báo chờ (RẤT QUAN TRỌNG)
        # (Lưu ý: hàm show_message của bạn phải là loại không-chặn (non-blocking)
        # Nếu nó là blocking, nó sẽ không hiện lên kịp)
        self.view.show_message("Đang huấn luyện", 
                                "Bắt đầu huấn luyện... Vui lòng chờ.\n"
                                "Giao diện sẽ bị đơ (KHÔNG PHẢI LỖI) trong ít phút.\n"
                                "Xin vui lòng KHÔNG tắt ứng dụng.", 
                                level="info")
        
        # Gọi service
        success, message = self.ai_service.start_training()
        
        # Hiển thị kết quả
        if success:
            self.view.show_message("Hoàn tất", message, level="info")
        else:
            self.view.show_message("Thất bại", message, level="error")