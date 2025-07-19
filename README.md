# raspi-env-monitor

Raspberry Pi と ST7789 LCD，BME280，MH-Z19C を用いた環境情報可視化システムです．
気温・湿度・気圧・CO2 濃度・不快指数を 10 秒ごとに表示します．

# 実行方法
以下の3つのスクリプトをそれぞれ別プロセスで起動してください：

- `sensor_bme280.py`：BME280 から温湿度・気圧を取得し JSON に保存
- `sensor_mhz19c.py`：MH-Z19C から CO₂ 濃度を取得し JSON に保存
- `monitor_st7789.py`：LCD に各種情報を表示（10秒ごとに更新）
