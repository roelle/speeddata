#!/usr/bin/env python3
"""
Temperature/Pressure Sensor Simulator
Sends simulated environmental data to demonstrate multi-channel registration
"""
import socket
import time
import random
import io
import os
import math
from pathlib import Path
import avro.schema
from avro.io import DatumWriter, BinaryEncoder

DEBUG = True
if DEBUG:
    from avro.datafile import DataFileWriter

# Resolve paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCHEMA_PATH = str(PROJECT_ROOT / "config/agents/temperature.avsc")
DATA_DIR = str(PROJECT_ROOT / "data")
DEVICE_ID = "TEMP-SENSOR-001"

# Target port for this sender (different from example sender)
UDP_PORT = 26001

def main():
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    schema = avro.schema.parse(open(SCHEMA_PATH, "r", encoding='utf-8').read())
    writer = DatumWriter(schema)

    if DEBUG:
        debug_file = f"{DATA_DIR}/temperature_data.avro"
        fwriter = DataFileWriter(open(debug_file, "wb"), DatumWriter(), schema)
        fwriter.sync_marker = b'\xa4\x8a\x1e\x90\x05\x04$x\nh3\x7f\xc2P\x95c'
        fwriter.flush()
        print(f"Debug: Writing to {debug_file}")

    # Base environmental values with realistic drift
    base_temp_c = 22.0  # Room temperature baseline
    base_pressure_pa = 101325.0  # Sea level pressure
    base_humidity = 45.0  # Comfortable humidity

    counter = 0
    print(f"Temperature sensor '{DEVICE_ID}' sending to port {UDP_PORT}")
    print("Simulating environmental data with realistic variations...")
    print()

    try:
        while True:
            t = time.time_ns()

            # Simulate realistic environmental changes
            # Temperature: slow drift + daily cycle + noise
            temp_drift = math.sin(2 * math.pi * counter / 200.0) * 2.0  # ±2°C slow drift
            temp_daily = math.sin(2 * math.pi * counter / 86400.0) * 5.0  # ±5°C daily cycle
            temp_noise = random.gauss(0, 0.1)  # Small random fluctuations
            temperature_c = base_temp_c + temp_drift + temp_daily + temp_noise

            # Convert to Fahrenheit
            temperature_f = temperature_c * 9.0/5.0 + 32.0

            # Pressure: inversely related to temperature + random weather changes
            pressure_temp_effect = -temperature_c * 100.0  # Temperature affects pressure
            pressure_weather = math.sin(2 * math.pi * counter / 300.0) * 500.0  # Weather systems
            pressure_noise = random.gauss(0, 50)
            pressure_pa = base_pressure_pa + pressure_temp_effect + pressure_weather + pressure_noise

            # Humidity: inversely related to temperature + weather
            humidity_temp_effect = -(temperature_c - base_temp_c) * 2.0
            humidity_weather = math.cos(2 * math.pi * counter / 250.0) * 10.0
            humidity_noise = random.gauss(0, 1.0)
            humidity_pct = base_humidity + humidity_temp_effect + humidity_weather + humidity_noise
            humidity_pct = max(0, min(100, humidity_pct))  # Clamp to valid range

            # Determine sensor status based on values
            if temperature_c > 35.0 or temperature_c < 10.0:
                status = "warning"
            elif temperature_c > 40.0 or temperature_c < 5.0:
                status = "error"
            else:
                status = "ok"

            data = {
                "time": t,
                "device_id": DEVICE_ID,
                "temperature_c": temperature_c,
                "temperature_f": temperature_f,
                "pressure_pa": pressure_pa,
                "humidity_pct": humidity_pct,
                "status": status
            }

            # Encode and send
            writer.write(data, BinaryEncoder(bytes_io := io.BytesIO()))
            if DEBUG:
                fwriter.append(data)
                fwriter.flush()
            sock.sendto(bytes_io.getvalue(), ("127.0.0.1", UDP_PORT))

            # Display current readings
            print(f"{counter:4d}  "
                  f"Temp: {temperature_c:6.2f}°C ({temperature_f:6.2f}°F)  "
                  f"Press: {pressure_pa:8.1f}Pa  "
                  f"Humid: {humidity_pct:5.1f}%  "
                  f"[{status}]")

            counter += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down temperature sensor...")
    finally:
        if DEBUG:
            fwriter.close()
            print(f"Debug file closed: {debug_file}")

if __name__ == "__main__":
    main()
