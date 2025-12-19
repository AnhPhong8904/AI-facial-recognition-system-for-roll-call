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
        l.TEN_LOP,
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
    Đầu vào: (MA_SV, HO_TEN, MA_LOP, TEN_LOP, THOI_GIAN, TRANG_THAI)
    """
    formatted_rows = []
    for row in rows:
        # row[4] là THOI_GIAN_DIEMDANH
        thoi_gian_dt = row[4]
        thoi_gian_str = thoi_gian_dt.strftime("%d-%m-%Y %H:%M:%S") if isinstance(thoi_gian_dt, datetime) else str(thoi_gian_dt)
        
        # Tạo tuple mới với 6 cột
        formatted_rows.append((
            row[0], # MA_SV
            row[1], # HO_TEN
            row[2], # MA_LOP
            row[3], # TEN_LOP
            thoi_gian_str, # THOI_GIAN
            row[5]  # TRANG_THAI
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
    search_by: "Mã Sinh viên", "Tên Sinh viên", "Mã Lớp", "Tên Lớp"
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
        elif search_by == 'Tên Lớp':
            sql_where += " AND l.TEN_LOP LIKE ?"
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

# ==========================================================
# HÀM TẢI DỮ LIỆU CHO BIỂU ĐỒ (CHARTS)
# ==========================================================

def get_attendance_by_date(days=7):
    """
    Lấy dữ liệu điểm danh theo ngày trong N ngày gần nhất.
    Trả về: list of tuples (date_str, co_mat, di_muon, vang)
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_query = """
            SELECT 
                CAST(dd.THOI_GIAN_DIEMDANH AS DATE) AS Ngay,
                SUM(CASE WHEN dd.TRANG_THAI = N'Có mặt' THEN 1 ELSE 0 END) AS CoMat,
                SUM(CASE WHEN dd.TRANG_THAI = N'Đi muộn' THEN 1 ELSE 0 END) AS DiMuon,
                SUM(CASE WHEN dd.TRANG_THAI = N'Vắng' THEN 1 ELSE 0 END) AS Vang
            FROM DIEMDANH dd
            WHERE dd.THOI_GIAN_DIEMDANH >= DATEADD(DAY, -?, GETDATE())
            GROUP BY CAST(dd.THOI_GIAN_DIEMDANH AS DATE)
            ORDER BY Ngay ASC;
        """
        
        cursor.execute(sql_query, (days,))
        rows = cursor.fetchall()
        
        # Format: (date_str, co_mat, di_muon, vang)
        result = []
        for row in rows:
            date_obj = row[0]
            date_str = date_obj.strftime("%d-%m") if isinstance(date_obj, datetime) else str(date_obj)
            result.append((date_str, row[1] or 0, row[2] or 0, row[3] or 0))
        
        return result
        
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu theo ngày (service): {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_attendance_by_class():
    """
    Lấy dữ liệu điểm danh theo lớp.
    Trả về: list of tuples (ten_lop, co_mat, di_muon, vang, tong)
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_query = """
            SELECT 
                l.TEN_LOP,
                SUM(CASE WHEN dd.TRANG_THAI = N'Có mặt' THEN 1 ELSE 0 END) AS CoMat,
                SUM(CASE WHEN dd.TRANG_THAI = N'Đi muộn' THEN 1 ELSE 0 END) AS DiMuon,
                SUM(CASE WHEN dd.TRANG_THAI = N'Vắng' THEN 1 ELSE 0 END) AS Vang,
                COUNT(dd.ID_DIEMDANH) AS Tong
            FROM DIEMDANH dd
            LEFT JOIN BUOIHOC b ON dd.ID_BUOI = b.ID_BUOI
            LEFT JOIN LOPHOC l ON b.ID_LOP = l.ID_LOP
            WHERE l.TEN_LOP IS NOT NULL
            GROUP BY l.TEN_LOP
            ORDER BY Tong DESC;
        """
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Format: (ten_lop, co_mat, di_muon, vang, tong)
        result = []
        for row in rows:
            result.append((
                row[0] or "Không xác định",
                row[1] or 0,
                row[2] or 0,
                row[3] or 0,
                row[4] or 0
            ))
        
        return result
        
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu theo lớp (service): {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_attendance_status_distribution():
    """
    Lấy phân bố trạng thái điểm danh (tổng quan).
    Trả về: dict với keys: 'co_mat', 'di_muon', 'vang'
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_query = """
            SELECT 
                SUM(CASE WHEN TRANG_THAI = N'Có mặt' THEN 1 ELSE 0 END) AS CoMat,
                SUM(CASE WHEN TRANG_THAI = N'Đi muộn' THEN 1 ELSE 0 END) AS DiMuon,
                SUM(CASE WHEN TRANG_THAI = N'Vắng' THEN 1 ELSE 0 END) AS Vang
            FROM DIEMDANH;
        """
        
        cursor.execute(sql_query)
        row = cursor.fetchone()
        
        return {
            'co_mat': row[0] or 0,
            'di_muon': row[1] or 0,
            'vang': row[2] or 0
        }
        
    except Exception as e:
        print(f"Lỗi khi tải phân bố trạng thái (service): {e}")
        return {'co_mat': 0, 'di_muon': 0, 'vang': 0}
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM PHỤ TRỢ: TÍNH SỐ TIẾT DỰA TRÊN LOẠI MÔN HỌC
# ==========================================================

def _get_subject_type_from_name(ten_mon):
    """
    Xác định loại môn học (LT/TH) dựa trên tên môn học.
    Nếu tên có chứa "Thực hành", "TH", "Lab" -> TH
    Ngược lại -> LT (mặc định)
    """
    if not ten_mon:
        return "LT"
    ten_mon_lower = ten_mon.lower()
    if any(keyword in ten_mon_lower for keyword in ["thực hành", "thuc hanh", "th", "lab", "laboratory"]):
        return "TH"
    return "LT"

def _calculate_total_periods(so_tin_chi, loai_mon):
    """
    Tính tổng số tiết dựa trên số tín chỉ và loại môn học.
    - 1 tín LT = 15 tiết
    - 1 tín TH = 30 tiết
    """
    if loai_mon == "TH":
        return so_tin_chi * 30
    else:  # LT
        return so_tin_chi * 15

def _calculate_total_sessions(total_periods):
    """
    Tính tổng số ca học dựa trên số tiết.
    - 3 tiết = 1 ca học
    """
    return total_periods // 3

# ==========================================================
# HÀM TÍNH CẤM THI THEO SỐ BUỔI / SỐ TIẾT
# ==========================================================

def get_exam_ban_by_class(ma_lop, max_absent_ratio=0.2):
    """
    Tính danh sách sinh viên có nguy cơ/đã bị CẤM THI theo lớp tín chỉ.

    Quy ước mới:
    - 1 tín LT = 15 tiết
    - 1 tín TH = 30 tiết
    - 3 tiết = 1 ca học
    - Mỗi buổi vắng được tính là vắng 3 tiết (1 ca).
    - Cấm thi nếu TỈ LỆ SỐ TIẾT VẮNG > max_absent_ratio (mặc định 20%).

    Tham số:
    - ma_lop: Mã lớp tín chỉ (ví dụ: 'L01')
    - max_absent_ratio: Ngưỡng tỉ lệ vắng cho phép (0.3 = 30%)

    Trả về list các dict:
    [
      {
        'ma_sv': ...,
        'ho_ten': ...,
        'ma_lop': ...,
        'ten_mon': ...,
        'so_tin_chi': ...,
        'tong_buoi': ...,
        'so_buoi_vang': ...,
        'tong_tiet': ...,
        'so_tiet_vang': ...,
        'ti_le_vang': ...,
        'cam_thi': True/False
      },
      ...
    ]
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")

        cursor = conn.cursor()

        # Gộp dữ liệu theo: SV - Lớp - Môn
        # Đếm tổng số BUOIHOC (buổi) và số buổi vắng (TRANG_THAI = 'Vắng')
        sql_query = """
            SELECT 
                s.MA_SV,
                s.HO_TEN,
                l.MA_LOP,
                m.TEN_MON,
                m.SO_TIN_CHI,
                COUNT(DISTINCT b.ID_BUOI) AS TongBuoi,
                SUM(
                    CASE 
                        WHEN dd.TRANG_THAI = N'Vắng' THEN 1 
                        ELSE 0 
                    END
                ) AS SoBuoiVang
            FROM DANGKY d
            JOIN SINHVIEN s ON d.ID_SV = s.ID_SV
            JOIN LOPHOC l ON d.ID_LOP = l.ID_LOP
            JOIN MONHOC m ON l.ID_MON = m.ID_MON
            JOIN BUOIHOC b ON b.ID_LOP = l.ID_LOP
            LEFT JOIN DIEMDANH dd 
                ON dd.ID_BUOI = b.ID_BUOI 
               AND dd.ID_SV = s.ID_SV
            WHERE l.MA_LOP = ?
            GROUP BY 
                s.MA_SV,
                s.HO_TEN,
                l.MA_LOP,
                m.TEN_MON,
                m.SO_TIN_CHI
            ORDER BY s.MA_SV;
        """

        cursor.execute(sql_query, (ma_lop,))
        rows = cursor.fetchall()

        result = []
        for row in rows:
            ma_sv = row[0]
            ho_ten = row[1]
            ma_lop_row = row[2]
            ten_mon = row[3]
            so_tin_chi = row[4] or 0
            tong_buoi = row[5] or 0
            so_buoi_vang = row[6] or 0

            # Nếu chưa có lịch buổi học thì bỏ qua
            if tong_buoi <= 0:
                continue

            # Xác định loại môn học và tính tổng số tiết
            loai_mon = _get_subject_type_from_name(ten_mon)
            tong_tiet_theo_tin_chi = _calculate_total_periods(so_tin_chi, loai_mon)
            
            # Tính số tiết thực tế dựa trên số buổi học (mỗi buổi = 3 tiết = 1 ca)
            tong_tiet_thuc_te = tong_buoi * 3
            so_tiet_vang = so_buoi_vang * 3
            
            # Sử dụng số tiết thực tế từ buổi học để tính tỷ lệ
            tong_tiet = tong_tiet_thuc_te
            ti_le_vang = float(so_tiet_vang) / float(tong_tiet) if tong_tiet > 0 else 0.0
            cam_thi = ti_le_vang > max_absent_ratio

            result.append({
                "ma_sv": ma_sv,
                "ho_ten": ho_ten,
                "ma_lop": ma_lop_row,
                "ten_mon": ten_mon,
                "so_tin_chi": so_tin_chi,
                "loai_mon": loai_mon,
                "tong_buoi": int(tong_buoi),
                "so_buoi_vang": int(so_buoi_vang),
                "tong_tiet": int(tong_tiet),
                "tong_tiet_theo_tin_chi": int(tong_tiet_theo_tin_chi),
                "so_tiet_vang": int(so_tiet_vang),
                "ti_le_vang": ti_le_vang,
                "cam_thi": cam_thi,
            })

        return result

    except Exception as e:
        print(f"Lỗi khi tính danh sách cấm thi (service): {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_student_attendance_statistics():
    """
    Lấy thống kê điểm danh theo từng sinh viên và lớp học.
    Tính toán số tiết vắng và xác định trạng thái cấm thi.
    
    Trả về list các dict với thông tin:
    {
        'ma_sv': ...,
        'ho_ten': ...,
        'ma_lop': ...,
        'ten_mon': ...,
        'so_tin_chi': ...,
        'loai_mon': ...,
        'tong_buoi': ...,
        'so_buoi_vang': ...,
        'tong_tiet': ...,
        'so_tiet_vang': ...,
        'ti_le_vang': ...,
        'cam_thi': True/False,
        'trang_thai': 'Cấm thi' hoặc 'Đủ điều kiện'
    }
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")

        cursor = conn.cursor()

        # Lấy tất cả sinh viên đã đăng ký lớp học
        sql_query = """
            SELECT 
                s.MA_SV,
                s.HO_TEN,
                l.MA_LOP,
                m.TEN_MON,
                m.SO_TIN_CHI,
                COUNT(DISTINCT b.ID_BUOI) AS TongBuoi,
                SUM(
                    CASE 
                        WHEN dd.TRANG_THAI = N'Vắng' THEN 1 
                        ELSE 0 
                    END
                ) AS SoBuoiVang
            FROM DANGKY d
            JOIN SINHVIEN s ON d.ID_SV = s.ID_SV
            JOIN LOPHOC l ON d.ID_LOP = l.ID_LOP
            JOIN MONHOC m ON l.ID_MON = m.ID_MON
            JOIN BUOIHOC b ON b.ID_LOP = l.ID_LOP
            LEFT JOIN DIEMDANH dd 
                ON dd.ID_BUOI = b.ID_BUOI 
               AND dd.ID_SV = s.ID_SV
            GROUP BY 
                s.MA_SV,
                s.HO_TEN,
                l.MA_LOP,
                m.TEN_MON,
                m.SO_TIN_CHI
            ORDER BY s.MA_SV, l.MA_LOP;
        """

        cursor.execute(sql_query)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            ma_sv = row[0]
            ho_ten = row[1]
            ma_lop_row = row[2]
            ten_mon = row[3]
            so_tin_chi = row[4] or 0
            tong_buoi = row[5] or 0
            so_buoi_vang = row[6] or 0

            # Nếu chưa có lịch buổi học thì bỏ qua
            if tong_buoi <= 0:
                continue

            # Xác định loại môn học và tính tổng số tiết
            loai_mon = _get_subject_type_from_name(ten_mon)
            tong_tiet_theo_tin_chi = _calculate_total_periods(so_tin_chi, loai_mon)
            
            # Tính số tiết thực tế dựa trên số buổi học (mỗi buổi = 3 tiết = 1 ca)
            tong_tiet_thuc_te = tong_buoi * 3
            so_tiet_vang = so_buoi_vang * 3
            
            # Sử dụng số tiết thực tế từ buổi học để tính tỷ lệ
            tong_tiet = tong_tiet_thuc_te
            ti_le_vang = float(so_tiet_vang) / float(tong_tiet) if tong_tiet > 0 else 0.0
            cam_thi = ti_le_vang > 0.2  # 20%

            result.append({
                "ma_sv": ma_sv,
                "ho_ten": ho_ten,
                "ma_lop": ma_lop_row,
                "ten_mon": ten_mon,
                "so_tin_chi": so_tin_chi,
                "loai_mon": loai_mon,
                "tong_buoi": int(tong_buoi),
                "so_buoi_vang": int(so_buoi_vang),
                "tong_tiet": int(tong_tiet),
                "tong_tiet_theo_tin_chi": int(tong_tiet_theo_tin_chi),
                "so_tiet_vang": int(so_tiet_vang),
                "ti_le_vang": ti_le_vang,
                "cam_thi": cam_thi,
                "trang_thai": "Cấm thi" if cam_thi else "Đủ điều kiện"
            })

        return result

    except Exception as e:
        print(f"Lỗi khi tính thống kê điểm danh sinh viên (service): {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_classes_list():
    """
    Lấy danh sách tất cả lớp học với thống kê tổng quan.
    Trả về list các dict:
    {
        'ma_lop': ...,
        'ten_lop': ...,
        'ten_mon': ...,
        'so_tin_chi': ...,
        'tong_sv': ...,
        'tong_buoi': ...,
        'so_sv_cam_thi': ...,
        'so_sv_du_dieu_kien': ...
    }
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")

        cursor = conn.cursor()

        sql_query = """
            SELECT 
                l.MA_LOP,
                l.TEN_LOP,
                m.TEN_MON,
                m.SO_TIN_CHI,
                COUNT(DISTINCT d.ID_SV) AS TongSV,
                COUNT(DISTINCT b.ID_BUOI) AS TongBuoi
            FROM LOPHOC l
            JOIN MONHOC m ON l.ID_MON = m.ID_MON
            LEFT JOIN DANGKY d ON l.ID_LOP = d.ID_LOP
            LEFT JOIN BUOIHOC b ON l.ID_LOP = b.ID_LOP
            GROUP BY 
                l.MA_LOP,
                l.TEN_LOP,
                m.TEN_MON,
                m.SO_TIN_CHI
            ORDER BY l.MA_LOP;
        """

        cursor.execute(sql_query)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            ma_lop = row[0]
            ten_lop = row[1]
            ten_mon = row[2]
            so_tin_chi = row[3] or 0
            tong_sv = row[4] or 0
            tong_buoi = row[5] or 0

            # Tính số sinh viên cấm thi và đủ điều kiện
            students_stats = get_students_by_class(ma_lop)
            so_sv_cam_thi = sum(1 for s in students_stats if s.get("cam_thi", False))
            so_sv_du_dieu_kien = len(students_stats) - so_sv_cam_thi

            result.append({
                "ma_lop": ma_lop,
                "ten_lop": ten_lop or "",
                "ten_mon": ten_mon or "",
                "so_tin_chi": so_tin_chi,
                "tong_sv": tong_sv,
                "tong_buoi": tong_buoi,
                "so_sv_cam_thi": so_sv_cam_thi,
                "so_sv_du_dieu_kien": so_sv_du_dieu_kien
            })

        return result

    except Exception as e:
        print(f"Lỗi khi lấy danh sách lớp học (service): {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_students_by_class(ma_lop):
    """
    Lấy danh sách sinh viên của một lớp học với thống kê điểm danh.
    
    Trả về list các dict:
    {
        'ma_sv': ...,
        'ho_ten': ...,
        'ma_lop': ...,
        'ten_mon': ...,
        'so_tin_chi': ...,
        'loai_mon': ...,
        'tong_buoi': ...,
        'so_buoi_vang': ...,
        'tong_tiet': ...,
        'so_tiet_vang': ...,
        'ti_le_vang': ...,
        'cam_thi': True/False,
        'trang_thai': 'Cấm thi' hoặc 'Đủ điều kiện'
    }
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")

        cursor = conn.cursor()

        sql_query = """
            SELECT 
                s.MA_SV,
                s.HO_TEN,
                l.MA_LOP,
                m.TEN_MON,
                m.SO_TIN_CHI,
                COUNT(DISTINCT b.ID_BUOI) AS TongBuoi,
                SUM(
                    CASE 
                        WHEN dd.TRANG_THAI = N'Vắng' THEN 1 
                        ELSE 0 
                    END
                ) AS SoBuoiVang
            FROM DANGKY d
            JOIN SINHVIEN s ON d.ID_SV = s.ID_SV
            JOIN LOPHOC l ON d.ID_LOP = l.ID_LOP
            JOIN MONHOC m ON l.ID_MON = m.ID_MON
            JOIN BUOIHOC b ON b.ID_LOP = l.ID_LOP
            LEFT JOIN DIEMDANH dd 
                ON dd.ID_BUOI = b.ID_BUOI 
               AND dd.ID_SV = s.ID_SV
            WHERE l.MA_LOP = ?
            GROUP BY 
                s.MA_SV,
                s.HO_TEN,
                l.MA_LOP,
                m.TEN_MON,
                m.SO_TIN_CHI
            ORDER BY s.MA_SV;
        """

        cursor.execute(sql_query, (ma_lop,))
        rows = cursor.fetchall()

        result = []
        for row in rows:
            ma_sv = row[0]
            ho_ten = row[1]
            ma_lop_row = row[2]
            ten_mon = row[3]
            so_tin_chi = row[4] or 0
            tong_buoi = row[5] or 0
            so_buoi_vang = row[6] or 0

            # Nếu chưa có lịch buổi học thì vẫn hiển thị nhưng không tính
            if tong_buoi <= 0:
                result.append({
                    "ma_sv": ma_sv,
                    "ho_ten": ho_ten,
                    "ma_lop": ma_lop_row,
                    "ten_mon": ten_mon,
                    "so_tin_chi": so_tin_chi,
                    "loai_mon": _get_subject_type_from_name(ten_mon),
                    "tong_buoi": 0,
                    "so_buoi_vang": 0,
                    "tong_tiet": 0,
                    "so_tiet_vang": 0,
                    "ti_le_vang": 0.0,
                    "cam_thi": False,
                    "trang_thai": "Chưa có lịch học"
                })
                continue

            # Xác định loại môn học và tính tổng số tiết
            loai_mon = _get_subject_type_from_name(ten_mon)
            tong_tiet_theo_tin_chi = _calculate_total_periods(so_tin_chi, loai_mon)
            
            # Tính số tiết thực tế dựa trên số buổi học (mỗi buổi = 3 tiết = 1 ca)
            tong_tiet_thuc_te = tong_buoi * 3
            so_tiet_vang = so_buoi_vang * 3
            
            # Sử dụng số tiết thực tế từ buổi học để tính tỷ lệ
            tong_tiet = tong_tiet_thuc_te
            ti_le_vang = float(so_tiet_vang) / float(tong_tiet) if tong_tiet > 0 else 0.0
            cam_thi = ti_le_vang > 0.2  # 20%

            result.append({
                "ma_sv": ma_sv,
                "ho_ten": ho_ten,
                "ma_lop": ma_lop_row,
                "ten_mon": ten_mon,
                "so_tin_chi": so_tin_chi,
                "loai_mon": loai_mon,
                "tong_buoi": int(tong_buoi),
                "so_buoi_vang": int(so_buoi_vang),
                "tong_tiet": int(tong_tiet),
                "tong_tiet_theo_tin_chi": int(tong_tiet_theo_tin_chi),
                "so_tiet_vang": int(so_tiet_vang),
                "ti_le_vang": ti_le_vang,
                "cam_thi": cam_thi,
                "trang_thai": "Cấm thi" if cam_thi else "Đủ điều kiện"
            })

        return result

    except Exception as e:
        print(f"Lỗi khi lấy danh sách sinh viên theo lớp (service): {e}")
        return []
    finally:
        if conn:
            conn.close()