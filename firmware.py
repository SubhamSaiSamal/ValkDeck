import time
import board
import busio
import digitalio
import usb_hid
import rotaryio
import neopixel
import keypad
import pwmio
import displayio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode


# ------ 1. USB HID SETUP -------
kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

# ------ 2. SWITCH MATRIX SETUP -------

# Diodes are pointing from row to column (cathode to anode)

row_pins = (board.GP09, board.GP10, board.GP11)
col_pins = (board.GP00, board.GP01, board.GP02)

keys = keypad.KeyMatrix(
    row_pins = row_pins,
    column_pins = col_pins,
    columns_to_rows = False
)

# Keymap for the 3x3 matrix

keymap = [
    Keycode.Q, Keycode.W, Keycode.E, #Row 0
    Keycode.A, Keycode.S, Keycode.D, #Row 1
    Keycode.Z, Keycode.X, Keycode.C, #Row 2
]

# Name to be shown on the OLED when pressed

key_names = ["Macro : Q", "Macro : W", "Macro : E",
             "Macro : A", "Macro : S", "Macro : D",
             "Macro : Z", "Macro : X", "Macro : C"]

# ------ 3. ROTARY ENCODER SETUP --------

encoder = rotaryio.IncrementalEncoder(board.GP03, board.GP04)
last_position = encoder.position

encoder_button = digitalio.DigitalInOut(board.GP05)
encoder_button.direction = digitalio.Direction.INPUT
encoder_button.pull = digitalio.Pull.UP

# -------- 4. NEOPIXEL SETUP ---------

num_pixels = 9
pixels = neopixel.NeoPixel(board.GP15, num_pixels, brightness = 0.3, auto_write = False)
pixels.fill(80, 0, 120) 
pixels.show()

# ------- 5. BUZZER SETUP --------

buzzer = pwmio.PWMOut(board.GP19, variable_frequency = True)
buzzer.duty_cycle = 0

def beep(freq, duration):
    buzzer.frequency = freq
    buzzer.duty_cycle = 32768
    time.sleep(duration)
    buzzer.duty_cycle = 0

beep(1000, 0.2) # Boot Beep!

# ------ OLED SETUP --------

# OLED code would go here, but it's not included in this snippet.

displayio.release_displays() # Remove any old display data on reboot
i2c = busio.I2C(scl=board.GP17, sda=board.GP16)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width = 128, height = 32)

# Create the display content

splash = displayio.Group()
display.root_group = splash

# Set up the text label

text_area = label.Label(terminalio.FONT, text="VALKDECK OS v1.0", color=0xFFFFFF, x=10, y=15)
splash.append(text_area)

beep(1000, 0.1) # System Ready Beep!
time.sleep(1) # Leave the boot
text_area.text = "Ready for Action!"

# ------ MAIN LOOP --------

while True:
    
    # 1.Read the matrix keys
    
    event = keys.events.get()
    if event:
        key_index = event.key_index
        if event.pressed:
            print(f"Key {key_index} pressed")
            kbd.press(keymap[key_index])
            # Make the LED under the key turn teal when pressed
            pixels[key_index] = (0, 255, 255)
            pixels.show()
        if event.released:
            print(f"Key {key_index} release")
            kbd.release(keymap[key_index])
            # Make the LED under the key turn purple when pressed
            pixels[key_index] = (80, 0, 120)
            pixels.show()
    
    # 2. Read the Rotary Encoder Turns (Volume Control)
    
    current_position = encoder.position
    if current_position > last_position:
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        last_position = current_position
    elif current_position < last_position:
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        last_position = current_position

    # 3. Read the Rotary Encoder Button (Mute Toggle)

    if not encoder_button.value:
        cc.send(ConsumerControlCode.MUTE)

        # Make all the LEDs turn teal when the button is pressed
        
        pixels.fill((0, 255, 255))
        pixels.show()
        time.sleep(0.2)
        
        # Restore the LED colours after the button press
        
        for i in range(num_pixels):
            pixels[i] = (80, 0, 120)
        pixels.show()
