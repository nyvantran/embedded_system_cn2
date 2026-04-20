# Nhật ký cập nhật hệ thống giám sát đa camera (Version 2.1)

## 1. Tích hợp thiết bị nhúng (ESP32-CAM)
- **Cập nhật API nhận frame:** Thay đổi endpoint `/api/frame` thành `/api/frame/<camera_id>` để hỗ trợ nhận dữ liệu hình ảnh thô (raw binary bytes) trực tiếp từ Body của POST request.
- **Tối ưu hóa băng thông:** Loại bỏ yêu cầu `multipart/form-data`, giúp thiết bị nhúng như ESP32 tiết kiệm RAM và xử lý nhanh hơn.
- **Hỗ trợ chế độ API:** Thêm cấu hình `source: "API"` trong `cameras.json`. Khi ở chế độ này, luồng camera sẽ không tự mở webcam mà đợi dữ liệu đẩy vào từ các thiết bị ngoại vi qua HTTP.

## 2. Cải thiện bộ xử lý trung tâm (BatchProcessor)
- **Khắc phục lỗi NMS:** Ép buộc sử dụng `device = 'cpu'` trong `batchprocessor.py` để tránh lỗi xung đột thư viện `torchvision::nms` với CUDA trên môi trường Windows.
- **Chỉnh sửa mục tiêu nhận diện:** Chuyển đổi `Class ID` lọc kết quả từ `19` (con bò) sang `0` (con người) để phù hợp với mục đích giám sát an ninh.

## 3. Nâng cấp kiến trúc luồng (Threading & Coordination)
- **ImprovedCameraWorker:** Tách biệt logic xử lý frame (`process_incoming_frame`) để có thể nhận dữ liệu từ cả nguồn vật lý (camera/file) và nguồn logic (API).
- **MultiCameraSurveillanceSystem:** Thêm phương thức cầu nối `process_external_frame` để điều hướng dữ liệu từ Web API vào đúng luồng xử lý của từng Camera Worker.

## 4. Sửa lỗi và ổn định hệ thống
- **app.py:** 
    - Bổ sung thư viện `numpy`.
    - Sửa lỗi cú pháp trong các route API.
    - Thêm cơ chế xử lý ngoại lệ (Try-Except) để server không bị treo khi nhận dữ liệu lỗi.
- **hungarian.py:** Kiểm tra và đảm bảo thuật toán gán ID hoạt động chính xác với ma trận khoảng cách.

## 5. Hướng dẫn kết nối thiết bị ngoại vi
Thiết bị nhúng (ESP32) có thể gửi ảnh về server qua địa chỉ:
`POST http://<SERVER_IP>:5000/api/frame/<CAMERA_ID>`

**Yêu cầu header:**
- `Content-Type: image/jpeg`

**Cấu hình cameras.json ví dụ:**
```json
{
  "camera_id": "ESP32_FRONT",
  "source": "API",
  "confidence_threshold": 0.4
}
```

---
*Ngày cập nhật: 10/04/2026*
*Người thực hiện: Gemini CLI Assistant*
