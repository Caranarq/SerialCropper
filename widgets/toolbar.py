from PyQt5.QtWidgets import QToolBar, QAction

from PyQt5.QtWidgets import QToolBar, QAction

class MainToolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Main", parent)
        
        self.act_open = QAction("Open (Ctrl+O)", self)
        self.act_open.setShortcut("Ctrl+O")
        self.act_open.setToolTip("Open Folder (Ctrl+O)")

        self.act_zoom_in = QAction("Zoom In", self)
        self.act_zoom_in.setShortcut("+")
        
        self.act_zoom_out = QAction("Zoom Out", self)
        self.act_zoom_out.setShortcut("-")
        
        self.act_zoom_extents = QAction("Fit (F)", self)
        self.act_zoom_extents.setShortcut("F")
        self.act_zoom_extents.setToolTip("Fit Image to Screen (F)")
        
        self.act_zoom_selection = QAction("Zoom Sel (Z)", self)
        self.act_zoom_selection.setShortcut("Z")
        self.act_zoom_selection.setToolTip("Zoom to Selection (Z)")
        
        self.act_reset = QAction("Reset (1)", self) 
        self.act_reset.setShortcut("1")
        self.act_reset.setToolTip("Reset Zoom 1:1 (1)")
        
        self.act_save = QAction("Save & Next (Enter)", self)
        self.act_save.setShortcut("Return")
        self.act_save.setToolTip("Save Crop and Next Image (Enter)")
        
        self.act_save_keep = QAction("Save & Keep (S)", self)
        self.act_save_keep.setShortcut("S")
        self.act_save_keep.setToolTip("Save Crop and Keep Image (S)")
        
        self.act_next = QAction("Next (Right)", self)
        self.act_next.setShortcut("Right")
        self.act_next.setToolTip("Skip to Next Image (Right Arrow)")

        # Mode Actions (Invisible in toolbar, but available for shortcuts)
        self.act_mode_rect = QAction("Rectangular Mode", self)
        self.act_mode_rect.setShortcut("R")
        
        self.act_mode_ellipse = QAction("Elliptical Mode", self)
        self.act_mode_ellipse.setShortcut("E")

        self.addAction(self.act_open)
        self.addSeparator()
        # Zoom In/Out actions exist but are not on toolbar (mouse wheel only)
        self.addAction(self.act_zoom_selection)
        self.addAction(self.act_zoom_extents)
        self.addAction(self.act_reset)
        self.addSeparator()
        self.addAction(self.act_save)
        self.addAction(self.act_save_keep)
        self.addSeparator()
        self.addAction(self.act_next)
