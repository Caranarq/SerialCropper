import os
import json
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QSplitter, QFileDialog, QWidget, QVBoxLayout, QMessageBox, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QKeySequence

from widgets.canvas import CanvasWidget
from widgets.canvas import CanvasWidget
from widgets.sidebar import Sidebar
from batch.batch_manager import BatchManager
from batch.batch_manager import BatchManager
from core.activity_log import ActivityLog
from core.utils import clean_filename

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Cropper v2.0")
        self.resize(1400, 900)

        # Core Logic
        self.log = ActivityLog()
        self.batch_manager = None
        
        # UI Setup
        # UI Setup
        # self.toolbar = MainToolbar(self) # Removed
        # self.addToolBar(self.toolbar) # Removed
        
        self.canvas = CanvasWidget()
        self.sidebar = Sidebar()
        
        # Shortcuts helper to access panels easily
        self.meta_panel = self.sidebar.meta_panel
        self.custom_panel = self.sidebar.custom_panel
        self.log_panel = self.sidebar.log_panel
        
        self._setup_theme()
        
        # Layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.canvas)
        splitter.addWidget(self.sidebar)
        splitter.setSizes([1100, 320])
        
        self.setCentralWidget(splitter)
        
        # Connections
        self._connect_signals()
        
        # Initialize state
        self.current_metadata = {}
        self.variant_counter = 1
        self.session_processed_count = 0
        
        # Register initial custom actions
        self.register_custom_actions()
        
        self._log("Application started")
        
        # Auto-load last session
        self.load_settings()

    def _setup_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #202020; }
            QToolBar { background: #2a2a2a; border-bottom: 1px solid #111; }
            QToolButton { color: #f0f0f0; background: transparent; padding: 4px; }
            QToolButton:hover { background: #3a3a3a; }
            QLabel, QRadioButton { color: #e0e0e0; }
            QLineEdit { background: #3a3a3a; color: #ffffff; border: 1px solid #555; padding: 4px; }
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QGroupBox { 
                border: 1px solid #444; 
                margin-top: 6px; 
                padding-top: 10px; 
                font-weight: bold;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 3px; 
                color: #e0e0e0; 
            }
        """)

    def _connect_signals(self):
        # File Panel
        self.sidebar.file_panel.open_requested.connect(self.open_folder_dialog)
        
        # Tools Panel
        self.sidebar.tools_panel.mode_changed.connect(self.canvas.set_select_mode)
        self.sidebar.tools_panel.action_triggered.connect(self._handle_tool_action)
        
        # Actions Panel
        self.sidebar.actions_panel.action_triggered.connect(self._handle_main_action)
        
        # Release Focus (Esc)
        self.act_release_focus = QAction("Release Focus", self)
        self.act_release_focus.setShortcut("Esc")
        self.act_release_focus.triggered.connect(self.canvas.setFocus)
        self.addAction(self.act_release_focus)
        
        # Metadata
        self.meta_panel.metadata_changed.connect(self.update_metadata)
        # self.meta_panel.selection_mode_changed.connect(self.canvas.set_select_mode) # Moved to ToolsPanel
        
        # Custom Buttons
        self.custom_panel.copy_requested.connect(self.custom_save_crop)
        self.custom_panel.actions_updated.connect(self.register_custom_actions)
        self.custom_panel.set_validator(self.check_shortcut_conflict)
        
        self.registered_custom_actions = []

    def _handle_tool_action(self, action):
        if action == "fit":
            self.canvas.zoom_extents()
        elif action == "1:1":
            self.canvas.zoom_100()
        elif action == "zoom_sel":
            self.canvas.zoom_selection()
        elif action == "restore":
            self.restore_selection()

    def _handle_main_action(self, action):
        if action == "save_next":
            self.save_crop(keep=False)
        elif action == "save_keep":
            self.save_crop(keep=True)
        elif action == "next":
            self.next_image()



    def check_shortcut_conflict(self, key_sequence_str):
        """
        Checks if the given key sequence string matches any existing action's shortcut.
        Returns (is_valid, owner_name).
        """
        # Normalize input
        seq = QKeySequence(key_sequence_str)
        
        # Check all actions in the window
        for action in self.findChildren(QAction):
            if action.shortcut() == seq:
                # Found a conflict
                return False, action.text().replace("&", "")
                
        return True, None

    def register_custom_actions(self):
        # Remove previously registered actions to avoid duplicates/ambiguity
        for action in self.registered_custom_actions:
            self.removeAction(action)
            self.canvas.removeAction(action)
        
        self.registered_custom_actions.clear()
        
        # Add new actions
        actions = self.custom_panel.get_actions()
        for action in actions:
            self.addAction(action)
            self.canvas.addAction(action)
            self.registered_custom_actions.append(action)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Batch Folder")
        if folder:
            self.open_folder(folder)

    def open_folder(self, folder):
        self.batch_manager = BatchManager(folder)
        count = self.batch_manager.scan()
        self._log(f"Batch folder loaded: {folder}")
        self._log(f"Found {count} images in _para_procesar")
        if count == 0:
            QMessageBox.warning(self, "No Images", "No images found in _para_procesar subfolder.")
        
        self.session_processed_count = 0
        self.load_current_image()
        self.save_settings()

    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    data = json.load(f)
                    last_folder = data.get("last_folder")
                    if last_folder and os.path.exists(last_folder):
                        self.open_folder(last_folder)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        if self.batch_manager and self.batch_manager.root_dir:
            try:
                data = {"last_folder": self.batch_manager.root_dir}
                with open("settings.json", "w") as f:
                    json.dump(data, f)
            except Exception as e:
                print(f"Error saving settings: {e}")

    def load_current_image(self):
        if not self.batch_manager:
            return
        
        path = self.batch_manager.current_path()
        if path:
            self.canvas.set_pixmap(QPixmap(path))
            self.variant_counter = 1
            
            # Update metadata defaults
            filename = os.path.basename(path)
            page = os.path.splitext(filename)[0]
            
            # Extract Artist and Work from path
            # Structure: .../_para_procesar/Artist/Work/Page.ext
            try:
                # Get path relative to _para_procesar
                # We need to find where _para_procesar is in the path
                # Since batch_manager knows todo_dir, we can use relpath
                rel_path = os.path.relpath(path, self.batch_manager.todo_dir)
                parts = rel_path.split(os.sep)
                
                if len(parts) >= 3:
                    artist = parts[0]
                    work = parts[1]
                    # page is parts[-1] (filename)
                elif len(parts) == 2:
                    artist = parts[0]
                    work = "ND"
                else:
                    artist = "ND"
                    work = "ND"
            except ValueError:
                # Path not relative to todo_dir (shouldn't happen in normal flow)
                artist = "ND"
                work = "ND"

            self.meta_panel.set_metadata(artist, work, page)
            self.meta_panel.set_metadata(artist, work, page)
            self.meta_panel.date_edit.setText(datetime.now().strftime("%Y-%m-%d %H:%M"))
            
            # Update Window Title with Relative Path and Progress
            remaining = len(self.batch_manager.files) if self.batch_manager else 0
            self.setWindowTitle(f"Serial Cropper v2.0 - [{self.session_processed_count}/{remaining}] - [{rel_path}]")
            
            self._log(f"Loaded: {filename} ({artist} - {work})")
        else:
            self.canvas.set_pixmap(None) # Clear canvas?
            self.setWindowTitle("Serial Cropper v2.0")
            self._log("No image loaded")

    def next_image(self):
        if self.batch_manager:
            self.session_processed_count += 1
            self.batch_manager.mark_current_processed()
            self.load_current_image()

    def save_crop(self, keep, output_path=None):
        crop = self.canvas.get_crop()
        if not crop:
            self._log("No selection to crop")
            return
            
        # Filename generation
        artist = clean_filename(self.current_metadata.get("artist", "ND"))
        if not artist: artist = "ND"
        
        work_raw = self.current_metadata.get("work", "")
        words = work_raw.split()
        work_init = "".join(w[0].upper() for w in words if w) if words else "ND"
        work_init = clean_filename(work_init)
        
        page = clean_filename(self.current_metadata.get("page", "000"))
        if not page: page = "000"

        base = f"{artist}_{work_init}_{page}"
        filename = f"{base}({self.variant_counter}).png"
        
        # Output dir
        if output_path:
            out_dir = output_path
        else:
            out_dir = self.batch_manager.output_dir if self.batch_manager else "_output"
            
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, filename)
        
        while os.path.exists(path):
            self.variant_counter += 1
            filename = f"{base}({self.variant_counter}).png"
            path = os.path.join(out_dir, filename)
            
        # Convert to QImage to add metadata
        image = crop.toImage()
        
        # Embed Metadata
        artist = self.current_metadata.get("artist", "ND")
        work = self.current_metadata.get("work", "ND")
        page = self.current_metadata.get("page", "000")
        
        image.setText("Artist", artist)
        image.setText("Work", work)
        image.setText("Page", page)
        image.setText("Software", "SerialCropper v2.0")
            
        if image.save(path, "PNG"):
            self._log(f"Saved: {filename}")
            self.variant_counter += 1
            if not keep:
                self.canvas.selection.clear()
                self.canvas.update()
                self.next_image()
        else:
            self._log("Error saving file")
            
    def custom_save_crop(self, path):
        # Custom save always behaves like "Keep" (doesn't advance image)
        self.save_crop(keep=True, output_path=path)

    def update_metadata(self, data):
        self.current_metadata = data
        # Update date
        self.meta_panel.date_edit.setText(datetime.now().strftime("%Y-%m-%d %H:%M"))

    def _log(self, msg):
        self.log.add(msg)
        self.log_panel.update_log(self.log.get_entries())

    def restore_selection(self):
        if self.canvas.selection.restore_previous():
            self.canvas.update()
            self._log("Selection restored")
        else:
            self._log("No previous selection to restore")
