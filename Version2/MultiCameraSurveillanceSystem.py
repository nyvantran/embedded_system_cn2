import json
import logging
import threading
import time
import numpy as np
from ImprovedCameraWorker import ImprovedCameraWorker
from batchprocessor import BatchProcessor
from DataClass import CameraConfig

class MultiCameraSurveillanceSystem:
    def __init__(self, config_file: str = "cameras.json", batch_size: int = 8):
        self.config_file = config_file
        self.batch_size = batch_size
        self.cameras = {}
        self.camera_workers = {}
        self.running = False
        self.logger = logging.getLogger("SurveillanceSystem")
        self.batch_processor = BatchProcessor(batch_size=self.batch_size)
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            for cam_config in config['cameras']:
                self.cameras[cam_config['camera_id']] = CameraConfig(**cam_config)
            self.logger.info(f"Loaded {len(self.cameras)} cameras from {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}. No cameras will be started.", exc_info=True)

    def start(self):
        if not self.cameras:
            self.logger.error("No cameras configured. System will not start.")
            return

        self.logger.info("Starting Multi-Camera Surveillance System")
        self.running = True
        self.batch_processor.start()

        for camera_id, config in self.cameras.items():
            worker = ImprovedCameraWorker(config, self.batch_processor)
            worker.start()
            self.camera_workers[camera_id] = worker

        self.result_thread = threading.Thread(target=self._process_batch_results, daemon=True)
        self.result_thread.start()
        self.logger.info("System started successfully.")

    def _process_batch_results(self):
        while self.running:
            try:
                batch_result = self.batch_processor.get_results()
                if batch_result is None:
                    time.sleep(0.005)
                    continue

                for camera_id, detections in batch_result.camera_results.items():
                    worker = self.camera_workers.get(camera_id)
                    if worker and worker.is_active:
                        frame = worker.get_latest_frame()
                        if frame is not None:
                            worker.process_detections(detections, frame)
            except Exception as e:
                self.logger.error(f"Error processing batch results: {e}", exc_info=True)
                time.sleep(0.01)

    def get_camera_frame(self, camera_id: str):
        """Lấy frame đã xử lý của camera để streaming."""
        worker = self.camera_workers.get(camera_id)
        if worker:
            return worker.get_processed_frame()
        return None

    def get_all_statistics(self):
        """Lấy thống kê của tất cả camera."""
        stats = {}
        for camera_id, worker in self.camera_workers.items():
            stats[camera_id] = worker.get_statistics()
        return stats

    def reset_all(self):
        """Reset tất cả tracker trên mọi camera."""
        for camera_id, worker in self.camera_workers.items():
            worker.reset_tracker()
        self.logger.info("All camera trackers have been reset.")

    def stop(self):
        self.logger.info("Stopping surveillance system...")
        self.running = False
        if self.batch_processor:
            self.batch_processor.stop()
        for worker in self.camera_workers.values():
            worker.stop()
        for worker in self.camera_workers.values():
            if worker.is_alive():
                worker.join(timeout=2.0)
        self.logger.info("Surveillance system stopped.")