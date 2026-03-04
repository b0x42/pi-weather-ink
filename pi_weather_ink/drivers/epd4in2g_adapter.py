"""Hardware adapter for epd4in2g (4-color display).

Bridges weatherstation's 2-buffer interface (black + red mode-"1" images)
to the epd4in2g driver which expects a single quantized 4-color RGB image.
"""

from PIL import Image, ImageChops
from .epd4in2g import EPD as _EPD


class EPD:
    """Adapter wrapping epd4in2g to match the standard waveshare_epd interface."""

    def __init__(self):
        self._epd = _EPD()
        self.width = self._epd.width
        self.height = self._epd.height

    def init(self):
        return self._epd.init()

    def sleep(self):
        self._epd.sleep()

    def Clear(self):
        self._epd.Clear()

    def getbuffer(self, image):
        """Passthrough — images are composited in display()."""
        return image

    def display(self, buf_black, buf_red=None):
        """Composite black and red mode-'1' images into RGB, then send to display."""
        rgb = self._composite(buf_black, buf_red)
        self._epd.display(self._epd.getbuffer(rgb))

    def _composite(self, img_black, img_red):
        """Merge two mode-'1' images into an RGB image for the 4-color driver.

        Pixel priority: red > black > white.
        Uses PIL paste with masks for efficiency.
        """
        rgb = Image.new("RGB", img_black.size, (255, 255, 255))

        black_mask = ImageChops.invert(img_black.convert("L"))
        rgb.paste(Image.new("RGB", img_black.size, (0, 0, 0)), mask=black_mask)

        if img_red is not None:
            red_mask = ImageChops.invert(img_red.convert("L"))
            rgb.paste(Image.new("RGB", img_red.size, (255, 0, 0)), mask=red_mask)

        return rgb
