from flask import Flask, Response, render_template, jsonify, request
import cv2
import time
import logging
import signal
import sys
from MultiCameraSurveillanceSystem import MultiCameraSurveillanceSystem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WebApp")
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

@app.route('/api/reset', methods=['POST'])
def api_reset():
    surveillance.reset_all()
    return jsonify({'status': 'ok', 'message': 'All trackers have been reset.'})

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