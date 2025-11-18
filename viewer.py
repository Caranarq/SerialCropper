import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout,
    QLabel, QLineEdit, QFileDialog, QToolBar, QAction,
    QStatusBar, QRadioButton
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QRectF


# ============================================================
# CANVAS: Dibuja y maneja zoom/pan/selección
# ============================================================
class CanvasWidget(QWidget):
    def __init__(self, viewer):
        super().__init__(viewer)
        self.viewer = viewer

        # Estado de imagen
        self.pixmap_original = None
        self.scale = 1.0
        self.min_scale = 0.1
        self.max_scale = 16.0
        self.offset = QPointF(0.0, 0.0)

        # Selección
        self.selecting = False
        self.sel_start_img = None
        self.sel_end_img = None
        self.selection_exists = False

        # Modo de selección: "rect" o "ellipse"
        self.select_mode = "rect"

        # Pan
        self.panning = False
        self.pan_last_pos = None

    # -----------------------------
    # API desde el viewer
    # -----------------------------
    def set_pixmap(self, pixmap: QPixmap):
        self.pixmap_original = pixmap
        self.scale = 1.0
        self.offset = QPointF(
            (self.width() - pixmap.width()) / 2,
            (self.height() - pixmap.height()) / 2,
        )
        self.clear_selection()
        self.update()

    def reset_view(self):
        if not self.pixmap_original:
            return
        self.scale = 1.0
        self.offset = QPointF(
            (self.width() - self.pixmap_original.width()) / 2,
            (self.height() - self.pixmap_original.height()) / 2,
        )
        self.update()

    def set_select_mode(self, mode: str):
        if mode not in ("rect", "ellipse"):
            return
        self.select_mode = mode
        self.clear_selection()

    # -----------------------------
    # Helpers de coordenadas
    # -----------------------------
    def screen_to_image(self, pos):
        x = (pos.x() - self.offset.x()) / self.scale
        y = (pos.y() - self.offset.y()) / self.scale
        return QPointF(x, y)

    def image_to_screen(self, pt):
        return QPointF(
            pt.x() * self.scale + self.offset.x(),
            pt.y() * self.scale + self.offset.y(),
        )

    def _selection_screen_rect(self):
        if self.sel_start_img is None or self.sel_end_img is None:
            return None
        p1 = self.image_to_screen(self.sel_start_img)
        p2 = self.image_to_screen(self.sel_end_img)
        return QRectF(p1, p2).normalized()

    # -----------------------------
    # Paint
    # -----------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(32, 32, 32))

        if not self.pixmap_original:
            return

        # Imagen
        painter.save()
        painter.translate(self.offset)
        painter.scale(self.scale, self.scale)
        painter.drawPixmap(0, 0, self.pixmap_original)
        painter.restore()

        # Selección + oscurecido
        if self.selection_exists and self.sel_start_img and self.sel_end_img:
            r = self._selection_screen_rect()
            if r is not None:
                painter.setRenderHint(QPainter.Antialiasing, True)

                dim_color = QColor(0, 0, 0, 140)
                canvas_rect = self.rect()

                # Camino oscuro global
                dark_path = QPainterPath()
                dark_path.addRect(QRectF(canvas_rect))

                # Hueco según modo
                hole_path = QPainterPath()
                if self.select_mode == "ellipse":
                    hole_path.addEllipse(r)
                else:
                    hole_path.addRect(r)

                # Resta: todo oscuro menos el hueco
                final_path = dark_path.subtracted(hole_path)
                painter.fillPath(final_path, dim_color)

                # Borde rojo
                pen = QPen(QColor(255, 60, 60), 2)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)

                if self.select_mode == "ellipse":
                    painter.drawEllipse(r)
                else:
                    painter.drawRect(r)

    # -----------------------------
    # Mouse
    # -----------------------------
    def mousePressEvent(self, event):
        if not self.pixmap_original:
            return

        if event.button() == Qt.LeftButton:
            self.selecting = True
            img = self.screen_to_image(event.pos())
            self.sel_start_img = img
            self.sel_end_img = img
            self.selection_exists = True
            self.update()

        elif event.button() == Qt.MiddleButton:
            self.panning = True
            self.pan_last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.pixmap_original:
            return

        if self.selecting:
            p_img = self.screen_to_image(event.pos())

            # Shift = cuadrado / círculo perfecto
            perfect = bool(event.modifiers() & Qt.ShiftModifier)
            if perfect and self.sel_start_img is not None:
                start_screen = self.image_to_screen(self.sel_start_img)
                cur = event.pos()
                dx = cur.x() - start_screen.x()
                dy = cur.y() - start_screen.y()
                side = max(abs(dx), abs(dy))
                dx_sign = 1 if dx >= 0 else -1
                dy_sign = 1 if dy >= 0 else -1
                new_screen = QPointF(
                    start_screen.x() + dx_sign * side,
                    start_screen.y() + dy_sign * side,
                )
                p_img = self.screen_to_image(new_screen.toPoint())

            self.sel_end_img = p_img
            self.selection_exists = True
            self.update()

        elif self.panning:
            cur = event.pos()
            delta = cur - self.pan_last_pos
            self.offset += QPointF(delta.x(), delta.y())
            self.pan_last_pos = cur
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selecting = False
        elif event.button() == Qt.MiddleButton:
            self.panning = False
            self.pan_last_pos = None

    # -----------------------------
    # Zoom
    # -----------------------------
    def wheelEvent(self, event):
        if not self.pixmap_original:
            return

        mouse = event.pos()
        img_x = (mouse.x() - self.offset.x()) / self.scale
        img_y = (mouse.y() - self.offset.y()) / self.scale

        if event.angleDelta().y() > 0:
            self.scale *= 1.15
        else:
            self.scale /= 1.15

        self.scale = max(self.min_scale, min(self.scale, self.max_scale))
        self.offset.setX(mouse.x() - img_x * self.scale)
        self.offset.setY(mouse.y() - img_y * self.scale)
        self.update()

    def zoom_button(self, factor):
        if not self.pixmap_original:
            return

        center = QPointF(self.width() / 2, self.height() / 2)
        img_x = (center.x() - self.offset.x()) / self.scale
        img_y = (center.y() - self.offset.y()) / self.scale

        self.scale *= factor
        self.scale = max(self.min_scale, min(self.scale, self.max_scale))

        self.offset.setX(center.x() - img_x * self.scale)
        self.offset.setY(center.y() - img_y * self.scale)
        self.update()

    # -----------------------------
    # Resize: mantener relativo al centro del canvas
    # -----------------------------
    def resizeEvent(self, event):
        if self.pixmap_original and event.oldSize().isValid():
            dw = event.size().width() - event.oldSize().width()
            dh = event.size().height() - event.oldSize().height()
            self.offset += QPointF(dw / 2, dh / 2)
        super().resizeEvent(event)

    # -----------------------------
    # Crop helper
    # -----------------------------
    def get_cropped_qpixmap(self):
        if not (self.selection_exists and self.sel_start_img and self.sel_end_img):
            return None

        # Bounding box en coordenadas imagen
        r = QRectF(self.sel_start_img, self.sel_end_img).normalized()
        left = int(max(0, r.left()))
        top = int(max(0, r.top()))
        right = int(min(self.pixmap_original.width(), r.right()))
        bottom = int(min(self.pixmap_original.height(), r.bottom()))
        w = right - left
        h = bottom - top

        if w <= 0 or h <= 0:
            return None

        # -----------------------------------
        # MODO RECTANGULAR (sin cambios)
        # -----------------------------------
        if self.select_mode == "rect":
            return self.pixmap_original.copy(left, top, w, h)

        # -----------------------------------
        # MODO ELÍPTICO (PNG con transparencia)
        # -----------------------------------
        # 1. Recorte rectangular base
        src = self.pixmap_original.copy(left, top, w, h)

        # 2. Pixmap de salida con alfa
        result = QPixmap(w, h)
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 3. Crear máscara elíptica
        path = QPainterPath()
        path.addEllipse(0, 0, w, h)
        painter.setClipPath(path)

        # 4. Dibujar imagen dentro de la máscara
        painter.drawPixmap(0, 0, src)

        painter.end()
        return result

    def clear_selection(self):
        self.selection_exists = False
        self.sel_start_img = None
        self.sel_end_img = None
        self.update()


# ============================================================
# IMAGE VIEWER (ventana principal + panel de metadatos)
# ============================================================
class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Serial Cropper")
        self.resize(1400, 900)

        # Metadata
        self.metadata = {
            "artist": "",
            "work": "",
            "work_initials": "",
            "page": "",
            "timestamp": "",
        }

        # Archivos
        self.output_dir = "_output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.current_folder = None
        self.current_file = None
        self.variant_counter = 1

        # Canvas
        self.canvas = CanvasWidget(self)

        # Toolbar, theme, status
        self._build_toolbar()
        self._setup_theme()

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Panel de metadatos
        self.meta_panel = QWidget()
        self.meta_layout = QVBoxLayout(self.meta_panel)
        self.meta_layout.setContentsMargins(12, 12, 12, 12)
        self.meta_layout.setSpacing(10)

        self.meta_layout.addWidget(QLabel("Artista:"))
        self.artist_edit = QLineEdit()
        self.meta_layout.addWidget(self.artist_edit)

        self.meta_layout.addWidget(QLabel("Obra:"))
        self.work_edit = QLineEdit()
        self.meta_layout.addWidget(self.work_edit)

        self.meta_layout.addWidget(QLabel("Página:"))
        self.page_edit = QLineEdit()
        self.meta_layout.addWidget(self.page_edit)

        self.meta_layout.addWidget(QLabel("Fecha/Hora:"))
        self.date_label = QLabel("")
        self.meta_layout.addWidget(self.date_label)

        # Controles de selección
        self.meta_layout.addWidget(QLabel("Selección:"))
        self.rect_radio = QRadioButton("Rectangular")
        self.ellipse_radio = QRadioButton("Elíptica")
        self.rect_radio.setChecked(True)
        self.meta_layout.addWidget(self.rect_radio)
        self.meta_layout.addWidget(self.ellipse_radio)

        self.meta_layout.addStretch()

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.canvas)
        splitter.addWidget(self.meta_panel)
        splitter.setSizes([1100, 300])
        self.setCentralWidget(splitter)

        # Bind metadata
        self.artist_edit.textChanged.connect(self._update_metadata)
        self.work_edit.textChanged.connect(self._update_metadata)
        self.page_edit.textChanged.connect(self._update_metadata)

        # Bind selección
        self.rect_radio.toggled.connect(self._on_selection_mode_changed)
        self.ellipse_radio.toggled.connect(self._on_selection_mode_changed)

    # -----------------------------
    # Theme
    # -----------------------------
    def _setup_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #202020;
            }
            QToolBar {
                background: #2a2a2a;
                padding: 4px;
                spacing: 6px;
                border-bottom: 1px solid #111;
            }
            QToolButton {
                background: transparent;
                color: #f0f0f0;
                padding: 4px 8px;
                border: none;
            }
            QToolButton:hover {
                background: #3a3a3a;
            }
            QToolButton:pressed {
                background: #505050;
            }
            QStatusBar {
                background: #2a2a2a;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QRadioButton {
                color: #e0e0e0;
            }
            QLineEdit {
                background: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                padding: 4px;
            }
        """)

    # -----------------------------
    # Toolbar
    # -----------------------------
    def _build_toolbar(self):
        tb = QToolBar("Main")
        self.addToolBar(tb)

        act_open = QAction("Open", self)
        act_open.triggered.connect(self.open_image_dialog)
        tb.addAction(act_open)

        tb.addSeparator()

        act_zoom_in = QAction("Zoom +", self)
        act_zoom_in.triggered.connect(lambda: self.canvas.zoom_button(1.15))
        tb.addAction(act_zoom_in)

        act_zoom_out = QAction("Zoom -", self)
        act_zoom_out.triggered.connect(lambda: self.canvas.zoom_button(1 / 1.15))
        tb.addAction(act_zoom_out)

        act_reset = QAction("Reset", self)
        act_reset.triggered.connect(self.canvas.reset_view)
        tb.addAction(act_reset)

        tb.addSeparator()

        act_save = QAction("Save Crop", self)
        act_save.triggered.connect(lambda: self.save_crop(False))
        tb.addAction(act_save)

        act_save_keep = QAction("Save & Keep", self)
        act_save_keep.triggered.connect(lambda: self.save_crop(True))
        tb.addAction(act_save_keep)

        tb.addSeparator()

        act_next = QAction("Next", self)
        act_next.triggered.connect(self.open_next_in_folder)
        tb.addAction(act_next)

    # -----------------------------
    # Metadata
    # -----------------------------
    def _update_metadata(self):
        self.metadata["artist"] = self.artist_edit.text().strip()
        self.metadata["work"] = self.work_edit.text().strip()
        self.metadata["page"] = self.page_edit.text().strip()

        words = self.metadata["work"].split()
        self.metadata["work_initials"] = "".join(
            w[0].upper() for w in words if w
        ) if words else ""

        self.metadata["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _build_filename_base(self):
        def clean(s):
            s = s.replace(" ", "_")
            return "".join(c for c in s if c.isalnum() or c in "_-")

        artist = clean(self.metadata["artist"] or "ND")
        work_init = clean(self.metadata["work_initials"] or "ND")
        page = clean(self.metadata["page"] or "000")

        return f"{artist}_{work_init}_{page}"

    # -----------------------------
    # Cambio de modo de selección
    # -----------------------------
    def _on_selection_mode_changed(self):
        if self.rect_radio.isChecked():
            self.canvas.set_select_mode("rect")
        elif self.ellipse_radio.isChecked():
            self.canvas.set_select_mode("ellipse")

    # -----------------------------
    # Hotkeys
    # -----------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:
            self.rect_radio.setChecked(True)
        elif event.key() == Qt.Key_E:
            self.ellipse_radio.setChecked(True)
        else:
            super().keyPressEvent(event)

    # -----------------------------
    # Carga de imagen
    # -----------------------------
    def open_image_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            self.load_image(path)

    def load_image(self, path):
        pix = QPixmap(path)
        if pix.isNull():
            self.status.showMessage("Error loading image", 3000)
            return

        self.canvas.set_pixmap(pix)

        self.current_file = path
        self.current_folder = os.path.dirname(path)
        self.variant_counter = 1

        filename = os.path.basename(path)
        page = os.path.splitext(filename)[0]
        self.page_edit.setText(page)

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.date_label.setText(now)

        self._update_metadata()
        self.status.showMessage(f"Loaded: {filename}", 3000)

    # -----------------------------
    # Save crop
    # -----------------------------
    def save_crop(self, keep):
        cropped = self.canvas.get_cropped_qpixmap()
        if cropped is None:
            self.status.showMessage("No valid selection", 2000)
            return

        base = self._build_filename_base()
        filename = f"{base}({self.variant_counter}).png"
        path = os.path.join(self.output_dir, filename)

        while os.path.exists(path):
            self.variant_counter += 1
            filename = f"{base}({self.variant_counter}).png"
            path = os.path.join(self.output_dir, filename)

        if cropped.save(path, "PNG"):
            self.status.showMessage(f"Saved {filename}", 3000)
            self.variant_counter += 1
            if not keep:
                self.canvas.clear_selection()
        else:
            self.status.showMessage("Failed to save", 3000)

    # -----------------------------
    # Next
    # -----------------------------
    def open_next_in_folder(self):
        if not self.current_folder or not self.current_file:
            return

        files = sorted(
            f for f in os.listdir(self.current_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))
        )
        if not files:
            return

        cur = os.path.basename(self.current_file)
        try:
            idx = files.index(cur)
        except ValueError:
            idx = -1

        next_idx = (idx + 1) % len(files)
        next_path = os.path.join(self.current_folder, files[next_idx])
        self.load_image(next_path)
