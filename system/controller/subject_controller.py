import sys
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QColor

# Sửa tên file import (nếu cần)
from ui.subject_info import SubjectWindow 
# Chúng ta sẽ cần file service mới
from model import subject_service 

class SubjectController:
    def __init__(self, role, on_close_callback):
        """
        Khởi tạo controller
        :param role: Vai trò ('Admin' hoặc 'GiangVien')
        :param on_close_callback: Hàm để gọi khi cửa sổ này đóng (để quay lại Home)
        """
        self.view = SubjectWindow()
        self.on_close_callback = on_close_callback
        self.user_role = role
        
        # Biến lưu trữ Môn học đang được chọn
        self.selected_ma_mon = None
        self.selected_id_mon = None # Cần ID_MON để thêm Lớp học
        
        # Kết nối các nút và sự kiện
        self.connect_signals()
        
        # Tải dữ liệu ban đầu
        self.load_initial_data()
        
        # Áp dụng phân quyền
        self.view.set_admin_mode(self.user_role == 'Admin')

    def connect_signals(self):
        """Kết nối tất cả các nút bấm từ View với các hàm xử lý trong Controller"""
        # Nút Quay lại (Header)
        self.view.back_btn.clicked.connect(self.handle_close)
        
        # === Group Môn học (Master) ===
        self.view.subject_btn_add.clicked.connect(self.handle_add_subject)
        self.view.subject_btn_update.clicked.connect(self.handle_update_subject)
        self.view.subject_btn_delete.clicked.connect(self.handle_delete_subject)
        self.view.subject_btn_refresh.clicked.connect(self.clear_subject_form_and_detail)
        self.view.subject_btn_search.clicked.connect(self.handle_search_subject)
        self.view.subject_btn_all.clicked.connect(self.load_all_subjects)
        self.view.table_subject.itemSelectionChanged.connect(self.handle_subject_table_click)

        # === Group Lớp học (Detail) ===
        self.view.class_btn_add.clicked.connect(self.handle_add_class)
        self.view.class_btn_update.clicked.connect(self.handle_update_class)
        self.view.class_btn_delete.clicked.connect(self.handle_delete_class)
        self.view.class_btn_refresh.clicked.connect(self.clear_class_form)
        self.view.table_class.itemSelectionChanged.connect(self.handle_class_table_click)

    def show(self):
        """Hiển thị cửa sổ"""
        self.view.show()

    def handle_close(self):
        """Đóng cửa sổ hiện tại và gọi callback để hiển thị lại cửa sổ Home"""
        print("Đóng cửa sổ Môn học/Lớp học.")
        self.view.close()
        self.on_close_callback()

    # ==========================================================
    # HÀM TẢI DỮ LIỆU BAN ĐẦU
    # ==========================================================
    
    def load_initial_data(self):
        """Tải danh sách Giảng viên (cho ComboBox) và danh sách Môn học (cho Bảng)"""
        print("Đang tải dữ liệu ban đầu cho Môn học...")
        # 1. Tải Giảng viên cho ComboBox
        teachers_data = subject_service.get_all_teachers_for_combo()
        if teachers_data is not None:
            self.view.populate_gv_combo(teachers_data)
        else:
            self.view.show_message("Lỗi", "Không thể tải danh sách giảng viên.", level="error")
            
        # 2. Tải Môn học cho Bảng
        self.load_all_subjects()

    # ==========================================================
    # --- PHẦN XỬ LÝ MÔN HỌC (MASTER) ---
    # ==========================================================

    def load_all_subjects(self):
        """Tải và hiển thị tất cả môn học lên bảng"""
        print("Đang tải danh sách môn học...")
        data = subject_service.get_all_subjects()
        self.view.populate_subject_table(data)
        self.view.subject_search_input.clear()
        self.clear_subject_form_and_detail()

    def handle_subject_table_click(self):
        """Khi nhấn vào một Môn học, điền form Môn học VÀ tải danh sách Lớp học"""
        selected_rows = self.view.table_subject.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        selected_row = selected_rows[0].row()
        
        # Lấy dữ liệu từ bảng
        ma_mon = self.view.table_subject.item(selected_row, 0).text()
        ten_mon = self.view.table_subject.item(selected_row, 1).text()
        so_tin_chi_str = self.view.table_subject.item(selected_row, 2).text()
        gv_phu_trach = self.view.table_subject.item(selected_row, 3).text()
        
        # Điền vào form Môn học
        self.view.subject_inputs["Mã môn học:"].setText(ma_mon)
        self.view.subject_inputs["Tên môn học:"].setText(ten_mon)
        self.view.subject_inputs["Số tín chỉ:"].setValue(int(so_tin_chi_str) if so_tin_chi_str.isdigit() else 1)
        
        # Tìm và set ComboBox Giảng viên
        combo = self.view.subject_inputs["Giảng viên phụ trách:"]
        index = combo.findText(gv_phu_trach, Qt.MatchContains)
        if index != -1:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentIndex(0) # Về "Không có"
        
        # Không cho sửa Mã môn khi đã chọn
        self.view.subject_inputs["Mã môn học:"].setEnabled(False)
        
        # === LOGIC MASTER-DETAIL ===
        print(f"Đã chọn môn: {ma_mon}. Đang tải các lớp học liên quan...")
        self.selected_ma_mon = ma_mon
        
        # Lấy ID_MON (cần cho việc Thêm/Sửa Lớp)
        # Lưu ý: Hàm này cần được tạo trong service
        id_mon = subject_service.get_subject_id_by_ma_mon(ma_mon)
        self.selected_id_mon = id_mon
        
        if id_mon:
            # Kích hoạt Group Lớp học
            self.view.set_selected_subject(ma_mon, ten_mon)
            # Tải danh sách Lớp học
            self.load_classes_for_subject(id_mon)
        else:
            # Xóa và tắt Group Lớp học
            self.clear_subject_form_and_detail()

    def clear_subject_form_and_detail(self):
        """Làm mới form Môn học VÀ tắt/xóa group Lớp học"""
        self.view.clear_subject_form()
        self.view.disable_class_group()
        self.view.populate_class_table(None)
        self.selected_ma_mon = None
        self.selected_id_mon = None
        
        # Áp dụng lại phân quyền (vì clear_form() đã bật lại ô Mã môn)
        self.view.set_admin_mode(self.user_role == 'Admin')

    def handle_add_subject(self):
        """Xử lý Thêm mới môn học"""
        data = self.view.get_subject_form_data()
        
        if not data["ma_mon"] or not data["ten_mon"]:
            self.view.show_message("Thiếu thông tin", "Mã môn học và Tên môn học là bắt buộc.", level="warning")
            return
            
        success, message = subject_service.add_subject(data)
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_subjects()
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_update_subject(self):
        """Xử lý Cập nhật môn học"""
        data = self.view.get_subject_form_data()
        
        if not data["ma_mon"]:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một môn học từ bảng để cập nhật.", level="warning")
            return

        success, message = subject_service.update_subject(data)
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_subjects()
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_delete_subject(self):
        """Xử lý Xóa môn học"""
        ma_mon = self.view.get_selected_ma_mon()
        
        if not ma_mon:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một môn học từ bảng để xóa.", level="warning")
            return

        confirm = self.view.show_message("Xác nhận xóa", 
                                         f"Bạn có chắc chắn muốn xóa môn '{ma_mon}' không?\n"
                                         "Hành động này sẽ xóa TẤT CẢ các lớp học liên quan.",
                                         level="question")
        
        if confirm != QMessageBox.Yes:
            return

        success, message = subject_service.delete_subject(ma_mon)
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_subjects() # Tự động xóa luôn group Lớp học
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_search_subject(self):
        """Xử lý Tìm kiếm môn học"""
        search_by = self.view.subject_search_by.currentText()
        keyword = self.view.subject_search_input.text()

        if not keyword:
            self.view.show_message("Thiếu thông tin", "Vui lòng nhập từ khóa tìm kiếm.", level="warning")
            return
            
        data = subject_service.search_subjects(search_by, keyword)
        
        if data is None:
            self.view.show_message("Lỗi", "Lỗi khi tìm kiếm CSDL.", level="error")
        elif not data:
            self.view.show_message("Thông báo", "Không tìm thấy kết quả nào.", level="info")
        
        self.view.populate_subject_table(data)
        self.clear_subject_form_and_detail()

    # ==========================================================
    # --- PHẦN XỬ LÝ LỚP HỌC (DETAIL) ---
    # ==========================================================
    
    def load_classes_for_subject(self, id_mon):
        """Tải các lớp học cho môn học (ID_MON) đã chọn"""
        print(f"Đang tải lớp học cho ID_MON: {id_mon}")
        data = subject_service.get_classes_for_subject(id_mon)
        self.view.populate_class_table(data)
        self.clear_class_form()

    def handle_class_table_click(self):
        """Khi nhấn vào một Lớp học, điền form Lớp học"""
        selected_rows = self.view.table_class.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        selected_row = selected_rows[0].row()
        
        # Lấy dữ liệu từ bảng
        id_lop = self.view.table_class.item(selected_row, 0).text()
        ma_lop = self.view.table_class.item(selected_row, 1).text()
        ten_lop = self.view.table_class.item(selected_row, 2).text()
        nam_hoc = self.view.table_class.item(selected_row, 3).text()
        hoc_ky = self.view.table_class.item(selected_row, 4).text()
        thu_hoc = self.view.table_class.item(selected_row, 5).text()
        gio_bd = self.view.table_class.item(selected_row, 6).text()
        gio_kt = self.view.table_class.item(selected_row, 7).text()
        phong_hoc = self.view.table_class.item(selected_row, 8).text()
        
        # Điền vào form Lớp học
        self.view.hidden_id_lop.setText(id_lop)
        self.view.class_inputs["Mã Lớp:"].setText(ma_lop)
        self.view.class_inputs["Tên Lớp:"].setText(ten_lop)
        self.view.class_inputs["Năm học:"].setText(nam_hoc)
        self.view.class_inputs["Học kỳ:"].setText(hoc_ky)
        self.view.class_inputs["Phòng học:"].setText(phong_hoc)
        
        # Xử lý ComboBox "Thứ học"
        index = self.view.class_inputs["Thứ học:"].findText(thu_hoc, Qt.MatchExactly)
        if index != -1:
            self.view.class_inputs["Thứ học:"].setCurrentIndex(index)
            
        # Xử lý QTimeEdit "Giờ"
        self.view.class_inputs["Giờ bắt đầu:"].setTime(QTime.fromString(gio_bd, "HH:mm"))
        self.view.class_inputs["Giờ kết thúc:"].setTime(QTime.fromString(gio_kt, "HH:mm"))
        
        # Không cho sửa Mã Lớp khi đã chọn
        self.view.class_inputs["Mã Lớp:"].setEnabled(False)

    def clear_class_form(self):
        """Làm mới form Lớp học"""
        self.view.clear_class_form()
        # Áp dụng lại phân quyền (vì clear_form() đã bật lại ô Mã lớp)
        self.view.set_admin_mode(self.user_role == 'Admin')

    def handle_add_class(self):
        """Xử lý Thêm mới Lớp học"""
        data = self.view.get_class_form_data()
        
        if not self.selected_id_mon:
             self.view.show_message("Lỗi", "Không có môn học nào được chọn.", level="error")
             return
             
        if not data["ma_lop"] or not data["ten_lop"]:
            self.view.show_message("Thiếu thông tin", "Mã lớp và Tên lớp là bắt buộc.", level="warning")
            return

        success, message = subject_service.add_class(data, self.selected_id_mon)
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_classes_for_subject(self.selected_id_mon)
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_update_class(self):
        """Xử lý Cập nhật Lớp học"""
        data = self.view.get_class_form_data()
        
        if not data["id_lop"]:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một lớp học từ bảng để cập nhật.", level="warning")
            return

        success, message = subject_service.update_class(data)
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_classes_for_subject(self.selected_id_mon)
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_delete_class(self):
        """Xử lý Xóa Lớp học"""
        id_lop = self.view.hidden_id_lop.text()
        
        if not id_lop:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một lớp học từ bảng để xóa.", level="warning")
            return

        confirm = self.view.show_message("Xác nhận xóa", 
                                         f"Bạn có chắc chắn muốn xóa Lớp học (ID: {id_lop}) không?\n"
                                         "Hành động này sẽ xóa TẤT CẢ các buổi học liên quan.",
                                         level="question")
        
        if confirm != QMessageBox.Yes:
            return

        success, message = subject_service.delete_class(int(id_lop))
        
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_classes_for_subject(self.selected_id_mon)
        else:
            self.view.show_message("Thất bại", message, level="error")