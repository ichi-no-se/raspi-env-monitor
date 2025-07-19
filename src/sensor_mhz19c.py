import time
import serial
import sys
import update_json


def main():
    DEVICE = "/dev/serial0"
    INTERVAL = 10  # seconds
    try:
        ser = serial.Serial(DEVICE, 9600, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port {DEVICE}: {e}")
        return
    while True:
        # Command to read CO2 concentration
        ser.write(b"\xFF\x01\x86\x00\x00\x00\x00\x00\x79")
        time.sleep(0.1)  # Wait for the response
        if ser.in_waiting >= 9:
            response = ser.read(9)

            if len(response) != 9:
                sys.stderr.write("Invalid response length received\n")
                continue
            # Calc checksum
            checksum = (0xFF - (sum(response[1:8]) & 0xFF)+1) & 0xFF

            if checksum == response[8] and response[0] == 0xFF and response[1] == 0x86:
                co2_concentration = (response[2] << 8) | response[3]
                data_to_write = {
                    'co2': co2_concentration,
                }
                update_json.update_sensor_data('mhz19c', data_to_write)
            else:
                sys.stderr.write("Invalid response received\n")
            time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
