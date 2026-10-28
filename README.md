# Monocast

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Transform images, GIFs, and videos into real-time ASCII art.**

</div>

## ✨ Features

- **Multi-format Support** – Convert images (`PNG`, `JPG`, `JPEG`, `BMP`, `WebP`), GIFs, and videos (`MP4`, `AVI`, `MKV`, `WebM`, `MOV`)
- **Real-time Preview** – Instantly see your ASCII conversion with live updates as you tweak settings
- **Customizable Charsets** – Choose from 30+ built-in character presets including Matrix, Braille, Blocks, Stars, and more
- **Fine-tuned Controls** – Adjust columns, brightness threshold, invert, and toggle per-pixel color rendering
- **Animated Playback** – Smooth playback for GIFs and videos with frame-by-frame control
- **Multiple Export Options** – Save as PNG, plain text, or JSON
- **Clean Dark UI** – Minimal, distraction-free interface with sidebar controls and live preview

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. Clone the repository
```bash
git clone https://github.com/sanjayadanushka712/Monocast.git
cd Monocast
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) | Desktop GUI framework |
| [NumPy](https://numpy.org/) | Vectorized pixel processing for high performance |
| [Pillow](https://python-pillow.org/) | Image loading and manipulation |
| [OpenCV](https://opencv.org/) | Video frame extraction |
| [imageio](https://imageio.readthedocs.io/) | GIF decoding with proper frame compositing |
| [moviepy](https://zulko.github.io/moviepy/) | Video/GIF export capabilities |

## 🏗️ Project Structure

```text
Monocast/
├── core/           # Pure conversion logic (BT.601 luminance mapping)
├── ui/             # PyQt6 UI components (MainWindow, Sidebar, Preview)
├── utils/          # Export utilities
├── assets/         # Icons and resources
└── main.py         # Application entry point
```

## 🎨 How It Works

Monocast uses the ITU-R BT.601 standard for luminance calculation:

1. **Downsample** – Images are resized to the target ASCII grid based on column count and aspect ratio
2. **Calculate Luminance** – Each pixel's brightness is computed using `0.299R + 0.587G + 0.114B`
3. **Map to Characters** – Brightness values are mapped to characters from darkest to brightest based on your selected charset
4. **Render** – The ASCII grid is displayed with optional per-pixel colors preserved from the source

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
