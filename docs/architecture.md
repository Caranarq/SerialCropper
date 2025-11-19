# SerialCropper Architecture v1.0

## Overview
SerialCropper is a PyQt5 desktop application designed for ultra-fast image cropping, with batch navigation, refined selection tools, and PNG output with transparent backgrounds. 

## Project Goals
- Fast rectangular and elliptical cropping
- Transparent PNG output
- Automatic batch navigation through folders
- Precise selection tools with handles and shift constraints
- Professional zoom/pan/viewport behavior
- Modular architecture for future expansion

## Directory Structure
serial_cropper/
    core/
        selection.py
        cropper.py
        viewport.py
        activity_log.py
        utils.py
    widgets/
        canvas.py
        metadata_panel.py
        log_panel.py
        toolbar.py
    batch/
        batch_manager.py
    viewer.py
    main.py

## Core Modules
### selection.py
Handles selection logic including:
- Rectangular and elliptical selections
- Shift-constrained square/circle mode
- Handles for resizing after creation
- Inversion correction
- Anchor-from-corner behavior
- Perfect Mode behavior
Defines:
- SelectionState
- SelectionBase
- RectSelection
- EllipseSelection

### cropper.py
Handles the actual image cutting:
- crop_rect() → rectangular crop
- crop_ellipse() → ellipse crop using alpha mask
- Always outputs PNG w/ transparency

### viewport.py
Handles:
- Zoom at cursor
- Pan
- Resize preserving visual center
- Zoom extents
- Zoom to selection

Includes:
- scale
- offset
- min/max scales
- to_screen(), to_image()
- apply_resize()

### activity_log.py
A simple FIFO log for user memory:
- add(message)
- get_entries()

### utils.py
- clamp()
- normalize rectangle helpers
- filename helpers

## Widgets
### canvas.py
A QWidget that:
- Paints image via viewport transform
- Paints selection + handles + dimming overlay
- Receives mouse/keyboard events
Delegates to:
- Viewport for zoom/pan
- Selection for drawing/hit testing
- Cropper for export

### metadata_panel.py
UI for:
- Artist (editable)
- Work Title (editable)
- Page (editable or auto-loaded from filename)
- Timestamp (auto-updated)

### log_panel.py
Displays recent activity log lines.

### toolbar.py (optional)
Handles buttons for:
- Open folder
- Next image
- Save crop
- Modes (rectangle/ellipse)
- Zoom controls

## Batch Manager
### batch_manager.py
Responsible for:
- Root folder `_para_procesar`
- `_processed` target folder
- `_output` folder for crops
- Scanning for unprocessed images
- Moving processed images
- Returning next image path
- Logging operations

API:
- scan()
- current_path()
- next()
- mark_current_processed()

## viewer.py
Main window:
- Hosts canvas + metadata panel + log panel
- Orchestrates everything
- Manages BatchManager + ActivityLog
- Connects toolbar events to canvas
- Connects metadata changes to crop naming

## main.py
Bootstraps the QApplication and shows the main viewer window.

## Migration Plan
1. Create folder structure.
2. Move zoom/pan logic → viewport.py.
3. Move cropping logic → cropper.py.
4. Move selection logic → selection.py.
5. Implement CanvasWidget using these modules.
6. Port metadata panel UI code.
7. Create ActivityLog + LogPanel.
8. Implement BatchManager and integrate.
9. Clean old viewer code, connect modules.
10. Add zoom extents, zoom selection, zoom window.

## TODO
- Implement Selection refactor w/ handles
- Implement perfect mode fully
- Integrate batch workflow
- Integrate activity log UI
- Implement zoom-to-selection
- Improve dim overlay performance
- Later: polygonal selection (optional)
