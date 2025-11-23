import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QDialog, QLabel, 
                             QLineEdit, QFileDialog, QKeySequenceEdit, QHBoxLayout, QMessageBox, QAction)
import json
import os
from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QPushButton, QDialog, QLabel, 
                             QLineEdit, QFileDialog, QKeySequenceEdit, QHBoxLayout, QMessageBox, QAction, QGridLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence

CONFIG_FILE = "custom_buttons.json"

class CustomButtonDialog(QDialog):
    def __init__(self, parent=None, validator=None):
        super().__init__(parent)
        self.validator = validator
        self.setWindowTitle("Add Custom Copy")
        self.setModal(True)
        self.resize(400, 200)
        
        # Apply Dark Theme to Dialog
        self.setStyleSheet("""
            QDialog { background-color: #2a2a2a; color: #f0f0f0; }
            QLabel { color: #e0e0e0; font-weight: bold; }
            QLineEdit { background: #3a3a3a; color: #ffffff; border: 1px solid #555; padding: 4px; }
            QPushButton { background: #444; color: #fff; border: 1px solid #555; padding: 5px; }
            QPushButton:hover { background: #555; }
            QKeySequenceEdit { background: #3a3a3a; color: #ffffff; border: 1px solid #555; }
        """)
        
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Button Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Path
        layout.addWidget(QLabel("Destination Folder:"))
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.browse_btn = QPushButton("...")
        self.browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)
        
        # Shortcut
        layout.addWidget(QLabel("Shortcut (Optional):"))
        self.shortcut_edit = QKeySequenceEdit()
        layout.addWidget(self.shortcut_edit)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Save")
        self.ok_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)
        
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.path_edit.setText(folder)
            
    def validate_and_accept(self):
        shortcut = self.shortcut_edit.keySequence().toString()
        if self.validator and shortcut:
            is_valid, owner = self.validator(shortcut)
            if not is_valid:
                QMessageBox.warning(self, "Duplicate Shortcut", 
                                  f"Shortcut '{shortcut}' is already in use by: '{owner}'.\n"
                                  "Please choose another.")
                return

        if not self.name_edit.text() or not self.path_edit.text():
             QMessageBox.warning(self, "Error", "Name and Folder are required.")
             return
             
        self.accept()

    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "path": self.path_edit.text(),
            "shortcut": self.shortcut_edit.keySequence().toString()
        }

class CustomButtonsPanel(QGroupBox):
    copy_requested = pyqtSignal(str) # Emits path
    actions_updated = pyqtSignal() # Emits when actions change so main window can re-register them

    def __init__(self, parent=None):
        super().__init__("Custom Save", parent)
        self.validator_callback = None
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        self.buttons_data = []
        self.actions = []
        
        self.add_btn = QPushButton("Add...")
        self.add_btn.setToolTip("Add custom copy button...")
        self.add_btn.setStyleSheet("background-color: #2d5a88; font-weight: bold;")
        self.add_btn.clicked.connect(self.open_add_dialog)
        
        # Initial load
        self.load_buttons()

    def set_validator(self, callback):
        self.validator_callback = callback

    def load_buttons(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.buttons_data = json.load(f)
            except Exception as e:
                print(f"Error loading custom buttons: {e}")
                self.buttons_data = []
        
        self.refresh_ui()

    def save_buttons(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.buttons_data, f, indent=4)
        except Exception as e:
            print(f"Error saving custom buttons: {e}")

    def refresh_ui(self):
        # Clear layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        
        self.actions.clear()
        
        # Add "Add" button at 0,0
        self.layout.addWidget(self.add_btn, 0, 0)
        
        # Add custom buttons
        # Grid logic: 3 columns.
        # Index 0 is taken by Add button.
        # So custom buttons start at index 1.
        
        col_count = 3
        
        for i, data in enumerate(self.buttons_data):
            grid_index = i + 1
            row = grid_index // col_count
            col = grid_index % col_count
            
            btn = self._create_button_ui(data)
            self.layout.addWidget(btn, row, col)
            
        # Add stretch to push everything up? 
        # In Grid, we can set row stretch on the last row + 1
        last_row = (len(self.buttons_data) + 1) // col_count
        self.layout.setRowStretch(last_row + 1, 1)
        
        self.actions_updated.emit()

    def _create_button_ui(self, data):
        name = data.get("name", "Unnamed")
        path = data.get("path", "")
        shortcut = data.get("shortcut", "")
        
        text = name
        if shortcut:
            text += f" ({shortcut})"
            
        btn = QPushButton(text)
        btn.setToolTip(f"Save to: {path}\nShortcut: {shortcut}")
        btn.clicked.connect(lambda: self.copy_requested.emit(path))
        
        # Create Action
        if shortcut:
            action = QAction(name, self)
            action.setShortcut(shortcut)
            action.triggered.connect(lambda: self.copy_requested.emit(path))
            self.actions.append(action)
            
        return btn

    def open_add_dialog(self):
        dlg = CustomButtonDialog(self, validator=self.validator_callback)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            self.buttons_data.append(data)
            self.save_buttons()
            self.refresh_ui()

    def get_actions(self):
        return self.actions
