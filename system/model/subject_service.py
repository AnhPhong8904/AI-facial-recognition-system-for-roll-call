import pyodbc
from model.connectdb import get_db_connection
from datetime import date

# ==========================================================
# --- PHẦN 1: HÀM XỬ LÝ MÔN HỌC (MASTER) ---
# ==========================================================

def get_all_teachers_for_combo():
    """
    Tải danh sách Giảng viên (chỉ ID và Tên) để điền vào ComboBox.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        sql_query = "SELECT ID_GV, HO_TEN FROM GIANGVIEN ORDER BY HO_TEN;"
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        # Trả về list of tuples [(1, 'Nguyễn Văn A'), (2, 'Trần Thị B')]
        return rows

    except Exception as e:
        print(f"Lỗi khi tải danh sách giảng viên cho ComboBox (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_subjects():
    """
    Tải danh sách tất cả Môn học (JOIN với Giảng viên để lấy tên).
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        sql_query = """
            SELECT 
                m.MA_MON, 
                m.TEN_MON, 
                m.SO_TIN_CHI, 
                g.HO_TEN AS TEN_GIANG_VIEN
            FROM MONHOC m
            LEFT JOIN GIANGVIEN g ON m.ID_GV = g.ID_GV
            ORDER BY m.ID_MON DESC;
        """
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print(f"Lỗi khi tải danh sách môn học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_subject(data):
    """
    Thêm môn học mới.
    data: dictionary từ get_subject_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        # Kiểm tra Mã môn học đã tồn tại chưa
        cursor.execute("SELECT 1 FROM MONHOC WHERE MA_MON = ?", (data["ma_mon"],))
        if cursor.fetchone():
            raise Exception(f"Mã môn học '{data['ma_mon']}' đã tồn tại.")

        sql_insert = """
            INSERT INTO MONHOC (MA_MON, TEN_MON, SO_TIN_CHI, ID_GV) 
            VALUES (?, ?, ?, ?);
        """
        params = (data["ma_mon"], data["ten_mon"], data["so_tin_chi"], data["id_gv"])
        cursor.execute(sql_insert, params)
        
        conn.commit()
        return True, "Thêm môn học thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi thêm môn học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

def update_subject(data):
    """
    Cập nhật thông tin môn học.
    data: dictionary từ get_subject_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        sql_update = """
            UPDATE MONHOC 
            SET TEN_MON = ?, SO_TIN_CHI = ?, ID_GV = ?
            WHERE MA_MON = ?;
        """
        params = (data["ten_mon"], data["so_tin_chi"], data["id_gv"], data["ma_mon"])
        cursor.execute(sql_update, params)

        if cursor.rowcount == 0:
            raise Exception("Không tìm thấy môn học để cập nhật (hoặc dữ liệu không đổi).")
            
        conn.commit()
        return True, "Cập nhật thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi cập nhật môn học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

def delete_subject(ma_mon):
    """
    Xóa môn học VÀ TẤT CẢ CÁC LỚP HỌC, BUỔI HỌC liên quan (Cascade Delete).
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

        # Bước 1: Lấy ID_MON từ MA_MON
        cursor.execute("SELECT ID_MON FROM MONHOC WHERE MA_MON = ?", (ma_mon,))
        row = cursor.fetchone()
        if not row:
            raise Exception("Không tìm thấy môn học để xóa.")
        id_mon = row[0]

        # Bước 2: Kiểm tra ràng buộc (bảng DIEMDANH, DANGKY)
        # Chúng ta cần xóa từ dưới lên: DIEMDANH -> BUOIHOC -> DANGKY -> LOPHOC -> MONHOC
        
        # Lấy danh sách ID_LOP liên quan
        cursor.execute("SELECT ID_LOP FROM LOPHOC WHERE ID_MON = ?", (id_mon,))
        lop_rows = cursor.fetchall()
        id_lops = [r[0] for r in lop_rows]
        
        if id_lops:
            # Lấy danh sách ID_BUOI liên quan
            placeholders = ", ".join("?" * len(id_lops))
            cursor.execute(f"SELECT ID_BUOI FROM BUOIHOC WHERE ID_LOP IN ({placeholders})", id_lops)
            buoi_rows = cursor.fetchall()
            id_buois = [r[0] for r in buoi_rows]
            
            if id_buois:
                # Xóa DIEMDANH liên quan
                placeholders_buoi = ", ".join("?" * len(id_buois))
                cursor.execute(f"DELETE FROM DIEMDANH WHERE ID_BUOI IN ({placeholders_buoi})", id_buois)
                
                # Xóa BUOIHOC liên quan
                cursor.execute(f"DELETE FROM BUOIHOC WHERE ID_BUOI IN ({placeholders_buoi})", id_buois)

            # Xóa DANGKY liên quan
            cursor.execute(f"DELETE FROM DANGKY WHERE ID_LOP IN ({placeholders})", id_lops)
            
            # Xóa LOPHOC liên quan
            cursor.execute(f"DELETE FROM LOPHOC WHERE ID_LOP IN ({placeholders})", id_lops)

        # Bước 3: Xóa MONHOC (sau cùng)
        cursor.execute("DELETE FROM MONHOC WHERE ID_MON = ?", (id_mon,))
        
        if cursor.rowcount == 0:
             raise Exception("Không tìm thấy môn học để xóa.")

        conn.commit()
        return True, "Xóa môn học (và các lớp liên quan) thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi xóa môn học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

def search_subjects(search_by, keyword):
    """
    Tìm kiếm môn học.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_base = """
            SELECT 
                m.MA_MON, m.TEN_MON, m.SO_TIN_CHI, g.HO_TEN AS TEN_GIANG_VIEN
            FROM MONHOC m
            LEFT JOIN GIANGVIEN g ON m.ID_GV = g.ID_GV
        """
        
        sql_where = ""
        keyword_like = f"%{keyword}%" 

        if search_by == 'Mã môn học':
            sql_where = " WHERE m.MA_MON LIKE ?"
        elif search_by == 'Tên môn học':
            sql_where = " WHERE m.TEN_MON LIKE ?"
        else:
            return None 

        sql_query = sql_base + sql_where + " ORDER BY m.ID_MON DESC;"
        cursor.execute(sql_query, (keyword_like,))
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print(f"Lỗi khi tìm kiếm môn học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_subject_id_by_ma_mon(ma_mon):
    """Hàm tiện ích: Lấy ID_MON từ MA_MON (cần cho Master-Detail)"""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT ID_MON FROM MONHOC WHERE MA_MON = ?", (ma_mon,))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Lỗi khi lấy ID_MON (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# --- PHẦN 2: HÀM XỬ LÝ LỚP HỌC (DETAIL) ---
# ==========================================================

def get_classes_for_subject(id_mon):
    """
    Tải danh sách các Lớp học cho một Môn học (id_mon) cụ thể.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        # Chỉ lấy từ bảng LOPHOC, lọc theo ID_MON
        sql_query = """
            SELECT 
                ID_LOP, MA_LOP, TEN_LOP, NAM_HOC, HOC_KY, 
                THU_HOC, GIO_BAT_DAU, GIO_KET_THUC, PHONG_HOC
            FROM LOPHOC
            WHERE ID_MON = ?
            ORDER BY ID_LOP DESC;
        """
        
        cursor.execute(sql_query, (id_mon,))
        rows = cursor.fetchall()
        
        # Chuyển đổi định dạng giờ
        formatted_rows = []
        for row in rows:
            gio_bd = row[6].strftime("%H:%M") if hasattr(row[6], 'strftime') else row[6]
            gio_kt = row[7].strftime("%H:%M") if hasattr(row[7], 'strftime') else row[7]
            
            formatted_rows.append((
                row[0], row[1], row[2], row[3], row[4], row[5], gio_bd, gio_kt, row[8]
            ))
            
        return formatted_rows

    except Exception as e:
        print(f"Lỗi khi tải danh sách lớp học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_class(data, id_mon):
    """
    Thêm Lớp học mới cho một Môn học (id_mon).
    data: dictionary từ get_class_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        # Kiểm tra Mã Lớp đã tồn tại chưa
        cursor.execute("SELECT 1 FROM LOPHOC WHERE MA_LOP = ?", (data["ma_lop"],))
        if cursor.fetchone():
            raise Exception(f"Mã lớp '{data['ma_lop']}' đã tồn tại.")

        sql_insert = """
            INSERT INTO LOPHOC (
                ID_MON, MA_LOP, TEN_LOP, NAM_HOC, HOC_KY, 
                THU_HOC, GIO_BAT_DAU, GIO_KET_THUC, PHONG_HOC
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            id_mon,
            data["ma_lop"], data["ten_lop"], data["nam_hoc"], data["hoc_ky"],
            data["thu_hoc"], data["gio_bd"], data["gio_kt"], data["phong_hoc"]
        )
        
        cursor.execute(sql_insert, params)
        conn.commit()
        return True, "Thêm lớp học thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi thêm lớp học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

def update_class(data):
    """
    Cập nhật thông tin Lớp học.
    data: dictionary từ get_class_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        # Kiểm tra Mã Lớp mới (nếu đổi) có trùng không
        cursor.execute("SELECT 1 FROM LOPHOC WHERE MA_LOP = ? AND ID_LOP != ?", 
                       (data["ma_lop"], data["id_lop"]))
        if cursor.fetchone():
            raise Exception(f"Mã lớp '{data['ma_lop']}' đã tồn tại.")

        sql_update = """
            UPDATE LOPHOC 
            SET MA_LOP = ?, TEN_LOP = ?, NAM_HOC = ?, HOC_KY = ?, 
                THU_HOC = ?, GIO_BAT_DAU = ?, GIO_KET_THUC = ?, PHONG_HOC = ?
            WHERE ID_LOP = ?;
        """
        params = (
            data["ma_lop"], data["ten_lop"], data["nam_hoc"], data["hoc_ky"],
            data["thu_hoc"], data["gio_bd"], data["gio_kt"], data["phong_hoc"],
            data["id_lop"]
        )
        
        cursor.execute(sql_update, params)

        if cursor.rowcount == 0:
            raise Exception("Không tìm thấy lớp học để cập nhật (hoặc dữ liệu không đổi).")
            
        conn.commit()
        return True, "Cập nhật lớp học thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi cập nhật lớp học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

def delete_class(id_lop):
    """
    Xóa Lớp học VÀ các Buổi học, Điểm danh liên quan.
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

        # Bước 1: Lấy danh sách ID_BUOI liên quan
        cursor.execute("SELECT ID_BUOI FROM BUOIHOC WHERE ID_LOP = ?", (id_lop,))
        buoi_rows = cursor.fetchall()
        id_buois = [r[0] for r in buoi_rows]
        
        if id_buois:
            # Bước 2: Xóa DIEMDANH liên quan
            placeholders_buoi = ", ".join("?" * len(id_buois))
            cursor.execute(f"DELETE FROM DIEMDANH WHERE ID_BUOI IN ({placeholders_buoi})", id_buois)
            
            # Bước 3: Xóa BUOIHOC liên quan
            cursor.execute(f"DELETE FROM BUOIHOC WHERE ID_BUOI IN ({placeholders_buoi})", id_buois)

        # Bước 4: Xóa DANGKY liên quan
        cursor.execute("DELETE FROM DANGKY WHERE ID_LOP = ?", (id_lop,))

        # Bước 5: Xóa LOPHOC
        cursor.execute("DELETE FROM LOPHOC WHERE ID_LOP = ?", (id_lop,))
        
        if cursor.rowcount == 0:
             raise Exception("Không tìm thấy lớp học để xóa.")

        conn.commit()
        return True, "Xóa lớp học (và các buổi học liên quan) thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi xóa lớp học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.autocommit = True
            conn.close()