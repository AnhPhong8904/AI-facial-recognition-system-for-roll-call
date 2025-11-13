import sys
import csv
import os
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog
from PyQt5.QtCore import Qt
# ĐỔI TÊN IMPORT
from ui.report import ReportWindow
from model import report_service # ĐỔI TÊN IMPORT

# ĐỔI TÊN CLASS
class ReportController:
    def __init__(self, on_close_callback):
        """
        Khởi tạo controller
        :param on_close_callback: Hàm để gọi khi cửa sổ này đóng (để quay lại Home)
        """
        self.view = ReportWindow() # ĐỔI TÊN CLASS
        self.on_close_callback = on_close_callback
        
        # Kết nối các nút và sự kiện
        self.connect_signals()
        
        # Tải dữ liệu ban đầu
        self.load_initial_data()

    def connect_signals(self):
        """Kết nối tất cả các nút bấm từ View với các hàm xử lý trong Controller"""
        # Nút Quay lại (Header)
        self.view.back_btn.clicked.connect(self.handle_close)
        
        # === Bảng "Đi muộn" ===
        self.view.btn_search_late.clicked.connect(self.handle_search_late)
        self.view.btn_all_late.clicked.connect(self.load_all_late_data)
        # Kết nối nút CSV
        self.view.btn_csv_late.clicked.connect(
            lambda: self.handle_export_csv(self.view.table_late, "thong_ke_di_muon")
        )

        # === Bảng "Vắng" ===
        self.view.btn_search_absent.clicked.connect(self.handle_search_absent)
        self.view.btn_all_absent.clicked.connect(self.load_all_absent_data)
        # Kết nối nút CSV
        self.view.btn_csv_absent.clicked.connect(
            lambda: self.handle_export_csv(self.view.table_absent, "thong_ke_vang")
        )

    def show(self):
        """Hiển thị cửa sổ"""
        self.view.show()

    def handle_close(self):
        """Đóng cửa sổ hiện tại và gọi callback để hiển thị lại cửa sổ Home"""
        print("Đóng cửa sổ Báo cáo.")
        self.view.close()
        self.on_close_callback()

    # ==========================================================
    # HÀM TẢI VÀ HIỂN THỊ DỮ LIỆU
    # ==========================================================
    
    def load_initial_data(self):
        """Tải tất cả dữ liệu (Thẻ, Bảng) khi mở cửa sổ"""
        print("Đang tải dữ liệu Báo cáo...")
        
        # 1. Tải Thẻ
        # ĐỔI TÊN SERVICE
        stats = report_service.get_stat_cards_data() 
        if stats:
            self.view.update_stat_cards(stats)
        
        # 2. Tải Bảng (Đi muộn)
        self.load_all_late_data()
        
        # 3. Tải Bảng (Vắng)
        self.load_all_absent_data()

    def load_all_late_data(self):
        """Tải dữ liệu cho bảng "Đi muộn" """
        # ĐỔI TÊN SERVICE
        data = report_service.get_attendance_records_by_status("Đi muộn")
        self.view.populate_table(self.view.table_late, data)
        self.view.search_input_late.clear()

    def load_all_absent_data(self):
        """Tải dữ liệu cho bảng "Vắng" """
        # ĐỔI TÊN SERVICE
        data = report_service.get_attendance_records_by_status("Vắng")
        self.view.populate_table(self.view.table_absent, data)
        self.view.search_input_absent.clear()

    # ==========================================================
    # HÀM XỬ LÝ TÌM KIẾM
    # ==========================================================

    def handle_search_late(self):
        """Tìm kiếm trong bảng "Đi muộn" """
        search_by = self.view.search_by_late.currentText()
        keyword = self.view.search_input_late.text()
        if not keyword:
            self.view.show_message("Thông báo", "Vui lòng nhập từ khóa.", level="warning")
            return
            
        # ĐỔI TÊN SERVICE
        data = report_service.search_records("Đi muộn", search_by, keyword)
        self.view.populate_table(self.view.table_late, data)

    def handle_search_absent(self):
        """Tìm kiếm trong bảng "Vắng" """
        search_by = self.view.search_by_absent.currentText()
        keyword = self.view.search_input_absent.text()
        if not keyword:
            self.view.show_message("Thông báo", "Vui lòng nhập từ khóa.", level="warning")
            return
            
        # ĐỔI TÊN SERVICE
        data = report_service.search_records("Vắng", search_by, keyword)
        self.view.populate_table(self.view.table_absent, data)
        
    # ==========================================================
    # HÀM XỬ LÝ XUẤT CSV (Bật nút)
    # ==========================================================
    
    def handle_export_csv(self, table_widget, default_filename):
        """
        Xuất dữ liệu hiện tại từ một QTableWidget ra file CSV.
        """
        print(f"Bắt đầu xuất CSV cho: {default_filename}")
        
        if table_widget.rowCount() == 0:
            self.view.show_message("Thông báo", "Không có dữ liệu để xuất.", level="warning")
            return

        # Mở hộp thoại "Lưu file"
        # Đặt đường dẫn mặc định là thư mục Downloads
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", f"{default_filename}.csv")
        
        filepath, _ = QFileDialog.getSaveFileName(
            self.view, 
            "Lưu file CSV", 
            default_path, 
            "CSV Files (*.csv)"
        )

        if not filepath:
            print("Hủy bỏ xuất CSV.")
            return

        try:
            # Dùng 'utf-8-sig' để Excel đọc tiếng Việt có dấu
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 1. Ghi Header (Tiêu đề cột)
                headers = [table_widget.horizontalHeaderItem(i).text() 
                           for i in range(table_widget.columnCount())]
                writer.writerow(headers)
                
                # 2. Ghi Dữ liệu (Nội dung)
                for row in range(table_widget.rowCount()):
                    row_data = []
                    for col in range(table_widget.columnCount()):
                        item = table_widget.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
                    
            self.view.show_message("Thành công", f"Đã xuất file thành công:\n{filepath}", level="info")
        
        except Exception as e:
            print(f"Lỗi khi xuất CSV: {e}")
            self.view.show_message("Thất bại", f"Không thể lưu file.\nLỗi: {e}", level="error")