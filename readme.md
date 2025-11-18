# 📘 SerialCropper
### *Fast, batch-oriented crop tool for manga pages and artwork*

**SerialCropper** is a desktop application built with **Python + PyQt5**, designed for **extremely fast, sequential cropping** of images.

The goal is simple:  
👉 **cut images as fast as humanly possible**, one after another, with a clean workflow and minimal friction.

---

## 🚀 Features

- 🖼 **Smooth canvas** with zoom & pan (Paint.NET-style)  
- 🔳 **Rectangular selection**  
- 🟠 **Elliptical selection with alpha-transparent PNG output**  
- ↔️ **Perfect Mode (Shift)**  
  - Rectangle → square  
  - Ellipse → circle  
- 🎯 **Selection handles** (edges & corners) for fine adjustments  
- 🔦 **Dynamic dimming** outside the selection (rect & ellipse)  
- ✂️ **PNG export** with transparency when using ellipse  
- 📂 **Batch navigation** through folders  
- 📝 **Editable metadata panel** (artist, work, page, timestamp)  
- 📜 **Recent activity log**  
- ⌨️ **Keyboard shortcuts for fast workflow**  

---

## 📁 Project Structure

```
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
        toolbar.py      (optional)
    batch/
        batch_manager.py
    viewer.py
    main.py
```

### 📌 Module Overview

#### `core/`
Pure logic: selection behavior, cropping engine, viewport math, logging utilities.  
No UI dependencies.

#### `widgets/`
Qt widgets: canvas, metadata panel, log panel, toolbar.

#### `batch/`
Manages folder-based workflows (`_para_procesar`, `_processed`, `_output`).

#### `viewer.py`
Main window controller: connects canvas, panels, batch manager, and toolbar.

#### `main.py`
Application entry point.

---

## 🔄 Workflow

1. Select root folder (`_para_procesar`)  
2. SerialCropper loads the first image  
3. Make as many crops as needed  
4. Save crop → PNG goes to `_output`  
5. When done with the current image:
   - it is moved to `_processed`
   - the next image loads automatically  
6. Repeat until finished

Designed for **rapid iteration** and zero mental overhead.

---

## 🧠 Advanced Selection System

- **Shift** toggles Perfect Mode:
  - Rectangle → Square  
  - Ellipse → Circle  
- Shift can be pressed or released **during drag**  
- Handles allow adjusting the selection after drawing  
- Dimmed overlay respects both rectangle and ellipse shapes  
- Behavior matches professional editors (Paint.NET, Photoshop)

---

## 🛠 Installation & Running

### Requirements

- Python 3.10+
- PyQt5

### Install

```bash
git clone https://github.com/yourname/serial_cropper.git
cd serial_cropper
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

---

## 🔧 Roadmap

- [ ] Zoom Selection  
- [ ] Zoom Window  
- [ ] Polygonal selection (future)  
- [ ] Sticker Cloud (future sticker workflow)  
- [ ] Undo/Redo for key actions  
- [ ] Large-batch optimization  
- [ ] Plugin-ready structure  

---

## 🤝 Contributing

Contributions are welcome.  
Follow the modular architecture and keep responsibilities separated by module.

---

## 📄 License

MIT — free to use, modify, and extend.
