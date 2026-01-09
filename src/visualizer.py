import cv2
import time
from typing import Dict
from .domain import Car, FinishLine, now
from .config import config

class Visualizer:
    """
    Static utility class for drawing UI elements, HUDs, and boxes on frames.
    """
    
    @staticmethod
    def draw_finish_line(frame, finish_line: FinishLine):
        """
        Draws the virtual finish line on the frame.
        
        Args:
            frame: OpenCV image.
            finish_line: FinishLine object.
        """
        if frame is None: return
        
        if finish_line.is_ready():
            cv2.line(frame, finish_line.p1, finish_line.p2, (0, 0, 255), 3)

    @staticmethod
    def draw_car_boxes(frame, cars: Dict[str, Car], detections):
        """
        Draws bounding boxes around detected cars.
        
        Args:
           frame: OpenCV image.
           cars: Dictionary of Car objects (to get colors/names).
           detections: Output from ObjectDetector.
        """
        if frame is None: return

        for name, (cx, cy, conf, box) in detections.items():
            if name not in cars:
                continue
                
            car = cars[name]
            x1, y1, x2, y2 = map(int, box)
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), car.color, 2)
            
            # Draw label background for specific readability
            label = f"{car.name} {conf:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), car.color, -1)
            
            # Draw text
            cv2.putText(frame, label,
                        (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    @staticmethod
    def draw_hud(frame, cars: Dict[str, Car], finish_line: FinishLine):
        """
        Draws the heads-up display with timings and status.
        
        Args:
            frame: OpenCV image.
            cars: Car data source.
            finish_line: Line status source.
        """
        if frame is None: return

        Visualizer.draw_finish_line(frame, finish_line)
        
        # Title
        cv2.putText(frame, "RACE CONTROL",
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        y = 70
        for car in cars.values():
            # Check if car has been seen recently (1.0s threshold)
            active = now() - car.last_seen < 1.0
            color = car.color if active else (120,120,120)  # Grey out if lost

            # Format Current Lap Time
            curr = "--"
            if car.last_cross_time:
                # Calculate current running lap time + penalty
                curr = f"{(now()-car.last_cross_time+car.current_penalty):.1f}s"

            # Format Best Lap Time
            best = f"{car.best_lap:.2f}s" if car.best_lap else "--"

            # Format Previous Laps
            prev_laps = car.lap_times[-3:] # Get last 3 laps
            prev_str = " ".join([f"{t:.1f}s" for t in prev_laps])
            if not prev_str:
                prev_str = "--"

            # Format Penalty State
            penalty = f"+{car.current_penalty:.1f}s"
            
            # Flash RED if recent penalty applied
            if now() < car.penalty_flash_until:
                color = (0,0,255)

            text = f"{car.name} | Curr {curr} | Best {best} | Prev [{prev_str}] | Pen {penalty}"
            
            # Text shadow for readability
            cv2.putText(frame, text, (22, y+2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
            cv2.putText(frame, text, (20, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y += 30

        # Draw controls help footer
        controls = "[B] Blue +2s | [G] Green +2s | [R] Reset | [E] Export | [Q] Quit"
        h = frame.shape[0]
        cv2.putText(frame, controls, (20, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
