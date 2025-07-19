from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7789
from PIL import ImageFont
import RPi.GPIO as GPIO
import time
import read_json
from datetime import datetime, timedelta

BLK_PIN = 21
BRIGHTNESS = 50


def get_font(size: int):
    try:
        return ImageFont.truetype("TakaoPGothic.ttf", size)
    except Exception:
        return ImageFont.load_default()


def parse_iso_ts(ts_str):
    try:
        return datetime.fromisoformat(ts_str)
    except ValueError:
        return None


def is_recent(ts_str, threshold_seconds=60):
    ts = parse_iso_ts(ts_str)
    if ts is None:
        return False
    return datetime.now() - ts < timedelta(seconds=threshold_seconds)


def calc_discomfort_index(temp: float, humidity: float):
    return 0.81 * temp + 0.01 * humidity * (0.99 * temp - 14.3) + 46.3


def interpolate_color(value, color_map):
    if value < color_map[0][0]:
        return color_map[0][1]
    for i in range(len(color_map) - 1):
        if color_map[i][0] <= value <= color_map[i + 1][0]:
            # 線形補間
            x0, c0 = color_map[i]
            x1, c1 = color_map[i + 1]
            ratio = (value - x0) / (x1 - x0)
            return tuple(int(c0[j] + ratio * (c1[j] - c0[j])) for j in range(3))
    return color_map[-1][1]


def get_color_for_discomfort(index):
    if index is None:
        return "gray"
    return interpolate_color(index, [
        (55, (128, 0, 255)),
        (60, (0, 64, 255)),
        (65, (0, 170, 255)),
        (70, (0, 255, 128)),
        (75, (150, 255, 0)),
        (80, (255, 170, 0)),
        (85, (255, 64, 0)),
        (90, (255, 0, 0))
    ])


def get_color_for_co2(ppm):
    if ppm is None:
        return "gray"
    return interpolate_color(ppm, [
        (400, (0, 200, 255)),
        (800, (80, 255, 80)),
        (1000, (255, 255, 0)),
        (1600, (255, 165, 0)),
        (2000, (255, 0, 0))
    ])


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BLK_PIN, GPIO.OUT)

    pwm = GPIO.PWM(BLK_PIN, 1000)  # 1 kHz frequency
    pwm.start(BRIGHTNESS)
    serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25,
                 gpio_CS=8, bus_speed_hz=52000000)
    device = st7789(serial, width=320, height=240, rotate=0)

    while True:
        data = read_json.read_sensor_data()
        bme_data = data.get('bme280', {}).get("data", {})
        bme_timestamp = data.get('bme280', {}).get("timestamp", None)
        temp = bme_data.get('temperature', None)
        humidity = bme_data.get('humidity', None)
        pressure = bme_data.get('pressure', None)

        mhz_data = data.get('mhz19c', {}).get("data", {})
        mhz_timestamp = data.get('mhz19c', {}).get("timestamp", None)
        co2 = mhz_data.get('co2', None)

        if not is_recent(bme_timestamp):
            temp = humidity = pressure = None

        if not is_recent(mhz_timestamp):
            co2 = None

        if temp is not None and humidity is not None:
            discomfort_index = calc_discomfort_index(temp, humidity)
        else:
            discomfort_index = None
        temp_str = f"{temp:.1f}" if temp is not None else "--"
        humidity_str = f"{humidity:.1f}" if humidity is not None else "--"
        pressure_str = f"{pressure:.1f}" if pressure is not None else "--"
        co2_str = f"{round(co2)}" if co2 is not None else "--"
        discomfort_str = f"{discomfort_index:.1f}" if discomfort_index is not None else "--"

        tiny_font = get_font(20)
        small_font = get_font(30)
        big_font = get_font(45)

        caption_color = "#999"
        value_color = "#ddd"
        co2_color = get_color_for_co2(co2)
        discomfort_color = get_color_for_discomfort(discomfort_index)

        with canvas(device) as draw:
            x_space = 5
            y_gap = 50

            y1 = 60
            x1 = 40
            x2 = 210

            draw.text((x1, y1), "CO", fill=caption_color,
                      font=small_font, anchor="lb")
            draw.text((x1 + 48, y1), "2", fill=caption_color,
                      font=tiny_font, anchor="lb")
            draw.text((x2, y1), co2_str, fill=co2_color,
                      font=big_font, anchor="rb")
            draw.text((x2 + x_space, y1), "ppm", fill=caption_color,
                      font=small_font, anchor="lb")

            y2 = y1 + y_gap
            x3 = x2

            draw.text((x3, y2), pressure_str, fill=value_color,
                      font=big_font, anchor="rb")
            draw.text((x3 + x_space, y2), "hPa", fill=caption_color,
                      font=small_font, anchor="lb")

            y3 = y2 + y_gap
            x4 = 130

            draw.text((x4, y3), temp_str, fill=value_color,
                      font=big_font, anchor="rb")
            draw.text((x4 + x_space, y3), "℃", fill=caption_color,
                      font=small_font, anchor="lb")

            x5 = 270

            draw.text((x5, y3), humidity_str, fill=value_color,
                      font=big_font, anchor="rb")
            draw.text((x5 + x_space, y3), "%", fill=caption_color,
                      font=small_font, anchor="lb")

            y4 = y3 + y_gap
            x6 = x1
            x7 = x5

            draw.text((x6, y4), "不快指数", fill=caption_color,
                      font=small_font, anchor="lb")
            draw.text((x7, y4), discomfort_str, fill=discomfort_color,
                      font=big_font, anchor="rb")

        time.sleep(10)


if __name__ == "__main__":
    main()
