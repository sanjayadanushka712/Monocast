"""GIF handling with proper frame compositing."""

from typing import Dict, List, Tuple

import numpy as np
from PIL import Image, ImageSequence


class GifHandler:
    """Handle GIF decoding with frame compositing."""

    @staticmethod
    def load_gif_frames(filepath: str) -> Tuple[List[Image.Image], List[int]]:
        """
        Load GIF frames with proper compositing.
        Returns (frames, delays_ms).
        """
        try:
            with Image.open(filepath) as im:
                frames = []
                delays = []

                # Get disposal method info if available
                for frame in ImageSequence.Iterator(im):
                    # Convert frame to RGBA
                    frame_rgba = frame.convert("RGBA")
                    frames.append(frame_rgba.copy())
                    delay = frame.info.get("duration", 100)
                    delays.append(delay)

                if not frames:
                    return [], []

                # Composite frames
                composited = []
                base = Image.new("RGBA", frames[0].size, (0, 0, 0, 0))

                for i, frame in enumerate(frames):
                    base.paste(frame, (0, 0), frame)
                    composited.append(base.copy())

                return composited, delays
        except Exception as e:
            raise RuntimeError(f"Failed to load GIF: {e}")

    @staticmethod
    def frames_to_pil_list(frames_rgba: List[Image.Image]) -> List[Image.Image]:
        """Convert RGBA frames to RGB for processing."""
        return [f.convert("RGB") for f in frames_rgba]
