from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
)
from PyQt6.QtCore import Qt

from ui.sidebar import Sidebar
from ui.preview_widget import PreviewWidget
from ui.topbar import TopBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monocast")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.topbar = TopBar()
        main_layout.addWidget(self.topbar)

        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)

        self.sidebar = Sidebar()
        splitter.addWidget(self.sidebar)

        self.preview = PreviewWidget()
        splitter.addWidget(self.preview)

        splitter.setSizes([280, 920])

        content_layout.addWidget(splitter)
        main_layout.addWidget(content_widget)

        self.sidebar.file_loaded.connect(self.preview.load_file)
        self.sidebar.settings_changed.connect(self.preview.update_settings)
        self.sidebar.appearance_changed.connect(self.preview.update_appearance)
        self.topbar.play_toggled.connect(self.preview.toggle_playback)
        self.topbar.frame_changed.connect(self.preview.set_frame)

        self._setup_export()

    def _setup_export(self):
        self.topbar.export_clicked.connect(self._export)

    def _export(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from utils.exporter import AsciiExporter

        if not hasattr(self.preview, 'text_edit'):
            return

        current_text = self.preview.text_edit.toPlainText()
        if not current_text:
            QMessageBox.warning(self, "Export", "No ASCII art to export")
            return

        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter(
            "PNG Image (*.png);;"
            "Text File (*.txt);;"
            "JSON (*.json);;"
            "All Files (*)"
        )
        file_dialog.setDefaultSuffix("png")

        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            if not files:
                return
            filepath = files[0]
            filter_selected = file_dialog.selectedNameFilter()

            try:
                if filter_selected.startswith("PNG"):
                    AsciiExporter.save_png_from_text(current_text, filepath,
                                                     bg_color=tuple(int(self.preview.bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)),
                                                     fg_color=tuple(int(self.preview.text_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))
                    QMessageBox.information(self, "Export", "Exported successfully")
                elif filter_selected.startswith("Text"):
                    AsciiExporter.save_text(current_text, filepath)
                    QMessageBox.information(self, "Export", "Exported successfully")
                elif filter_selected.startswith("JSON"):
                    AsciiExporter.save_json([current_text], filepath)
                    QMessageBox.information(self, "Export", "Exported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
