# crop_manager.py
from PIL import Image, ImageDraw
import os

class CropManager:
    def __init__(self, output_dir="_output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def ensure_png(self, img):
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        return img

    def crop_rectangle(self, original, box):
        crop = original.crop(box)
        return self.ensure_png(crop)

    def crop_ellipse(self, original, box):
        crop = original.crop(box)
        crop = self.ensure_png(crop)

        # Crear máscara
        mask = Image.new("L", crop.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, crop.size[0], crop.size[1]), fill=255)

        crop.putalpha(mask)
        return crop

    def save_crop(self, img, page, variant):
        filename = f"{page}_{variant}.png"
        path = os.path.join(self.output_dir, filename)
        img.save(path, format="PNG")
        return path
