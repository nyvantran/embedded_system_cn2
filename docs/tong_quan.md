# TỔNG QUAN ĐỀ TÀI

## 1. Giới thiệu đề tài

### Bối cảnh và đặt vấn đề

*   **Bối cảnh:**
    Trong kỷ nguyên chuyển đổi số và phát triển đô thị thông minh, việc giám sát an ninh và quản lý lưu lượng người ra vào tại các khu vực công cộng, tòa nhà văn phòng, nhà xưởng, hoặc các trung tâm thương mại đã trở thành một nhu cầu thiết yếu. Các phương pháp giám sát truyền thống chủ yếu dựa trên sức người hoặc các hệ thống camera ghi hình thụ động (Closed-Circuit Television - CCTV) không có khả năng tự động phân tích hành vi hoặc đếm số lượng người theo thời gian thực. Sự phát triển mạnh mẽ của Trí tuệ Nhân tạo (AI), đặc biệt là Thị giác Máy tính (Computer Vision) kết hợp với các thiết bị Internet of Things (IoT), đã mở ra hướng đi mới cho việc tự động hóa quá trình giám sát này với chi phí thấp và hiệu quả cao.

*   **Đặt vấn đề:**
    Các hệ thống giám sát thông minh thương mại hiện nay thường yêu cầu các dòng camera IP cao cấp có tích hợp sẵn chip xử lý AI tại biên (Edge AI) hoặc yêu cầu hệ thống máy chủ xử lý cực kỳ mạnh mẽ để giải mã và phân tích từng luồng video riêng lẻ. Điều này dẫn đến chi phí lắp đặt, vận hành rất cao và thiếu tính linh hoạt khi cần mở rộng quy mô.
    Từ đó, yêu cầu đặt ra là cần xây dựng một giải pháp kiến trúc phân tán: sử dụng các thiết bị nhúng giá thành rẻ, tiêu thụ năng lượng thấp (như ESP32-CAM) chỉ thực hiện nhiệm vụ thu thập hình ảnh và truyền tải dữ liệu; kết hợp với một máy chủ xử lý trung tâm tận dụng công nghệ tính toán song song (Batch Processing trên GPU) để chạy mô hình học sâu nhận diện và theo vết đối tượng. Đồng thời, cần có các thiết bị đầu cuối hiển thị trực quan (như ESP32-C3 kết hợp màn hình LCD) đặt tại các chốt kiểm soát để nhân viên giám sát có thể nắm bắt thông tin tức thời mà không cần liên tục theo dõi màn hình máy tính.

*   **Phạm vi nghiên cứu:**
    *   **Phần cứng:** Thử nghiệm và triển khai trên thiết bị nhúng thu nhận hình ảnh ESP32-CAM và thiết bị hiển thị đầu cuối ESP32-C3 kết hợp màn hình LCD 20x4 qua giao tiếp I2C.
    *   **Phần phần mềm & AI:** Xây dựng máy chủ Flask nhận luồng ảnh qua giao thức HTTP POST dạng nhị phân JPEG; áp dụng mô hình YOLOv5m để phát hiện đối tượng con người (lớp `person` trong tập dữ liệu COCO); xây dựng và tối ưu thuật toán theo vết đối tượng (Multi-Object Tracking) sử dụng thuật toán Hungarian dựa trên khoảng cách Euclidean của tâm các hộp giới hạn.
    *   **Môi trường:** Giám sát trong không gian có góc nhìn camera cố định (phòng học, sảnh ra vào, hành lang).

*   **Giả định:**
    1.  **Độ ổn định mạng:** Kết nối mạng không dây (WiFi) tại khu vực lắp đặt thiết bị nhúng đủ ổn định, băng thông tối thiểu đảm bảo truyền tải hình ảnh định dạng JPEG (HVGA - 480x320) liên tục với tốc độ từ 15-20 FPS.
    2.  **Điều kiện ánh sáng và lắp đặt:** Camera được lắp đặt ở góc nhìn cố định, có độ cao từ 2.5m - 3.5m hướng xuống khu vực giám sát để giảm thiểu hiện tượng che khuất (occlusion). Cường độ ánh sáng môi trường ở mức cơ bản để cảm biến camera thu nhận rõ nét hình ảnh.
    3.  **Đối tượng giám sát:** Đối tượng mục tiêu cần đếm và theo vết là con người di chuyển trong vùng quét của camera. Các đối tượng không phải con người sẽ bị mô hình lọc bỏ.

### Mục tiêu đề tài

1.  **Xây dựng giải pháp phần cứng nhúng giá rẻ:** Thiết kế và lập trình thành công thiết bị thu hình ESP32-CAM gửi luồng ảnh nhị phân hiệu năng cao và thiết bị ESP32-C3 truy xuất API để hiển thị số lượng người trực tiếp lên màn hình LCD 20x4 thông qua I2C.
2.  **Tối ưu hóa hiệu năng truyền tải và xử lý phía máy chủ:** Thiết lập máy chủ Flask có khả năng tiếp nhận đồng thời nhiều luồng dữ liệu camera nhị phân và tối ưu hóa xử lý suy diễn AI bằng cơ chế xử lý theo lô (Batch Processing) trên GPU CUDA để giảm thiểu độ trễ.
3.  **Phát hiện và theo vết đối tượng chính xác:** Áp dụng mô hình YOLOv5m kết hợp với thuật toán gán nhãn tối ưu Hungarian để tự động nhận diện và gán ID duy nhất cho từng người di chuyển qua khung hình, hạn chế tối đa việc đếm trùng hoặc mất vết khi đối tượng bị che khuất tạm thời.
4.  **Xây dựng giao diện giám sát trực quan (Dashboard):** Thiết kế giao diện Web Dashboard hiển thị thời gian thực luồng video đã vẽ hộp nhận diện (Bounding Box) kèm ID, hiển thị các thông số hiệu năng cốt lõi (Input/Output FPS, thời gian xử lý của mô hình AI - Model Time) để người vận hành dễ dàng theo dõi trạng thái hệ thống.

---

## 2. Cơ sở lý thuyết

### 2.1. Hệ thống nhúng và Internet of Things (IoT)
*   **Vi điều khiển ESP32-CAM:**
    Là một board mạch phát triển nhỏ gọn dựa trên chip ESP32 của hãng Espressif, tích hợp camera OV2640 và khe cắm thẻ nhớ MicroSD. ESP32 cung cấp kết nối WiFi và Bluetooth chuẩn, tốc độ xung nhịp lên tới 240MHz. Điểm cốt lõi là việc sử dụng PSRAM (External SPI RAM) cho phép lưu trữ và xử lý các khung hình ảnh lớn tạm thời trong bộ nhớ trước khi truyền tải qua mạng.
*   **Vi điều khiển ESP32-C3:**
    Là vi điều khiển thế hệ mới sử dụng kiến trúc mã nguồn mở RISC-V 32-bit của Espressif. Thiết bị này hỗ trợ kết nối WiFi và Bluetooth 5 (LE) với mức tiêu thụ năng lượng thấp và giá thành rất rẻ, cực kỳ phù hợp làm thiết bị thu nhận dữ liệu trung gian và điều khiển màn hình hiển thị phụ trợ thông qua giao tiếp I2C.
*   **Giao thức truyền tải HTTP và dữ liệu nhị phân:**
    Để tối ưu hóa tốc độ và giảm dung lượng gói tin truyền tải từ ESP32-CAM lên server, thay vì mã hóa ảnh sang chuỗi Base64 (làm tăng kích thước gói tin khoảng 33%), hệ thống sử dụng phương thức truyền tải nhị phân thô (`application/octet-stream` hoặc truyền trực tiếp dữ liệu nhị phân của ảnh JPEG thông qua HTTP POST). Điều này giúp giảm thiểu tải xử lý CPU trên chip nhúng và giảm dung lượng gói tin truyền đi.
*   **Giao tiếp I2C và màn hình LCD:**
    Giao tiếp Inter-Integrated Circuit (I2C) là giao thức truyền thông nối tiếp đồng bộ, sử dụng hai dây: SDA (dữ liệu) và SCL (xung nhịp). Hệ thống sử dụng I2C để tối giản số lượng dây kết nối từ ESP32-C3 tới màn hình LCD 20x4 (chỉ cần 4 dây gồm VCC, GND, SDA, SCL thay vì 6-12 dây ở chế độ song song thông thường), giúp thiết bị nhỏ gọn và dễ lắp đặt.

### 2.2. Thị giác máy tính và Phát hiện đối tượng (Object Detection)
*   **Khái niệm phát hiện đối tượng:**
    Là một nhiệm vụ trong thị giác máy tính nhằm xác định vị trí của các đối tượng thuộc các lớp mục tiêu trong ảnh hoặc video và vẽ một khung giới hạn (Bounding Box) xung quanh chúng, kèm theo độ tin cậy (Confidence Score).
*   **Mô hình YOLOv5 (You Only Look Once):**
    YOLOv5 là một trong những kiến trúc phát hiện đối tượng phổ biến nhất nhờ tốc độ xử lý nhanh và độ chính xác cao. YOLO giải quyết bài toán phát hiện đối tượng như một bài toán hồi quy duy nhất, dự đoán trực tiếp tọa độ hộp giới hạn và xác suất lớp từ toàn bộ hình ảnh trong một lần lan truyền tiến (single forward pass).
    *   **Kiến trúc:** Gồm 3 phần chính: Backbone (sử dụng CSPDarknet53 để trích xuất đặc trưng), Neck (sử dụng PANet để kết hợp các đặc trưng ở các tỷ lệ khác nhau), và Head (thực hiện dự đoán neo - anchor prediction).
    *   **YOLOv5m (Medium):** Phiên bản kích thước trung bình, cân bằng hoàn hảo giữa độ chính xác nhận diện và tốc độ suy diễn (Inference Time), thích hợp chạy trên các máy chủ có hỗ trợ tăng tốc GPU.

### 2.3. Theo vết đa đối tượng (Multi-Object Tracking - MOT)
*   **Nguyên lý Detection-based Tracking:**
    Hệ thống theo vết đối tượng dựa trên kết quả phát hiện của mô hình AI ở từng khung hình. Ở mỗi khung hình mới, mô hình YOLOv5 sẽ cung cấp danh sách các hộp giới hạn của đối tượng. Thuật toán tracking sẽ thực hiện nhiệm vụ liên kết các hộp giới hạn ở khung hình hiện tại với danh sách các đối tượng đang được theo dõi (Tracks) từ các khung hình trước đó.
*   **Thuật toán Hungarian (Kuhn-Munkres):**
    Là một thuật toán tối ưu hóa tổ hợp giải bài toán phân công (Assignment Problem) trong thời gian đa thức $O(V^3)$.
    *   Trong bài toán theo vết, ta xây dựng một ma trận chi phí (Cost Matrix) kích thước $M \times N$, với $M$ là số lượng vết cũ đang theo dõi và $N$ là số lượng phát hiện mới trong khung hình hiện tại.
    *   Chi phí (Cost) giữa vết thứ $i$ và phát hiện thứ $j$ được tính bằng khoảng cách hình học Euclidean giữa tâm của hộp giới hạn cũ và tâm hộp giới hạn mới:
        $$d = \sqrt{(x_{track} - x_{det})^2 + (y_{track} - y_{det})^2}$$
    *   Thuật toán Hungarian sẽ tìm ra cách ghép cặp giữa vết cũ và phát hiện mới sao cho tổng khoảng cách ghép cặp là nhỏ nhất. Nếu khoảng cách ghép cặp vượt quá ngưỡng tối đa (`max_distance = 150`), mối liên kết đó sẽ bị loại bỏ, phát hiện mới sẽ được coi là một đối tượng mới hoàn toàn và được cấp một ID mới.
*   **Quản lý trạng thái vòng đời của Vết (Track Lifecycle Management):**
    *   **Khởi tạo (Initialization):** Khi một phát hiện mới không được khớp với bất kỳ vết cũ nào, hệ thống sẽ tạo một vết mới (`Track`) với ID tăng dần.
    *   **Cập nhật (Update):** Khi phát hiện được ghép cặp thành công với vết cũ, tọa độ hộp giới hạn, tâm đối tượng sẽ được cập nhật, đồng thời bộ đếm số khung hình biến mất (`disappeared`) được đặt lại về 0.
    *   **Xóa bỏ (Deletion):** Khi một vết không được ghép cặp với bất kỳ phát hiện nào trong khung hình hiện tại, bộ đếm `disappeared` sẽ tăng lên 1. Nếu đối tượng không xuất hiện lại trong vòng `max_disappeared = 30` khung hình liên tiếp, vết đó sẽ bị xóa khỏi bộ nhớ hệ thống để giải phóng tài nguyên.

### 2.4. Kỹ thuật xử lý song song và truyền luồng video trên Web
*   **Xử lý song song theo lô (Batch Processing):**
    Việc nạp từng khung hình từ các camera đơn lẻ lên GPU để chạy suy diễn sẽ gây lãng phí tài nguyên tính toán của card đồ họa và làm tăng độ trễ tổng thể do băng thông truyền dữ liệu giữa CPU và GPU. Bằng cách gom nhiều khung hình từ các camera khác nhau vào một lô (Batch) có kích thước cố định (`batch_size = 4` hoặc `8`) và đưa vào GPU xử lý đồng thời, hệ thống tận dụng tối đa kiến trúc phần cứng song song của CUDA, giúp nâng cao đáng kể thông lượng (throughput) và giảm thời gian suy diễn trung bình trên mỗi camera.
*   **MJPEG (Motion JPEG) Streaming:**
    Là một định dạng nén video trong đó mỗi khung hình của video được nén riêng lẻ dưới dạng hình ảnh JPEG. Máy chủ Flask sử dụng giao thức truyền luồng với header `multipart/x-mixed-replace; boundary=frame` để liên tục đẩy các khung hình JPEG đã vẽ hộp nhận diện và ID xuống trình duyệt của khách hàng mà không cần giải pháp phát trình phát video phức tạp ở phía client.
