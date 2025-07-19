from bme280 import bme280
from bme280 import bme280_i2c
import time
import update_json

INTERVAL = 10  # seconds


def main():
    # 初期化
    bme280_i2c.set_default_i2c_address(0x76)
    bme280_i2c.set_default_bus(1)

    # キャリブレーション
    bme280.setup()
    while True:
        # データ取得
        data_all = bme280.read_all()

        data_to_write = {
            'temperature': data_all.temperature,
            'humidity': data_all.humidity,
            'pressure': data_all.pressure
        }

        update_json.update_sensor_data('bme280', data_to_write)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
