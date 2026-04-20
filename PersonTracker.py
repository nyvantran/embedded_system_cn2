import cv2
import numpy as np
import logging
from collections import deque
from DataClass import CameraConfig

import time

from hungarian import *

class Track:
    def __init__(self, track_id, detection):
        self.id = track_id
        self.bbox = detection['bbox']
        self.center = detection['center']
        self.confidence = detection['confidence']
        self.height_pixels = detection['height_pixels']
        self.disappeared = 0
        self.trail = deque([detection['center']], maxlen=30)

    def update(self, detection):
        self.bbox = detection['bbox']
        self.center = detection['center']
        self.confidence = detection['confidence']
        self.height_pixels = detection['height_pixels']
        self.disappeared = 0
        self.trail.append(detection['center'])

class PersonTracker:

    def __init__(self, camera_id: str, config: CameraConfig):
        self.camera_id = camera_id
        self.config = config
        self.tracks = {}
        self.next_id = 1
        self.max_disappeared = 30
        self.max_distance = 150
        self.frame_count = 0
        self.current_fps = 30
        self.colors = [tuple(np.random.randint(64, 255, 3).tolist()) for _ in range(100)]
        self.logger = logging.getLogger(f"Tracker-{camera_id}")

    def get_statistics(self):
        """Get current statistics"""
        active_tracks = sum(1 for track in self.tracks.values() if track.disappeared == 0)
        return {
            'active_tracks': active_tracks,
            'total_tracks': len(self.tracks),
            'total_count': self.next_id - 1,  # = max ID đã gán
        }

    def reset(self):
        """Reset tracker: xóa tất cả track, đặt lại ID về 1."""
        self.tracks.clear()
        self.next_id = 1
        self.frame_count = 0
        self.logger.info(f"Tracker {self.camera_id} has been reset.")

    def update_tracks(self, detections):
        active_track_ids = list(self.tracks.keys())
        if not detections:
            for track_id in active_track_ids:
                self.tracks[track_id].disappeared += 1
            return
        if not self.tracks:
            for det in detections:
                self.tracks[self.next_id] = Track(self.next_id, det)
                self.next_id += 1
            return
        cost_matrix = np.zeros((len(active_track_ids), len(detections)))
        for i, track_id in enumerate(active_track_ids):
            for j, det in enumerate(detections):
                dist = np.linalg.norm(np.array(self.tracks[track_id].center) - np.array(det['center']))
                cost_matrix[i, j] = dist
        row_ind, col_ind, total_cost = hungary(cost_matrix)
        assigned_track_ids = set()
        assigned_det_indices = set()
        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r, c] < self.max_distance:
                track_id = active_track_ids[r]
                self.tracks[track_id].update(detections[c])
                assigned_track_ids.add(track_id)
                assigned_det_indices.add(c)
        unassigned_track_ids = set(active_track_ids) - assigned_track_ids
        for track_id in unassigned_track_ids:
            self.tracks[track_id].disappeared += 1
        new_det_indices = set(range(len(detections))) - assigned_det_indices
        for i in new_det_indices:
            self.tracks[self.next_id] = Track(self.next_id, detections[i])
            self.next_id += 1
        self.tracks = {tid: t for tid, t in self.tracks.items() if t.disappeared <= self.max_disappeared}

    def draw_tracks(self, frame):
        """Vẽ bounding box và ID lên frame."""
        active_tracks = {tid: t for tid, t in self.tracks.items() if t.disappeared == 0}
        for tid, track in active_tracks.items():
            x1, y1, x2, y2 = track.bbox
            color = self.colors[tid % len(self.colors)]
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f'ID: {tid}'
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
