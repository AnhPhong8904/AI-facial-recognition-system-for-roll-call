# model/ai_service.py

import subprocess
import sys
import os

class AIService:
    def __init__(self):
        """
        Khởi tạo service quản lý các script AI.
        """
        # Lấy đường dẫn tuyệt đối đến trình thông dịch Python hiện tại
        # (ví dụ: C:\Users\YourUser\miniconda3\envs\ai_env\python.exe)
        # Điều này đảm bảo script được chạy bằng đúng môi trường (environment)
        # mà ứng dụng của bạn đang chạy.
        self.python_executable = sys.executable
        
        # --- CẤU HÌNH ĐƯỜNG DẪN ---
        
        # Lấy đường dẫn thư mục gốc của dự án 
        # (Giả định file này nằm trong 'model/', 
        # và 'model/' nằm trong thư mục gốc)
        try:
            # __file__ là đường dẫn đến file hiện tại (ai_service.py)
            # os.path.abspath(__file__) -> .../project_root/model/ai_service.py
            # os.path.dirname(...) -> .../project_root/model
            # os.path.dirname(os.path.dirname(...)) -> .../project_root
            # Code sửa (đi lùi 3 cấp)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        except NameError:
            # Fallback nếu chạy trong môi trường không có __file__ (ví dụ: interactive)
            base_dir = os.path.abspath(".") 
            
        
        # Trỏ đến file collect_data.py
        # [QUAN TRỌNG] Đảm bảo thư mục 'AI_model' nằm ở thư mục gốc
        self.collect_script_path = os.path.join(base_dir, "AI_model", "collect_data.py")
        
        # Trỏ đến file train_recognizer.py
        self.train_script_path = os.path.join(base_dir, "AI_model", "train_recognizer.py")

        # Kiểm tra xem các file script có tồn tại không
        if not os.path.exists(self.collect_script_path):
            print(f"LỖI (AIService): Không tìm thấy 'collect_data.py' tại: {self.collect_script_path}")
            print("Vui lòng kiểm tra lại cấu trúc thư mục.")
            
        if not os.path.exists(self.train_script_path):
            print(f"LỖI (AIService): Không tìm thấy 'train_recognizer.py' tại: {self.train_script_path}")
            print("Vui lòng kiểm tra lại cấu trúc thư mục.")

    def start_data_collection(self, student_id):
        """
        Gọi script collect_data.py trong một tiến trình riêng biệt.
        
        Args:
            student_id (str): ID (hoặc tên thư mục) của sinh viên (ví dụ: 'SV003').
            
        Returns:
            tuple: (success, message)
        """
        if not os.path.exists(self.collect_script_path):
            return (False, f"Lỗi: Không tìm thấy file script tại\n{self.collect_script_path}")

        # Lệnh này tương đương gõ trong terminal:
        # "C:\path\to\python.exe" "D:\project\AI_model\collect_data.py" "SV003"
        command = [
            self.python_executable,
            self.collect_script_path,
            student_id  # Đây chính là sys.argv[1] mà script kia sẽ nhận được
        ]
        
        print(f"Đang thực thi: {' '.join(command)}")
        
        try:
            # Chạy script và CHỜ nó kết thúc (vì script này mở webcam và cần tương tác)
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            
            # Nếu script chạy thành công (không có exception)
            print("STDOUT (Collect):", result.stdout)
            
            # Kiểm tra xem script có báo lỗi gì trong output của nó không
            if "Loi:" in result.stdout or "Error:" in result.stdout:
                 return (False, f"Script báo lỗi:\n{result.stdout}")
            
            return (True, f"Thu thập dữ liệu thành công cho {student_id}.\n\nOutput:\n{result.stdout}")

        except subprocess.CalledProcessError as e:
            # Lỗi này xảy ra khi script trả về mã lỗi (ví dụ: exit(1) do không mở được cam)
            print(f"Lỗi khi thực thi (Collect): {e.stderr}")
            return (False, f"Script chạy thất bại:\n{e.stderr}")
        except FileNotFoundError:
            return (False, f"Lỗi: Không tìm thấy file script tại {self.collect_script_path} hoặc python executable")
        except Exception as e:
            # Các lỗi chung khác
            return (False, f"Lỗi không xác định: {e}")

    def start_training(self):
        """
        Gọi script train_recognizer.py trong một tiến trình riêng biệt.
        
        Returns:
            tuple: (success, message)
        """
        if not os.path.exists(self.train_script_path):
            return (False, f"Lỗi: Không tìm thấy file script tại\n{self.train_script_path}")
            
        # Lệnh này tương đương gõ trong terminal:
        # "C:\path\to\python.exe" "D:\project\AI_model\train_recognizer.py"
        command = [
            self.python_executable,
            self.train_script_path
        ]
        
        print(f"Đang thực thi: {' '.join(command)}")
        
        try:
            # Chạy script và CHỜ nó kết thúc.
            # Việc này sẽ làm "đơ" giao diện chính trong giây lát.
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            
            print("STDOUT (Train):", result.stdout)

            if "Loi:" in result.stdout or "Error:" in result.stdout:
                 return (False, f"Script báo lỗi:\n{result.stdout}")
                 
            return (True, f"Huấn luyện model thành công.\n\nOutput:\n{result.stdout}")

        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi thực thi (Train): {e.stderr}")
            return (False, f"Script chạy thất bại:\n{e.stderr}")
        except FileNotFoundError:
            return (False, f"Lỗi: Không tìm thấy file script tại {self.train_script_path} hoặc python executable")
        except Exception as e:
            return (False, f"Lỗi không xác định: {e}")