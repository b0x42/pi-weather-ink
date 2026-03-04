# Driver for Waveshare 4.2inch e-Paper Module (G) — 4-color (black/white/red/yellow)
# Source: https://github.com/waveshareteam/e-Paper/tree/master/E-paper_Separate_Program/4in2_e-Paper_G
# Bundled here because this display is not included in the waveshare-epaper PyPI package.

import logging
from PIL import Image

try:
    from waveshare_epd import epdconfig
except ImportError:
    from . import epdconfig  # fallback for local install

EPD_WIDTH = 400
EPD_HEIGHT = 300

logger = logging.getLogger(__name__)


class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.BLACK = 0x000000
        self.WHITE = 0xffffff
        self.YELLOW = 0x00ffff
        self.RED = 0x0000ff

    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200)
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200)

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte2(data)
        epdconfig.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        logger.debug("e-Paper busy H")
        epdconfig.delay_ms(100)
        while epdconfig.digital_read(self.busy_pin) == 0:
            epdconfig.delay_ms(5)
        logger.debug("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x12)
        self.send_data(0x00)
        self.ReadBusy()

    def init(self):
        if epdconfig.module_init() != 0:
            return -1
        self.reset()
        self.ReadBusy()
        self.send_command(0x4D)
        self.send_data(0x78)
        self.send_command(0x00)
        self.send_data(0x0F)
        self.send_data(0x29)
        self.send_command(0x06)
        self.send_data(0x0d)
        self.send_data(0x12)
        self.send_data(0x24)
        self.send_data(0x25)
        self.send_data(0x12)
        self.send_data(0x29)
        self.send_data(0x10)
        self.send_command(0x30)
        self.send_data(0x08)
        self.send_command(0x50)
        self.send_data(0x37)
        self.send_command(0x61)
        self.send_data(0x01)
        self.send_data(0x90)
        self.send_data(0x01)
        self.send_data(0x2C)
        self.send_command(0xae)
        self.send_data(0xcf)
        self.send_command(0xb0)
        self.send_data(0x13)
        self.send_command(0xbd)
        self.send_data(0x07)
        self.send_command(0xbe)
        self.send_data(0xfe)
        self.send_command(0xE9)
        self.send_data(0x01)
        self.send_command(0x04)
        self.ReadBusy()
        return 0

    def getbuffer(self, image):
        pal_image = Image.new("P", (1, 1))
        pal_image.putpalette((0, 0, 0, 255, 255, 255, 255, 255, 0, 255, 0, 0) + (0, 0, 0) * 252)

        imwidth, imheight = image.size
        if imwidth == self.width and imheight == self.height:
            image_temp = image
        elif imwidth == self.height and imheight == self.width:
            image_temp = image.rotate(90, expand=True)
        else:
            logger.warning("Invalid image dimensions: %d x %d, expected %d x %d",
                           imwidth, imheight, self.width, self.height)
            image_temp = image

        image_4color = image_temp.convert("RGB").quantize(palette=pal_image)
        buf_4color = bytearray(image_4color.tobytes('raw'))

        Width = self.width // 4 if self.width % 4 == 0 else self.width // 4 + 1
        Height = self.height
        buf = [0x00] * int(Width * Height)
        idx = 0
        for j in range(Height):
            for i in range(Width):
                buf[i + j * Width] = (
                    (buf_4color[idx] << 6) +
                    (buf_4color[idx + 1] << 4) +
                    (buf_4color[idx + 2] << 2) +
                    buf_4color[idx + 3]
                )
                idx += 4
        return buf

    def display(self, image):
        self.send_command(0x10)
        self.send_data2(image)
        self.TurnOnDisplay()

    def Clear(self, color=0x55):
        Width = self.width // 4 if self.width % 4 == 0 else self.width // 4 + 1
        Height = self.height
        self.send_command(0x10)
        for j in range(Height):
            for i in range(Width):
                self.send_data(color)
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x02)
        self.send_data(0x00)
        epdconfig.delay_ms(100)
        self.send_command(0x07)
        self.send_data(0xA5)
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
