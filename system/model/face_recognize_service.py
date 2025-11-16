# model/face_recognize_service.py
# [PHIÊN BẢN SỬA LỖI]
# - Sửa cú pháp cursor.execute để truyền tham số an toàn (dùng tuple)
# [PHIÊN BẢN CẬP NHẬT]
# - Thêm hàm finalize_attendance để chốt sổ (ghi vắng)

import datetime
from model import connectdb # Import module kết nối CSDL của bạn

def get_available_sessions():
    """
    Lấy danh sách các buổi học (lớp học phần) có sẵn để điểm danh.
    (Giả định là các buổi học trong NGÀY HÔM NAY)
    """
    sql = """
        SELECT 
            bh.ID_BUOI, 
            CONCAT(l.MA_LOP, ' - ', m.TEN_MON, ' (', 
                   CONVERT(varchar(5), bh.GIO_BAT_DAU, 108), ' - ', 
                   CONVERT(varchar(5), bh.GIO_KET_THUC, 108), ')') AS TenHienThi
        FROM 
            BUOIHOC AS bh
        JOIN 
            LOPHOC AS l ON bh.ID_LOP = l.ID_LOP
        JOIN 
            MONHOC AS m ON l.ID_MON = m.ID_MON
        WHERE 
            bh.NGAY_HOC = CAST(GETDATE() AS DATE)
    """
    conn = None
    cursor = None
    try:
        conn = connectdb.get_db_connection()
        if not conn:
             raise Exception("Kết nối CSDL thất bại.")
             
        cursor = conn.cursor()
        cursor.execute(sql) 
        sessions = cursor.fetchall()
        
        if sessions:
            print(f"[FaceRecognizeService] Tim thay {len(sessions)} buoi hoc cho hom nay.")
            return [tuple(row) for row in sessions]
        else:
            print("[FaceRecognizeService] Khong tim thay buoi hoc nao cho hom nay.")
            return []
            
    except Exception as e:
        print(f"Loi khi lay danh sach buoi hoc: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_session_info(session_id):
    """
    Lấy thông tin chi tiết của một buổi học (session_id)
    """
    sql = """
        SELECT 
            l.MA_LOP,
            m.TEN_MON,
            CONCAT(CONVERT(varchar(5), bh.GIO_BAT_DAU, 108), ' - ', CONVERT(varchar(5), bh.GIO_KET_THUC, 108)) AS ThoiGian,
            gv.HO_TEN AS TenGiangVien,
            bh.PHONG_HOC,
            bh.GIO_BAT_DAU,
            bh.GIO_KET_THUC
        FROM 
            BUOIHOC AS bh
        JOIN 
            LOPHOC AS l ON bh.ID_LOP = l.ID_LOP
        JOIN 
            MONHOC AS m ON l.ID_MON = m.ID_MON
        LEFT JOIN 
            GIANGVIEN AS gv ON m.ID_GV = gv.ID_GV
        WHERE 
            bh.ID_BUOI = ?
    """
    conn = None
    cursor = None
    try:
        conn = connectdb.get_db_connection()
        if not conn:
             raise Exception("Kết nối CSDL thất bại.")
             
        cursor = conn.cursor()
        
        # [SỬA] Truyền tham số dưới dạng tuple (session_id,)
        # Dấu phẩy (,) là bắt buộc để Python hiểu đây là tuple
        cursor.execute(sql, (session_id,))
        
        result = cursor.fetchone()
        
        if result:
            return result
        return None
            
    except Exception as e:
        print(f"Loi khi lay thong tin buoi hoc {session_id}: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_roster(session_id):
    """
    Lấy danh sách sinh viên (dạng dictionary) đã đăng ký buổi học này.
    """
    sql = """
        SELECT 
            sv.ID_SV, 
            sv.MA_SV, 
            sv.HO_TEN
        FROM 
            SINHVIEN AS sv
        JOIN 
            DANGKY AS dk ON sv.ID_SV = dk.ID_SV
        JOIN 
            LOPHOC AS l ON dk.ID_LOP = l.ID_LOP
        JOIN 
            BUOIHOC AS bh ON l.ID_LOP = bh.ID_LOP
        WHERE 
            bh.ID_BUOI = ?
            AND sv.TRANG_THAI = 1
    """
    
    student_roster = {}
    conn = None
    cursor = None
    try:
        conn = connectdb.get_db_connection()
        if not conn:
             raise Exception("Kết nối CSDL thất bại.")
             
        cursor = conn.cursor()
        
        # [SỬA] Truyền tham số dưới dạng tuple (session_id,)
        cursor.execute(sql, (session_id,))
        
        results = cursor.fetchall()
        
        if not results:
            print(f"Khong tim thay SV nao dang ky buoi hoc {session_id}")
            return {}
            
        for row in results:
            (id_sv, ma_sv, ho_ten) = row
            student_roster[ma_sv] = {
                "id": id_sv,
                "name": ho_ten,
                "status": "Vắng" # Đây là status hiển thị trên UI, không phải ghi xuống CSDL
            }
            
        print(f"Da tai {len(student_roster)} SV cho buoi hoc {session_id}")
        return student_roster
            
    except Exception as e:
        print(f"Loi khi lay danh sach SV: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
def mark_present(session_id, student_id, ma_sv, status='Có mặt'):
    """
    Ghi danh (INSERT) một sinh viên vào bảng DIEMDANH.
    """
    print(f"DEBUG: Ham mark_present duoc goi voi status = {status} (Kieu du lieu: {type(status)})")
    sql = """
        INSERT INTO DIEMDANH (ID_BUOI, ID_SV, THOI_GIAN_DIEMDANH, TRANG_THAI)
        VALUES (?, ?, GETDATE(), ?) 
    """
    conn = None
    cursor = None
    try:
        conn = connectdb.get_db_connection()
        if not conn:
             raise Exception("Kết nối CSDL thất bại.")
             
        cursor = conn.cursor()
        
        # [SỬA] Truyền tất cả tham số vào MỘT TUPLE duy nhất
        params = (session_id, student_id, status)
        cursor.execute(sql, params)
        
        conn.commit()
        
        print(f"[FaceRecognizeService] Da ghi danh {ma_sv} (ID: {student_id}) vao buoi {session_id} voi trang thai {status}")
        return True, "Điểm danh thành công"
        
    except Exception as e:
        print(f"Loi khi ghi danh CSDL: {e}")
        if conn:
            conn.rollback()
        return False, f"Lỗi CSDL: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==========================================================
# [MỚI] HÀM CHỐT SỔ (GHI VẮNG TỰ ĐỘNG)
# ==========================================================

def finalize_attendance(session_id):
    """
    Chốt sổ buổi học: Tự động INSERT 'Vắng' cho các SV đã đăng ký
    nhưng CHƯA CÓ bản ghi nào trong bảng DIEMDANH của buổi này.
    """
    
    # Câu SQL này sẽ INSERT 'Vắng' cho tất cả SV (từ DANGKY)
    # mà không tồn tại (NOT IN) trong bảng DIEMDANH của buổi học này.
    sql = """
        INSERT INTO DIEMDANH (ID_BUOI, ID_SV, THOI_GIAN_DIEMDANH, TRANG_THAI, GHI_CHU)
        SELECT
            bh.ID_BUOI,
            sv.ID_SV,
            GETDATE(),          -- Thời gian chốt sổ là lúc chạy lệnh
            N'Vắng',            -- Gán trạng thái 'Vắng'
            N'Tự động ghi vắng' -- Ghi chú
        FROM
            SINHVIEN sv
        JOIN
            DANGKY dk ON sv.ID_SV = dk.ID_SV
        JOIN
            LOPHOC lh ON dk.ID_LOP = lh.ID_LOP
        JOIN
            BUOIHOC bh ON lh.ID_LOP = bh.ID_LOP
        WHERE
            bh.ID_BUOI = ?  -- Chỉ buổi học này
        AND
            sv.ID_SV NOT IN (
                SELECT dd.ID_SV
                FROM DIEMDANH dd
                WHERE dd.ID_BUOI = bh.ID_BUOI
            );
    """
    
    conn = None
    cursor = None
    try:
        conn = connectdb.get_db_connection()
        if not conn:
             raise Exception("Kết nối CSDL thất bại.")
             
        cursor = conn.cursor()
        
        # Thực thi câu lệnh
        cursor.execute(sql, (session_id,))
        
        # Lấy số hàng (sinh viên) đã được INSERT
        # Cần commit() trước khi .rowcount có thể trả về giá trị đúng
        conn.commit()
        
        affected_rows = cursor.rowcount
        
        print(f"[FaceRecognizeService] Da chot so buoi {session_id}. Ghi vang cho {affected_rows} SV.")
        return True, f"Chốt sổ thành công. Đã ghi vắng cho {affected_rows} sinh viên.", affected_rows
        
    except Exception as e:
        print(f"Loi khi chot so CSDL: {e}")
        if conn:
            conn.rollback()
        return False, f"Lỗi CSDL khi chốt sổ: {e}", 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()