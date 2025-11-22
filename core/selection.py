from PyQt5.QtCore import QPointF, QRectF
from enum import Enum, auto

class HitTest(Enum):
    NONE = auto()
    INSIDE = auto()
    TOP_LEFT = auto()
    TOP = auto()
    TOP_RIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM = auto()
    BOTTOM_RIGHT = auto()
    ROTATE = auto()

class Selection:
    def __init__(self):
        self.is_dragging = False
        self.start_img = None
        self.end_img = None
        self.mode = "rect"  # rect, ellipse
        
        # For modification
        self.active_handle = HitTest.NONE
        self.drag_start_pos = None
        self.initial_rect = None
        self.angle = 0.0

    def set_mode(self, mode: str):
        if mode in ("rect", "ellipse"):
            self.mode = mode

    def start(self, pos_img: QPointF):
        self.is_dragging = True
        self.start_img = pos_img
        self.end_img = pos_img
        self.angle = 0.0 # Reset angle on new selection

    def update(self, pos_img: QPointF, is_perfect: bool = False):
        if is_perfect and self.start_img:
            dx = pos_img.x() - self.start_img.x()
            dy = pos_img.y() - self.start_img.y()
            side = max(abs(dx), abs(dy))
            dx_sign = 1 if dx >= 0 else -1
            dy_sign = 1 if dy >= 0 else -1
            self.end_img = QPointF(
                self.start_img.x() + dx_sign * side,
                self.start_img.y() + dy_sign * side
            )
        else:
            self.end_img = pos_img

    def finish(self):
        self.is_dragging = False
        self.active_handle = HitTest.NONE

    def get_rect(self) -> QRectF:
        if self.start_img and self.end_img:
            return QRectF(self.start_img, self.end_img).normalized()
        return QRectF()
    
    def clear(self):
        self.is_dragging = False
        self.start_img = None
        self.end_img = None
        self.angle = 0.0
        self.active_handle = HitTest.NONE
    
    def has_selection(self):
        # Debug
        # print(f"DEBUG: has_selection: start={self.start_img}, end={self.end_img}")
        return self.start_img is not None and self.end_img is not None

    # -----------------------------
    # Advanced Interaction
    # -----------------------------
    def hit_test(self, pos_img: QPointF, scale: float, handle_radius_screen: float = 8.0) -> HitTest:
        if not self.has_selection():
            return HitTest.NONE
            
        r = self.get_rect()
        tol = handle_radius_screen / scale
        
        # Transform point to local selection coordinates for hit testing
        # Center of selection
        center = r.center()
        
        # Rotate point around center by -angle to align with unrotated rect
        import math
        rad = math.radians(-self.angle)
        dx = pos_img.x() - center.x()
        dy = pos_img.y() - center.y()
        
        local_x = center.x() + dx * math.cos(rad) - dy * math.sin(rad)
        local_y = center.y() + dx * math.sin(rad) + dy * math.cos(rad)
        local_pos = QPointF(local_x, local_y)

        # Helper for point distance
        def near(p1, p2):
            return (p1.x() - p2.x())**2 + (p1.y() - p2.y())**2 <= tol**2

        # Rotation Handle (Top Center + Offset)
        # In local coords, it's above the top edge
        rotate_handle_pos = QPointF(center.x(), r.top() - (20 / scale))
        if near(local_pos, rotate_handle_pos): return HitTest.ROTATE

        # Corners
        if near(local_pos, r.topLeft()): return HitTest.TOP_LEFT
        if near(local_pos, r.topRight()): return HitTest.TOP_RIGHT
        if near(local_pos, r.bottomLeft()): return HitTest.BOTTOM_LEFT
        if near(local_pos, r.bottomRight()): return HitTest.BOTTOM_RIGHT
        
        # Edges
        if abs(local_pos.y() - r.top()) <= tol and r.left() <= local_pos.x() <= r.right(): return HitTest.TOP
        if abs(local_pos.y() - r.bottom()) <= tol and r.left() <= local_pos.x() <= r.right(): return HitTest.BOTTOM
        if abs(local_pos.x() - r.left()) <= tol and r.top() <= local_pos.y() <= r.bottom(): return HitTest.LEFT
        if abs(local_pos.x() - r.right()) <= tol and r.top() <= local_pos.y() <= r.bottom(): return HitTest.RIGHT
        
        # Inside
        if r.contains(local_pos):
            return HitTest.INSIDE
            
        return HitTest.NONE

    def start_modification(self, pos_img: QPointF, handle: HitTest):
        self.active_handle = handle
        self.drag_start_pos = pos_img
        self.initial_rect = self.get_rect()
        self.initial_angle = self.angle

    def update_modification(self, pos_img: QPointF, is_perfect: bool = False):
        if self.active_handle == HitTest.NONE or not self.initial_rect:
            return

        if self.active_handle == HitTest.ROTATE:
            # Calculate angle from center to mouse
            center = self.initial_rect.center()
            import math
            dx = pos_img.x() - center.x()
            dy = pos_img.y() - center.y()
            
            # Angle in degrees. 0 is Right, -90 is Up.
            # We want the handle (at local top) to track mouse.
            current_angle = math.degrees(math.atan2(dy, dx))
            self.angle = current_angle + 90
            return

        if self.active_handle == HitTest.INSIDE:
            # Move: Translate everything
            delta = pos_img - self.drag_start_pos
            r = QRectF(self.initial_rect)
            r.translate(delta)
            self.start_img = r.topLeft()
            self.end_img = r.bottomRight()
            return

        # Resizing with Rotation
        # We need to anchor the opposite side/corner
        
        import math
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Unit vectors for the rotated axes
        u = QPointF(cos_a, sin_a)   # Local X
        v = QPointF(-sin_a, cos_a)  # Local Y
        
        r_init = self.initial_rect
        center_init = r_init.center()
        
        # Helper to get global pos of a local point (relative to initial center)
        def to_global(local_p):
            # Rotate local_p by angle then add to center_init
            lx = local_p.x()
            ly = local_p.y()
            gx = center_init.x() + lx * cos_a - ly * sin_a
            gy = center_init.y() + lx * sin_a + ly * cos_a
            return QPointF(gx, gy)

        # Determine Anchor Point (Global) and the "Moving Point" (Global) logic
        # We define the rect by (min_x, min_y) to (max_x, max_y) in local space relative to center
        w = r_init.width()
        h = r_init.height()
        half_w = w / 2
        half_h = h / 2
        
        # Local coords of corners relative to center
        # TL: (-hw, -hh), TR: (hw, -hh), BL: (-hw, hh), BR: (hw, hh)
        
        anchor_local = QPointF(0, 0)
        moving_handle_local = QPointF(0, 0)
        
        # Constraints: 0 = free, 1 = fixed
        constrain_x = False
        constrain_y = False
        
        if self.active_handle == HitTest.TOP_LEFT:
            anchor_local = QPointF(half_w, half_h)      # BR is anchor
        elif self.active_handle == HitTest.TOP_RIGHT:
            anchor_local = QPointF(-half_w, half_h)     # BL is anchor
        elif self.active_handle == HitTest.BOTTOM_LEFT:
            anchor_local = QPointF(half_w, -half_h)     # TR is anchor
        elif self.active_handle == HitTest.BOTTOM_RIGHT:
            anchor_local = QPointF(-half_w, -half_h)    # TL is anchor
        elif self.active_handle == HitTest.TOP:
            anchor_local = QPointF(0, half_h)           # Bottom Center is anchor (approx)
            # Actually for edge, we just fix the opposite edge coordinate
            constrain_x = True # Width doesn't change
        elif self.active_handle == HitTest.BOTTOM:
            anchor_local = QPointF(0, -half_h)          # Top Center
            constrain_x = True
        elif self.active_handle == HitTest.LEFT:
            anchor_local = QPointF(half_w, 0)           # Right Center
            constrain_y = True # Height doesn't change
        elif self.active_handle == HitTest.RIGHT:
            anchor_local = QPointF(-half_w, 0)          # Left Center
            constrain_y = True

        anchor_global = to_global(anchor_local)
        
        # Calculate vector from Anchor to Mouse
        vec = pos_img - anchor_global
        
        # Project vec onto u and v to get new width/height components
        # Dot product
        proj_x = vec.x() * u.x() + vec.y() * u.y()
        proj_y = vec.x() * v.x() + vec.y() * v.y()
        
        # Calculate new dimensions
        # Note: The direction depends on which handle.
        # e.g. if resizing Right (handle at +x), vector from Left (anchor) to Mouse should be positive X.
        
        new_w = w
        new_h = h
        
        # Adjust projections based on handle direction to ensure positive width/height
        # If handle is LEFT, anchor is RIGHT. Vector points Left (negative local X).
        # So width is abs(proj_x).
        
        # Simplification: We calculate the new local bounds relative to the anchor.
        # But simpler: Just use the absolute projection as the new size?
        # We need to be careful about flipping.
        
        if constrain_x:
            # Width unchanged
            dx_local = 0
        else:
            # Check handle 'polarity'
            if self.active_handle in (HitTest.LEFT, HitTest.TOP_LEFT, HitTest.BOTTOM_LEFT):
                # Mouse is 'left' of anchor. proj_x should be negative.
                # If proj_x is positive, we flipped.
                pass
            dx_local = proj_x

        if constrain_y:
            dy_local = 0
        else:
            dy_local = proj_y
            
        # Handle specific edge cases to get Size
        if self.active_handle == HitTest.RIGHT:
            new_w = dx_local # Anchor is Left. Mouse is Right. dx > 0.
        elif self.active_handle == HitTest.LEFT:
            new_w = -dx_local # Anchor is Right. Mouse is Left. dx < 0.
        elif self.active_handle == HitTest.BOTTOM:
            new_h = dy_local
        elif self.active_handle == HitTest.TOP:
            new_h = -dy_local
        elif self.active_handle == HitTest.BOTTOM_RIGHT:
            new_w = dx_local
            new_h = dy_local
        elif self.active_handle == HitTest.TOP_LEFT:
            new_w = -dx_local
            new_h = -dy_local
        elif self.active_handle == HitTest.TOP_RIGHT:
            new_w = dx_local
            new_h = -dy_local
        elif self.active_handle == HitTest.BOTTOM_LEFT:
            new_w = -dx_local
            new_h = dy_local

        # Minimum size constraint
        new_w = max(1.0, new_w)
        new_h = max(1.0, new_h)
        
        # Calculate New Center
        # The new center is: Anchor + (NewSize / 2) * DirectionFromAnchor
        # DirectionFromAnchor depends on handle.
        
        dir_x = 0
        dir_y = 0
        
        if self.active_handle in (HitTest.RIGHT, HitTest.TOP_RIGHT, HitTest.BOTTOM_RIGHT): dir_x = 1
        if self.active_handle in (HitTest.LEFT, HitTest.TOP_LEFT, HitTest.BOTTOM_LEFT): dir_x = -1
        
        if self.active_handle in (HitTest.BOTTOM, HitTest.BOTTOM_LEFT, HitTest.BOTTOM_RIGHT): dir_y = 1
        if self.active_handle in (HitTest.TOP, HitTest.TOP_LEFT, HitTest.TOP_RIGHT): dir_y = -1
        
        # Offset from Anchor to New Center in Local Space
        offset_local_x = (new_w / 2) * dir_x
        offset_local_y = (new_h / 2) * dir_y
        
        # Rotate this offset to global
        offset_global_x = offset_local_x * cos_a - offset_local_y * sin_a
        offset_global_y = offset_local_x * sin_a + offset_local_y * cos_a
        
        new_center = QPointF(
            anchor_global.x() + offset_global_x,
            anchor_global.y() + offset_global_y
        )
        
        # Update start_img / end_img to match new_center and new_w/h
        # We construct an unrotated rect centered at new_center
        self.start_img = QPointF(new_center.x() - new_w/2, new_center.y() - new_h/2)
        self.end_img = QPointF(new_center.x() + new_w/2, new_center.y() + new_h/2)
