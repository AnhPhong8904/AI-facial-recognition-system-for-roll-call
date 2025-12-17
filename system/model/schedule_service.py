import pyodbc
from model.connectdb import get_db_connection
from datetime import date, datetime, timedelta # Cần import date

# ==========================================================
# HÀM TẢI DỮ LIỆU (READ)
# ==========================================================

def get_all_classes_for_combo():
    """
    Tải danh sách Lớp học (ID, Mã, Tên) để điền vào ComboBox.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        # Chỉ lấy ID_LOP, MA_LOP, TEN_LOP từ bảng LOPHOC
        sql_query = "SELECT ID_LOP, MA_LOP, TEN_LOP FROM LOPHOC ORDER BY MA_LOP;"
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        # Trả về list of tuples [(1, 'L01', 'Lớp KTLT T2'), ...]
        return rows

    except Exception as e:
        print(f"Lỗi khi tải danh sách lớp học cho ComboBox (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_class_details(id_lop):
    """
    Lấy chi tiết (Tên Môn, Tên GV, Giờ BĐ, Giờ KT) của một Lớp học
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        # JOIN 3 bảng: LOPHOC -> MONHOC -> GIANGVIEN
        sql_query = """
            SELECT 
                m.TEN_MON, 
                g.HO_TEN,
                l.GIO_BAT_DAU, -- <<< THÊM DÒNG NÀY
                l.GIO_KET_THUC -- <<< THÊM DÒNG NÀY
            FROM LOPHOC l
            LEFT JOIN MONHOC m ON l.ID_MON = m.ID_MON
            LEFT JOIN GIANGVIEN g ON m.ID_GV = g.ID_GV
            WHERE l.ID_LOP = ?;
        """
        
        cursor.execute(sql_query, (id_lop,))
        row = cursor.fetchone()
        if not row:
            return None
        # Chuẩn hóa giờ về HH:MM để view setTime() luôn đúng giờ mới nhất
        ten_mon, ho_ten, gio_bd, gio_kt = row
        return ten_mon, ho_ten, _format_time_value(gio_bd), _format_time_value(gio_kt)

    except Exception as e:
        print(f"Lỗi khi tải chi tiết lớp học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_schedules():
    """
    Tải danh sách buổi học trong 7 ngày tới (JOIN với Lớp học để lấy Mã Lớp, Tên môn, Thứ).
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        today = date.today()
        window_end = today + timedelta(days=6)
        today_str = _format_date_value(today)
        window_end_str = _format_date_value(window_end)
        
        # JOIN BUOIHOC -> LOPHOC -> MONHOC để lấy thêm Tên môn; giới hạn trong tuần hiện tại
        sql_query = """
            SELECT 
                b.ID_BUOI, 
                b.NGAY_HOC, 
                b.GIO_BAT_DAU, 
                b.GIO_KET_THUC, 
                b.PHONG_HOC, 
                l.MA_LOP,
                m.TEN_MON,
                b.GHI_CHU
            FROM BUOIHOC b
            LEFT JOIN LOPHOC l ON b.ID_LOP = l.ID_LOP
            LEFT JOIN MONHOC m ON l.ID_MON = m.ID_MON
            WHERE b.NGAY_HOC BETWEEN ? AND ?
            ORDER BY b.NGAY_HOC ASC, b.GIO_BAT_DAU ASC;
        """
        
        cursor.execute(sql_query, (today_str, window_end_str))
        rows = cursor.fetchall()
        
        # Chuyển đổi định dạng ngày và giờ trước khi trả về
        formatted_rows = []
        for row in rows:
            # row[1] là NGAY_HOC, row[2] là GIO_BAT_DAU, row[3] là GIO_KET_THUC
            ngay_hoc_raw = row[1]
            ngay_hoc_str = ngay_hoc_raw.strftime("%d-%m-%Y") if isinstance(ngay_hoc_raw, date) else str(ngay_hoc_raw)
            gio_bd = _format_time_value(row[2])
            gio_kt = _format_time_value(row[3])
            phong_hoc = row[4]
            ma_lop = row[5]
            ten_mon = row[6] if len(row) > 6 else ""
            ghi_chu = row[7] if len(row) > 7 else ""

            thu_str = _weekday_vn(ngay_hoc_raw)
            
            formatted_rows.append((
                row[0],            # ID_BUOI
                ngay_hoc_str,      # Ngày
                thu_str,           # Thứ
                gio_bd,            # Giờ BĐ
                gio_kt,            # Giờ KT
                phong_hoc,         # Phòng
                ma_lop,            # Mã lớp
                ten_mon,           # Tên môn
                ghi_chu,           # Ghi chú
            ))
            
        return formatted_rows

    except Exception as e:
        print(f"Lỗi khi tải danh sách lịch học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# ĐỒNG BỘ LỊCH TỪ KHAI BÁO LỚP HỌC (NGÀY BẮT ĐẦU/KẾT THÚC + THỨ)
# ==========================================================

def sync_schedules_from_classes():
    """
    Sinh hoặc cập nhật BUOIHOC dựa trên thông tin lớp học (LOPHOC).
    - Chỉ xử lý trong cửa sổ 7 ngày tới để tránh phình dữ liệu (mỗi lần mở sẽ cập nhật tuần kế tiếp).
    - Dựa vào NGAY_BAT_DAU, NGAY_KET_THUC, THU_HOC, GIO_BĐ/KẾT_THÚC, PHÒNG_HỌC.
    - Nếu đã có buổi ở ngày đó: cập nhật giờ/phòng theo lớp.
    - Nếu chưa có: chèn mới.
    Hàm idempotent, gọi nhiều lần không tạo trùng.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")

        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID_LOP, NGAY_BAT_DAU, NGAY_KET_THUC, THU_HOC, GIO_BAT_DAU, GIO_KET_THUC, PHONG_HOC
            FROM LOPHOC
        """)
        classes = cursor.fetchall()

        summary = {
            "classes": len(classes),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "window_days": 7,
        }

        for row in classes:
            id_lop, ngay_bd, ngay_kt, thu_hoc, gio_bd, gio_kt, phong_hoc = row
            if not (ngay_bd and ngay_kt and thu_hoc):
                continue

            weekdays = _parse_weekdays_from_string(str(thu_hoc))
            if not weekdays:
                continue

            try:
                start_date = ngay_bd if isinstance(ngay_bd, date) else datetime.strptime(str(ngay_bd), "%Y-%m-%d").date()
                end_date = ngay_kt if isinstance(ngay_kt, date) else datetime.strptime(str(ngay_kt), "%Y-%m-%d").date()
            except Exception:
                continue

            if end_date < start_date:
                continue

            # Giới hạn: chỉ sinh lịch trong 7 ngày kế tiếp tính từ hôm nay
            today = date.today()
            window_end = min(end_date, today + timedelta(days=6))
            current = max(start_date, today)
            gio_bd_str = _format_time_value(gio_bd)
            gio_kt_str = _format_time_value(gio_kt)
            phong_hoc_str = (phong_hoc or "").strip()

            while current <= window_end:
                current_str = _format_date_value(current)
                if current.weekday() in weekdays:
                    cursor.execute(
                        "SELECT ID_BUOI, GIO_BAT_DAU, GIO_KET_THUC, PHONG_HOC FROM BUOIHOC WHERE ID_LOP = ? AND NGAY_HOC = ?",
                        (id_lop, current_str)
                    )
                    existing = cursor.fetchone()

                    if existing:
                        id_buoi, gio_bd_old, gio_kt_old, phong_old = existing
                        need_update = (
                            _format_time_value(gio_bd_old) != gio_bd_str or
                            _format_time_value(gio_kt_old) != gio_kt_str or
                            (phong_old or "").strip() != phong_hoc_str
                        )
                        if need_update:
                            cursor.execute(
                                """
                                UPDATE BUOIHOC
                                SET GIO_BAT_DAU = ?, GIO_KET_THUC = ?, PHONG_HOC = ?
                                WHERE ID_BUOI = ?
                                """,
                                (gio_bd_str, gio_kt_str, phong_hoc_str, id_buoi)
                            )
                            summary["updated"] += 1
                        else:
                            summary["skipped"] += 1
                    else:
                        cursor.execute(
                            """
                            INSERT INTO BUOIHOC (ID_LOP, NGAY_HOC, GIO_BAT_DAU, GIO_KET_THUC, PHONG_HOC, GHI_CHU)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (id_lop, current_str, gio_bd_str, gio_kt_str, phong_hoc_str, f"Tự động tạo cho lớp {id_lop}")
                        )
                        summary["inserted"] += 1
                current += timedelta(days=1)

        conn.commit()
        return summary

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi đồng bộ lịch học từ lớp học: {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM THÊM MỚI (CREATE)
# ==========================================================

def add_schedule(data):
    """
    Thêm buổi học mới.
    data: dictionary từ get_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        phong_hoc = (data["phong_hoc"] or "").strip()

        conflict = _find_room_conflict(
            cursor,
            phong_hoc,
            data["ngay_hoc"],
            data["gio_bd"],
            data["gio_kt"]
        )
        if conflict:
            return False, _build_conflict_message(phong_hoc, conflict)

        sql_insert = """
            INSERT INTO BUOIHOC (ID_LOP, NGAY_HOC, GIO_BAT_DAU, GIO_KET_THUC, PHONG_HOC, GHI_CHU) 
            VALUES (?, ?, ?, ?, ?, ?);
        """
        params = (
            data["id_lop"],
            data["ngay_hoc"],
            data["gio_bd"],
            data["gio_kt"],
            phong_hoc,
            data["ghi_chu"]
        )
        
        cursor.execute(sql_insert, params)
        conn.commit()
        return True, "Thêm lịch học thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi thêm lịch học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM CẬP NHẬT (UPDATE)
# ==========================================================

def update_schedule(data):
    """
    Cập nhật thông tin buổi học.
    data: dictionary từ get_form_data()
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()

        phong_hoc = (data["phong_hoc"] or "").strip()
        exclude_id = int(data["id_buoi"]) if str(data["id_buoi"]).isdigit() else data["id_buoi"]

        conflict = _find_room_conflict(
            cursor,
            phong_hoc,
            data["ngay_hoc"],
            data["gio_bd"],
            data["gio_kt"],
            exclude_id=exclude_id
        )
        if conflict:
            return False, _build_conflict_message(phong_hoc, conflict)

        # Cập nhật bảng BUOIHOC
        # Lưu ý: Không cho phép đổi ID_LOP khi cập nhật (đã disable ComboBox)
        sql_update = """
            UPDATE BUOIHOC 
            SET NGAY_HOC = ?, GIO_BAT_DAU = ?, GIO_KET_THUC = ?, 
                PHONG_HOC = ?, GHI_CHU = ?
            WHERE ID_BUOI = ?;
        """
        params = (
            data["ngay_hoc"],
            data["gio_bd"],
            data["gio_kt"],
            phong_hoc,
            data["ghi_chu"],
            data["id_buoi"]
        )
        
        cursor.execute(sql_update, params)

        if cursor.rowcount == 0:
            raise Exception("Không tìm thấy lịch học để cập nhật (hoặc dữ liệu không đổi).")
            
        conn.commit()
        return True, "Cập nhật thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi cập nhật lịch học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM XÓA (DELETE)
# ==========================================================

def delete_schedule(id_buoi):
    """
    Xóa buổi học.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        conn.autocommit = False # Bắt đầu Transaction
        cursor = conn.cursor()

        # Bước 1: Kiểm tra ràng buộc (bảng DIEMDANH)
        cursor.execute("SELECT 1 FROM DIEMDANH WHERE ID_BUOI = ?", (id_buoi,))
        if cursor.fetchone():
            raise Exception("Không thể xóa. Lịch học này đã có dữ liệu điểm danh.")

        # Bước 2: Xóa BUOIHOC
        cursor.execute("DELETE FROM BUOIHOC WHERE ID_BUOI = ?", (id_buoi,))
        
        if cursor.rowcount == 0:
             raise Exception("Không tìm thấy lịch học để xóa.")

        conn.commit()
        return True, "Xóa lịch học thành công."

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi xóa lịch học (service): {e}")
        return False, str(e)
    finally:
        if conn:
            conn.autocommit = True # Đặt lại autocommit
            conn.close()

# ==========================================================
# HÀM TÌM KIẾM (SEARCH)
# ==========================================================

def search_schedules(search_by, keyword):
    """
    Tìm kiếm buổi học.
    search_by: 'Mã lớp', 'Tên môn', 'Tên giảng viên'
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        
        sql_base = """
            SELECT 
                b.ID_BUOI, b.NGAY_HOC, b.GIO_BAT_DAU, b.GIO_KET_THUC, 
                b.PHONG_HOC, l.MA_LOP, b.GHI_CHU
            FROM BUOIHOC b
            LEFT JOIN LOPHOC l ON b.ID_LOP = l.ID_LOP
            LEFT JOIN MONHOC m ON l.ID_MON = m.ID_MON
            LEFT JOIN GIANGVIEN g ON m.ID_GV = g.ID_GV
        """
        
        sql_where = ""
        params = ()
        keyword_like = f"%{keyword}%" 

        if search_by == 'Mã lớp':
            sql_where = " WHERE l.MA_LOP LIKE ?"
            params = (keyword_like,)
        elif search_by == 'Tên môn':
            sql_where = " WHERE m.TEN_MON LIKE ?"
            params = (keyword_like,)
        elif search_by == 'Tên giảng viên':
            sql_where = " WHERE g.HO_TEN LIKE ?"
            params = (keyword_like,)
        else:
            return None # Tiêu chí tìm kiếm không hợp lệ

        sql_query = sql_base + sql_where + " ORDER BY b.ID_BUOI DESC;"
        
        cursor.execute(sql_query, params)
        rows = cursor.fetchall()
        
        # Chuyển đổi định dạng ngày và giờ
        formatted_rows = []
        for row in rows:
            ngay_hoc = row[1].strftime("%d-%m-%Y") if isinstance(row[1], date) else row[1]
            gio_bd = _format_time_value(row[2])
            gio_kt = _format_time_value(row[3])
            
            formatted_rows.append((
                row[0], ngay_hoc, gio_bd, gio_kt, row[4], row[5], row[6]
            ))
            
        return formatted_rows

    except Exception as e:
        print(f"Lỗi khi tìm kiếm lịch học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM KIỂM TRA VÀ HIỂN THỊ TÌNH TRẠNG PHÒNG HỌC
# ==========================================================

def get_room_availability(ngay_hoc, gio_bd, gio_kt):
    """
    Lấy danh sách phòng học và trạng thái trống/bận cho khoảng thời gian cụ thể.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Không thể kết nối CSDL.")
        
        cursor = conn.cursor()
        rooms = _fetch_all_known_rooms(cursor)
        if not rooms:
            return []

        busy_map = _fetch_busy_rooms(cursor, ngay_hoc, gio_bd, gio_kt)
        availability = []
        for room in rooms:
            conflicts = busy_map.get(room, [])
            availability.append({
                "phong_hoc": room,
                "is_free": len(conflicts) == 0,
                "conflicts": conflicts
            })
        return availability

    except Exception as e:
        print(f"Lỗi khi lấy tình trạng phòng học (service): {e}")
        return None
    finally:
        if conn:
            conn.close()

# ==========================================================
# HÀM PHỤ TRỢ
# ==========================================================

def _format_time_value(value):
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    if isinstance(value, str):
        return value[:5]
    return str(value) if value is not None else ""

def _weekday_vn(value):
    """Trả về chuỗi Thứ tiếng Việt từ giá trị date/datetime/str."""
    try:
        if isinstance(value, date) and not isinstance(value, datetime):
            d = value
        elif isinstance(value, datetime):
            d = value.date()
        elif isinstance(value, str):
            d = datetime.strptime(value[:10], "%Y-%m-%d").date()
        else:
            return ""
        mapping = {
            0: "Thứ 2",
            1: "Thứ 3",
            2: "Thứ 4",
            3: "Thứ 5",
            4: "Thứ 6",
            5: "Thứ 7",
            6: "Chủ nhật",
        }
        return mapping.get(d.weekday(), "")
    except Exception:
        return ""

def _format_date_value(value):
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str):
        return value[:10]
    if isinstance(value, datetime):
        return value.date().strftime("%Y-%m-%d")
    return str(value) if value is not None else ""

def _parse_weekdays_from_string(thu_hoc_str):
    """
    Chuyển chuỗi 'Thứ 2, Thứ 4, Thứ 6' thành danh sách weekday (0=Mon ... 6=Sun).
    Hỗ trợ cả định dạng ngắn như '2,4,6'.
    """
    if not thu_hoc_str:
        return []

    thu_hoc_str = thu_hoc_str.lower()
    tokens = [t.strip() for t in thu_hoc_str.replace(";", ",").split(",") if t.strip()]
    weekdays = set()

    for token in tokens:
        t = token
        if "chủ nhật" in t or "chu nhat" in t or "cn" in t:
            weekdays.add(6)
            continue

        for d, wd in [("2", 0), ("3", 1), ("4", 2), ("5", 3), ("6", 4), ("7", 5)]:
            if d in t:
                weekdays.add(wd)
                break

    return sorted(list(weekdays))

def _fetch_all_known_rooms(cursor):
    sql_rooms = """
        SELECT DISTINCT room_name
        FROM (
            SELECT LTRIM(RTRIM(ISNULL(PHONG_HOC, ''))) AS room_name FROM LOPHOC
            UNION ALL
            SELECT LTRIM(RTRIM(ISNULL(PHONG_HOC, ''))) AS room_name FROM BUOIHOC
        ) AS rooms
        WHERE room_name <> ''
        ORDER BY room_name;
    """
    cursor.execute(sql_rooms)
    return [row[0] for row in cursor.fetchall()]

def _fetch_busy_rooms(cursor, ngay_hoc, gio_bd, gio_kt, exclude_id=None):
    sql_busy = """
        SELECT 
            b.PHONG_HOC,
            l.MA_LOP,
            b.GIO_BAT_DAU,
            b.GIO_KET_THUC
        FROM BUOIHOC b
        LEFT JOIN LOPHOC l ON b.ID_LOP = l.ID_LOP
        WHERE b.NGAY_HOC = ?
          AND b.PHONG_HOC IS NOT NULL
          AND LTRIM(RTRIM(b.PHONG_HOC)) <> ''
          AND NOT (b.GIO_KET_THUC <= ? OR b.GIO_BAT_DAU >= ?)
    """
    params = [ngay_hoc, gio_bd, gio_kt]
    if exclude_id:
        sql_busy += " AND b.ID_BUOI != ?"
        params.append(exclude_id)

    cursor.execute(sql_busy, tuple(params))

    busy_map = {}
    for row in cursor.fetchall():
        if not row[0]:
            continue
        room = row[0].strip()
        info = {
            "ma_lop": row[1],
            "gio_bd": _format_time_value(row[2]),
            "gio_kt": _format_time_value(row[3])
        }
        busy_map.setdefault(room, []).append(info)
    return busy_map

def _find_room_conflict(cursor, phong_hoc, ngay_hoc, gio_bd, gio_kt, exclude_id=None):
    if not phong_hoc:
        return None

    sql_conflict = """
        SELECT TOP 1 
            b.ID_BUOI,
            l.MA_LOP,
            b.GIO_BAT_DAU,
            b.GIO_KET_THUC
        FROM BUOIHOC b
        LEFT JOIN LOPHOC l ON b.ID_LOP = l.ID_LOP
        WHERE LTRIM(RTRIM(b.PHONG_HOC)) = ?
          AND b.NGAY_HOC = ?
          AND NOT (b.GIO_KET_THUC <= ? OR b.GIO_BAT_DAU >= ?)
    """
    params = [phong_hoc, ngay_hoc, gio_bd, gio_kt]
    if exclude_id:
        sql_conflict += " AND b.ID_BUOI != ?"
        params.append(exclude_id)

    cursor.execute(sql_conflict, tuple(params))
    return cursor.fetchone()

def _build_conflict_message(phong_hoc, conflict_row):
    ma_lop = conflict_row[1] or "khác"
    gio_bd = _format_time_value(conflict_row[2])
    gio_kt = _format_time_value(conflict_row[3])
    return f"Phòng {phong_hoc} đã có lớp {ma_lop} từ {gio_bd} đến {gio_kt}. Vui lòng chọn phòng khác."