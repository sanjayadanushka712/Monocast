"""Pure image -> ASCII conversion utilities."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image


@dataclass
class ImageToAsciiResult:
    text: str
    rows: int
    cols: int
    colors: Optional[List[List[Tuple[int, int, int]]]] = None


class AsciiConverter:
    """ASCII conversion logic ported from Glyphcast."""

    def __init__(self):
        pass

    def image_to_ascii(
        self,
        source: Union[Image.Image, np.ndarray],
        columns: int = 100,
        charset: str = " .:-=+*#%@",
        invert: bool = False,
        threshold: int = 0,
        cell_aspect: float = 0.5,
        use_colors: bool = False,
    ) -> ImageToAsciiResult:
        if isinstance(source, np.ndarray):
            if source.ndim == 3 and source.shape[2] == 4:
                source = Image.fromarray(source).convert("RGB")
            elif source.ndim == 3:
                source = Image.fromarray(source.astype(np.uint8))
            elif source.ndim == 2:
                source = Image.fromarray(source.astype(np.uint8)).convert("RGB")
            else:
                raise ValueError("Unsupported array shape")

        if not isinstance(source, Image.Image):
            raise ValueError("Source must be PIL Image or numpy array")

        img = source.convert("RGB")
        src_w, src_h = img.size

        if not src_w or not src_h:
            return ImageToAsciiResult(text="", rows=0, cols=0)

        if not charset or len(charset) == 0:
            charset = " .:-=+*#%@"

        cols = max(1, int(columns))
        cell_aspect = max(0.1, float(cell_aspect))
        rows = max(1, int(round((cols * src_h * cell_aspect) / src_w)))

        # Downsample to ASCII grid
        resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
        arr = np.array(resized).astype(np.float32)

        # BT.601 luminance
        lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

        offset = (float(threshold) / 100.0) * 255.0
        lum = lum + offset
        lum = np.clip(lum, 0, 255)

        # Map luminance to charset (darkest -> index 0)
        charset_len = len(charset)
        last_idx = charset_len - 1
        # Normalize to [0, last_idx]
        norm = lum / 255.0
        idx = (norm * last_idx).astype(np.int32)
        idx = np.clip(idx, 0, last_idx)

        if invert:
            idx = last_idx - idx

        chars_array = np.array(list(charset))[idx]
        lines = ["".join(row) for row in chars_array]
        text = "\n".join(lines)

        colors = None
        if use_colors:
            colors = []
            for y in range(rows):
                row_colors = []
                for x in range(cols):
                    r, g, b = arr[y, x].astype(int)
                    row_colors.append((int(r), int(g), int(b)))
                colors.append(row_colors)

        return ImageToAsciiResult(text=text, rows=rows, cols=cols, colors=colors)


def image_to_ascii(*args, **kwargs) -> ImageToAsciiResult:
    converter = AsciiConverter()
    return converter.image_to_ascii(*args, **kwargs)
