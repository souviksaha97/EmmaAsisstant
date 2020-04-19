import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import time
# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 64
# Change to 64 if needed
BORDER = 5

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c, reset=oled_reset)

image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
draw.rectangle((0, 0, oled.width, oled.height),
                   outline=0, fill=0)

text="They see me rollin'"
wait_time=300
(font_width, font_height) = font.getsize(text)
print(font_width, font_height)
while True:
    for x in range(0, font_width+oled.width):
        draw.rectangle((0, 0, oled.width, oled.height),
                   outline=0, fill=0)
        draw.text((oled.width-x,oled.height//2 - font_height//2),text,font=font,fill=255)
        oled.image(image)
        oled.show()
        time.sleep(0.001)
