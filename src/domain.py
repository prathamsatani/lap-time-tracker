import time
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import cv2
from .config import logger, config

def now() -> float:
    return time.time()

@dataclass
class Car:
    """
    Represents a single RC car in the race.
    
    Tracks the car's state including position history, lap times, penalties,
    and visual properties like name and color.
    """
    name: str
    color: Tuple[int, int, int]
    position: Optional[Tuple[int, int]] = None
    last_seen: float = 0
    history: deque = field(default_factory=lambda: deque(maxlen=50))

    lap_times: List[float] = field(default_factory=list)
    lap_penalties: List[float] = field(default_factory=list)

    last_cross_time: Optional[float] = None
    best_lap: Optional[float] = None

    current_penalty: float = 0.0
    penalty_flash_until: float = 0.0

    def add_penalty(self, seconds: float = 1.0):
        """
        Adds a time penalty to the current lap.
        
        Args:
            seconds (float): The number of seconds to add to the penalty accumulator.
        """
        self.current_penalty += seconds
        self.penalty_flash_until = now() + config.PENALTY_FLASH_DURATION
        logger.warning(f"⚠️ {self.name} PENALTY +{seconds:.1f}s (Total {self.current_penalty:.1f}s)")

    def reset(self):
        """
        Reset car state (laps, history, penalties) while preserving identity (name, color).
        Used when restarting a race.
        """
        self.position = None
        self.last_seen = 0
        self.history.clear()
        self.lap_times.clear()
        self.lap_penalties.clear()
        self.last_cross_time = None
        self.best_lap = None
        self.current_penalty = 0.0
        self.penalty_flash_until = 0.0
        logger.info(f"🔄 {self.name} RESET")

    def update(self, pos: Tuple[int, int], finish_line: 'FinishLine'):
        """
        Updates the car's position and checks for finish line crossing.
        
        Args:
            pos (Tuple[int, int]): The current (x, y) centroid of the car.
            finish_line (FinishLine): The finish line object to check against.
        """
        self.position = pos
        self.last_seen = now()
        self.history.append(pos)

        # Need at least 2 points to form a line segment for intersection check
        if len(self.history) < config.MIN_HISTORY_LENGTH or not finish_line.is_ready():
            return

        t = now()
        # Debounce: Prevent multiple lap detections within a short cooldown period
        if self.last_cross_time and t - self.last_cross_time < config.LAP_COOLDOWN_SECONDS:
            return

        # Check if the line segment defined by the last two positions crosses the finish line
        if finish_line.crossed(self.history[-2], self.history[-1]):
            if self.last_cross_time:
                # Complete a lap
                raw_lap = t - self.last_cross_time
                lap = raw_lap + self.current_penalty

                self.lap_times.append(lap)
                self.lap_penalties.append(self.current_penalty)

                if not self.best_lap or lap < self.best_lap:
                    self.best_lap = lap

                logger.info(f"🏁 {self.name} LAP: {lap:.2f}s (+{self.current_penalty:.1f}s)")
            else:
                # First crossing starts the timer
                logger.info(f"🚦 {self.name} START!")

            self.last_cross_time = t
            self.current_penalty = 0.0

@dataclass
class FinishLine:
    """
    Represents the start/finish line on the track.
    defined by two points (p1, p2).
    """
    p1: Optional[Tuple[int, int]] = None
    p2: Optional[Tuple[int, int]] = None

    def is_ready(self) -> bool:
        """Returns True if the finish line is fully defined (both points set)."""
        return self.p1 is not None and self.p2 is not None

    def set_p1(self, point: Tuple[int, int]):
        self.p1 = point
        
    def set_p2(self, point: Tuple[int, int]):
        self.p2 = point

    def crossed(self, A: Tuple[int, int], B: Tuple[int, int]) -> bool:
        """
        Determines if the segment AB intersects with the finish line segment P1P2.
        
        Args:
            A (Tuple[int, int]): Previous position.
            B (Tuple[int, int]): Current position.
            
        Returns:
            bool: True if intersected, False otherwise.
        """
        if not self.is_ready():
            return False
            
        C, D = self.p1, self.p2

        def ccw(p1, p2, p3):
            # Returns true if the points p1, p2, p3 are in counter-clockwise order
            return (p3[1]-p1[1])*(p2[0]-p1[0]) > (p2[1]-p1[1])*(p3[0]-p1[0])

        # Standard segment intersection check using counter-clockwise logic
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
