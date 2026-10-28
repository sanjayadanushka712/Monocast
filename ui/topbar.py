from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSlider
from PyQt6.QtCore import Qt, pyqtSignal


class TopBar(QWidget):
    play_toggled = pyqtSignal(bool)
    frame_changed = pyqtSignal(int)
    export_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(50)
        self.playing = False
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # App title
        title = QLabel("Monocast")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        layout.addSpacing(20)

        # Play/Pause button
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self._toggle_play)
        layout.addWidget(self.play_btn)

        # Frame scrubber
        self.frame_label = QLabel("Frame:")
        layout.addWidget(self.frame_label)

        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.setRange(0, 0)
        self.frame_slider.valueChanged.connect(self._on_frame_changed)
        layout.addWidget(self.frame_slider)

        self.frame_count_label = QLabel("0 / 0")
        layout.addWidget(self.frame_count_label)

        layout.addStretch()

        # Export button
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_clicked.emit)
        layout.addWidget(self.export_btn)

    def _toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.play_btn.setText("Pause")
        else:
            self.play_btn.setText("Play")
        self.play_toggled.emit(self.playing)

    def _on_frame_changed(self, value):
        self.frame_changed.emit(value)
        self.frame_count_label.setText(f"{value + 1} / {self.frame_slider.maximum() + 1}")
