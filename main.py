from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
import cv2
import numpy as np
import asyncio
from collections import deque
from datetime import datetime
import time

app = FastAPI()

# High performance frame buffer
frame_buffer = deque(maxlen=5)
latest_frame = None
frame_ready = asyncio.Event()
status_message = {"message": "Running", "value": 0}

# Statistics
stats = {
    "fps": 0,
    "frame_count": 0,
    "last_time": time.time(),
    "avg_size": 0,
    "total_size": 0
}


@app.post("/upload_frame")
async def upload_frame(request: Request):
    """Ultra-fast frame receiver"""
    global latest_frame, stats

    try:
        # Read frame data
        frame_data = await request.body()

        if len(frame_data) < 100:
            return {"status": "error"}

        # Update stats
        stats["frame_count"] += 1
        stats["total_size"] += len(frame_data)

        # Calculate FPS
        current_time = time.time()
        elapsed = current_time - stats["last_time"]
        if elapsed >= 1.0:
            stats["fps"] = stats["frame_count"] / elapsed
            stats["avg_size"] = stats["total_size"] / stats["frame_count"]
            stats["frame_count"] = 0
            stats["total_size"] = 0
            stats["last_time"] = current_time

        # Decode in background (non-blocking)
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is not None:
            latest_frame = frame
            frame_buffer.append(frame)
            frame_ready.set()
            return {"ok": 1}

        return {"status": "decode_error"}

    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.get("/get_status")
async def get_status():
    """Fast status endpoint"""
    return status_message


@app.post("/set_status")
async def set_status(message: str = "OK", value: int = 0):
    """Update status"""
    global status_message
    status_message = {"message": message, "value": value}
    return {"ok": 1}


async def generate_frames():
    """High-speed frame generator"""
    global latest_frame

    # JPEG encoding parameters for speed
    encode_params = [
        cv2.IMWRITE_JPEG_QUALITY, 75,
        cv2.IMWRITE_JPEG_PROGRESSIVE, 0,
        cv2.IMWRITE_JPEG_OPTIMIZE, 0
    ]

    while True:
        if latest_frame is not None:
            try:
                # Fast JPEG encoding
                ret, jpeg = cv2.imencode('.jpg', latest_frame, encode_params)

                if ret:
                    frame_bytes = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' +
                           frame_bytes + b'\r\n')

            except Exception as e:
                print(f"Encode error: {e}")

        # Minimal delay for max FPS
        await asyncio.sleep(0.01)  # 100 FPS theoretical max


@app.get("/video_feed")
async def video_feed():
    """Video stream endpoint"""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/stats")
async def get_stats():
    """Performance statistics"""
    return {
        "fps": round(stats["fps"], 2),
        "avg_frame_size_kb": round(stats["avg_size"] / 1024, 2),
        "has_frame": latest_frame is not None,
        "buffer_size": len(frame_buffer)
    }


@app.get("/")
async def index():
    """Optimized web interface"""
    html_path = "templates/index.html"
    return HTMLResponse(content=open(html_path, "rb").read())


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting High-Performance FastAPI Server")
    print("📊 Access dashboard at: http://localhost:8000")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning",  # Reduce logging overhead
        access_log=False  # Disable access logs for speed
    )
