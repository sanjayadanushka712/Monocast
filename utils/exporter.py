"""Export utilities for ASCII art."""

import os
import json
from typing import List
from PIL import Image, ImageDraw, ImageFont


class AsciiExporter:
    @staticmethod
    def save_text(text: str, filepath: str):
        """Save ASCII art as plain text."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)

    @staticmethod
    def save_json(frames: List[str], filepath: str):
        """Save frames as JSON."""
        data = {
            'version': 1,
            'frameCount': len(frames),
            'frames': frames
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def save_png_from_text(text: str, filepath: str, font_size: int = 8,
                           bg_color=(0, 0, 0), fg_color=(255, 255, 255)):
        """Render ASCII text to PNG."""
        try:
            # Try to use a monospace font
            try:
                font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", font_size)
                except:
                    font = ImageFont.load_default()

            lines = text.split('\n')
            # Calculate size
            max_width = max((len(line) for line in lines), default=0)
            line_height = font_size + 2

            img_width = max_width * (font_size // 2 + 1)
            img_height = len(lines) * line_height

            img = Image.new('RGB', (img_width, img_height), bg_color)
            draw = ImageDraw.Draw(img)

            y = 0
            for line in lines:
                draw.text((0, y), line, fill=fg_color, font=font)
                y += line_height

            img.save(filepath)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to save PNG: {e}")
