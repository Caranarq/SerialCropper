# 🤖 AI Context & Session Memory

## 📌 Project: SerialCropper
**Description**: High-speed, batch-oriented image cropping tool using Python + PyQt5.
**Goal**: Minimize friction for the user to crop thousands of images sequentially.

## 🧠 Architecture & Key Decisions
- **Framework**: PyQt5 (chosen for performance and robust widget system).
- **Core Logic**: Separated into `core/` (pure logic) and `widgets/` (UI).
- **Viewport**: Custom implementation in `widgets/canvas.py` and `core/viewport.py` handling zoom/pan math manually (Paint.NET style) rather than using `QGraphicsView`'s built-in transformation, to have pixel-perfect control over the crop rect.
- **Selection**: 
  - Supports Rectangle and Ellipse.
  - **Perfect Mode**: Shift key forces 1:1 aspect ratio (Square/Circle).
  - **Cropping**: Ellipses save as PNG with transparency (alpha channel).
- **Batch System**: 
  - `_para_procesar` (Input) -> `_processed` (Done) -> `_output` (Result).
  - Files are moved physically on disk to track progress.

## 🔄 Current State (As of Nov 22, 2025)
- **Working**: Basic cropping, batch navigation, metadata editing, zoom/pan.
- **Recent Fixes**: Fixed `NameError: QColor` in `core/cropper.py` regarding ellipse cropping.
- **Pending/Roadmap**:
  - User mentioned an "adjustment" needed (TBD).
  - Zoom Selection (Roadmap).
  - Undo/Redo (Roadmap).

## ⚠️ Risks & "Gotchas"
- **Coordinate Systems**: Be careful with mapping between *Screen Coordinates* (mouse events), *Widget Coordinates* (canvas), and *Image Coordinates* (actual pixels). `viewport.py` manages this.
- **Performance**: Large images can lag if `QPixmap` updates are unoptimized.

## 📝 Session Log
- **Session 1-3**: Initial build, core logic, UI implementation.
- **Session 4 (Nov 22, 2025)**: 
    - Established AI Context Workflow (`AI_CONTEXT.md`, protocols).
    - Adjusted "Zoom Selection" margin from 0.95 to 0.75 (25% padding) in `core/viewport.py` to provide better context.
    - Implemented custom **Rotation Cursor** (programmatic curved arrow bitmap) in `widgets/canvas.py` for better UX when hovering the rotation handle.
    - Implemented **Restore Previous Selection (P)**:
        - Modified `core/selection.py` to save state before clearing.
        - Added toolbar action and shortcut (P).
        - Fixed bug where `start()` didn't save previous state.
    - **UI Redesign (Unified Sidebar)**:
        - Replaced top toolbar with a unified right sidebar (`widgets/sidebar.py`).
        - Organized controls into File, Metadata, Tools, Actions, Custom Save, and Log panels.
        - **Refinements**:
            - Implemented 2-column grid layouts for File and Actions panels.
            - Switched Metadata fields to horizontal layout (Label | Field).
            - Renamed "Quick Tags" to "Custom Save" and enabled shortcut display on buttons.
            - Polished Dark Theme (visible GroupBox titles) and translated UI to English.
    - **Workflow Update**:
        - Updated `/update-context` workflow to include `.gitignore` maintenance step.

