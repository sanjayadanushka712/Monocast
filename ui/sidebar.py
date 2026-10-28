from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QPushButton,
    QLabel,
    QSlider,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QColorDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor


class Sidebar(QWidget):
    file_loaded = pyqtSignal(str)
    settings_changed = pyqtSignal(dict)
    appearance_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(250)
        self.setMaximumWidth(350)
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(150)
        self._debounce_timer.timeout.connect(self._emit_settings)
        self.bg_color = "#000000"
        self.text_color = "#ffffff"
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # File section
        file_group = QGroupBox("Source")
        file_layout = QVBoxLayout(file_group)

        self.load_btn = QPushButton("Open File...")
        self.load_btn.clicked.connect(self._load_file)
        file_layout.addWidget(self.load_btn)

        self.file_label = QLabel("No file loaded")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("color: gray;")
        file_layout.addWidget(self.file_label)

        scroll_layout.addWidget(file_group)

        # Conversion settings
        conv_group = QGroupBox("Conversion")
        conv_layout = QVBoxLayout(conv_group)

        # Columns
        conv_layout.addWidget(QLabel("Columns"))
        self.columns_slider = QSlider(Qt.Orientation.Horizontal)
        self.columns_slider.setRange(40, 400)
        self.columns_slider.setValue(120)
        self.columns_slider.valueChanged.connect(self._on_settings_changed)
        self.columns_label = QLabel("120")
        self.columns_slider.valueChanged.connect(lambda v: self.columns_label.setText(str(v)))
        conv_layout.addWidget(self.columns_slider)
        conv_layout.addWidget(self.columns_label)

        # Charset
        conv_layout.addWidget(QLabel("Charset"))
        self.charset_combo = QComboBox()
        from core.palettes import ASCII_CHAR_PRESETS
        self.charsets = []
        for preset in ASCII_CHAR_PRESETS:
            self.charset_combo.addItem(f"{preset['label']}")
            self.charsets.append(preset['chars'])
        self.charset_combo.setCurrentIndex(2)
        self.charset_combo.currentIndexChanged.connect(self._on_settings_changed)
        conv_layout.addWidget(self.charset_combo)

        # Threshold
        conv_layout.addWidget(QLabel("Threshold"))
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(-100, 100)
        self.threshold_slider.setValue(0)
        self.threshold_slider.valueChanged.connect(self._on_settings_changed)
        self.threshold_label = QLabel("0")
        self.threshold_slider.valueChanged.connect(lambda v: self.threshold_label.setText(str(v)))
        conv_layout.addWidget(self.threshold_slider)
        conv_layout.addWidget(self.threshold_label)

        # Invert
        self.invert_check = QCheckBox("Invert")
        self.invert_check.stateChanged.connect(self._on_settings_changed)
        conv_layout.addWidget(self.invert_check)

        # Use colors
        self.colors_check = QCheckBox("Use Colors")
        self.colors_check.stateChanged.connect(self._on_settings_changed)
        conv_layout.addWidget(self.colors_check)

        scroll_layout.addWidget(conv_group)

        # Appearance
        app_group = QGroupBox("Appearance")
        app_layout = QVBoxLayout(app_group)

        bg_btn = QPushButton("Background Color")
        bg_btn.clicked.connect(self._pick_bg)
        app_layout.addWidget(bg_btn)

        text_btn = QPushButton("Text Color")
        text_btn.clicked.connect(self._pick_text)
        app_layout.addWidget(text_btn)

        scroll_layout.addWidget(app_group)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self._on_settings_changed()
        self._emit_appearance()

    def _load_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter(
            "All Supported (*.png *.jpg *.jpeg *.bmp *.gif *.mp4 *.avi *.mkv *.webm);;"
            "Images (*.png *.jpg *.jpeg *.bmp);;"
            "GIFs (*.gif);;"
            "Videos (*.mp4 *.avi *.mkv *.webm)"
        )
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            if files:
                filepath = files[0]
                self.file_label.setText(filepath.split('/')[-1])
                self.file_loaded.emit(filepath)

    def _on_settings_changed(self):
        self._debounce_timer.start()

    def _emit_settings(self):
        settings = {
            'columns': self.columns_slider.value(),
            'charset': self.charsets[self.charset_combo.currentIndex()] if self.charsets else " .:-=+*#%@",
            'threshold': self.threshold_slider.value(),
            'invert': self.invert_check.isChecked(),
            'use_colors': self.colors_check.isChecked(),
        }
        self.settings_changed.emit(settings)

    def _pick_bg(self):
        color = QColorDialog.getColor(QColor(self.bg_color), self)
        if color.isValid():
            self.bg_color = color.name()
            self._emit_appearance()

    def _pick_text(self):
        color = QColorDialog.getColor(QColor(self.text_color), self)
        if color.isValid():
            self.text_color = color.name()
            self._emit_appearance()

    def _emit_appearance(self):
        self.appearance_changed.emit({
            'bg_color': self.bg_color,
            'text_color': self.text_color,
        })
