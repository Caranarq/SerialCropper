from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt

class LogPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Log", parent)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Log started...")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignTop)
        
        scroll = QScrollArea()
        scroll.setWidget(self.label)
        scroll.setWidgetResizable(True)
        self.layout.addWidget(scroll)

    def update_log(self, entries):
        text = "\n".join(entries)
        self.label.setText(text)
