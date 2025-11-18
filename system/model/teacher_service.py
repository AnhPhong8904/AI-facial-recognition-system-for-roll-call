import pyodbc
from model.connectdb import get_db_connection
from datetime import date, datetime

def _format_ngay_sinh(value):
    """
    Chuẩn hóa giá trị ngày sinh thành chuỗi dd/MM/yyyy để hiển thị.
    Hỗ trợ các kiểu date/datetime và chuỗi (yyyy-MM-dd hoặc dd/MM/yyyy).
    """
    if value is None:
        return ""

    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y")

    if isinstance(value, str):
        cleaned = value.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                parsed = datetime.strptime(cleaned, fmt)
                return parsed.strftime("%d/%m/%Y")
            except ValueError:
                continue
        return cleaned  # Trả lại nguyên bản nếu không parse được

    return str(value)

def get_all_teachers():
    """
    Tải toàn bộ danh sách giảng viên (JOIN từ 2 bảng TAIKHOAN và GIANGVIEN)
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            # Sửa: Trả về None thay vì raise Exception
            print("Lỗi: Không thể kết nối CSDL trong get_all_teachers.")
            return None 
            
        cursor = conn.cursor()
        
        # MỚI: Thêm GIOI_TINH, NGAY_SINH, DIA_CHI và các ID
        # Trả về ID để dùng cho Sửa/Xóa
        query = """
            SELECT 
                tk.ID_TAIKHOAN, gv.ID_GV, gv.MA_GV, gv.HO_TEN,
                gv.GIOI_TINH, gv.NGAY_SINH, gv.DIA_CHI,
                gv.SDT, gv.EMAIL, tk.TEN_DANG_NHAP
            FROM GIANGVIEN gv
            INNER JOIN TAIKHOAN tk ON gv.ID_TAIKHOAN = tk.ID_TAIKHOAN
            WHERE tk.QUYEN = 'GiangVien'
            ORDER BY gv.ID_GV DESC;
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Chuyển đổi ngày sinh thành chuỗi dd/MM/yyyy
        formatted_rows = []
        for row in rows:
            row_list = list(row)
            row_list[5] = _format_ngay_sinh(row_list[5])  # Cột NGAY_SINH (index 5)
            formatted_rows.append(tuple(row_list))
            
        return formatted_rows
        
    except Exception as e:
        print(f"Lỗi khi tải danh sách GV (teacher_service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_teacher(data):
    """
    Thêm giảng viên mới. Yêu cầu transaction vì phải thêm vào 2 bảng.
    data: Dictionary chứa thông tin từ form.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return False, "Không thể kết nối CSDL."
        
        # Bắt đầu transaction
        conn.autocommit = False
        cursor = conn.cursor()

        # --- Bước 1: Thêm vào bảng TAIKHOAN ---
        sql_add_account = """
            INSERT INTO TAIKHOAN (TEN_DANG_NHAP, MAT_KHAU, QUYEN)
            VALUES (?, ?, 'GiangVien');
        """
        try:
            # Đảm bảo Tên đăng nhập và Mật khẩu là bắt buộc khi thêm mới
            if not data.get('ten_dang_nhap') or not data.get('mat_khau'):
                 return False, "Tên đăng nhập và Mật khẩu là bắt buộc khi tạo mới."
            cursor.execute(sql_add_account, (data['ten_dang_nhap'], data['mat_khau']))
        except pyodbc.IntegrityError as e:
            conn.rollback()
            if "UNIQUE" in str(e):
                return False, f"Tên đăng nhập '{data['ten_dang_nhap']}' đã tồn tại."
            return False, f"Lỗi khi thêm tài khoản: {e}"

        # --- Bước 2: Lấy ID_TAIKHOAN vừa tạo ---
        cursor.execute("SELECT @@IDENTITY AS ID;")
        id_taikhoan = cursor.fetchone()[0]

        if not id_taikhoan:
            conn.rollback()
            return False, "Không thể tạo ID tài khoản."

        # --- Bước 3: Thêm vào bảng GIANGVIEN ---
        sql_add_teacher = """
            INSERT INTO GIANGVIEN (
                MA_GV, HO_TEN, SDT, EMAIL, 
                GIOI_TINH, NGAY_SINH, DIA_CHI, ID_TAIKHOAN
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        
        # Xử lý các giá trị có thể là None (trống)
        ngay_sinh = data.get('ngay_sinh') or None
        gioi_tinh = data.get('gioi_tinh') or None
        dia_chi = data.get('dia_chi') or None
        
        try:
            cursor.execute(sql_add_teacher, (
                data['ma_gv'], data['ho_ten'], data['sdt'], data['email'],
                gioi_tinh, ngay_sinh, dia_chi,
                id_taikhoan
            ))
        except pyodbc.IntegrityError as e:
            conn.rollback()
            if "UNIQUE" in str(e):
                return False, f"Mã giảng viên '{data['ma_gv']}' đã tồn tại."
            return False, f"Lỗi khi thêm giảng viên: {e}"

        # --- Bước 4: Hoàn tất transaction ---
        conn.commit()
        return True, "Thêm giảng viên thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi (add_teacher): {e}")
        return False, f"Đã xảy ra lỗi: {e}"
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

def update_teacher(id_gv, id_taikhoan, data):
    """
    Cập nhật thông tin giảng viên và tài khoản (nếu có)
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return False, "Không thể kết nối CSDL."
            
        conn.autocommit = False
        cursor = conn.cursor()

        # --- Bước 1: Cập nhật bảng TAIKHOAN ---
        # Chỉ cập nhật TAIKHOAN nếu có ID (phòng trường hợp GV không có TK)
        if id_taikhoan:
            if data['mat_khau']:
                # Nếu có nhập mật khẩu mới
                sql_update_account = "UPDATE TAIKHOAN SET MAT_KHAU = ? WHERE ID_TAIKHOAN = ?"
                params_account = (data['mat_khau'], id_taikhoan)
            else:
                # Nếu không nhập mật khẩu mới (không làm gì)
                sql_update_account = None
                params_account = None

            try:
                if sql_update_account:
                    cursor.execute(sql_update_account, params_account)
            except pyodbc.Error as e:
                conn.rollback()
                return False, f"Lỗi cập nhật tài khoản: {e}"
        else:
            print("Bỏ qua cập nhật TAIKHOAN (ID=None)")


        # --- Bước 2: Cập nhật bảng GIANGVIEN ---
        sql_update_teacher = """
            UPDATE GIANGVIEN
            SET HO_TEN = ?, SDT = ?, EMAIL = ?,
                GIOI_TINH = ?, NGAY_SINH = ?, DIA_CHI = ?
            WHERE ID_GV = ?;
        """
        
        # Xử lý các giá trị có thể là None (trống)
        ngay_sinh = data.get('ngay_sinh') or None
        gioi_tinh = data.get('gioi_tinh') or None
        dia_chi = data.get('dia_chi') or None

        try:
            # Lưu ý: Không cho cập nhật MA_GV và TEN_DANG_NHAP (đã bị vô hiệu hóa ở UI)
            cursor.execute(sql_update_teacher, (
                data['ho_ten'], data['sdt'], data['email'],
                gioi_tinh, ngay_sinh, dia_chi,
                id_gv
            ))
        except pyodbc.IntegrityError as e:
            conn.rollback()
            return False, f"Lỗi cập nhật giảng viên: {e}"

        # --- Bước 3: Hoàn tất transaction ---
        conn.commit()
        return True, "Cập nhật giảng viên thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi (update_teacher): {e}")
        return False, f"Đã xảy ra lỗi khi cập nhật: {e}"
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

def delete_teacher(id_gv, id_taikhoan):
    """
    Xóa giảng viên và tài khoản liên kết (yêu cầu transaction)
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return False, "Không thể kết nối CSDL."
            
        conn.autocommit = False
        cursor = conn.cursor()

        # --- Bước 1: Xóa khỏi bảng GIANGVIEN (vì có khóa ngoại) ---
        # Cần kiểm tra ràng buộc trước
        cursor.execute("SELECT 1 FROM MONHOC WHERE ID_GV = ?", (id_gv,))
        if cursor.fetchone():
            conn.rollback()
            return False, "Không thể xóa. Giảng viên này đã được gán vào Môn học. Vui lòng gỡ gán trước."
            
        sql_delete_teacher = "DELETE FROM GIANGVIEN WHERE ID_GV = ?;"
        cursor.execute(sql_delete_teacher, (id_gv,))

        # --- Bước 2: Xóa khỏi bảng TAIKHOAN (nếu có) ---
        if id_taikhoan:
            sql_delete_account = "DELETE FROM TAIKHOAN WHERE ID_TAIKHOAN = ?;"
            cursor.execute(sql_delete_account, (id_taikhoan,))

        # --- Bước 3: Hoàn tất transaction ---
        conn.commit()
        return True, "Xóa giảng viên thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi (delete_teacher): {e}")
        if "REFERENCE constraint" in str(e):
            return False, "Không thể xóa. Giảng viên này đã được gán vào Môn học. Vui lòng gỡ gán trước."
        return False, f"Đã xảy ra lỗi khi xóa: {e}"
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

def search_teachers(criteria, term):
    """
    Tìm kiếm giảng viên dựa trên tiêu chí và từ khóa
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return None 
            
        cursor = conn.cursor()
        
        # Thêm GIOI_TINH, NGAY_SINH, DIA_CHI
        base_query = """
            SELECT 
                tk.ID_TAIKHOAN, gv.ID_GV, gv.MA_GV, gv.HO_TEN,
                gv.GIOI_TINH, gv.NGAY_SINH, gv.DIA_CHI,
                gv.SDT, gv.EMAIL, tk.TEN_DANG_NHAP
            FROM GIANGVIEN gv
            INNER JOIN TAIKHOAN tk ON gv.ID_TAIKHOAN = tk.ID_TAIKHOAN
            WHERE tk.QUYEN = 'GiangVien' AND
        """
        
        # Tạo câu lệnh WHERE an toàn
        # criteria là tên cột (an toàn vì chúng ta map nó trong controller)
        query = f"{base_query} gv.{criteria} LIKE ?"
        
        params = (f"%{term}%",)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Chuyển đổi ngày sinh thành chuỗi dd/MM/yyyy
        formatted_rows = []
        for row in rows:
            row_list = list(row)
            row_list[5] = _format_ngay_sinh(row_list[5])  # Cột NGAY_SINH (index 5)
            formatted_rows.append(tuple(row_list))
            
        return formatted_rows
        
    except Exception as e:
        print(f"Lỗi khi tìm kiếm GV (teacher_service): {e}")
        return None
    finally:
        if conn:
            conn.close()