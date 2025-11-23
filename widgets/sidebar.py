from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QScrollArea, QFrame, QSizePolicy, QRadioButton, QButtonGroup, QGridLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from widgets.metadata_panel import MetadataPanel
from widgets.custom_buttons_panel import CustomButtonsPanel
from widgets.log_panel import LogPanel

class FilePanel(QGroupBox):
    open_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__("File")
        layout = QGridLayout(self)
        layout.setSpacing(5)
        
        self.btn_open = QPushButton("Open Folder (Ctrl+O)")
        self.btn_open.setShortcut("Ctrl+O")
        self.btn_open.clicked.connect(self.open_requested.emit)
        
        layout.addWidget(self.btn_open, 0, 0, 1, 2) # Span 2 columns

class ToolsPanel(QGroupBox):
    mode_changed = pyqtSignal(str)
    action_triggered = pyqtSignal(str) # "fit", "1:1", "zoom_sel", "restore"
    
    def __init__(self):
        super().__init__("Toolbox")
        layout = QVBoxLayout(self)
        
        # Mode Selection
        mode_layout = QHBoxLayout()
        self.bg_mode = QButtonGroup(self)
        
        self.rb_rect = QRadioButton("Rect (R)")
        self.rb_rect.setShortcut("R")
        self.rb_rect.setChecked(True)
        self.bg_mode.addButton(self.rb_rect)
        
        self.rb_ellipse = QRadioButton("Ellipse (E)")
        self.rb_ellipse.setShortcut("E")
        self.bg_mode.addButton(self.rb_ellipse)
        
        mode_layout.addWidget(self.rb_rect)
        mode_layout.addWidget(self.rb_ellipse)
        layout.addLayout(mode_layout)
        
        self.bg_mode.buttonClicked.connect(self._emit_mode)
        
        # Grid Tools
        grid = QHBoxLayout() # Using HBox rows for simple grid feel
        
        self.btn_fit = QPushButton("Fit (F)")
        self.btn_fit.setShortcut("F")
        self.btn_fit.clicked.connect(lambda: self.action_triggered.emit("fit"))
        
        self.btn_11 = QPushButton("1:1 (1)")
        self.btn_11.setShortcut("1")
        self.btn_11.clicked.connect(lambda: self.action_triggered.emit("1:1"))
        
        grid.addWidget(self.btn_fit)
        grid.addWidget(self.btn_11)
        layout.addLayout(grid)
        
        grid2 = QHBoxLayout()
        self.btn_zoom_sel = QPushButton("Zoom Sel (Z)")
        self.btn_zoom_sel.setShortcut("Z")
        self.btn_zoom_sel.clicked.connect(lambda: self.action_triggered.emit("zoom_sel"))
        
        self.btn_restore = QPushButton("Restore (P)")
        self.btn_restore.setShortcut("P")
        self.btn_restore.clicked.connect(lambda: self.action_triggered.emit("restore"))
        
        grid2.addWidget(self.btn_zoom_sel)
        grid2.addWidget(self.btn_restore)
        layout.addLayout(grid2)

    def _emit_mode(self, btn):
        if btn == self.rb_rect:
            self.mode_changed.emit("rect")
        else:
            self.mode_changed.emit("ellipse")
            
    def set_mode(self, mode):
        if mode == "rect": self.rb_rect.setChecked(True)
        else: self.rb_ellipse.setChecked(True)

class ActionsPanel(QGroupBox):
    action_triggered = pyqtSignal(str) # "save_next", "save_keep", "next"
    
    def __init__(self):
        super().__init__("Actions")
        layout = QGridLayout(self)
        layout.setSpacing(5)
        
        self.btn_save_next = QPushButton("Save & Next (Enter)")
        self.btn_save_next.setShortcut("Return")
        # Removed blue highlight as requested
        self.btn_save_next.clicked.connect(lambda: self.action_triggered.emit("save_next"))
        
        self.btn_save_keep = QPushButton("Save & Keep (S)")
        self.btn_save_keep.setShortcut("S")
        self.btn_save_keep.clicked.connect(lambda: self.action_triggered.emit("save_keep"))
        
        self.btn_next = QPushButton("Skip / Next (Right)")
        self.btn_next.setShortcut("Right")
        self.btn_next.clicked.connect(lambda: self.action_triggered.emit("next"))
        
        # 2-Column Layout
        # Row 0: Save Next (Span 2)
        # Row 1: Save Keep | Skip
        layout.addWidget(self.btn_save_next, 0, 0, 1, 2)
        layout.addWidget(self.btn_save_keep, 1, 0)
        layout.addWidget(self.btn_next, 1, 1)

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320) # Fixed width for consistency
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 1. File
        self.file_panel = FilePanel()
        layout.addWidget(self.file_panel)
        
        # 2. Metadata (Reusing existing panel logic, but maybe we can style it to fit)
        self.meta_panel = MetadataPanel()
        self.meta_panel.setTitle("Metadata") # Ensure it looks like a groupbox
        layout.addWidget(self.meta_panel)
        
        # 3. Tools
        self.tools_panel = ToolsPanel()
        layout.addWidget(self.tools_panel)
        
        # 4. Actions
        self.actions_panel = ActionsPanel()
        layout.addWidget(self.actions_panel)
        
        # 5. Custom Buttons
        self.custom_panel = CustomButtonsPanel()
        # self.custom_panel.setTitle("Quick Tags") # Handled in class
        layout.addWidget(self.custom_panel)
        
        # 6. Log
        self.log_panel = LogPanel()
        layout.addWidget(self.log_panel)
        
        # Spacer to push everything up if needed, but LogPanel expands so it's fine
