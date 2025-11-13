import pyodbc
from model.connectdb import get_db_connection
from datetime import datetime

# ==========================================================
# HÀM TẢI DỮ LIỆU CHO 4 THẺ (CARDS)
# ==========================================================

def get_stat_cards_data():
    """
    Tải dữ liệu thống kê tổng quan cho 4 thẻ.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        stats = {}
        
        # 1. Tổng số sinh viên
        cursor.execute("SELECT COUNT(*) FROM SINHVIEN")
        stats["tong_sv"] = cursor.fetchone()[0]
        
        # 2. Tổng số bản điểm danh
        cursor.execute("SELECT COUNT(*) FROM DIEMDANH")
        stats["tong_diemdanh"] = cursor.fetchone()[0]

        # 3. Tổng số lần đi muộn (Sử dụng N'' cho chuỗi Unicode)
        cursor.execute("SELECT COUNT(*) FROM DIEMDANH WHERE TRANG_THAI = N'Đi muộn'")
        stats["tong_dimuon"] = cursor.fetchone()[0]
        
        # 4. Tổng số lần vắng
        cursor.execute("SELECT COUNT(*) FROM DIEMDANH WHERE TRANG_THAI = N'Vắng'")
        stats["tong_vang"] = cursor.fetchone()[0]

        return stats

    except Exception as e:
        print(f"Lỗi khi tải dữ liệu thẻ thống kê (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM TRUY VẤN CƠ SỞ (BASE QUERY) CHO BẢNG
# ==========================================================

# Xây dựng câu lệnh SELECT cơ sở để tái sử dụng
# JOIN 4 bảng: DIEMDANH (dd) -> SINHVIEN (s)
#            -> BUOIHOC (b) -> LOPHOC (l)
BASE_STATS_QUERY = """
    SELECT 
        s.MA_SV,
        s.HO_TEN,
        l.MA_LOP,
        dd.THOI_GIAN_DIEMDANH,
        dd.TRANG_THAI
    FROM DIEMDANH dd
    LEFT JOIN SINHVIEN s ON dd.ID_SV = s.ID_SV
    LEFT JOIN BUOIHOC b ON dd.ID_BUOI = b.ID_BUOI
    LEFT JOIN LOPHOC l ON b.ID_LOP = l.ID_LOP
"""

def _format_rows_for_stats(rows):
    """
    Hàm tiện ích: Chuyển đổi datetime sang chuỗi dd-MM-yyyy HH:mm:ss
    Đầu vào: (MA_SV, HO_TEN, MA_LOP, THOI_GIAN, TRANG_THAI)
    """
    formatted_rows = []
    for row in rows:
        # row[3] là THOI_GIAN_DIEMDANH
        thoi_gian_dt = row[3]
        thoi_gian_str = thoi_gian_dt.strftime("%d-%m-%Y %H:%M:%S") if isinstance(thoi_gian_dt, datetime) else str(thoi_gian_dt)
        
        # Tạo tuple mới với 5 cột
        formatted_rows.append((
            row[0], row[1], row[2], thoi_gian_str, row[4]
        ))
    return formatted_rows

# ==========================================================
# HÀM TẢI DỮ LIỆU CHO BẢNG (READ)
# ==========================================================

def get_attendance_records_by_status(status):
    """
    Tải danh sách điểm danh dựa trên trạng thái (N'Đi muộn' hoặc N'Vắng').
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        # Nối câu query cơ sở với điều kiện WHERE
        sql_query = f"""
            {BASE_STATS_QUERY}
            WHERE dd.TRANG_THAI = ?
            ORDER BY dd.THOI_GIAN_DIEMDANH DESC;
        """
        
        cursor.execute(sql_query, (status,))
        rows = cursor.fetchall()
        return _format_rows_for_stats(rows)

    except Exception as e:
        print(f"Lỗi khi tải bản ghi theo trạng thái (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM TÌM KIẾM (SEARCH)
# ==========================================================

def search_records(status, search_by, keyword):
    """
    Tìm kiếm trong các bản ghi điểm danh (Đi muộn / Vắng).
    status: N'Đi muộn' hoặc N'Vắng'
    search_by: "Mã Sinh viên", "Tên Sinh viên", "Mã Lớp"
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_where = " WHERE dd.TRANG_THAI = ?"
        params = [status] # Dùng list để .append()
        keyword_like = f"%{keyword}%" 

        if search_by == 'Mã Sinh viên':
            sql_where += " AND s.MA_SV LIKE ?"
            params.append(keyword_like)
        elif search_by == 'Tên Sinh viên':
            sql_where += " AND s.HO_TEN LIKE ?"
            params.append(keyword_like)
        elif search_by == 'Mã Lớp':
            sql_where += " AND l.MA_LOP LIKE ?"
            params.append(keyword_like)
        else:
            return None # Tiêu chí tìm kiếm không hợp lệ

        sql_query = f"{BASE_STATS_QUERY} {sql_where} ORDER BY dd.THOI_GIAN_DIEMDANH DESC;"
        
        cursor.execute(sql_query, tuple(params))
        rows = cursor.fetchall()
        return _format_rows_for_stats(rows)

    except Exception as e:
        print(f"Lỗi khi tìm kiếm thống kê (service): {e}")
        return None
    finally:
        if conn:
            conn.close()