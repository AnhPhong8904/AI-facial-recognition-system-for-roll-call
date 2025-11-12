import pyodbc

# --- 1. Định nghĩa thông tin kết nối ---
# (Chọn 1 trong 2 cách bên dưới)

# Cách 1: Dùng SQL Server Authentication
server = 'DESKTOP-MUUEIFA'  # Hoặc tên server của bạn
database = 'DIEMDANH_NHAN_DIEN'
username = 'sa'
password = '123'
conn_str = f'DRIVER={{SQL Server}};' \
           f'SERVER={server};' \
           f'DATABASE={database};' \
           f'UID={username};' \
           f'PWD={password};'

# Cách 2: Dùng Windows Authentication
# server = 'MY_WORK_PC\SQLEXPRESS'
# database = 'MyDatabase'
# conn_str = f'DRIVER={{SQL Server}};' \
#            f'SERVER={server};' \
#            f'DATABASE={database};' \
#            f'Trusted_Connection=yes;'


conn = None  # Khởi tạo conn
try:
    # --- 2. Kết nối ---
    conn = pyodbc.connect(conn_str)
    print("Kết nối thành công!")
    
    # --- 3. Tạo một đối tượng 'cursor' ---
    # Cursor dùng để thực thi các câu lệnh SQL
    cursor = conn.cursor()

    # --- 4. Thực thi câu lệnh SELECT ---
    print("Đang đọc dữ liệu...")
    cursor.execute("SELECT GETDATE();")  # Lấy ngày giờ hiện tại của server
    
    # Lấy 1 dòng kết quả
    row = cursor.fetchone()
    
    if row:
        print(f"Ngày giờ máy chủ SQL: {row[0]}")

    # Ví dụ: Lấy dữ liệu từ bảng 'Employees'
    # cursor.execute("SELECT EmployeeID, FirstName, LastName FROM Employees")
    # all_rows = cursor.fetchall()
    # for r in all_rows:
    #     print(f"ID: {r.EmployeeID}, Tên: {r.FirstName} {r.LastName}")


except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    if sqlstate == '28000':
        print(f"Lỗi xác thực: Sai username hoặc password.")
    else:
        print(f"Lỗi kết nối hoặc thực thi: {ex}")

except Exception as e:
    print(f"Lỗi không xác định: {e}")

finally:
    # --- 5. Đóng kết nối (Rất quan trọng) ---
    # Luôn đóng kết nối trong khối 'finally'
    # để đảm bảo nó được đóng ngay cả khi có lỗi xảy ra.
    if conn:
        cursor.close()
        conn.close()
        print("Đã đóng kết nối.")