import pyodbc

# --- Đã cập nhật thông tin CSDL của bạn ---
SERVER = 'DESKTOP-MUUEIFA'
DATABASE = 'DIEMDANH_NHAN_DIEN'
USERNAME = 'sa'
PASSWORD = '123'

CONN_STR = (
    f'DRIVER={{SQL Server}};'
    f'SERVER={SERVER};'
    f'DATABASE={DATABASE};'
    f'UID={USERNAME};'
    f'PWD={PASSWORD};'
)

def get_db_connection():
    """
    Hàm này lấy một kết nối mới từ Pool.
    """
    try:
        conn = pyodbc.connect(CONN_STR)
        return conn
    except pyodbc.Error as ex:
        # Xử lý lỗi chi tiết dựa trên mã lỗi SQL
        print(f"Lỗi kết nối CSDL trong get_db_connection: {ex}")
        sqlstate = ex.args[0]
        
        if sqlstate == '28000':
            print("LỖI 28000: Sai tên đăng nhập (UID) hoặc mật khẩu (PWD).")
        elif sqlstate == '42000':
             print(f"LỖI 42000: Không tìm thấy CSDL '{DATABASE}' hoặc lỗi quyền truy cập CSDL.")
        elif sqlstate == '08001':
             print(f"LỖI 08001: Không tìm thấy máy chủ (Server) '{SERVER}' hoặc máy chủ không thể truy cập.")
        else:
            print(f"Lỗi pyodbc không xác định: {sqlstate}")
            
        return None
    except Exception as e:
        print(f"Lỗi không xác định khi kết nối DB: {e}")
        return None
    
if __name__ == "__main__":
    # Test kết nối
    connection = get_db_connection()
    if connection:
        print("Kết nối CSDL thành công!")
        connection.close()
    else:
        print("Kết nối CSDL thất bại.")