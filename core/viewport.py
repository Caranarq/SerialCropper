from PyQt5.QtCore import QPointF

class Viewport:
    def __init__(self):
        self.scale = 1.0
        self.offset = QPointF(0.0, 0.0)
        self.min_scale = 0.1
        self.max_scale = 16.0

    def fit_extents(self, view_width, view_height, img_width, img_height):
        # Fit to extents
        scale_w = view_width / img_width
        scale_h = view_height / img_height
        self.scale = min(scale_w, scale_h) * 0.95 # 5% margin
        
        # Center
        self.offset = QPointF(
            (view_width - img_width * self.scale) / 2,
            (view_height - img_height * self.scale) / 2,
        )

    def set_one_to_one(self, view_width, view_height, img_width, img_height):
        self.scale = 1.0
        # Center
        self.offset = QPointF(
            (view_width - img_width) / 2,
            (view_height - img_height) / 2,
        )

    def zoom_to_rect(self, rect_img, view_width, view_height):
        if rect_img.isEmpty():
            return

        # Calculate scale to fit rect
        scale_w = view_width / rect_img.width()
        scale_h = view_height / rect_img.height()
        self.scale = min(scale_w, scale_h) * 0.75 # 25% margin (User requested context)
        self.scale = max(self.min_scale, min(self.scale, self.max_scale))

        # Center rect in view
        # The top-left of the rect in image coords should be positioned such that 
        # the center of the rect aligns with the center of the view
        
        # Center of rect in image coords
        center_img = rect_img.center()
        
        # We want center_img to be at (view_width/2, view_height/2) in screen coords
        # screen_x = img_x * scale + offset_x
        # offset_x = screen_x - img_x * scale
        
        self.offset = QPointF(
            view_width / 2 - center_img.x() * self.scale,
            view_height / 2 - center_img.y() * self.scale
        )

    def screen_to_image(self, pos: QPointF) -> QPointF:
        x = (pos.x() - self.offset.x()) / self.scale
        y = (pos.y() - self.offset.y()) / self.scale
        return QPointF(x, y)

    def image_to_screen(self, pt: QPointF) -> QPointF:
        return QPointF(
            pt.x() * self.scale + self.offset.x(),
            pt.y() * self.scale + self.offset.y(),
        )

    def zoom(self, factor, focus_point: QPointF):
        img_x = (focus_point.x() - self.offset.x()) / self.scale
        img_y = (focus_point.y() - self.offset.y()) / self.scale

        self.scale *= factor
        self.scale = max(self.min_scale, min(self.scale, self.max_scale))

        self.offset.setX(focus_point.x() - img_x * self.scale)
        self.offset.setY(focus_point.y() - img_y * self.scale)

    def pan(self, delta: QPointF):
        self.offset += delta

    def apply_resize(self, old_size, new_size):
        if old_size.isValid():
            dw = new_size.width() - old_size.width()
            dh = new_size.height() - old_size.height()
            self.offset += QPointF(dw / 2, dh / 2)
