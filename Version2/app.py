from flask import Flask, Response, render_template, jsonify, request
import cv2
import time
import logging
import signal
import sys
import numpy as np
import warnings
from MultiCameraSurveillanceSystem import MultiCameraSurveillanceSystem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WebApp")
warnings.filterwarnings("ignore", category=FutureWarning, message=".*torch.cuda.amp.autocast.*")

app = Flask(__name__, static_folder='static', template_folder='templates')
surveillance = MultiCameraSurveillanceSystem(config_file="cameras.json", batch_size=4)


def generate_mjpeg(camera_id: str):
    """Generator cho MJPEG stream."""
    while True:
        frame = surveillance.get_camera_frame(camera_id)
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                yield (
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
                )
        time.sleep(1 / 25)  # ~25 FPS cho stream


@app.route('/')
def index():
    camera_ids = list(surveillance.cameras.keys())
    return render_template('index.html', camera_ids=camera_ids)


@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    return Response(
        generate_mjpeg(camera_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/api/stats')
def api_stats():
    return jsonify(surveillance.get_all_statistics())


@app.route('/api/count/<camera_id>')
def api_count(camera_id):
    stats = surveillance.get_all_statistics()

    if not stats:
        return jsonify({'status': 'error', 'message': 'No cameras found'}), 404

    if camera_id and camera_id in stats:
        target_stats = stats[camera_id]
    else:
        # Lấy camera đầu tiên nếu không chỉ định hoặc không tìm thấy
        first_key = list(stats.keys())[0]
        target_stats = stats[first_key]

    return jsonify({
        "status": "ok",
        "data": {
            "current_count": target_stats['active_tracks'],
            "total_count": target_stats['total_count']
        }
    })


@app.route('/api/reset', methods=['POST'])
def api_reset():
    surveillance.reset_all()
    return jsonify({'status': 'ok', 'message': 'All trackers have been reset.'})


@app.route('/api/frame/<camera_id>', methods=['POST'])
def api_frame(camera_id):
    """Nhận frame thô từ thiết bị nhúng qua POST request."""
    try:
        # Đọc dữ liệu thô từ Body (dành cho thiết bị gửi image/jpeg trực tiếp)
        frame_data = request.get_data()

        if not frame_data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        # Chuyển dữ liệu binary sang OpenCV frame
        img_array = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        frame = cv2.rotate(frame, 2)
        if frame is None:
            return jsonify({'status': 'error', 'message': 'Invalid image format'}), 400

        # Xử lý frame
        success = surveillance.process_external_frame(camera_id, frame)

        if success:
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'error', 'message': f'Camera {camera_id} not found'}), 404

    except Exception as e:
        logger.error(f"Error processing API frame: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def signal_handler(sig, frame):
    logger.info("Shutting down...")
    surveillance.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    surveillance.start()
    logger.info("Web server starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
