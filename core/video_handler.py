"""Video handling utilities."""

from typing import Generator, Tuple

import cv2
import numpy as np


class VideoHandler:
    """Handle video frame extraction."""

    @staticmethod
    def get_video_info(filepath: str) -> Tuple[int, int, float, int]:
        """
        Get video information.
        Returns (width, height, fps, frame_count).
        """
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {filepath}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        cap.release()
        return width, height, fps, frame_count

    @staticmethod
    def frames_generator(filepath: str) -> Generator[np.ndarray, None, None]:
        """Generate video frames as numpy arrays (RGB)."""
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {filepath}")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                yield frame_rgb
        finally:
            cap.release()
