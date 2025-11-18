import pyodbc
from model.connectdb import get_db_connection
from datetime import date, datetime

# ==========================================================
# --- PHẦN 1: HÀM XỬ LÝ SINH VIÊN (Bảng SINHVIEN) ---
# ==========================================================

def _format_ngay_sinh(value):
    """
    Chuẩn hóa giá trị ngày sinh thành chuỗi dd-MM-yyyy để hiển thị.
    Hỗ trợ các kiểu date/datetime và chuỗi (yyyy-MM-dd hoặc dd-MM-yyyy).
    """
    if value is None:
        return ""

    if isinstance(value, (datetime, date)):
        return value.strftime("%d-%m-%Y")

    if isinstance(value, str):
        cleaned = value.strip()
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                parsed = datetime.strptime(cleaned, fmt)
                return parsed.strftime("%d-%m-%Y")
            except ValueError:
                continue
        return cleaned  # Trả lại nguyên bản nếu không parse được

    return str(value)

def get_all_students():
    """
    Tải danh sách tất cả sinh viên từ bảng SINHVIEN.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_query = """
            SELECT 
                MA_SV, HO_TEN, GIOI_TINH, NGAY_SINH,
                EMAIL, SDT, NGANH, NAM_HOC, LOP_HOC, TRANG_THAI
            FROM SINHVIEN
            ORDER BY ID_SV DESC;
        """
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Chuyển đổi đối tượng 'date' thành chuỗi 'dd-MM-yyyy'
        formatted_rows = []
        for row in rows:
            row_list = list(row)
            row_list[3] = _format_ngay_sinh(row_list[3])  # Cột NGAY_SINH
            formatted_rows.append(tuple(row_list))
            
        return formatted_rows

    except Exception as e:
        print(f"Lỗi khi tải danh sách sinh viên (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_student(data):
    """
    Thêm sinh viên mới.
    data: dictionary từ get_student_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        # Kiểm tra Mã sinh viên đã tồn tại chưa
        cursor.execute("SELECT 1 FROM SINHVIEN WHERE MA_SV = ?", (data["ma_sv"],))
        if cursor.fetchone():
            raise Exception(f"Mã sinh viên '{data['ma_sv']}' đã tồn tại.")
            
        sql_insert = """
            INSERT INTO SINHVIEN (
                MA_SV, HO_TEN, GIOI_TINH, NGAY_SINH,
                EMAIL, SDT, NGANH, NAM_HOC, LOP_HOC, TRANG_THAI
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            data["ma_sv"], data["ho_ten"], data["gioi_tinh"], data["ngay_sinh"],
            data["email"], data["sdt"], data["nganh"], data["nam_hoc"],
            data["lop_hoc"], data["trang_thai"]
        )
        
        cursor.execute(sql_insert, params)
        conn.commit()
        return True, "Thêm sinh viên thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi thêm sinh viên (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

def update_student(data):
    """
    Cập nhật thông tin sinh viên.
    data: dictionary từ get_student_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        sql_update = """
            UPDATE SINHVIEN 
            SET HO_TEN = ?, GIOI_TINH = ?, NGAY_SINH = ?,
                EMAIL = ?, SDT = ?, NGANH = ?, NAM_HOC = ?, 
                LOP_HOC = ?, TRANG_THAI = ?
            WHERE MA_SV = ?;
        """
        params = (
            data["ho_ten"], data["gioi_tinh"], data["ngay_sinh"],
            data["email"], data["sdt"], data["nganh"], data["nam_hoc"],
            data["lop_hoc"], data["trang_thai"],
            data["ma_sv"] # MA_SV ở cuối cùng cho mệnh đề WHERE
        )
        
        cursor.execute(sql_update, params)

        if cursor.rowcount == 0:
            raise Exception("Không tìm thấy sinh viên để cập nhật (hoặc dữ liệu không đổi).")
            
        conn.commit()
        return True, "Cập nhật thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi cập nhật sinh viên (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

def delete_student(ma_sv):
    """
    Xóa sinh viên VÀ các dữ liệu liên quan (Điểm danh, Đăng ký, Nhận diện, Thống kê).
    Sử dụng TRANSACTION.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        conn.autocommit = False # Bắt đầu Transaction
        cursor = conn.cursor()

        # Bước 1: Lấy ID_SV từ MA_SV
        cursor.execute("SELECT ID_SV FROM SINHVIEN WHERE MA_SV = ?", (ma_sv,))
        row = cursor.fetchone()
        if not row:
            raise Exception("Không tìm thấy sinh viên để xóa.")
        id_sv = row[0]

        # Bước 2: Xóa các bảng phụ thuộc
        
        # Xóa THONGKE
        cursor.execute("DELETE FROM THONGKE WHERE ID_SV = ?", (id_sv,))
        
        # Xóa DIEMDANH
        cursor.execute("DELETE FROM DIEMDANH WHERE ID_SV = ?", (id_sv,))
        
        # Xóa DANGKY (Đăng ký học phần)
        cursor.execute("DELETE FROM DANGKY WHERE ID_SV = ?", (id_sv,))
        
        # Xóa NHAN_DIEN (Ảnh khuôn mặt)
        cursor.execute("DELETE FROM NHAN_DIEN WHERE ID_SV = ?", (id_sv,))
        
        # Bước 3: Xóa SINHVIEN (sau cùng)
        cursor.execute("DELETE FROM SINHVIEN WHERE ID_SV = ?", (id_sv,))
        
        if cursor.rowcount == 0:
             raise Exception("Không tìm thấy sinh viên để xóa (lỗi logic).")

        conn.commit()
        return True, "Xóa sinh viên (và dữ liệu liên quan) thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi xóa sinh viên (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

def search_students(search_by, keyword):
    """
    Tìm kiếm sinh viên.
    search_by: "Mã sinh viên", "Tên sinh viên", "Email", "SĐT", "Lớp hành chính"
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_base = "SELECT MA_SV, HO_TEN, GIOI_TINH, NGAY_SINH, EMAIL, SDT, NGANH, NAM_HOC, LOP_HOC, TRANG_THAI FROM SINHVIEN"
        sql_where = ""
        keyword_like = f"%{keyword}%" 

        if search_by == 'Mã sinh viên':
            sql_where = " WHERE MA_SV LIKE ?"
        elif search_by == 'Tên sinh viên':
            sql_where = " WHERE HO_TEN LIKE ?"
        elif search_by == 'Email':
            sql_where = " WHERE EMAIL LIKE ?"
        elif search_by == 'SĐT':
            sql_where = " WHERE SDT LIKE ?"
        elif search_by == 'Lớp hành chính':
            sql_where = " WHERE LOP_HOC LIKE ?"
        else:
            return None 

        sql_query = sql_base + sql_where + " ORDER BY ID_SV DESC;"
        cursor.execute(sql_query, (keyword_like,))
        rows = cursor.fetchall()
        
        # Định dạng lại ngày sinh
        formatted_rows = []
        for row in rows:
            row_list = list(row)
            row_list[3] = _format_ngay_sinh(row_list[3])  # Cột NGAY_SINH
            formatted_rows.append(tuple(row_list))
            
        return formatted_rows

    except Exception as e:
        print(f"Lỗi khi tìm kiếm sinh viên (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_student_id_by_ma_sv(ma_sv):
    """Hàm tiện ích: Lấy ID_SV (int) từ MA_SV (string)"""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None: return None
        cursor = conn.cursor()
        cursor.execute("SELECT ID_SV FROM SINHVIEN WHERE MA_SV = ?", (ma_sv,))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Lỗi khi lấy ID_SV (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# --- PHẦN 2: HÀM XỬ LÝ ĐĂNG KÝ (Bảng DANGKY) ---
# ==========================================================

def get_registrations_for_student(id_sv):
    """
    Tải danh sách các Lớp học (Đã đăng ký) của một Sinh viên.
    (ID_DK, MA_LOP, TEN_LOP, TEN_MON)
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None: return None
        cursor = conn.cursor()
        
        # JOIN 3 bảng: DANGKY -> LOPHOC -> MONHOC
        sql_query = """
            SELECT 
                d.ID_DK,
                l.MA_LOP,
                l.TEN_LOP,
                m.TEN_MON
            FROM DANGKY d
            LEFT JOIN LOPHOC l ON d.ID_LOP = l.ID_LOP
            LEFT JOIN MONHOC m ON l.ID_MON = m.ID_MON
            WHERE d.ID_SV = ?
            ORDER BY d.ID_DK DESC;
        """
        cursor.execute(sql_query, (id_sv,))
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Lỗi khi tải danh sách đăng ký (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_available_classes_for_student(id_sv):
    """
    Tải danh sách các Lớp học (Chưa đăng ký) để điền vào ComboBox.
    (ID_LOP, MA_LOP, TEN_LOP)
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None: return None
        cursor = conn.cursor()
        
        # Lấy tất cả Lớp học mà ID_LOP KHÔNG CÓ trong bảng DANGKY của SV này
        sql_query = """
            SELECT 
                l.ID_LOP,
                l.MA_LOP,
                l.TEN_LOP
            FROM LOPHOC l
            WHERE l.ID_LOP NOT IN (
                SELECT d.ID_LOP FROM DANGKY d WHERE d.ID_SV = ?
            )
            ORDER BY l.MA_LOP;
        """
        cursor.execute(sql_query, (id_sv,))
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Lỗi khi tải danh sách lớp học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_registration(id_sv, id_lop):
    """
    Thêm (Đăng ký) Sinh viên vào Lớp học.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        # Kiểm tra xem đã tồn tại chưa (CSDL đã có ràng buộc UQ_SV_LOP, nhưng check trước vẫn tốt)
        cursor.execute("SELECT 1 FROM DANGKY WHERE ID_SV = ? AND ID_LOP = ?", (id_sv, id_lop))
        if cursor.fetchone():
            raise Exception("Sinh viên này đã đăng ký lớp học này rồi.")

        sql_insert = "INSERT INTO DANGKY (ID_SV, ID_LOP) VALUES (?, ?);"
        cursor.execute(sql_insert, (id_sv, id_lop))
        conn.commit()
        return True, "Đăng ký thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi thêm đăng ký (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

def delete_registration(id_dk):
    """
    Hủy đăng ký (Xóa) khỏi bảng DANGKY.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        # Kiểm tra ràng buộc (DIEMDANH) - Nếu SV đã có điểm danh, không cho hủy
        # (Logic này phức tạp, tạm thời cho phép xóa)
        # Tốt hơn là nên kiểm tra:
        # cursor.execute("""
        #     SELECT 1 FROM DIEMDANH dd
        #     JOIN BUOIHOC bh ON dd.ID_BUOI = bh.ID_BUOI
        #     JOIN DANGKY d ON bh.ID_LOP = d.ID_LOP AND dd.ID_SV = d.ID_SV
        #     WHERE d.ID_DK = ?
        # """, (id_dk,))
        # if cursor.fetchone():
        #     raise Exception("Không thể hủy. Sinh viên đã có dữ liệu điểm danh trong lớp này.")

        sql_delete = "DELETE FROM DANGKY WHERE ID_DK = ?;"
        cursor.execute(sql_delete, (id_dk,))
        
        if cursor.rowcount == 0:
            raise Exception("Không tìm thấy đăng ký để hủy.")
            
        conn.commit()
        return True, "Hủy đăng ký thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi hủy đăng ký (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()