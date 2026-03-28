import cv2
import time
import numpy as np
import asyncio
from collections import deque
from fastapi import Request


class FrameService:
    def __init__(self, buffer_size=5):
        self.frame_buffer = deque(maxlen=buffer_size)
        self.frame = None
        self.lastest_frame = None
        self.frame_ready = asyncio.Event()
        self.stats = {
            "fps": 0,
            "frame_count": 0,
            "last_time": time.time(),
            "avg_size": 0,
            "total_size": 0
        }

    def get_frame(self):
        return self.lastest_frame

    async def receive_frame(self, request: Request):
        try:
            # Read frame data
            frame_data = await request.body()
            if len(frame_data) < 100:
                return {"status": "error"}
                # Decode in background (non-blocking)
                # Update stats
            self.stats["frame_count"] += 1
            self.stats["total_size"] += len(frame_data)

            # Calculate FPS
            current_time = time.time()
            elapsed = current_time - self.stats["last_time"]
            if elapsed >= 1.0:
                self.stats["fps"] = self.stats["frame_count"] / elapsed
                self.stats["avg_size"] = self.stats["total_size"] / self.stats["frame_count"]
                self.stats["frame_count"] = 0
                self.stats["total_size"] = 0
                self.stats["last_time"] = current_time
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                self.frame = frame
                self.lastest_frame = frame.copy()
                self.frame_buffer.append(frame)
                self.frame_ready.set()
                return {"ok": 1}

            return {"status": "decode_error"}

        except Exception:
            print("Error reading frame data")
            return {"status": "error"}

    async def stream_frame(self):
        encode_params = [
            cv2.IMWRITE_JPEG_QUALITY, 75,
            cv2.IMWRITE_JPEG_PROGRESSIVE, 0,
            cv2.IMWRITE_JPEG_OPTIMIZE, 0
        ]
        while True:
            if self.frame is not None:
                try:
                    # Fast JPEG encoding
                    ret, jpeg = cv2.imencode('.jpg', self.frame, encode_params)
                    if ret:
                        frame_bytes = jpeg.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' +
                               frame_bytes + b'\r\n')

                except Exception as e:
                    print(f"Encode error: {e}")

            # Minimal delay for max FPS
            await asyncio.sleep(0.01)  # 100 FPS theoretical max

    def get_stats(self):
        return {
            "fps": round(self.stats["fps"], 2),
            "avg_frame_size_kb": round(self.stats["avg_size"] / 1024, 2),
            "has_frame": self.frame is not None,
            "buffer_size": len(self.frame_buffer)
        }


frame_service = FrameService()
