from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QRadioButton
from PyQt5.QtCore import pyqtSignal, Qt

class MetadataPanel(QWidget):
    metadata_changed = pyqtSignal(dict)
    selection_mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(10)
        
        # Fields
        self.artist_edit = self._add_field("Artista:")
        self.work_edit = self._add_field("Obra:")
        self.page_edit = self._add_field("Página:")
        
        self.layout.addWidget(QLabel("Fecha/Hora:"))
        self.date_label = QLabel("")
        self.layout.addWidget(self.date_label)

        # Selection Mode
        self.layout.addWidget(QLabel("Selección:"))
        self.rect_radio = QRadioButton("Rectangular")
        self.ellipse_radio = QRadioButton("Elíptica")
        self.rect_radio.setChecked(True)
        self.layout.addWidget(self.rect_radio)
        self.layout.addWidget(self.ellipse_radio)
        
        self.layout.addStretch()

        # Connects
        self.artist_edit.textChanged.connect(self._emit_metadata)
        self.work_edit.textChanged.connect(self._emit_metadata)
        self.page_edit.textChanged.connect(self._emit_metadata)
        
        self.rect_radio.toggled.connect(self._emit_mode)
        self.ellipse_radio.toggled.connect(self._emit_mode)

    def _add_field(self, label):
        self.layout.addWidget(QLabel(label))
        edit = QLineEdit()
        self.layout.addWidget(edit)
        return edit

    def _emit_metadata(self):
        data = {
            "artist": self.artist_edit.text(),
            "work": self.work_edit.text(),
            "page": self.page_edit.text()
        }
        self.metadata_changed.emit(data)

    def _emit_mode(self):
        mode = "rect" if self.rect_radio.isChecked() else "ellipse"
        self.selection_mode_changed.emit(mode)

    def set_metadata(self, artist, work, page):
        """Programmatically set metadata fields."""
        self.artist_edit.setText(artist)
        self.work_edit.setText(work)
        self.page_edit.setText(page)
        # Trigger update manually since setText might not trigger if value is same, 
        # but we want to ensure current_metadata is up to date in viewer
        self._emit_metadata()
    
    def set_selection_mode(self, mode):
        if mode == "rect":
            self.rect_radio.setChecked(True)
        else:
            self.ellipse_radio.setChecked(True)
