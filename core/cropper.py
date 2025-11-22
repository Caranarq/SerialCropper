from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QColor
from PyQt5.QtCore import Qt, QRectF

class Cropper:
    @staticmethod
    def crop(pixmap: QPixmap, rect: QRectF, angle: float = 0.0, mode: str = "rect") -> QPixmap:
        if angle != 0 or mode == "ellipse":
            return Cropper.crop_rotated(pixmap, rect, angle, mode)
            
        if not pixmap or rect.isEmpty():
            return None

        # Normalize and integerize
        r = rect.normalized()
        left = int(max(0, r.left()))
        top = int(max(0, r.top()))
        right = int(min(pixmap.width(), r.right()))
        bottom = int(min(pixmap.height(), r.bottom()))
        w = right - left
        h = bottom - top

        if w <= 0 or h <= 0:
            return None

        if mode == "rect":
            return pixmap.copy(left, top, w, h)
        
        return None

    @staticmethod
    def crop_rotated(pixmap: QPixmap, rect: QRectF, angle: float, mode: str = "rect") -> QPixmap:
        if not pixmap or rect.isEmpty():
            return None
            
        # 1. Create a new transparent pixmap of the target size (selection size)
        # We use the full width/height of the selection
        w = int(rect.width())
        h = int(rect.height())
        
        result = QPixmap(w, h)
        result.fill(Qt.transparent)
        
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # Masking for Ellipse (Apply ClipPath BEFORE transforms)
        if mode == "ellipse":
            path = QPainterPath()
            path.addEllipse(0, 0, w, h)
            painter.setClipPath(path)
        
        # 2. Setup the coordinate system to draw the source image into our result
        # We want the center of the selection to map to the center of our result
        
        # Move painter to center of result
        painter.translate(w / 2, h / 2)
        
        # Rotate painter by -angle (to counter-rotate the image into place)
        painter.rotate(-angle)
        
        # Translate back to the top-left of the source image relative to the selection center
        center_src = rect.center()
        painter.translate(-center_src.x(), -center_src.y())
        
        # 3. Draw the source pixmap
        painter.drawPixmap(0, 0, pixmap)
            
        painter.end()
        return result
