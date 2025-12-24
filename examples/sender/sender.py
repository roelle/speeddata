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

# Resolve paths relative to project root (not script location)
PROJECT_ROOT = Path(__file__).parent.parent.parent
WORD_FILE = "/usr/share/dict/american-english"
SCHEMA_PATH = str(PROJECT_ROOT / "config/agents/example.avsc")
DATA_DIR = str(PROJECT_ROOT / "data")

def main():
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    schema = avro.schema.parse(open(SCHEMA_PATH, "r", encoding='utf-8').read())
    writer = DatumWriter(schema)
    if DEBUG:
        fwriter = DataFileWriter(open(f"{DATA_DIR}/data.avro", "wb"), DatumWriter(), schema)
        fwriter.sync_marker = b'\xa4\x8a\x1e\x90\x05\x04$x\nh3\x7f\xc2P\x95c'
        fwriter.flush()
        print(fwriter.sync_marker)
        print(' '.join(f'{byte:02X}' for byte in fwriter.sync_marker))
    words = [word.rstrip('\n') for word in open(WORD_FILE, 'r', encoding='utf-8')]
    counter = 0
    try:
        while True:
            word = words[random.randrange(0, len(words))]
            message = f'{word}'
            t = time.time_ns()

            # Generate test signals with known patterns for visualization
            # All signals range from -1 to +1 for easy plotting
            sine_wave = math.sin(2 * math.pi * counter / 20.0)  # Period = 20 samples
            ramp = (counter % 40) / 40.0 * 2.0 - 1.0  # Sawtooth: -1 to +1 over 40 samples
            square_wave = 1.0 if (counter % 20) < 10 else -1.0  # Square wave: period = 20
            noise = random.uniform(-0.5, 0.5)  # Random noise

            data = {
                "time": t,
                "message": message,
                "counter": counter,
                "sine_wave": sine_wave,
                "ramp": ramp,
                "square_wave": square_wave,
                "noise": noise
            }

            writer.write(data, BinaryEncoder(bytes_io := io.BytesIO()))
            if DEBUG:
                fwriter.append(data)
                fwriter.flush()
            sock.sendto(bytes_io.getvalue(), ("127.0.0.1", 26000))

            print(f"{counter:4d}  sine={sine_wave:+.3f}  ramp={ramp:+.3f}  square={square_wave:+.1f}  noise={noise:+.3f}")

            counter += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        if DEBUG:
            fwriter.close()

if __name__ == "__main__":
    main()
