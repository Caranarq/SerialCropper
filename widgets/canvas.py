from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QPixmap, QCursor
from PyQt5.QtCore import Qt, QRectF, QPointF

from core.viewport import Viewport
from core.selection import Selection, HitTest
from core.cropper import Cropper

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.viewport = Viewport()
        self.selection = Selection()
        
        self.pixmap = None
        self.panning = False
        self.pan_last_pos = None

    def set_pixmap(self, pixmap: QPixmap):
        self.pixmap = pixmap
        if pixmap:
            self.viewport.fit_extents(self.width(), self.height(), pixmap.width(), pixmap.height())
        self.selection.clear()
        self.update()

    def set_select_mode(self, mode: str):
        self.selection.set_mode(mode)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(32, 32, 32))

        if not self.pixmap:
            return

        # Draw Image
        painter.save()
        painter.translate(self.viewport.offset)
        painter.scale(self.viewport.scale, self.viewport.scale)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.restore()

        # Draw Selection
        if self.selection.has_selection():
            r_img = self.selection.get_rect()
            
            # To draw rotated, we need to map the center to screen, then rotate painter
            center_img = r_img.center()
            center_screen = self.viewport.image_to_screen(center_img)
            
            # Calculate width/height in screen coords
            # Since scale is uniform, we can just scale dimensions
            w_screen = r_img.width() * self.viewport.scale
            h_screen = r_img.height() * self.viewport.scale
            
            # Create rect centered at 0,0 for drawing after translation
            r_draw = QRectF(-w_screen/2, -h_screen/2, w_screen, h_screen)

            painter.save()
            painter.translate(center_screen)
            painter.rotate(self.selection.angle)
            
            painter.setRenderHint(QPainter.Antialiasing, True)
            dim_color = QColor(0, 0, 0, 140)
            
            # Dimming is tricky with rotation. 
            # Simplest approach: Draw full screen dim, then subtract the rotated shape?
            # QPainterPath supports subtraction.
            
            # Reset transform for the "Outer" path (screen rect)
            painter.restore() 
            painter.save()
            
            path = QPainterPath()
            path.addRect(QRectF(self.rect()))
            
            # Create the "Hole" path
            hole_path = QPainterPath()
            
            # We need the hole path in SCREEN coordinates but rotated
            # So we create it centered, rotate it, then translate it
            temp_path = QPainterPath()
            if self.selection.mode == "ellipse":
                temp_path.addEllipse(r_draw)
            else:
                temp_path.addRect(r_draw)
                
            # Apply transform to path manually
            from PyQt5.QtGui import QTransform
            transform = QTransform()
            transform.translate(center_screen.x(), center_screen.y())
            transform.rotate(self.selection.angle)
            hole_path = transform.map(temp_path)
            
            final_path = path.subtracted(hole_path)
            painter.fillPath(final_path, dim_color)
            
            # Now draw the border and handles (using the rotated coordinate system)
            painter.translate(center_screen)
            painter.rotate(self.selection.angle)
            
            pen = QPen(QColor(255, 60, 60), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            if self.selection.mode == "ellipse":
                painter.drawEllipse(r_draw)
            else:
                painter.drawRect(r_draw)
                
            # Handles
            self._draw_handles(painter, r_draw)
            
            painter.restore()

    def _draw_handles(self, painter, rect):
        handle_size = 8
        half = handle_size / 2
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        
        points = [
            rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight(),
            QPointF(rect.center().x(), rect.top()),
            QPointF(rect.center().x(), rect.bottom()),
            QPointF(rect.left(), rect.center().y()),
            QPointF(rect.right(), rect.center().y())
        ]
        
        for p in points:
            painter.drawRect(QRectF(p.x() - half, p.y() - half, handle_size, handle_size))
            
        # Rotation Handle
        # Sticking out from top center
        top_center = QPointF(rect.center().x(), rect.top())
        handle_center = QPointF(rect.center().x(), rect.top() - 20)
        
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawLine(top_center, handle_center)
        
        painter.setBrush(QColor(255, 255, 0)) # Yellow for rotation
        painter.drawEllipse(handle_center, 4, 4)

    def mousePressEvent(self, event):
        self.setFocus() # Claim focus on click
        if not self.pixmap:
            return

        if event.button() == Qt.LeftButton:
            img_pos = self.viewport.screen_to_image(event.pos())
            
            # Check for hit
            hit = self.selection.hit_test(img_pos, self.viewport.scale)
            
            if hit != HitTest.NONE:
                self.selection.start_modification(img_pos, hit)
            else:
                self.selection.start(img_pos)
            
            self.update()
            
        elif event.button() == Qt.MiddleButton:
            self.panning = True
            self.pan_last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.pixmap:
            return

        img_pos = self.viewport.screen_to_image(event.pos())

        if self.selection.active_handle != HitTest.NONE:
            # Modifying (Move or Resize)
            is_perfect = bool(event.modifiers() & Qt.ShiftModifier)
            self.selection.update_modification(img_pos, is_perfect)
            self.update()
            
        elif self.selection.is_dragging:
            # Creating new
            is_perfect = bool(event.modifiers() & Qt.ShiftModifier)
            self.selection.update(img_pos, is_perfect)
            self.update()
            
        elif self.panning:
            delta = event.pos() - self.pan_last_pos
            self.viewport.pan(delta)
            self.pan_last_pos = event.pos()
            self.update()
            
        else:
            # Hover - Update cursor
            hit = self.selection.hit_test(img_pos, self.viewport.scale)
            self._update_cursor(hit)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selection.finish()
        elif event.button() == Qt.MiddleButton:
            self.panning = False

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

    def _update_cursor(self, hit):
        if hit in (HitTest.TOP_LEFT, HitTest.BOTTOM_RIGHT):
            self.setCursor(Qt.SizeFDiagCursor)
        elif hit in (HitTest.TOP_RIGHT, HitTest.BOTTOM_LEFT):
            self.setCursor(Qt.SizeBDiagCursor)
        elif hit in (HitTest.TOP, HitTest.BOTTOM):
            self.setCursor(Qt.SizeVerCursor)
        elif hit in (HitTest.LEFT, HitTest.RIGHT):
            self.setCursor(Qt.SizeHorCursor)
        elif hit == HitTest.INSIDE:
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event):
        if not self.pixmap:
            return
        
        factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        self.viewport.zoom(factor, event.pos())
        self.update()

    def resizeEvent(self, event):
        self.viewport.apply_resize(event.oldSize(), event.size())
        super().resizeEvent(event)

    def get_crop(self):
        if not self.selection.has_selection():
            return None
        return Cropper.crop(self.pixmap, self.selection.get_rect(), self.selection.angle, self.selection.mode)
    
    def reset_view(self):
        if self.pixmap:
            self.viewport.fit_extents(self.width(), self.height(), self.pixmap.width(), self.pixmap.height())
            self.update()
    
    def zoom(self, factor):
        if self.pixmap:
            center = QPointF(self.width() / 2, self.height() / 2)
            self.viewport.zoom(factor, center)
            self.update()

    def zoom_extents(self):
        if self.pixmap:
            self.viewport.fit_extents(self.width(), self.height(), self.pixmap.width(), self.pixmap.height())
            self.update()
            
    def zoom_100(self):
        if self.pixmap:
            self.viewport.set_one_to_one(self.width(), self.height(), self.pixmap.width(), self.pixmap.height())
            self.update()

    def zoom_selection(self):
        if self.pixmap and self.selection.has_selection():
            self.viewport.zoom_to_rect(self.selection.get_rect(), self.width(), self.height())
            self.update()
