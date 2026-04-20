import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class FrameBatch:
    camera_frames: Dict[str, np.ndarray]
    camera_metadata: Dict[str, Dict]
    batch_id: int
    timestamp: float

@dataclass
class BatchResult:
    batch_id: int
    camera_results: Dict[str, List[Dict]]
    processing_time: float
    timestamp: float

@dataclass
class DetectionResult:
    camera_id: str
    frame_id: int
    timestamp: float
    detections: List[Dict]
    frame: np.ndarray = None


@dataclass
class CameraConfig:
    camera_id: str
    source: str
    position: str
    enable_recording: bool = True
    recording_path: str = None
    confidence_threshold: float = 0.5
    loop_video: bool = True
    frame_height: int = 480
    frame_width: int = 640
    acreage: int = 50
