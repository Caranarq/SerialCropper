# Implementation Plan - UI Redesign (Unified Sidebar)

## Goal
Professionalize the interface by removing the top toolbar and consolidating all controls into a structured, semantic sidebar on the right.

## User Review Required
- **Grouping Logic**: Confirm the proposed hierarchy of panels.
- **Visual Style**: Dark theme, flat buttons, text + shortcuts (no icons required).

## Proposed Structure (Sidebar)

### 1. 📂 File
*System operations and navigation.*
- **[Open Folder (Ctrl+O)]**
- *[Reveal in Explorer]* (Future)
- *[About]* (Future)

### 2. 📝 Metadata
*Image information and context.*
- **Artist** (Input)
- **Work** (Input)
- **Page** (Input)
- *Date/Time Label* (Small, subtle)

### 3. 🛠️ Toolbox
*Tools for manipulating the view and selection.*
- **Selection Mode**:
    - [Rect (R)] [Ellipse (E)] (Segmented toggle)
- **View Controls** (Grid layout):
    - [Fit (F)] [1:1 (1)]
    - [Zoom Sel (Z)] [Restore (P)]

### 4. 💾 Actions
*Commit actions. Prominent buttons.*
- **[Save & Next (Enter)]** (Primary Action - Accent Color)
- **[Save & Keep (S)]**
- **[Skip / Next (Right)]**

### 5. 🏷️ Quick Tags
*Custom user-defined buttons.*
- [Bold] [Cover] [Best] ... (Scrollable grid if many)
- [Edit Buttons...]

### 6. 📜 Log
*History and feedback.*
- (Scrollable text area, reduced height)

## Technical Changes
### [MODIFY] [viewer.py](file:///e:/Arte/Imagen/_ahe/serial_cropper/viewer.py)
- Remove `MainToolbar`.
- Update layout: `QSplitter` remains, but Right Widget now hosts *everything*.

### [NEW] [widgets/sidebar.py](file:///e:/Arte/Imagen/_ahe/serial_cropper/widgets/sidebar.py)
- New widget that orchestrates the sub-groups.
- Will contain the `FilePanel`, `MetadataPanel` (reused/refactored), `ToolsPanel`, `ActionsPanel`, `CustomButtonsPanel` (reused), and `LogPanel` (reused).

### [DELETE] [widgets/toolbar.py](file:///e:/Arte/Imagen/_ahe/serial_cropper/widgets/toolbar.py)
- No longer needed. Logic moves to `Sidebar`.
