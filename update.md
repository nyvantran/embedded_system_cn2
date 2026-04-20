# Chi tiết cập nhật hệ thống (20/04/2026)

Tài liệu này liệt kê các thay đổi chi tiết để hiển thị FPS (đầu vào/đầu ra) và thời gian xử lý của model trên giao diện người dùng.

## 1. File `ImprovedCameraWorker.py`

### Thêm khởi tạo biến tracking trong `__init__` (Khoảng dòng 27-36)
- **Thêm:** Khởi tạo các biến để tính toán FPS đầu vào, FPS đầu ra và lưu trữ thời gian xử lý của model.
```python
# FPS and processing time tracking
self.fps_start_time = time.time()
self.fps_frame_count = 0
self.current_input_fps = 0.0
self.last_model_time = 0.0

# Output FPS tracking
self.output_fps_start_time = time.time()
self.output_fps_frame_count = 0
self.current_output_fps = 0.0
```

### Cập nhật logic tính FPS đầu vào trong `process_incoming_frame` (Khoảng dòng 80-87)
- **Sửa:** Thêm bộ đếm frame và tính toán FPS dựa trên thời gian thực tế nhận frame.

### Cập nhật logic tính FPS đầu ra trong `get_processed_frame` (Khoảng dòng 118-125)
- **Sửa:** Mỗi khi stream (Flask) gọi lấy frame đã xử lý, hệ thống sẽ tính toán tốc độ phản hồi (Output FPS).

### Cập nhật `process_detections` (Khoảng dòng 131)
- **Sửa:** Chấp nhận tham số `model_time` từ hệ thống điều phối để lưu lại thời gian xử lý của batch chứa frame đó.

### Cập nhật `get_statistics` (Khoảng dòng 147-154)
- **Sửa:** Trả thêm các trường `input_fps`, `output_fps`, và `model_time` (đã đổi sang ms) về API.

---

## 2. File `MultiCameraSurveillanceSystem.py`

### Cập nhật luồng xử lý kết quả `_process_batch_results` (Khoảng dòng 62)
- **Sửa:** Lấy `processing_time` từ kết quả của `BatchProcessor` và truyền vào hàm `process_detections` của từng camera worker.
```python
worker.process_detections(detections, frame, batch_result.processing_time)
```

---

## 3. File `templates/index.html`

### Thêm HTML hiển thị trên Overlay (Khoảng dòng 120-130)
- **Thêm:** Các thẻ `div` và `span` để hiển thị Input FPS, Output FPS và Model Time ngay trên mỗi khung hình camera.
```html
<div class="overlay-stat">
    <span class="overlay-label">Input FPS</span>
    <span class="overlay-value" id="overlay-fps-in-{{ cam_id }}">0</span>
</div>
<div class="overlay-stat">
    <span class="overlay-label">Output FPS</span>
    <span class="overlay-value" id="overlay-fps-out-{{ cam_id }}">0</span>
</div>
<div class="overlay-stat">
    <span class="overlay-label">Model Time</span>
    <span class="overlay-value" id="overlay-model-{{ cam_id }}">0 ms</span>
</div>
```

### Cập nhật JavaScript `fetchStats` (Khoảng dòng 165-175)
- **Sửa:** Bổ sung logic lấy dữ liệu từ API `/api/stats` và gán vào các thẻ HTML tương ứng thông qua ID.
- **Chi tiết:** Cập nhật `overlay-fps-in`, `overlay-fps-out` và `overlay-model`.

---

## Tóm tắt thông số mới:
- **Input FPS:** Tốc độ camera/thiết bị gửi frame về server.
- **Output FPS:** Tốc độ server gửi frame đã xử lý lên trình duyệt.
- **Model Time:** Thời gian model YOLO chạy inference cho một batch (ms).
