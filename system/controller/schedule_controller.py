import sys
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt, QDate, QTime
from ui.school_schedule import ScheduleWindow
from model import schedule_service

class ScheduleController:
    def __init__(self, on_close_callback):
        """
        Khởi tạo controller
        :param on_close_callback: Hàm để gọi khi cửa sổ này đóng (để quay lại Home)
        """
        self.view = ScheduleWindow()
        self.on_close_callback = on_close_callback
        
        # Kết nối các nút và sự kiện
        self.connect_signals()
        
        # Tải dữ liệu ban đầu (Danh sách Lớp học và Buổi học)
        self.load_initial_data()

    def connect_signals(self):
        """Kết nối tất cả các nút bấm từ View với các hàm xử lý trong Controller"""
        # Nút chức năng (Form)
        self.view.btn_add.clicked.connect(self.handle_add_schedule)
        self.view.btn_update.clicked.connect(self.handle_update_schedule)
        self.view.btn_delete.clicked.connect(self.handle_delete_schedule)
        self.view.btn_refresh.clicked.connect(self.clear_form)
        self.view.btn_pick_room.clicked.connect(self.handle_pick_room_dialog)
        
        # Nút chức năng (Tìm kiếm)
        self.view.btn_search.clicked.connect(self.handle_search_schedule)
        self.view.btn_all.clicked.connect(self.load_all_schedules)
        
        # Nút Quay lại (Header)
        self.view.back_btn.clicked.connect(self.handle_close)
        
        # Sự kiện click vào bảng (Table)
        self.view.table.itemSelectionChanged.connect(self.handle_table_click)
        
        # QUAN TRỌNG: Sự kiện khi thay đổi ComboBox Lớp học
        self.view.combo_lophoc.currentIndexChanged.connect(self.handle_class_selected)

    def show(self):
        """Hiển thị cửa sổ"""
        self.view.show()

    def handle_close(self):
        """Đóng cửa sổ hiện tại và gọi callback để hiển thị lại cửa sổ Home"""
        print("Đóng cửa sổ Lịch học.")
        self.view.close()
        self.on_close_callback()

    # ==========================================================
    # HÀM TẢI VÀ HIỂN THỊ DỮ LIỆU
    # ==========================================================
    
    def load_initial_data(self):
        """Tải danh sách Lớp học (cho ComboBox) và danh sách Buổi học (cho Bảng)"""
        print("Đang tải dữ liệu ban đầu cho Lịch học...")
        # 1. Tải Lớp học cho ComboBox
        classes_data = schedule_service.get_all_classes_for_combo()
        if classes_data is not None:
            self.view.populate_lophoc_combo(classes_data)
        else:
            self.view.show_message("Lỗi", "Không thể tải danh sách Lớp học.", level="error")
            
        # 2. Tải Buổi học cho Bảng
        self.load_all_schedules()

    def load_all_schedules(self):
        """Tải và hiển thị tất cả buổi học lên bảng"""
        print("Đang tải danh sách lịch học...")
        # Đồng bộ lịch học tự động từ cấu hình lớp (ngày bắt đầu/kết thúc + thứ)
        sync_info = schedule_service.sync_schedules_from_classes()
        if sync_info:
            print(f"Đồng bộ lịch: lớp={sync_info['classes']}, mới={sync_info['inserted']}, cập nhật={sync_info['updated']}, giữ nguyên={sync_info['skipped']}")
        data = schedule_service.get_all_schedules()
        self.view.populate_table(data)
        self.view.search_input.clear()
        self.clear_form()

    def handle_class_selected(self):
        """Khi người dùng chọn một lớp từ ComboBox, tự động điền Tên môn, Tên GV"""
        id_lop = self.view.combo_lophoc.currentData()
        if id_lop is None:
            self.view.set_class_details(None)
            return
            
        # Gọi service để lấy chi tiết (Giờ hàm này trả về 4 giá trị)
        details = schedule_service.get_class_details(id_lop)
        
        # Truyền 4 giá trị đó vào hàm view (hàm view đã được sửa ở bước 2)
        self.view.set_class_details(details)

    def handle_table_click(self):
        """Khi nhấn vào một dòng trên bảng, điền thông tin vào form"""
        selected_rows = self.view.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        selected_row = selected_rows[0].row()
        
        # Lấy dữ liệu từ bảng (cột đã bổ sung Thứ và Tên môn)
        id_buoi = self.view.table.item(selected_row, 0).text()
        ngay_hoc_str = self.view.table.item(selected_row, 1).text()
        gio_bd_str = self.view.table.item(selected_row, 3).text()
        gio_kt_str = self.view.table.item(selected_row, 4).text()
        phong_hoc = self.view.table.item(selected_row, 5).text()
        ma_lop = self.view.table.item(selected_row, 6).text()
        ghi_chu = self.view.table.item(selected_row, 8).text()
        
        # Điền vào form
        self.view.hidden_id_buoi.setText(id_buoi)
        self.view.line_phong_hoc.setText(phong_hoc)
        self.view.line_ghi_chu.setText(ghi_chu)
        
        # Set ngày và giờ
        self.view.date_ngay_hoc.setDate(QDate.fromString(ngay_hoc_str, "dd-MM-yyyy"))
        self.view.time_bat_dau.setTime(QTime.fromString(gio_bd_str, "HH:mm"))
        self.view.time_ket_thuc.setTime(QTime.fromString(gio_kt_str, "HH:mm"))
        
        # Tìm và set ComboBox Lớp học
        combo = self.view.combo_lophoc
        index = combo.findText(ma_lop, Qt.MatchContains)
        combo.blockSignals(True)
        if index != -1:
            combo.setCurrentIndex(index)
        combo.blockSignals(False)

        # Cập nhật thông tin môn/GV nhưng giữ nguyên giờ đã chọn từ bảng
        id_lop = combo.currentData()
        if id_lop is not None:
            details = schedule_service.get_class_details(id_lop)
            self.view.set_class_details(details, update_times=False)
            
        # Không cho sửa Lớp học khi đã chọn (để Cập nhật/Xóa)
        self.view.combo_lophoc.setEnabled(False)

    def clear_form(self):
        """Làm mới (xóa) tất cả các trường trong form"""
        self.view.clear_form()

    def handle_pick_room_dialog(self):
        """Hiển thị danh sách phòng trống dựa trên ngày/giờ đã chọn."""
        gio_bd = self.view.time_bat_dau.time()
        gio_kt = self.view.time_ket_thuc.time()

        if not (gio_bd.isValid() and gio_kt.isValid()):
            self.view.show_message("Thời gian không hợp lệ", "Vui lòng nhập giờ học hợp lệ trước khi chọn phòng.", level="warning")
            return

        if gio_bd >= gio_kt:
            self.view.show_message("Thời gian không hợp lệ", "Giờ bắt đầu phải nhỏ hơn giờ kết thúc trước khi chọn phòng.", level="warning")
            return

        ngay_hoc = self.view.date_ngay_hoc.date().toString("yyyy-MM-dd")
        data = schedule_service.get_room_availability(
            ngay_hoc,
            gio_bd.toString("HH:mm"),
            gio_kt.toString("HH:mm")
        )

        if data is None:
            self.view.show_message("Lỗi", "Không thể tải danh sách phòng học.", level="error")
            return

        if not data:
            self.view.show_message("Thông báo", "Chưa có phòng học nào trong hệ thống. Bạn có thể nhập thủ công.", level="info")
            return

        selected_room = self.view.show_room_dialog(data)
        if selected_room:
            self.view.line_phong_hoc.setText(selected_room)

    # ==========================================================
    # HÀM XỬ LÝ CRUD (THÊM, SỬA, XÓA)
    # ==========================================================

    def handle_add_schedule(self):
        """Xử lý Thêm mới buổi học"""
        # 1. Lấy dữ liệu từ Form
        data = self.view.get_form_data()

        # 2. Kiểm tra dữ liệu (cơ bản)
        if data["id_lop"] is None:
            self.view.show_message("Thiếu thông tin", "Bạn phải chọn một Lớp học.", level="warning")
            return

        # Ngày học không được trước ngày hiện tại
        ngay_hoc_qdate = QDate.fromString(data["ngay_hoc"], "yyyy-MM-dd")
        if (not ngay_hoc_qdate.isValid()) or (ngay_hoc_qdate < QDate.currentDate()):
            self.view.show_message("Ngày học không hợp lệ", "Ngày học phải từ hôm nay trở đi.", level="warning")
            return

        # Trường bắt buộc: Phòng học
        if not data["phong_hoc"].strip():
            self.view.show_message("Thiếu thông tin", "Vui lòng nhập Phòng học.", level="warning")
            return

        gio_bd = QTime.fromString(data["gio_bd"], "HH:mm")
        gio_kt = QTime.fromString(data["gio_kt"], "HH:mm")
        if not (gio_bd.isValid() and gio_kt.isValid()):
            self.view.show_message("Thời gian không hợp lệ", "Vui lòng nhập giờ bắt đầu/kết thúc hợp lệ.", level="warning")
            return
        if gio_bd >= gio_kt:
            self.view.show_message(
                "Thời gian không hợp lệ",
                "Giờ bắt đầu phải nhỏ hơn giờ kết thúc.",
                level="warning"
            )
            return
            
        # 3. Gọi Service
        success, message = schedule_service.add_schedule(data)
        
        # 4. Hiển thị kết quả và tải lại
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_schedules()
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_update_schedule(self):
        """Xử lý Cập nhật buổi học"""
        # 1. Lấy dữ liệu từ Form
        data = self.view.get_form_data()

        # 2. Kiểm tra
        if not data["id_buoi"]:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một lịch học từ bảng để cập nhật.", level="warning")
            return

        # Ngày học không được trước ngày hiện tại
        ngay_hoc_qdate = QDate.fromString(data["ngay_hoc"], "yyyy-MM-dd")
        if (not ngay_hoc_qdate.isValid()) or (ngay_hoc_qdate < QDate.currentDate()):
            self.view.show_message("Ngày học không hợp lệ", "Ngày học phải từ hôm nay trở đi.", level="warning")
            return

        # Trường bắt buộc: Phòng học
        if not data["phong_hoc"].strip():
            self.view.show_message("Thiếu thông tin", "Vui lòng nhập Phòng học.", level="warning")
            return

        gio_bd = QTime.fromString(data["gio_bd"], "HH:mm")
        gio_kt = QTime.fromString(data["gio_kt"], "HH:mm")
        if not (gio_bd.isValid() and gio_kt.isValid()):
            self.view.show_message("Thời gian không hợp lệ", "Vui lòng nhập giờ bắt đầu/kết thúc hợp lệ.", level="warning")
            return
        if gio_bd >= gio_kt:
            self.view.show_message(
                "Thời gian không hợp lệ",
                "Giờ bắt đầu phải nhỏ hơn giờ kết thúc.",
                level="warning"
            )
            return

        # 3. Gọi Service
        success, message = schedule_service.update_schedule(data)
        
        # 4. Hiển thị kết quả và tải lại
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_schedules()
        else:
            self.view.show_message("Thất bại", message, level="error")

    def handle_delete_schedule(self):
        """Xử lý Xóa buổi học"""
        # 1. Lấy ID Buổi học
        id_buoi = self.view.hidden_id_buoi.text()
        
        if not id_buoi:
            self.view.show_message("Chưa chọn", "Vui lòng chọn một lịch học từ bảng để xóa.", level="warning")
            return

        # 2. Hộp thoại XÁC NHẬN
        confirm = self.view.show_message("Xác nhận xóa", 
                                         f"Bạn có chắc chắn muốn xóa lịch học (ID: {id_buoi}) không?",
                                         level="question")
        
        if confirm != QMessageBox.Yes:
            return

        # 3. Gọi Service
        success, message = schedule_service.delete_schedule(int(id_buoi))
        
        # 4. Hiển thị kết quả và tải lại
        if success:
            self.view.show_message("Thành công", message, level="info")
            self.load_all_schedules()
        else:
            self.view.show_message("Thất bại", message, level="error")

    # ==========================================================
    # HÀM XỬ LÝ TÌM KIẾM
    # ==========================================================

    def handle_search_schedule(self):
        """Xử lý Tìm kiếm buổi học"""
        data = self.view.get_search_data()
        search_by = data["search_by"]
        keyword = data["keyword"]

        if not keyword:
            self.view.show_message("Thiếu thông tin", "Vui lòng nhập từ khóa tìm kiếm.", level="warning")
            return
            
        print(f"Đang tìm kiếm lịch học: {search_by} - {keyword}")
        result_data = schedule_service.search_schedules(search_by, keyword)
        
        if result_data is None:
            self.view.show_message("Lỗi", "Lỗi khi tìm kiếm CSDL.", level="error")
        elif not result_data:
            self.view.show_message("Thông báo", "Không tìm thấy kết quả nào.", level="info")
            self.view.populate_table(result_data)
        else:
            self.view.populate_table(result_data)