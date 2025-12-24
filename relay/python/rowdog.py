import socket
import os
import time
import io
import sys
from pathlib import Path

import avro.schema
import avro.datafile
import avro.io

# Add lib to path for config access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib/python'))
from speeddata_config import load_config

def new_writer(schema: str, output_dir: str) -> avro.datafile.DataFileWriter:
    """Create a new Avro writer object."""
    os.makedirs(output_dir, exist_ok=True)
    writer = avro.datafile.DataFileWriter(
        open(
            os.path.join(
                output_dir,
                f"data_{int(time.time())}.avro",
            ),
            "wb",
        ),
        avro.io.DatumWriter(),
        schema,
    )
    writer.sync_marker = b'\xa4\x8a\x1e\x90\x05\x04$x\nh3\x7f\xc2P\x95c'
    print(writer.sync_marker)
    writer.flush()
    return writer


class Decimator:
    """Handles decimation of incoming data packets."""

    def __init__(self, factor: int, algorithm: str):
        self.factor = factor
        self.algorithm = algorithm
        self.buffer = []
        self.count = 0

    def add_packet(self, data: bytes) -> bytes:
        """
        Add packet to decimation buffer.
        Returns decimated packet when buffer is full, None otherwise.
        """
        if self.factor <= 1:
            return data  # No decimation

        self.buffer.append(data)
        self.count += 1

        if self.count >= self.factor:
            result = self._process_buffer()
            self.buffer = []
            self.count = 0
            return result

        return None

    def _process_buffer(self) -> bytes:
        """Process buffer according to algorithm."""
        if self.algorithm == "downsample":
            # Return last packet (most recent)
            return self.buffer[-1]
        elif self.algorithm == "average":
            # For AVRO packets, just return last (averaging requires deserialization)
            # TODO: Implement proper averaging with AVRO deserialization
            return self.buffer[-1]
        elif self.algorithm == "minmax":
            # Return last packet (min/max requires deserialization)
            return self.buffer[-1]
        elif self.algorithm == "rms":
            # Return last packet (RMS requires deserialization)
            return self.buffer[-1]
        else:
            return self.buffer[-1]


def encode_long(n: int) -> bytes:
    """Encode a long integer as a byte array per Avro."""
    avro.io.BinaryEncoder(bytes_io := io.BytesIO()).write_long(n)
    return bytes_io.getvalue()


def main():
    """Main entry point."""
    # Load configuration
    config = load_config('relay')

    # Get first channel config (support single channel for now)
    if not config.get('channels'):
        raise ValueError("No channels configured in relay.yaml")

    channel = config['channels'][0]
    rx_port = channel['port']
    schema_path = channel['schema']

    # Get multicast config
    multicast_config = config.get('multicast', {})
    full_rate = multicast_config.get('full_rate', {'address': '239.1.1.1', 'port': 6000})
    decimated = multicast_config.get('decimated', {'address': '239.1.1.2', 'port': 6001})

    # Get decimation config
    decimation_config = config.get('decimation', {})
    decimation_enabled = decimation_config.get('enabled', False)
    decimation_factor = decimation_config.get('factor', 50)
    decimation_algorithm = decimation_config.get('algorithm', 'downsample')

    # Get rotation config
    rotation_config = config.get('rotation', {})
    rotation_mode = rotation_config.get('mode', 'size')
    rotation_threshold = rotation_config.get('threshold', 50 * 1024 * 1024)  # bytes

    # Get storage path
    storage_config = config.get('storage', {})
    output_dir = storage_config.get('avro_path', '../../data')

    # UDP receive socket setup
    rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    rx_sock.bind(("127.0.0.1", rx_port))
    print(f"Listening for UDP packets on 127.0.0.1:{rx_port}...")

    # Full-rate multicast socket
    tx_full_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    tx_full_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    print(f"Publishing full-rate to {full_rate['address']}:{full_rate['port']}")

    # Decimated multicast socket (if enabled)
    tx_dec_sock = None
    decimator = None
    if decimation_enabled:
        tx_dec_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        tx_dec_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        decimator = Decimator(decimation_factor, decimation_algorithm)
        print(f"Publishing decimated to {decimated['address']}:{decimated['port']}")
        print(f"Decimation: factor={decimation_factor}, algorithm={decimation_algorithm}")

    # Load Avro schema
    schema = avro.schema.parse(open(schema_path, "r", encoding="utf-8").read())
    writer = new_writer(schema, output_dir)
    current_file_size = 0

    try:
        while True:
            # Rotate file if size exceeds limit
            if rotation_mode == 'size' and current_file_size >= rotation_threshold:
                writer.close()
                print(f"Rotated file: {writer.writer.name}")
                writer = new_writer(schema, output_dir)
                current_file_size = 0

            # Receive data from UDP
            data, addr = rx_sock.recvfrom(65535)  # Maximum UDP packet size
            print(f"Received {len(data)} bytes from {addr}")

            # Relay to full-rate multicast (zero processing overhead)
            tx_full_sock.sendto(data, (full_rate['address'], full_rate['port']))

            # Relay to decimated multicast (if enabled)
            if decimation_enabled and decimator:
                decimated_packet = decimator.add_packet(data)
                if decimated_packet:
                    tx_dec_sock.sendto(decimated_packet, (decimated['address'], decimated['port']))

            # Write raw data as a block to Avro file
            writer.writer.raw.write(encode_long(1))
            writer.writer.raw.write(encode_long(len(data)))
            writer.writer.raw.write(data)
            writer.writer.raw.write(writer.sync_marker)
            current_file_size += len(data) + len(writer.sync_marker)

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        writer.close()

if __name__ == "__main__":
    main()
