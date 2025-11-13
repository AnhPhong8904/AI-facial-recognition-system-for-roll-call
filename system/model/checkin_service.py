import pyodbc
from model.connectdb import get_db_connection
from datetime import datetime

# ==========================================================
# HÀM TRUY VẤN CƠ SỞ (BASE QUERY)
# ==========================================================

# Xây dựng câu lệnh SELECT cơ sở để tái sử dụng
# JOIN 4 bảng: DIEMDANH -> SINHVIEN (lấy Tên, Mã)
#            -> BUOIHOC (lấy ID_LOP)
#            -> LOPHOC (lấy Mã Lớp)
BASE_SELECT_QUERY = """
    SELECT 
        dd.ID_DIEMDANH,
        dd.ID_BUOI,
        s.MA_SV,
        s.HO_TEN AS TEN_SINH_VIEN,
        l.MA_LOP,
        dd.THOI_GIAN_DIEMDANH,
        dd.TRANG_THAI,
        dd.GHI_CHU
    FROM DIEMDANH dd
    LEFT JOIN SINHVIEN s ON dd.ID_SV = s.ID_SV
    LEFT JOIN BUOIHOC b ON dd.ID_BUOI = b.ID_BUOI
    LEFT JOIN LOPHOC l ON b.ID_LOP = l.ID_LOP
"""

def _format_rows(rows):
    """Hàm tiện ích: Chuyển đổi datetime sang chuỗi dd-MM-yyyy HH:mm:ss"""
    formatted_rows = []
    for row in rows:
        # row[5] là THOI_GIAN_DIEMDANH
        thoi_gian_dt = row[5]
        thoi_gian_str = thoi_gian_dt.strftime("%d-%m-%Y %H:%M:%S") if isinstance(thoi_gian_dt, datetime) else str(thoi_gian_dt)
        
        # Tạo tuple mới với thời gian đã định dạng
        formatted_rows.append((
            row[0], row[1], row[2], row[3], row[4], thoi_gian_str, row[6], row[7]
        ))
    return formatted_rows

# ==========================================================
# HÀM TẢI DỮ LIỆU (READ)
# ==========================================================

def get_all_checkins():
    """Tải tất cả dữ liệu điểm danh."""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        sql_query = f"{BASE_SELECT_QUERY} ORDER BY dd.ID_DIEMDANH DESC;"
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return _format_rows(rows)

    except Exception as e:
        print(f"Lỗi khi tải danh sách điểm danh (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_today_checkins():
    """Tải dữ liệu điểm danh chỉ trong ngày hôm nay."""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        # Lọc theo ngày hiện tại
        sql_query = f"""
            {BASE_SELECT_QUERY}
            WHERE CONVERT(date, dd.THOI_GIAN_DIEMDANH) = CONVERT(date, GETDATE())
            ORDER BY dd.ID_DIEMDANH DESC;
        """
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return _format_rows(rows)

    except Exception as e:
        print(f"Lỗi khi tải danh sách điểm danh hôm nay (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM CẬP NHẬT (UPDATE)
# ==========================================================

def update_checkin(data):
    """
    Cập nhật thông tin điểm danh.
    data: dictionary từ get_form_data()
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        conn.autocommit = False
        cursor = conn.cursor()
        
        # --- QUAN TRỌNG: Chuyển đổi Mã SV (MA_SV) sang ID_SV (int) ---
        id_sv = None
        if data["id_sv"]:
            cursor.execute("SELECT ID_SV FROM SINHVIEN WHERE MA_SV = ?", (data["id_sv"],))
            sv_row = cursor.fetchone()
            if not sv_row:
                raise Exception(f"Không tìm thấy Sinh viên với Mã SV: {data['id_sv']}")
            id_sv = sv_row[0]
        else:
             raise Exception("Mã Sinh viên là bắt buộc.")
        
        # Chuyển đổi chuỗi thời gian từ "dd-MM-yyyy HH:mm:ss" sang "yyyy-MM-dd HH:mm:ss"
        try:
            thoi_gian_dt = datetime.strptime(data["thoi_gian"], "%d-%m-%Y %H:%M:%S")
            thoi_gian_sql = thoi_gian_dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
             # Nếu QDateTimeEdit gửi định dạng khác
             thoi_gian_dt = datetime.strptime(data["thoi_gian"], "%d/%m/%Y %H:%M:%S")
             thoi_gian_sql = thoi_gian_dt.strftime("%Y-%m-%d %H:%M:%S")


        # Cập nhật bảng DIEMDANH
        sql_update = """
            UPDATE DIEMDANH 
            SET 
                ID_BUOI = ?, 
                ID_SV = ?, 
                THOI_GIAN_DIEMDANH = ?, 
                TRANG_THAI = ?, 
                GHI_CHU = ?
            WHERE ID_DIEMDANH = ?;
        """
        params = (
            int(data["id_buoi"]),
            id_sv,
            thoi_gian_sql,
            data["trang_thai"],
            data["ghi_chu"],
            int(data["id_diemdanh"])
        )
        
        cursor.execute(sql_update, params)

        if cursor.rowcount == 0:
            raise Exception("Không tìm thấy mục điểm danh để cập nhật (hoặc dữ liệu không đổi).")
            
        conn.commit()
        return True, "Cập nhật thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi cập nhật điểm danh (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

# ==========================================================
# HÀM XÓA (DELETE)
# ==========================================================

def delete_checkin(id_diemdanh):
    """
    Xóa mục điểm danh.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        # Xóa DIEMDANH
        cursor.execute("DELETE FROM DIEMDANH WHERE ID_DIEMDANH = ?", (id_diemdanh,))
        
        if cursor.rowcount == 0:
             raise Exception("Không tìm thấy mục điểm danh để xóa.")

        conn.commit()
        return True, "Xóa mục điểm danh thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi xóa điểm danh (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM TÌM KIẾM (SEARCH)
# ==========================================================

def search_checkins(search_by, keyword):
    """
    Tìm kiếm điểm danh.
    search_by: "Mã Sinh viên", "Tên Sinh viên", "Mã Lớp", "Ngày (yyyy-MM-dd)"
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_where = ""
        params = ()
        
        if search_by == 'Mã Sinh viên':
            sql_where = " WHERE s.MA_SV LIKE ?"
            params = (f"%{keyword}%",)
        elif search_by == 'Tên Sinh viên':
            sql_where = " WHERE s.HO_TEN LIKE ?"
            params = (f"%{keyword}%",)
        elif search_by == 'Mã Lớp':
            sql_where = " WHERE l.MA_LOP LIKE ?"
            params = (f"%{keyword}%",)
        elif search_by == 'Ngày (yyyy-MM-dd)':
            # Tìm kiếm ngày chính xác, không dùng LIKE
            # Giả định keyword là 'yyyy-MM-dd'
            try:
                datetime.strptime(keyword, "%Y-%m-%d")
                sql_where = " WHERE CONVERT(date, dd.THOI_GIAN_DIEMDANH) = ?"
                params = (keyword,)
            except ValueError:
                return None # Hoặc trả về [] nếu định dạng ngày sai
        else:
            return None # Tiêu chí tìm kiếm không hợp lệ

        sql_query = f"{BASE_SELECT_QUERY} {sql_where} ORDER BY dd.ID_DIEMDANH DESC;"
        
        cursor.execute(sql_query, params)
        rows = cursor.fetchall()
        return _format_rows(rows)

    except Exception as e:
        print(f"Lỗi khi tìm kiếm điểm danh (service): {e}")
        return None
    finally:
        if conn:
            conn.close()