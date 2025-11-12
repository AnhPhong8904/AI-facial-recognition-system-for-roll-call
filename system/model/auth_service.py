import pyodbc
from model.connectdb import get_db_connection

def check_credentials(username, password, is_admin_check):
    """
    Kiểm tra tên đăng nhập và mật khẩu với database.
    
    Trả về:
    - (True, 'Admin') nếu đăng nhập admin thành công.
    - (True, 'GiangVien') nếu đăng nhập giảng viên thành công.
    - (False, "Thông báo lỗi") nếu thất bại.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return False, "Không thể kết nối CSDL."

        cursor = conn.cursor()
        
        sql_query = ""
        params = (username, password)
        
        if is_admin_check:
            # Nếu người dùng check vào ô "Đăng nhập bằng tài khoản admin"
            # Chỉ tìm chính xác tài khoản 'Admin'
            sql_query = """
                SELECT QUYEN 
                FROM TAIKHOAN 
                WHERE TEN_DANG_NHAP = ? AND MAT_KHAU = ? AND QUYEN = 'Admin'
            """
        else:
            # Nếu không check, chỉ tìm tài khoản 'GiangVien'
            sql_query = """
                SELECT QUYEN 
                FROM TAIKHOAN 
                WHERE TEN_DANG_NHAP = ? AND MAT_KHAU = ? AND QUYEN = 'GiangVien'
            """

        cursor.execute(sql_query, params)
        row = cursor.fetchone()
        
        if row:
            # Đăng nhập thành công, trả về vai trò (QUYEN)
            return True, row[0] 
        else:
            # Sai thông tin, hoặc chọn sai vai trò (ví dụ: là admin nhưng không check)
            return False, "Sai tên đăng nhập, mật khẩu hoặc vai trò."
            
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        if sqlstate == '28000':
            return False, "Lỗi xác thực CSDL. Kiểm tra lại config."
        print(f"Lỗi SQL (auth_service): {ex}")
        return False, f"Lỗi SQL: {ex}"
    except Exception as e:
        print(f"Lỗi auth_service: {e}")
        return False, f"Lỗi hệ thống: {e}"
    
    finally:
        if conn:
            conn.close() # Trả kết nối về pool