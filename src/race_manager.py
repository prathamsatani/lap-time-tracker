import cv2
import csv
import time
import os
from typing import Dict, Optional
from .config import config, logger
from .domain import Car, FinishLine
from .detector import ObjectDetector
from .visualizer import Visualizer

class RaceManager:
    """
    Main application controller.
    
    Orchestrates:
    - Input acquisition (Camera/Video)
    - Object Detection (via ObjectDetector)
    - Game State Management (via Car/FinishLine)
    - Visualization (via Visualizer)
    - User Input Handling
    """
    
    def __init__(self):
        """
        Initialize the race manager.
        Sets up the detector, cars, and video input source.
        
        Raises:
            RuntimeError: If video source cannot be opened.
        """
        self.detector = ObjectDetector()
        self.video_writer: Optional[cv2.VideoWriter] = None
        
        # Initialize default race entrants
        self.cars: Dict[str, Car] = {
            "blue-car": Car("Blue Car", (255, 0, 0)),
            "green-car": Car("Green Car", (0, 255, 0)),
        }

        self.finish_line = FinishLine()
        
        # Determine source (File vs Webcam)
        source = config.INPUT_VIDEO_PATH if config.INPUT_VIDEO_PATH else config.CAMERA_INDEX
        logger.info(f"Initializing input source: {source}")
        
        self.cap = cv2.VideoCapture(source)
        
        # Config options specific to webcams (files ignore these)
        if config.INPUT_VIDEO_PATH is None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        
        if not self.cap.isOpened():
            logger.error(f"Could not open input source: {source}")
            raise RuntimeError("Input setup failed - Check camera connection or file path")

    def reset_race(self):
        """Reset all cars' state but keep finish line and global settings."""
        logger.info("[RACE RESET]")
        for car in self.cars.values():
            car.reset()

    def handle_keypress(self, key: int) -> bool:
        """
        Process keyboard input.
        
        Args:
            key (int): The ASCII key code from cv2.waitKey().
            
        Returns:
            bool: True if the application should exit, False otherwise.
        """
        if key == ord('q'):
            return True
        elif key == ord('b') or key == ord('B'):
            self.cars["blue-car"].add_penalty(config.PENALTY_SECONDS)
        elif key == ord('g') or key == ord('G'):
            self.cars["green-car"].add_penalty(config.PENALTY_SECONDS)
        elif key == ord('r') or key == ord('R'):
            self.reset_race()
        elif key == ord('e') or key == ord('E'):
            self.export_csv()
        return False

    def export_csv(self):
        """Exports lap data for all cars to individual CSV files."""
        ts = time.strftime("%Y%m%d_%H%M%S")
        for car in self.cars.values():
            if not car.lap_times:
                continue
                
            fname = f"{car.name.replace(' ', '_')}_{ts}.csv"
            try:
                with open(fname, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Lap", "Time", "Penalty"])
                    for i, (t, p) in enumerate(zip(car.lap_times, car.lap_penalties), 1):
                        writer.writerow([i, f"{t:.2f}", f"{p:.1f}"])
                logger.info(f"📁 Saved {fname}")
            except IOError as e:
                logger.error(f"Failed to write CSV {fname}: {e}")

    def on_mouse(self, event, x, y, flags, param):
        """Mouse callback for setting finish line points."""
        if event == cv2.EVENT_LBUTTONDOWN:
            if not self.finish_line.p1:
                self.finish_line.set_p1((x, y))
                logger.info(f"Finish line P1 set at {x}, {y}")
            else:
                self.finish_line.set_p2((x, y))
                logger.info(f"Finish line P2 set at {x}, {y}")

    def setup_finish_line(self, window_name: str):
        """
        Interactive setup phase for video files.
        Pauses on the first frame to allow the user to draw lines.
        """
        if not self.cap.isOpened(): return
        
        logger.info("Reading first frame for setup...")
        ret, frame = self.cap.read()
        if not ret:
            logger.error("Could not read frame for setup")
            return

        frame = cv2.resize(frame, (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))
        
        logger.info("Waiting for user to draw finish line. Press SPACE to confirm and start.")
        while True:
            display_frame = frame.copy()
            Visualizer.draw_finish_line(display_frame, self.finish_line)
            
            msg = "DRAW FINISH LINE (Click 2 points)"
            if self.finish_line.is_ready():
                 msg = "FINISH LINE READY - Press SPACE to Start"
            
            # Simple UI overlay for setup
            cv2.putText(display_frame, msg, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.imshow(window_name, display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32 and self.finish_line.is_ready(): # Spacebar
                break
            elif key == ord('q'):
                raise KeyboardInterrupt("Setup cancelled")

        # Rewind video to start if we are reading from a file
        if config.INPUT_VIDEO_PATH:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def run(self):
        """
        Main Event Loop.
        Reads frames -> DETECT -> UPDATE -> DRAW -> REPEAT
        """
        window_name = "Race Content"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        # Optional: Set window property for specific use cases
        # cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        cv2.setMouseCallback(window_name, self.on_mouse)

        try:
            # If video file, force setup first
            if config.INPUT_VIDEO_PATH:
                self.setup_finish_line(window_name)

            # Setup Video Writer if requested
            if config.SAVE_OUTPUT_VIDEO:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    self.video_writer = cv2.VideoWriter(
                        config.OUTPUT_VIDEO_PATH, 
                        fourcc, 
                        config.FPS, 
                        (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
                    )
                    if not self.video_writer.isOpened():
                         logger.error("Failed to open video writer.")
                    else:
                         logger.info(f"Recording to {config.OUTPUT_VIDEO_PATH}")
                except Exception as e:
                    logger.error(f"Video writer setup failed: {e}")

            logger.info("Starting race loop. Press 'q' to quit.")
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("End of stream or failed to read")
                    break

                # Resize to standard display size for consistency
                frame = cv2.resize(frame, (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))

                # 1. Detect Objects
                detections = self.detector.detect(frame, list(self.cars.keys()))

                # 2. Update Game State
                for name, (cx, cy, conf, box) in detections.items():
                    self.cars[name].update((cx, cy), self.finish_line)

                # 3. Visualize
                Visualizer.draw_car_boxes(frame, self.cars, detections)
                Visualizer.draw_hud(frame, self.cars, self.finish_line)
                
                # 4. Record Frame (if active)
                if self.video_writer and self.video_writer.isOpened():
                    self.video_writer.write(frame)

                cv2.imshow(window_name, frame)

                key = cv2.waitKey(1) & 0xFF
                if self.handle_keypress(key):
                    break

        except KeyboardInterrupt:
            logger.info("Interrupted by user input (Ctrl+C).")
        except Exception as e:
            logger.error(f"Unexpected critical error during run loop: {e}", exc_info=True)
        finally:
            # Cleanup resources securely
            if self.cap: self.cap.release()
            if self.video_writer: self.video_writer.release()
            cv2.destroyAllWindows()
            logger.info("Race Manager stopped and resources released.")
