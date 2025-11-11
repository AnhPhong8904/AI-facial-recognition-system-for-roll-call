# AI_model/Recognition/knn_recognizer.py

import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np

class KNNRecognizer:
    def __init__(self, n_neighbors=5, metric='euclidean'):
        """
        Khởi tạo bộ phân loại KNN (từ sklearn) và bộ mã hóa nhãn.
        Chúng ta dùng n_neighbors=5 (hoặc K) để `predict` ổn định,
        nhưng khi check distance, chúng ta sẽ chỉ check 1 hàng xóm gần nhất.
        """
        self.n_neighbors = n_neighbors
        self.metric = metric
        # Khởi tạo model KNN
        self.knn_model = KNeighborsClassifier(
            n_neighbors=self.n_neighbors, 
            metric=self.metric
            # Không dùng weights='distance' ở đây vội
        )
        # Khởi tạo bộ mã hóa nhãn (tên -> số)
        self.label_encoder = LabelEncoder()

    def train(self, embeddings, labels):
        """
        Huấn luyện model KNN và LabelEncoder trên TẤT CẢ các embedding.
        
        Args:
            embeddings (list or np.array): Danh sách các vector đặc trưng.
            labels (list of str): Danh sách các nhãn (tên) tương ứng.
        """
        print("Đang mã hóa nhãn...")
        # Fit LabelEncoder (ví dụ: 'Nguoi_A' -> 0, 'Nguoi_B' -> 1)
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        print(f"Đang huấn luyện KNN với {len(embeddings)} mẫu...")
        # Huấn luyện KNN
        self.knn_model.fit(embeddings, encoded_labels)
        print("Huấn luyện hoàn tất.")

    def predict(self, embedding, distance_threshold=0.9):
        """
        Dự đoán tên từ một vector đặc trưng, sử dụng ngưỡng khoảng cách.
        
        Args:
            embedding (list or np.array): Vector đặc trưng của khuôn mặt cần nhận diện.
            distance_threshold (float): Ngưỡng khoảng cách L2 (Euclidean).
        
        Returns:
            tuple: (tên_dự_đoán, khoảng_cách_nhỏ_nhất)
        """
        if embedding is None:
            return "Unknown", float('inf')

        try:
            # Chuyển embedding về 2D array
            if len(embedding.shape) == 1:
                embedding = embedding.reshape(1, -1)

            # 1. Tìm khoảng cách và chỉ số của 1 HÀNG XÓM GẦN NHẤT
            # Đây là logic cốt lõi của "True KNN"
            distances, indices = self.knn_model.kneighbors(embedding, n_neighbors=1)
            
            min_distance = distances[0][0]
            
            # 2. Kiểm tra với ngưỡng
            if min_distance <= distance_threshold:
                # Nếu OK, LẤY nhãn của hàng xóm đó
                
                # Lấy chỉ số (index) của hàng xóm đó trong TẬP DỮ LIỆU GỐC
                # (Lưu ý: indices[0][0] là chỉ số trong danh sách .fit() )
                # Chúng ta cần lấy nhãn đã mã hóa (encoded label)
                
                # Cách dễ hơn: dùng .predict()
                predicted_encoded_label = self.knn_model.predict(embedding)[0]
                
                # Giải mã nhãn
                name = self.label_encoder.inverse_transform([predicted_encoded_label])[0]
                return name, min_distance
            else:
                # Nếu khoảng cách quá xa -> Không biết
                return "Unknown", min_distance
                
        except Exception as e:
            print(f"Lỗi khi dự đoán: {e}")
            return "Error", 0.0

    def save(self, model_path, le_path):
        """Lưu model KNN và LabelEncoder ra file."""
        print(f"Đang lưu KNN model tới {model_path}")
        with open(model_path, 'wb') as f:
            pickle.dump(self.knn_model, f)
            
        print(f"Đang lưu Label Encoder tới {le_path}")
        with open(le_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)

    def load(self, model_path, le_path):
        """Tải model KNN và LabelEncoder từ file."""
        print(f"Đang tải KNN model từ {model_path}")
        with open(model_path, 'rb') as f:
            self.knn_model = pickle.load(f)
            
        print(f"Đang tải Label Encoder từ {le_path}")
        with open(le_path, 'rb') as f:
            self.label_encoder = pickle.load(f)
        print("Tải model hoàn tất.")