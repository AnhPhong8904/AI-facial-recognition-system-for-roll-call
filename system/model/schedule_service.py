import pyodbc
from model.connectdb import get_db_connection
from datetime import date # Cần import date

# ==========================================================
# HÀM TẢI DỮ LIỆU (READ)
# ==========================================================

def get_all_classes_for_combo():
    """
    Tải danh sách Lớp học (ID, Mã, Tên) để điền vào ComboBox.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        # Chỉ lấy ID_LOP, MA_LOP, TEN_LOP từ bảng LOPHOC
        sql_query = "SELECT ID_LOP, MA_LOP, TEN_LOP FROM LOPHOC ORDER BY MA_LOP;"
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        # Trả về list of tuples [(1, 'L01', 'Lớp KTLT T2'), ...]
        return rows

    except Exception as e:
        print(f"Lỗi khi tải danh sách lớp học cho ComboBox (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_class_details(id_lop):
    """
    Lấy chi tiết (Tên Môn, Tên GV, Giờ BĐ, Giờ KT) của một Lớp học
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        # JOIN 3 bảng: LOPHOC -> MONHOC -> GIANGVIEN
        sql_query = """
            SELECT 
                m.TEN_MON, 
                g.HO_TEN,
                l.GIO_BAT_DAU, -- <<< THÊM DÒNG NÀY
                l.GIO_KET_THUC -- <<< THÊM DÒNG NÀY
            FROM LOPHOC l
            LEFT JOIN MONHOC m ON l.ID_MON = m.ID_MON
            LEFT JOIN GIANGVIEN g ON m.ID_GV = g.ID_GV
            WHERE l.ID_LOP = ?;
        """
        
        cursor.execute(sql_query, (id_lop,))
        row = cursor.fetchone()
        return row # Trả về tuple (TEN_MON, HO_TEN, GIO_BD, GIO_KT)

    except Exception as e:
        print(f"Lỗi khi tải chi tiết lớp học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_schedules():
    """
    Tải danh sách tất cả Buổi học (JOIN với Lớp học để lấy Mã Lớp).
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        # JOIN 2 bảng: BUOIHOC -> LOPHOC
        sql_query = """
            SELECT 
                b.ID_BUOI, 
                b.NGAY_HOC, 
                b.GIO_BAT_DAU, 
                b.GIO_KET_THUC, 
                b.PHONG_HOC, 
                l.MA_LOP,
                b.GHI_CHU
            FROM BUOIHOC b
            LEFT JOIN LOPHOC l ON b.ID_LOP = l.ID_LOP
            ORDER BY b.ID_BUOI DESC;
        """
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Chuyển đổi định dạng ngày và giờ trước khi trả về
        formatted_rows = []
        for row in rows:
            # row[1] là NGAY_HOC, row[2] là GIO_BAT_DAU, row[3] là GIO_KET_THUC
            ngay_hoc = row[1].strftime("%d-%m-%Y") if isinstance(row[1], date) else row[1]
            gio_bd = row[2].strftime("%H:%M") if hasattr(row[2], 'strftime') else row[2]
            gio_kt = row[3].strftime("%H:%M") if hasattr(row[3], 'strftime') else row[3]
            
            formatted_rows.append((
                row[0], ngay_hoc, gio_bd, gio_kt, row[4], row[5], row[6]
            ))
            
        return formatted_rows

    except Exception as e:
        print(f"Lỗi khi tải danh sách buổi học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM THÊM MỚI (CREATE)
# ==========================================================

def add_schedule(data):
    """
    Thêm buổi học mới.
    data: dictionary từ get_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        sql_insert = """
            INSERT INTO BUOIHOC (ID_LOP, NGAY_HOC, GIO_BAT_DAU, GIO_KET_THUC, PHONG_HOC, GHI_CHU) 
            VALUES (?, ?, ?, ?, ?, ?);
        """
        params = (
            data["id_lop"],
            data["ngay_hoc"],
            data["gio_bd"],
            data["gio_kt"],
            data["phong_hoc"],
            data["ghi_chu"]
        )
        
        cursor.execute(sql_insert, params)
        conn.commit()
        return True, "Thêm buổi học thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi thêm buổi học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM CẬP NHẬT (UPDATE)
# ==========================================================

def update_schedule(data):
    """
    Cập nhật thông tin buổi học.
    data: dictionary từ get_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        # Cập nhật bảng BUOIHOC
        # Lưu ý: Không cho phép đổi ID_LOP khi cập nhật (đã disable ComboBox)
        sql_update = """
            UPDATE BUOIHOC 
            SET NGAY_HOC = ?, GIO_BAT_DAU = ?, GIO_KET_THUC = ?, 
                PHONG_HOC = ?, GHI_CHU = ?
            WHERE ID_BUOI = ?;
        """
        params = (
            data["ngay_hoc"],
            data["gio_bd"],
            data["gio_kt"],
            data["phong_hoc"],
            data["ghi_chu"],
            data["id_buoi"]
        )
        
        cursor.execute(sql_update, params)

        if cursor.rowcount == 0:
            raise Exception("Không tìm thấy buổi học để cập nhật (hoặc dữ liệu không đổi).")
            
        conn.commit()
        return True, "Cập nhật thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi cập nhật buổi học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM XÓA (DELETE)
# ==========================================================

def delete_schedule(id_buoi):
    """
    Xóa buổi học.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        conn.autocommit = False # Bắt đầu Transaction
        cursor = conn.cursor()

        # Bước 1: Kiểm tra ràng buộc (bảng DIEMDANH)
        cursor.execute("SELECT 1 FROM DIEMDANH WHERE ID_BUOI = ?", (id_buoi,))
        if cursor.fetchone():
            raise Exception("Không thể xóa. Buổi học này đã có dữ liệu điểm danh.")

        # Bước 2: Xóa BUOIHOC
        cursor.execute("DELETE FROM BUOIHOC WHERE ID_BUOI = ?", (id_buoi,))
        
        if cursor.rowcount == 0:
             raise Exception("Không tìm thấy buổi học để xóa.")

        conn.commit()
        return True, "Xóa buổi học thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi xóa buổi học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.autocommit = True # Đặt lại autocommit
            conn.close()

# ==========================================================
# HÀM TÌM KIẾM (SEARCH)
# ==========================================================

def search_schedules(search_by, keyword):
    """
    Tìm kiếm buổi học.
    search_by: 'Mã lớp', 'Tên môn', 'Tên giảng viên'
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_base = """
            SELECT 
                b.ID_BUOI, b.NGAY_HOC, b.GIO_BAT_DAU, b.GIO_KET_THUC, 
                b.PHONG_HOC, l.MA_LOP, b.GHI_CHU
            FROM BUOIHOC b
            LEFT JOIN LOPHOC l ON b.ID_LOP = l.ID_LOP
            LEFT JOIN MONHOC m ON l.ID_MON = m.ID_MON
            LEFT JOIN GIANGVIEN g ON m.ID_GV = g.ID_GV
        """
        
        sql_where = ""
        params = ()
        keyword_like = f"%{keyword}%" 

        if search_by == 'Mã lớp':
            sql_where = " WHERE l.MA_LOP LIKE ?"
            params = (keyword_like,)
        elif search_by == 'Tên môn':
            sql_where = " WHERE m.TEN_MON LIKE ?"
            params = (keyword_like,)
        elif search_by == 'Tên giảng viên':
            sql_where = " WHERE g.HO_TEN LIKE ?"
            params = (keyword_like,)
        else:
            return None # Tiêu chí tìm kiếm không hợp lệ

        sql_query = sql_base + sql_where + " ORDER BY b.ID_BUOI DESC;"
        
        cursor.execute(sql_query, params)
        rows = cursor.fetchall()
        
        # Chuyển đổi định dạng ngày và giờ
        formatted_rows = []
        for row in rows:
            ngay_hoc = row[1].strftime("%d-%m-%Y") if isinstance(row[1], date) else row[1]
            gio_bd = row[2].strftime("%H:%M") if hasattr(row[2], 'strftime') else row[2]
            gio_kt = row[3].strftime("%H:%M") if hasattr(row[3], 'strftime') else row[3]
            
            formatted_rows.append((
                row[0], ngay_hoc, gio_bd, gio_kt, row[4], row[5], row[6]
            ))
            
        return formatted_rows

    except Exception as e:
        print(f"Lỗi khi tìm kiếm buổi học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()