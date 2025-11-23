from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, Qt

class MetadataPanel(QGroupBox):
    metadata_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__("Metadata", parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        
        # Fields
        self.artist_edit = self._add_field("Artist:")
        self.work_edit = self._add_field("Work:")
        self.page_edit = self._add_field("Page:")
        
        self.date_edit = self._add_field("Date/Time:")
        self.date_edit.setReadOnly(True)
        self.date_edit.setStyleSheet("color: #aaaaaa; background: #2a2a2a; border: none;")
        # self.layout.addWidget(QLabel("Fecha/Hora:"))
        # self.date_label = QLabel("")
        # self.layout.addWidget(self.date_label)
        
        # Selection Mode moved to ToolsPanel in Sidebar

    def _add_field(self, label_text):
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        label.setFixedWidth(60) # Fixed width for alignment
        h_layout.addWidget(label)
        
        edit = QLineEdit()
        h_layout.addWidget(edit)
        
        self.layout.addWidget(container)
        return edit

    def _emit_metadata(self):
        data = {
            "artist": self.artist_edit.text(),
            "work": self.work_edit.text(),
            "page": self.page_edit.text()
        }
        self.metadata_changed.emit(data)

    def set_metadata(self, artist, work, page):
        """Programmatically set metadata fields."""
        self.artist_edit.setText(artist)
        self.work_edit.setText(work)
        self.page_edit.setText(page)
        # Trigger update manually since setText might not trigger if value is same, 
        # but we want to ensure current_metadata is up to date in viewer
        self._emit_metadata()
