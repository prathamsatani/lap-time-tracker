import os
import logging
from dataclasses import dataclass
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@dataclass
class Config:
    """
    Central configuration for the RC Car Lap Time Tracker.
    
    This class holds all configurable parameters for inputs, outputs, model settings,
    camera properties, and race logic. It is initialized once and used across the application.
    """
    
    # Input/Output Configuration
    # If INPUT_VIDEO_PATH is set, it will be used instead of the webcam
    INPUT_VIDEO_PATH: Optional[str] = None  # Path to a video file for processing (overrides webcam)
    SAVE_OUTPUT_VIDEO: bool = False         # Whether to record the processed output to a file
    OUTPUT_VIDEO_PATH: str = "output_race.mp4"  # Filename for the recorded output

    # Model Configuration
    # Using relative path or environment variable is better
    MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", r"./models/best.pt")  # Path to the YOLO model file
    CONFIDENCE_THRESHOLD: float = 0.5  # Minimum confidence score (0-1) for valid detections
    
    # Camera Configuration
    CAMERA_INDEX: int = 0       # OpenCV camera index (usually 0 for default webcam)
    CAMERA_WIDTH: int = 1280    # Requested capture width
    CAMERA_HEIGHT: int = 720    # Requested capture height
    FPS: int = 30               # Requested capture FPS
    
    # Display Configuration
    DISPLAY_WIDTH: int = 1920   # Width to resize frames to for display/processing consistency
    DISPLAY_HEIGHT: int = 1080  # Height to resize frames to
    
    # Race Configuration
    MIN_HISTORY_LENGTH: int = 2      # Minimum history points required before calculating intersection
    LAP_COOLDOWN_SECONDS: float = 2.0 # Minimum time between laps to prevent double-counting
    PENALTY_SECONDS: float = 2.0     # Time penalty added per penalty event
    PENALTY_FLASH_DURATION: float = 0.5 # How long the HUD flashes red after a penalty (in seconds)

config = Config()
logger = logging.getLogger("LapTracker")
