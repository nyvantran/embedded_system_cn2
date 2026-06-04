## tổng quan: (duy)

### 1. giời thiệu đề tài

**bối cảnh và đặt vấn đề**: trong đây có phạm vi, giả định
**mục tiêu đề tài**:

### 2. cơ sở lý thuyết

tự chém

## thiết kế hệ thống: (duy)

### 1. sơ đồ tổng quan luồng làm việc:

### 2. kiến trúc phần cứng, phần mền

- **kiến trúc phần cứng**: giới thiệu phần cứng, chức năng của phần cứng, sơ đồ kết nối phần cứng

- **kiến trúc phần mền**: luồng hoạt động của phần mền, api giao tiếp

## triển khai hệ thống: (tao )

chụp kết quả, đánh giá hiệu suất

## kết luận (tao)

Dựa trên kết quả thiết kế, phát triển và thử nghiệm thực tế, dự án đã xây dựng thành công **Hệ thống giám sát đa camera thời gian thực tích hợp trí tuệ nhân tạo (YOLOv5) và theo dõi đối tượng (Hungarian Algorithm) kết hợp các thiết bị nhúng IoT (ESP32-CAM & ESP32-C3)**. Dưới đây là tóm tắt các kết quả đạt được, đóng góp kỹ thuật, ưu nhược điểm và định hướng phát triển tương lai của hệ thống.

### 1. Các kết quả đã đạt được
* **Kiến trúc phân tán tối ưu (Edge-to-Server)**: Thiết lập thành công mô hình biên-trung-tâm. Các node camera nhúng (ESP32-CAM trong [Arduino.ino](file:///D:/Project/Embedded_system/CN2/Arduino/Arduino.ino)) thực hiện thu thập và truyền tải dòng ảnh chất lượng HVGA qua HTTP POST với kết nối tái sử dụng (TCP Keep-Alive) giúp tối ưu hóa băng thông mạng.
* **Xử lý Batch thông minh (Batch Inference)**: Máy chủ trung tâm (Flask trong [app.py](file:///D:/Project/Embedded_system/CN2/app.py)) sử dụng cơ chế hàng đợi [batchprocessor.py](file:///D:/Project/Embedded_system/CN2/batchprocessor.py) để gộp các khung hình từ nhiều camera khác nhau trước khi đưa vào mô hình YOLOv5. Điều này giúp tối ưu hóa hiệu suất tính toán song song trên GPU, giảm thiểu độ trễ suy luận đáng kể so với việc xử lý tuần tự từng camera độc lập.
* **Theo dõi đối tượng liên tục (Multi-Object Tracking - MOT)**: Xây dựng thành công bộ theo dõi [PersonTracker.py](file:///D:/Project/Embedded_system/CN2/PersonTracker.py) dựa trên thuật toán Hungarian tự thiết kế ([hungarian.py](file:///D:/Project/Embedded_system/CN2/hungarian.py)) giải quyết bài toán phân công lưỡng phân (Bipartite Matching) dựa trên khoảng cách centroid. Hệ thống có khả năng duy trì định danh (ID) ổn định cho các đối tượng, vẽ vệt di chuyển (trails) trực quan và quản lý vòng đời đối tượng (chấp nhận mất dấu tạm thời tới 30 khung hình).
* **Trực quan hóa và Tương tác trực tiếp**: Thiết kế bảng điều khiển Web Dashboard hiện đại, mượt mà ([index.html](file:///D:/Project/Embedded_system/CN2/templates/index.html) và [style.css](file:///D:/Project/Embedded_system/CN2/static/style.css)) với giao diện Glassmorphism thời thượng. Hiển thị trực quan chỉ số Input/Output FPS và thời gian suy luận (Model Time) riêng biệt cho từng camera cùng nút reset bộ đếm thời gian thực.
* **Tích hợp IoT Phản hồi**: Sử dụng ESP32-C3 kết nối qua giao tiếp I2C điều khiển màn hình LCD 20x4 ([Arduino1.ino](file:///D:/Project/Embedded_system/CN2/Arduino1/Arduino1.ino)), tự động truy vấn dữ liệu từ REST API của máy chủ để hiển thị các số liệu thống kê tại chỗ (số lượng đối tượng hiện tại, tổng tích lũy) một cách trực quan, hoàn thiện luồng IoT khép kín.

### 2. Đóng góp về mặt giải pháp kỹ thuật nổi bật
* **Tối ưu hóa phần cứng giới hạn (ESP32-CAM)**: Bằng cách tắt bớt các tính năng xử lý hình ảnh không cần thiết trên cảm biến, sử dụng Double Buffering trong PSRAM, và thiết lập mức chất lượng JPEG hợp lý (Quality: 20), thiết bị nhúng đạt được tốc độ truyền tải khung hình cao (~20 FPS) ổn định qua kết nối WiFi dân dụng.
* **Xử lý đa luồng & Hàng đợi bất đồng bộ**: Kiến trúc máy chủ Flask kết hợp các [ImprovedCameraWorker.py](file:///D:/Project/Embedded_system/CN2/ImprovedCameraWorker.py) chạy đa luồng độc lập, giao tiếp thông qua các thread-safe Queue giúp tránh tình trạng nghẽn cổ chai (bottleneck) khi một hoặc nhiều camera gặp sự cố mạng hoặc gián đoạn kết nối.
* **Giải thuật phân loại linh hoạt**: Mặc dù cấu hình hiện tại đang được tối ưu hóa cho đối tượng cụ thể (ví dụ: lớp 19 trong tập dữ liệu COCO - thích hợp cho các ứng dụng nông nghiệp thông minh như theo dõi gia súc/bò, hoặc có thể dễ dàng đổi sang lớp 0 để nhận diện người), hệ thống đã chứng minh tính đa dụng cao, dễ cấu hình ngưỡng tin cậy và kích thước khung hình thông qua file cấu hình [cameras.json](file:///D:/Project/Embedded_system/CN2/cameras.json).

### 3. Đánh giá ưu điểm và Hạn chế

#### Ưu điểm:
* Tốc độ xử lý cao, tận dụng tối đa phần cứng nhờ cơ chế Batch Processing trên GPU.
* Cơ chế theo dõi đối tượng (Tracking) hoạt động ổn định trong điều kiện chuyển động vừa phải, có khả năng bù đắp mất khung hình ngắn hạn.
* Dashboard có tính thẩm mỹ cao, cập nhật trạng thái thời gian thực thông qua AJAX API mượt mà.
* Khả năng chịu lỗi tốt (Fault tolerance): Tự động phát hiện trạng thái ONLINE/OFFLINE của từng camera và cập nhật trạng thái kết nối tức thì.

#### Hạn chế:
* **Mất dấu do vật cản (Occlusion)**: Giải thuật tracking hiện tại mới chỉ dựa trên khoảng cách hình học centroid (Euclid), chưa kết hợp đặc trưng ngoại hình (Appearance Re-ID) hoặc dự báo động học (Kalman Filter) nên có thể bị nhầm lẫn ID khi hai đối tượng che khuất hoặc đi giao cắt quá gần nhau.
* **Phụ thuộc vào băng thông WiFi**: Độ trễ truyền dòng ảnh từ ESP32-CAM phụ thuộc nhiều vào chất lượng và sự ổn định của sóng WiFi tại khu vực triển khai.
* **Bảo mật**: Các luồng truyền nhận ảnh (POST) và truy vấn dữ liệu (GET) chưa được mã hóa hoặc xác thực bảo mật.

### 4. Định hướng phát triển tương lai
* **Nâng cấp giải thuật Tracking**: Tích hợp bộ lọc Kalman (như thuật toán SORT) hoặc kết hợp trích xuất đặc trưng sâu (DeepSORT) để tăng tính ổn định của ID khi đối tượng bị che khuất.
* **Tối ưu hóa mô hình**: Chuyển đổi mô hình YOLOv5 sang định dạng TensorRT hoặc ONNX để gia tăng thêm tốc độ suy luận (inference speed) trên các phần cứng biên chuyên dụng.
* **Tích hợp các giao thức IoT thời gian thực**: Thay thế phương pháp HTTP Polling/POST truyền thống bằng giao thức MQTT hoặc WebSockets nhằm giảm tải tiêu thụ tài nguyên mạng và tăng tốc phản hồi cho thiết bị nhúng ESP32-C3.
* **Tăng cường bảo mật**: Triển khai giao thức HTTPS, xác thực JWT cho thiết bị gửi ảnh và hệ thống LCD giám sát biên để bảo vệ an toàn luồng dữ liệu tránh các cuộc tấn công giả mạo. 





