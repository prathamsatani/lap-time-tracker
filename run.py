import sys
import os
import argparse

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.race_manager import RaceManager
from src.config import logger, config

def parse_args():
    parser = argparse.ArgumentParser(description="RC Car Lap Time Tracker")
    parser.add_argument("--video", "-v", type=str, help="Path to input video file (overrides webcam)")
    parser.add_argument("--cam", "-c", type=int, help="Camera index (default: 0)")
    parser.add_argument("--save", "-s", action="store_true", help="Save processed video output")
    parser.add_argument("--out", "-o", type=str, help="Path for output video (default: output_race.mp4)")
    parser.add_argument("--model", "-m", type=str, help="Path to custom YOLO model")
    parser.add_argument("--conf", type=float, help="Confidence threshold (default: 0.5)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Update configuration from command line arguments
    if args.video:
        config.INPUT_VIDEO_PATH = args.video
    
    if args.cam is not None:
        config.CAMERA_INDEX = args.cam
        
    if args.save:
        config.SAVE_OUTPUT_VIDEO = True
        
    if args.out:
        config.OUTPUT_VIDEO_PATH = args.out
        
    if args.model:
        config.MODEL_PATH = args.model
        
    if args.conf is not None:
        config.CONFIDENCE_THRESHOLD = args.conf

    try:
        app = RaceManager()
        app.run()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
