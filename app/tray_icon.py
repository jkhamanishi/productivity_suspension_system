# cspell:disable

import pystray
from PIL import Image, ImageDraw, ImageFont


class SystemTrayIcon(pystray.Icon):
    def __init__(self, name) -> None:
        super().__init__(name, self.create_image(), name, pystray.Menu(
            pystray.MenuItem("Quit", self.stop)
        ))
    
    @staticmethod
    def create_image():
        image = Image.new('RGB', (64, 64), "#0067AC")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("courbd.ttf", 44)
        draw.text((6, -8), "PS", "white", font, stroke_width=1)
        draw.text((6, 24), "SI", "white", font, stroke_width=1)
        return image
