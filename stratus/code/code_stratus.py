# PULSE STRATUS Firmware
# Copyright (c) 2025 9OneFour
# SPDX-License-Identifier: Apache-2.0


import time
import board
import busio
import digitalio
import storage
import os
import math

import displayio
from i2cdisplaybus import I2CDisplayBus
from adafruit_displayio_sh1107 import SH1107, DISPLAY_OFFSET_ADAFRUIT_128x128_OLED_5297
import terminalio
from adafruit_display_text import label

import adafruit_sdcard
import adafruit_lsm6ds.lsm6dso32 as lsm6dso32
import adafruit_ahtx0
import adafruit_mmc56x3
import neopixel

# ——— OLED SETUP ————————————————————————————————————————————————————————
displayio.release_displays()
i2c = board.I2C()
display_bus = I2CDisplayBus(i2c, device_address=0x3D)
WIDTH, HEIGHT = 128, 128

display = SH1107(
    display_bus,
    width=WIDTH,
    height=HEIGHT,
    display_offset=DISPLAY_OFFSET_ADAFRUIT_128x128_OLED_5297,
    rotation=90
)

# Prepare info screen labels
info_group = displayio.Group()

battery_label = label.Label(terminalio.FONT, text="-- V", color=0xFFFFFF)
battery_label.anchor_point = (0.5, 0)
battery_label.anchored_position = (WIDTH // 2, 5)
info_group.append(battery_label)

temp_hum_label = label.Label(terminalio.FONT, text="T: -- C, H: --%", color=0xFFFFFF)
temp_hum_label.anchor_point = (0.5, 0)
temp_hum_label.anchored_position = (WIDTH // 2, 20)
info_group.append(temp_hum_label)

file_info_label = label.Label(terminalio.FONT, text="File: ----", color=0xFFFFFF)
file_info_label.anchor_point = (0.5, 0)
file_info_label.anchored_position = (WIDTH // 2, HEIGHT // 2 - 20)
info_group.append(file_info_label)

status_label = label.Label(terminalio.FONT, text="Status: Ready to log", color=0xFFFFFF)
status_label.anchor_point = (0.5, 0.5)
status_label.anchored_position = (WIDTH // 2, HEIGHT // 2)
info_group.append(status_label)

compass_label = label.Label(terminalio.FONT, text="Heading: --°", color=0xFFFFFF)
compass_label.anchor_point = (0.5, 1)
compass_label.anchored_position = (WIDTH // 2, HEIGHT - 30)
info_group.append(compass_label)

max_g_label = label.Label(terminalio.FONT, text="Max G: 0.00 g", color=0xFFFFFF)
max_g_label.anchor_point = (0.5, 1)
max_g_label.anchored_position = (WIDTH // 2, HEIGHT - 5)
info_group.append(max_g_label)

# Welcome splash
def show_splash():
    splash = displayio.Group()
    welcome = label.Label(terminalio.FONT, text="Welcome to PULSE", color=0xFFFFFF)
    welcome.anchor_point = (0.5, 0.5)
    welcome.anchored_position = (WIDTH // 2, HEIGHT // 2)
    splash.append(welcome)
    display.root_group = splash
    time.sleep(2)
    display.root_group = info_group

show_splash()

# ——— NEOPIXEL SETUP ——————————————————————————————————————————————————————
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=True)
pixel[0] = (0, 0, 255)

# ——— SD CARD SETUP ——————————————————————————————————————————————————————
cs = digitalio.DigitalInOut(board.SD_CS)
sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
storage.mount(storage.VfsFat(sdcard), "/sd")

# ——— SENSOR INITIALIZATION ——————————————————————————————————————————————
sensor = lsm6dso32.LSM6DSO32(i2c)
aht    = adafruit_ahtx0.AHTx0(i2c)
mag    = adafruit_mmc56x3.MMC5603(i2c)

# ——— BATTERY MONITORING SETUP ——————————————————————————————————————————
try:
    from analogio import AnalogIn
    # Use board.BATTERY if defined, otherwise fall back to A0 (or another ADC pin you broke out)
    batt_pin = board.BATTERY if hasattr(board, "BATTERY") else board.A0
    batt_sense = AnalogIn(batt_pin)
    # Scale: 3.3 V full-scale, 16-bit reading, with a simple divider of 2:1
    BATT_FACTOR = 3.3 / 65535 * 2
    BATTERY_AVAILABLE = True
except (ImportError, AttributeError):
    # no AnalogIn or no valid pin → skip battery monitoring
    BATTERY_AVAILABLE = False

def get_batt():
    return batt_sense.value * BATT_FACTOR

# ——— LOGGING SWITCH SETUP —————————————————————————————————————————————
switch = digitalio.DigitalInOut(board.D24)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP


# ——— ERROR DISPLAY UTILITY —————————————————————————————————————————————
def show_error(msg, duration=2):
    err_group = displayio.Group()
    err_label = label.Label(
        terminalio.FONT, text=f"Error:\n{msg}", color=0xFF0000
    )
    err_label.anchor_point = (0.5, 0.5)
    err_label.anchored_position = (WIDTH // 2, HEIGHT // 2)
    err_group.append(err_label)
    display.root_group = err_group
    time.sleep(duration)
    display.root_group = info_group

# ——— CALIBRATION ROUTINES w/ PROGRESS —————————————————————————————
def calibrate_gyro(sensor, samples=200):
    splash = displayio.Group()
    title = label.Label(terminalio.FONT, text="Gyro Cal:\nKeep Still", color=0xFFFFFF)
    title.anchor_point = (0.5, 0.5)
    title.anchored_position = (WIDTH//2, HEIGHT//2 - 10)
    splash.append(title)

    spinner = ["|", "/", "–", "\\"]
    spin_label = label.Label(terminalio.FONT, text=spinner[0], color=0xFFFFFF)
    spin_label.anchor_point = (0.5, 0.5)
    spin_label.anchored_position = (WIDTH//2, HEIGHT//2 + 20)
    splash.append(spin_label)

    display.root_group = splash
    bias = [0.0, 0.0, 0.0]
    for i in range(samples):
        spin_label.text = spinner[i % len(spinner)]
        gx, gy, gz = sensor.gyro
        bias[0] += gx
        bias[1] += gy
        bias[2] += gz
        time.sleep(0.01)

    display.root_group = info_group
    return [b / samples for b in bias]

def calibrate_mag(sensor, duration=10.0):
    splash = displayio.Group()
    title = label.Label(terminalio.FONT, text="Mag Cal:\nRotate", color=0xFFFFFF)
    title.anchor_point = (0.5, 0.5)
    title.anchored_position = (WIDTH//2, HEIGHT//2 - 20)
    splash.append(title)

    prog_label = label.Label(terminalio.FONT, text="0%", color=0xFFFFFF)
    prog_label.anchor_point = (0.5, 0.5)
    prog_label.anchored_position = (WIDTH//2, HEIGHT//2 + 20)
    splash.append(prog_label)

    display.root_group = splash
    t0    = time.monotonic()
    mins  = [1e6]*3
    maxs  = [-1e6]*3

    while True:
        elapsed = time.monotonic() - t0
        if elapsed >= duration:
            break
        pct = int((elapsed/duration)*100)
        prog_label.text = f"{pct}%"
        mx, my, mz = sensor.magnetic
        for idx, v in enumerate((mx, my, mz)):
            mins[idx] = min(mins[idx], v)
            maxs[idx] = max(maxs[idx], v)
        time.sleep(0.05)

    prog_label.text = "100%"
    time.sleep(0.3)
    offsets = [(maxs[i] + mins[i]) / 2 for i in range(3)]
    scales  = [(maxs[i] - mins[i]) / 2 for i in range(3)]
    display.root_group = info_group
    return offsets, scales

# ——— RUN CALIBRATION ———————————————————————————————————————————————
gyro_bias           = calibrate_gyro(sensor)
mag_offset, mag_scale = calibrate_mag(mag)

# ——— CONFIGURATION —————————————————————————————————————————————————————
TARGET_RATE            = 6700
TARGET_PERIOD          = 1.0 / TARGET_RATE
BATTERY_CHECK_INTERVAL = 5.0
TEMP_HUM_INTERVAL      = 3.0
MAG_INTERVAL           = 1.0
OLED_INTERVAL          = 1.0

# ——— UTILITIES —————————————————————————————————————————————————————————
def next_filename():
    i = 1
    while True:
        name = f"/sd/LOG{i:03d}.CSV"
        try:
            os.stat(name)
        except OSError:
            return name
        i += 1

# ——— STATE VARIABLES —————————————————————————————————————————————————————
logging_active  = False
current_file    = ""
last_oled = last_temp_hum = last_mag = time.monotonic()
yaw             = 0.0
aht_temp        = aht.temperature
aht_humidity    = aht.relative_humidity
mag_x = mag_y = mag_z = 0.0
max_g = last_max_g = 0.0

print("PULSE Data Logger")
print("Slide switch ON to start, OFF to stop.")

# ——— MAIN LOOP —————————————————————————————————————————————————————
while True:
    now = time.monotonic()

    # — Switch edge detection — START
    sw = switch.value
    if sw and not prev_switch:
        try:
            current_file = next_filename()
            f = open(current_file, "w")
            if BATTERY_AVAILABLE:
                f.write(f"# Battery Start Voltage: {get_batt():.2f} V\n")
                f.flush()
            f.write("Timestamp,Roll,Pitch,Yaw,AccX,AccY,AccZ,GyroX,GyroY,GyroZ,Temp,Humidity,MagX,MagY,MagZ\n")
            f.flush()
        except OSError as e:
            print("File open error:", e)
            pixel[0] = (255, 0, 0)
            show_error("File Open Fail")
        else:
            logging_active = True
            yaw            = time.monotonic()
            max_g          = 0.0
            file_info_label.text = "File: " + current_file.split("/")[-1]
            pixel[0]       = (0, 255, 0)
            print("Started:", current_file)

    # — Switch edge detection — STOP
    if not sw and prev_switch and logging_active:
        if BATTERY_AVAILABLE:
            try:
                f.write(f"# Battery End Voltage: {get_batt():.2f} V\n")
                f.flush()
            except OSError as e:
                print("Battery write error:", e)
                pixel[0] = (255, 0, 0)
                show_error("End-Volt Write Fail")
        try:
            f.close()
        except OSError as e:
            print("File close error:", e)
            pixel[0] = (255, 0, 0)
            show_error("File Close Fail")
        finally:
            logging_active = False
            last_max_g     = max_g
            file_info_label.text = "Last: " + current_file.split("/")[-1]
            pixel[0]       = (0, 0, 255)
            print("Stopped:", current_file)

    prev_switch = sw

    # — Battery voltage update —
    if BATTERY_AVAILABLE and (now - last_oled) >= BATTERY_CHECK_INTERVAL:
        battery_label.text = f"{get_batt():.2f} V"
        last_oled = now

    # — Temp/Humidity update —
    if (now - last_temp_hum) >= TEMP_HUM_INTERVAL:
        aht_temp     = aht.temperature
        aht_humidity = aht.relative_humidity
        temp_hum_label.text = f"T:{aht_temp:.1f}C H:{aht_humidity:.1f}%"
        last_temp_hum = now

    # — Magnetometer update —
    if (now - last_mag) >= MAG_INTERVAL:
        mx, my, mz = mag.magnetic
        mag_x = (mx - mag_offset[0]) / mag_scale[0]
        mag_y = (my - mag_offset[1]) / mag_scale[1]
        mag_z = (mz - mag_offset[2]) / mag_scale[2]
        last_mag = now

    # — Sensor sampling & logging —
    if logging_active:
        t0 = time.monotonic()
        dt = t0 - yaw
        yaw = t0

        ax, ay, az = sensor.acceleration
        gx, gy, gz = sensor.gyro
        gx -= gyro_bias[0]
        gy -= gyro_bias[1]
        gz -= gyro_bias[2]

        roll      = math.degrees(math.atan2(ay, az))
        pitch     = math.degrees(math.atan2(-ax, math.sqrt(ay*ay + az*az)))
        yaw_read  = yaw + gz * dt

        acc_mag   = math.sqrt(ax*ax + ay*ay + az*az)
        g_val     = acc_mag / 9.8
        if g_val > max_g:
            max_g = g_val

        line = "{:.6f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(
            t0, roll, pitch, yaw_read,
            ax, ay, az, gx, gy, gz,
            aht_temp, aht_humidity,
            mag_x, mag_y, mag_z
        )
        try:
            f.write(line)
        except OSError as e:
            print("Write error:", e)
            pixel[0] = (255, 0, 0)
            show_error("Log Write Fail")
            try:
                f.close()
            except OSError:
                pass
            logging_active = False
        else:
            if int(t0 * TARGET_RATE) % 1000 == 0:
                f.flush()

        # maintain sample rate
        dt2 = time.monotonic() - t0
        if dt2 < TARGET_PERIOD:
            time.sleep(TARGET_PERIOD - dt2)

    # — OLED info update —
    if (now - last_oled) >= OLED_INTERVAL:
        status_label.text = "Status: Logging" if logging_active else "Status: Ready to log"
        heading = math.degrees(math.atan2(mag_y, mag_x))
        if heading < 0:
            heading += 360
        compass_label.text = f"Heading:{heading:.1f}°"
        mg = max_g if logging_active else last_max_g
        max_g_label.text = f"Max G:{mg:.2f} g"
        last_oled = now
