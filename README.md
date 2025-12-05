# Hệ Thống Nhận Diện Khuôn Mặt Cho Điểm Danh

Hệ thống nhận diện khuôn mặt tự động sử dụng YOLOv8 và FaceNet để điểm danh học sinh/sinh viên. Hệ thống được xây dựng bằng Python với giao diện PyQt5 và tích hợp với SQL Server.

## 📋 Mục Lục

- [Tính Năng](#tính-năng)
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt](#cài-đặt)
- [Cấu Hình](#cấu-hình)
- [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Troubleshooting](#troubleshooting)

## ✨ Tính Năng

- **Nhận diện khuôn mặt tự động**: Sử dụng YOLOv8 để phát hiện khuôn mặt và FaceNet để nhận diện
- **Giao diện quản lý**: Quản lý học sinh, giáo viên, môn học, lịch học
- **Điểm danh tự động**: Tự động ghi nhận điểm danh khi nhận diện được khuôn mặt
- **Báo cáo thống kê**: Xem báo cáo điểm danh theo thời gian
- **Huấn luyện mô hình**: Thêm người mới vào hệ thống một cách dễ dàng
- **Đánh giá hiệu suất**: Đánh giá độ chính xác của mô hình detection và recognition

## 🖥️ Yêu Cầu Hệ Thống

### Phần Cứng
- CPU: Intel Core i5 trở lên (khuyến nghị)
- RAM: Tối thiểu 4GB (khuyến nghị 8GB trở lên)
- GPU: NVIDIA GPU với CUDA (tùy chọn, để tăng tốc xử lý)
- Webcam: Camera USB hoặc tích hợp

### Phần Mềm
- **Hệ điều hành**: Windows 10/11, Linux, hoặc macOS
- **Python**: 3.8 trở lên
- **SQL Server**: SQL Server 2014 trở lên (hoặc SQL Server Express)
- **ODBC Driver**: Microsoft ODBC Driver for SQL Server

## 📦 Cài Đặt

### 1. Clone Repository

```bash
git clone <repository-url>
cd AI-facial-recognition-system-for-roll-call
```

### 2. Tạo Virtual Environment (Khuyến nghị)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### 4. Tải Model YOLO

Model YOLO sẽ được tải tự động khi chạy lần đầu. Nếu cần tải thủ công, đảm bảo file `AI_model/weights/yolov8n-face.pt` tồn tại.

### 5. Cấu Hình Database

Chỉnh sửa file `system/model/connectdb.py` với thông tin SQL Server của bạn:

```python
SERVER = 'TEN_SERVER_CUA_BAN'
DATABASE = 'TEN_DATABASE'
USERNAME = 'TEN_USER'
PASSWORD = 'MAT_KHAU'
```

### 6. Tạo Database Schema

Tạo database và các bảng cần thiết trong SQL Server. (Xem phần Database Schema bên dưới)

## ⚙️ Cấu Hình

### Cấu Hình Detection

Chỉnh sửa file `AI_model/Detection/config_detect.py` để thay đổi:
- Confidence threshold
- Số lượng khuôn mặt tối đa
- Đường dẫn model YOLO

### Cấu Hình Recognition

Chỉnh sửa ngưỡng similarity trong các file:
- `AI_model/main_webcam.py`: `SIMILARITY_THRESHOLD = 0.6`
- `system/controller/face_recognize_controller.py`: Tìm và chỉnh sửa threshold

## 📖 Hướng Dẫn Sử Dụng

### 1. Thu Thập Dữ Liệu (Collect Data)

Để thêm người mới vào hệ thống:

```bash
python AI_model/collect_data.py TEN_NGUOI
```

Ví dụ:
```bash
python AI_model/collect_data.py SV001
```

**Lưu ý**: 
- Đưa khuôn mặt vào khung hình
- Hệ thống sẽ tự động chụp khi phát hiện 1 khuôn mặt
- Nhấn 'q' để thoát
- Mặc định thu thập 50 ảnh

### 2. Huấn Luyện Model

Sau khi thu thập dữ liệu, huấn luyện model:

```bash
python AI_model/train_recognizer.py
```

Model sẽ được lưu tại: `system/models/face_prototypes.pth`

**Tính năng**:
- Hỗ trợ incremental training (thêm người mới mà không mất dữ liệu cũ)
- Tự động bỏ qua người đã được huấn luyện
- Sử dụng data augmentation để tăng độ chính xác

### 3. Chạy Hệ Thống Chính

Khởi động giao diện quản lý:

```bash
python system/main.py
```

**Các chức năng trong giao diện**:
- **Đăng nhập**: Đăng nhập vào hệ thống
- **Quản lý học sinh**: Thêm, sửa, xóa thông tin học sinh
- **Quản lý giáo viên**: Quản lý thông tin giáo viên
- **Quản lý môn học**: Quản lý các môn học
- **Lịch học**: Tạo và quản lý lịch học
- **Nhận diện khuôn mặt**: Sử dụng webcam để điểm danh
- **Báo cáo**: Xem báo cáo điểm danh

### 4. Chạy Webcam Demo

Để test nhận diện khuôn mặt trực tiếp:

```bash
cd AI_model
python main_webcam.py
```

**Lưu ý**: 
- Đảm bảo model đã được huấn luyện (`system/models/face_prototypes.pth` tồn tại)
- Nhấn 'q' để thoát

### 5. Đánh Giá Model

Để đánh giá hiệu suất của model:

```bash
python AI_model/evaluate_yolo_facenet.py --dataset dataset --model system/models/face_prototypes.pth --threshold 0.6
```

**Tham số**:
- `--dataset`: Đường dẫn đến thư mục dataset (mặc định: `dataset`)
- `--model`: Đường dẫn đến file model (mặc định: `system/models/face_prototypes.pth`)
- `--threshold`: Ngưỡng similarity (mặc định: 0.6)
- `--max-samples`: Giới hạn số lượng ảnh đánh giá (0 = tất cả)

**Kết quả**:
- File CSV: `eval_detection.csv`, `eval_recognition.csv`
- Confusion Matrix: `confusion_matrix_rec.png`

## 📁 Cấu Trúc Dự Án

```
AI-facial-recognition-system-for-roll-call/
├── AI_model/                    # Module AI và Machine Learning
│   ├── Detection/              # Module phát hiện khuôn mặt (YOLO)
│   │   ├── face_detector.py
│   │   ├── config_detect.py
│   │   └── ...
│   ├── Recognition/            # Module nhận diện khuôn mặt (FaceNet)
│   │   ├── embedding_extractor.py
│   │   ├── torch_recognizer.py
│   │   └── ...
│   ├── utils/                  # Tiện ích
│   │   └── data_augmentor.py
│   ├── weights/                 # Model weights
│   │   └── yolov8n-face.pt
│   ├── collect_data.py         # Thu thập dữ liệu
│   ├── train_recognizer.py     # Huấn luyện model
│   ├── main_webcam.py          # Demo webcam
│   └── evaluate_yolo_facenet.py # Đánh giá model
│
├── system/                      # Hệ thống quản lý
│   ├── controller/             # Controllers (MVC pattern)
│   │   ├── login_controller.py
│   │   ├── home_controller.py
│   │   ├── face_recognize_controller.py
│   │   └── ...
│   ├── model/                  # Models và Services
│   │   ├── connectdb.py       # Kết nối database
│   │   ├── ai_service.py
│   │   ├── auth_service.py
│   │   └── ...
│   ├── ui/                     # Giao diện PyQt5
│   │   ├── login.py
│   │   ├── home.py
│   │   ├── face_recognize.py
│   │   └── ...
│   ├── models/                 # Model đã huấn luyện
│   │   └── face_prototypes.pth
│   └── main.py                 # Entry point
│
├── dataset/                     # Dataset ảnh khuôn mặt
│   ├── person1/
│   ├── person2/
│   └── ...
│
├── video/                       # Video test (tùy chọn)
│
├── requirements.txt             # Dependencies
└── README.md                   # File này
```

## 🗄️ Database Schema

Hệ thống cần các bảng sau trong SQL Server:

- **Users/Teachers**: Thông tin người dùng/giáo viên
- **Students**: Thông tin học sinh
- **Subjects**: Thông tin môn học
- **Schedules**: Lịch học
- **Checkins**: Bản ghi điểm danh

*(Chi tiết schema cần được cung cấp bởi nhóm phát triển hoặc trong tài liệu database)*

## 🔧 Troubleshooting

### Lỗi: Không tìm thấy model YOLO

**Giải pháp**: Model sẽ được tải tự động. Nếu lỗi, kiểm tra kết nối internet hoặc tải thủ công file `yolov8n-face.pt` vào `AI_model/weights/`

### Lỗi: Không kết nối được SQL Server

**Giải pháp**:
1. Kiểm tra SQL Server đang chạy
2. Kiểm tra thông tin kết nối trong `system/model/connectdb.py`
3. Đảm bảo đã cài đặt ODBC Driver for SQL Server
4. Kiểm tra firewall và network

### Lỗi: CUDA out of memory

**Giải pháp**: 
- Giảm batch size hoặc sử dụng CPU
- Model sẽ tự động chuyển sang CPU nếu không có GPU

### Lỗi: ImportError với PyQt5

**Giải pháp**:
```bash
pip install --upgrade PyQt5
```

### Lỗi: Không nhận diện được khuôn mặt

**Giải pháp**:
1. Đảm bảo ánh sáng đủ
2. Khuôn mặt rõ ràng, không bị che khuất
3. Kiểm tra model đã được huấn luyện với dữ liệu của người đó
4. Điều chỉnh `SIMILARITY_THRESHOLD` (giảm để dễ nhận diện hơn, tăng để chặt chẽ hơn)

## 📝 Ghi Chú

- **Ngưỡng Similarity**: Giá trị mặc định 0.6. Có thể điều chỉnh tùy theo độ chính xác mong muốn:
  - Giảm (0.4-0.5): Dễ nhận diện hơn nhưng có thể nhầm lẫn
  - Tăng (0.7-0.8): Chặt chẽ hơn nhưng có thể bỏ sót

- **Data Augmentation**: Hệ thống tự động tăng cường dữ liệu (flip, brightness) khi huấn luyện để tăng độ chính xác

- **Incremental Training**: Hệ thống hỗ trợ thêm người mới mà không cần huấn luyện lại từ đầu

## 👥 Đóng Góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## 📄 License

*(Thêm thông tin license nếu có)*

## 📧 Liên Hệ

*(Thêm thông tin liên hệ nếu cần)*

---

**Lưu ý**: Đảm bảo bạn đã đọc kỹ hướng dẫn trước khi sử dụng. Nếu gặp vấn đề, vui lòng kiểm tra phần Troubleshooting hoặc tạo issue.
