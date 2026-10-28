from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QTextEdit
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QTextCharFormat, QColor
import os

from core.converter import AsciiConverter
from core.gif_handler import GifHandler
from core.video_handler import VideoHandler
from PIL import Image


class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.converter = AsciiConverter()
        self.current_file = None
        self.file_type = None
        self.settings = {
            'columns': 100,
            'charset': " .:-=+*#%@",
            'threshold': 0,
            'invert': False,
            'use_colors': False,
        }

        self.gif_frames = []
        self.gif_delays = []
        self.current_gif_frame = 0
        self.gif_timer = QTimer()
        self.gif_timer.timeout.connect(self._next_gif_frame)

        self.video_frames = []
        self.current_video_frame = 0
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self._next_video_frame)

        self.playing = False

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        font = QFont("Courier New", 7)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_edit.setFont(font)
        self.text_edit.setStyleSheet("background-color: #000000; color: #ffffff;")

        self.scroll.setWidget(self.text_edit)
        layout.addWidget(self.scroll)

    @pyqtSlot(str)
    def load_file(self, filepath):
        self.current_file = filepath
        self.file_type = self._detect_file_type(filepath)

        self.gif_timer.stop()
        self.video_timer.stop()
        self.playing = False

        if self.file_type == 'image':
            self._load_image(filepath)
        elif self.file_type == 'gif':
            self._load_gif(filepath)
        elif self.file_type == 'video':
            self._load_video(filepath)

    def _detect_file_type(self, filepath):
        ext = os.path.splitext(filepath.lower())[1]
        if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
            return 'image'
        elif ext == '.gif':
            return 'gif'
        elif ext in ['.mp4', '.avi', '.mkv', '.webm', '.mov']:
            return 'video'
        return None

    def _convert_and_display(self, img: Image.Image):
        try:
            result = self.converter.image_to_ascii(
                img,
                columns=self.settings['columns'],
                charset=self.settings['charset'],
                invert=self.settings['invert'],
                threshold=self.settings['threshold'],
                use_colors=self.settings['use_colors'],
            )

            if self.settings['use_colors'] and result.colors and result.rows > 0 and result.cols > 0:
                # For performance, limit colored rendering for large outputs
                if result.rows * result.cols > 10000:
                    self.text_edit.setPlainText(result.text)
                    return result
                self.text_edit.setUpdatesEnabled(False)
                self.text_edit.clear()
                cursor = self.text_edit.textCursor()
                fmt = QTextCharFormat()
                fmt.setFont(self.text_edit.font())
                lines = result.text.split('\n')
                for y in range(min(result.rows, len(lines))):
                    line = lines[y]
                    for x in range(min(result.cols, len(line))):
                        ch = line[x]
                        if ch == ' ':
                            cursor.insertText(' ', fmt)
                            continue
                        r, g, b = result.colors[y][x]
                        cfmt = QTextCharFormat()
                        cfmt.setForeground(QColor(int(r), int(g), int(b)))
                        cfmt.setFont(self.text_edit.font())
                        cursor.insertText(ch, cfmt)
                    cursor.insertText('\n')
                self.text_edit.setUpdatesEnabled(True)
            else:
                self.text_edit.setPlainText(result.text)
            return result
        except Exception as e:
            self.text_edit.setPlainText(f"Error: {e}")
            return None

    def _load_image(self, filepath):
        try:
            img = Image.open(filepath)
            self._convert_and_display(img)
        except Exception as e:
            self.text_edit.setPlainText(f"Error: {e}")

    def _load_gif(self, filepath):
        try:
            frames_rgba, delays = GifHandler.load_gif_frames(filepath)
            self.gif_frames = GifHandler.frames_to_pil_list(frames_rgba)
            self.gif_delays = delays
            self.current_gif_frame = 0

            if self.gif_frames:
                self._render_current_gif_frame()
                if self.gif_delays and self.gif_delays[0] > 0:
                    self.gif_timer.start(self.gif_delays[0])
        except Exception as e:
            self.text_edit.setPlainText(f"Error: {e}")

    def _load_video(self, filepath):
        try:
            width, height, fps, frame_count = VideoHandler.get_video_info(filepath)
            gen = VideoHandler.frames_generator(filepath)
            self.video_frames = []
            max_frames = min(100, frame_count) if frame_count > 0 else 30
            step = max(1, frame_count // max_frames) if frame_count > 0 else 1
            frame_idx = 0
            for frame in gen:
                if frame_idx % step == 0 and len(self.video_frames) < max_frames:
                    self.video_frames.append(Image.fromarray(frame))
                frame_idx += 1
                if len(self.video_frames) >= max_frames:
                    break

            self.current_video_frame = 0
            if self.video_frames:
                self._render_current_video_frame()
                if fps and fps > 0:
                    interval = max(30, int(1000 / min(fps, 15)))
                    self.video_timer.start(interval)
        except Exception as e:
            self.text_edit.setPlainText(f"Error: {e}")

    def _render_current_gif_frame(self):
        if self.gif_frames and 0 <= self.current_gif_frame < len(self.gif_frames):
            self._convert_and_display(self.gif_frames[self.current_gif_frame])

    def _render_current_video_frame(self):
        if self.video_frames and 0 <= self.current_video_frame < len(self.video_frames):
            self._convert_and_display(self.video_frames[self.current_video_frame])

    def _next_gif_frame(self):
        if self.gif_frames:
            self.current_gif_frame = (self.current_gif_frame + 1) % len(self.gif_frames)
            self._render_current_gif_frame()
            if self.gif_delays and self.current_gif_frame < len(self.gif_delays):
                delay = self.gif_delays[self.current_gif_frame]
                if delay > 0:
                    self.gif_timer.setInterval(delay)

    def _next_video_frame(self):
        if self.video_frames:
            self.current_video_frame = (self.current_video_frame + 1) % len(self.video_frames)
            self._render_current_video_frame()

    @pyqtSlot(dict)
    def update_settings(self, settings):
        self.settings.update(settings)
        if self.current_file and self.file_type == 'image':
            self._load_image(self.current_file)
        elif self.file_type == 'gif' and self.gif_frames:
            self._render_current_gif_frame()
        elif self.file_type == 'video' and self.video_frames:
            self._render_current_video_frame()

    @pyqtSlot(bool)
    def toggle_playback(self, playing):
        self.playing = playing
        if self.file_type == 'gif':
            if playing and self.gif_frames:
                if self.gif_delays and self.current_gif_frame < len(self.gif_delays):
                    self.gif_timer.start(self.gif_delays[self.current_gif_frame])
            else:
                self.gif_timer.stop()
        elif self.file_type == 'video':
            if playing and self.video_frames:
                self.video_timer.start()
            else:
                self.video_timer.stop()

    @pyqtSlot(int)
    def set_frame(self, frame):
        if self.file_type == 'gif' and self.gif_frames:
            self.current_gif_frame = max(0, min(frame, len(self.gif_frames) - 1))
            self._render_current_gif_frame()
        elif self.file_type == 'video' and self.video_frames:
            self.current_video_frame = max(0, min(frame, len(self.video_frames) - 1))
            self._render_current_video_frame()
