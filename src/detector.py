from typing import Dict, List, Tuple, Any
from ultralytics import YOLO
from .config import config, logger
import numpy as np

class ObjectDetector:
    """
    Wrapper around Ultralytics YOLO to handle object detection.
    """
    def __init__(self, model_path: str = config.MODEL_PATH):
        """
        Initialize the detector with a specific YOLO model.
        
        Args:
            model_path (str): Path to the .pt model file.
            
        Raises:
            RuntimeError: If the model fails to load.
        """
        try:
            self.model = YOLO(model_path)
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {e}")
            raise RuntimeError(f"Could not load YOLO model: {e}")

    def detect(self, frame: np.ndarray, vehicle_names: List[str]) -> Dict[str, Tuple[int, int, float, List[int]]]:
        """
        Detects objects in the frame and filters for specific vehicle names.
        
        Args:
            frame (np.ndarray): The BGR image frame from OpenCV.
            vehicle_names (List[str]): List of class names we care about (e.g. 'blue-car').
            
        Returns:
            Dict[str, Tuple]: A dictionary mapping vehicle name to detection details:
                              {name: (center_x, center_y, confidence, [x1, y1, x2, y2])}
        """
        if frame is None or frame.size == 0:
            logger.warning("Empty frame passed to detector")
            return {}

        try:
            # Perform inference
            results = self.model.predict(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)[0]
            
            best: Dict[str, Any] = {}
            
            if not results.boxes:
                return best

            for box, cls, conf in zip(
                results.boxes.xyxy,
                results.boxes.cls,
                results.boxes.conf
            ):
                name = self.model.names[int(cls)]
                if name not in vehicle_names:
                    continue

                # Keep only the highest confidence detection for each class logic:
                # If we haven't seen this car yet, OR this detection is more confident than the last one for this car
                if name not in best or conf > best[name][2]:
                    cx = int((box[0] + box[2]) / 2)
                    cy = int((box[1] + box[3]) / 2)
                    # Store as native python float/int for safety
                    best[name] = (cx, cy, float(conf), box.cpu().numpy())
                    
            return best

        except Exception as e:
            logger.error(f"Detection error: {e}")
            return {}
