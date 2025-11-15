# model/face_recognize_service.py
# [PHIÊN BẢN HOÀN CHỈNH]
# Đã sửa lỗi tên hàm connectdb, cú pháp SQL Server, 
# tên bảng/cột, và lỗi CHECK constraint.

import datetime
from model import connectdb # Import module kết nối CSDL của bạn

def get_available_sessions():
    """
    Lấy danh sách các buổi học (lớp học phần) có sẵn để điểm danh.
    (Giả định là các buổi học trong NGÀY HÔM NAY)
    """
    # [SỬA] Đổi tên bảng: BUOI_HOC -> BUOIHOC, LOP_HOC_PHAN -> LOPHOC, MON_HOC -> MONHOC
    # [SỬA] Đổi ID: ID_BUOI_HOC -> ID_BUOI
    # [SỬA] Đổi cú pháp: CURDATE() -> CAST(GETDATE() AS DATE)
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
        # [SỬA] Đổi tên hàm
        conn = connectdb.get_db_connection()
        if not conn:
             raise Exception("Kết nối CSDL thất bại.")
             
        cursor = conn.cursor()
        cursor.execute(sql) 
        sessions = cursor.fetchall()
        
        if sessions:
            print(f"[FaceRecognizeService] Tim thay {len(sessions)} buoi hoc cho hom nay.")
            # Đảm bảo trả về list of tuples
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
    # [SỬA] Đổi tên bảng: BUOI_HOC -> BUOIHOC, LOP_HOC_PHAN -> LOPHOC, MON_HOC -> MONHOC, GIANG_VIEN -> GIANGVIEN
    # [SỬA] Đổi cú pháp: %s -> ?
    sql = """
        SELECT 
            l.MA_LOP,
            m.TEN_MON,
            CONCAT(CONVERT(varchar(5), bh.GIO_BAT_DAU, 108), ' - ', CONVERT(varchar(5), bh.GIO_KET_THUC, 108)) AS ThoiGian,
            gv.HO_TEN AS TenGiangVien,
            bh.PHONG_HOC
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
        # [SỬA] Đổi tên hàm
        conn = connectdb.get_db_connection()
        if not conn:
             raise Exception("Kết nối CSDL thất bại.")
             
        cursor = conn.cursor()
        cursor.execute(sql, session_id)
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
    # [SỬA] Đổi tên bảng: DANG_KY -> DANGKY, LOP_HOC_PHAN -> LOPHOC, BUOI_HOC -> BUOIHOC
    # [SỬA] Đổi cú pháp: %s -> ?
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
        # [SỬA] Đổi tên hàm
        conn = connectdb.get_db_connection()
        if not conn:
             raise Exception("Kết nối CSDL thất bại.")
             
        cursor = conn.cursor()
        cursor.execute(sql, session_id)
        results = cursor.fetchall()
        
        if not results:
            print(f"Khong tim thay SV nao dang ky buoi hoc {session_id}")
            return {}
            
        for row in results:
            (id_sv, ma_sv, ho_ten) = row
            student_roster[ma_sv] = {
                "id": id_sv,
                "name": ho_ten,
                "status": "Vắng"
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
        
def mark_present(session_id, student_id, ma_sv):
    """
    Ghi danh (INSERT) một sinh viên vào bảng DIEMDANH.
    """
    # [SỬA] Đổi tên cột: ID_BUOI_HOC -> ID_BUOI, THOI_GIAN_DIEM_DANH -> THOI_GIAN_DIEMDANH
    # [SỬA] Đổi cú pháp: %s -> ?, NOW() -> GETDATE()
    # [SỬA LỖI CHECK CONSTRAINT] Đổi N'Có mặt' -> 'Có mặt'
    sql = """
        INSERT INTO DIEMDANH (ID_BUOI, ID_SV, THOI_GIAN_DIEMDANH, TRANG_THAI)
        VALUES (?, ?, GETDATE(), 'Có mặt') 
    """
    conn = None
    cursor = None
    try:
        # [SỬA] Đổi tên hàm
        conn = connectdb.get_db_connection()
        if not conn:
             raise Exception("Kết nối CSDL thất bại.")
             
        cursor = conn.cursor()
        cursor.execute(sql, session_id, student_id)
        conn.commit()
        
        print(f"[FaceRecognizeService] Da ghi danh {ma_sv} (ID: {student_id}) vao buoi {session_id}")
        return True, "Điểm danh thành công"
        
    except Exception as e:
        print(f"Loi khi ghi danh CSDL: {e}")
        # [THÊM] Rollback nếu có lỗi
        if conn:
            conn.rollback()
        return False, f"Lỗi CSDL: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()