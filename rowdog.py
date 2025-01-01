import socket
import os
import time
import io

import avro.schema
import avro.datafile
import avro.io

# Configuration
OUTPUT_DIR = "data"
MAX_FILE_SIZE_MB = 50  # Rotate file when this size is exceeded
MULTICAST_GROUP = "224.0.0.1"
TX_PORT = 26001

def new_writer(schema: str) -> avro.datafile.DataFileWriter:
    """Create a new Avro writer object."""
    writer = avro.datafile.DataFileWriter(
        open(
            os.path.join(
                OUTPUT_DIR,
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


def encode_long(n: int) -> bytes:
    """Encode a long integer as a byte array per Avro."""
    avro.io.BinaryEncoder(bytes_io := io.BytesIO()).write_long(n)
    return bytes_io.getvalue()


def main():
    """Main entry point."""
    # UDP receive socket setup
    rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    rx_sock.bind((RX_IP := "127.0.0.1", RX_PORT := 26000))
    print(f"Listening for UDP packets on {RX_IP}:{RX_PORT}...")

    # Set output multicast socket
    tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    tx_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    print(f"Publishing to multicast group {MULTICAST_GROUP}:{TX_PORT}...")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load Avro schema
    schema = avro.schema.parse(open("schema.avsc", "r", encoding="utf-8").read())
    writer = new_writer(schema)
    current_file_size = 0

    try:
        while True:
            # Rotate file if size exceeds limit
            if current_file_size >= MAX_FILE_SIZE_MB * 1024 * 1024:
                writer.close()
                print(f"Rotated file: {writer.writer.name}")
                writer = new_writer(schema)
                current_file_size = 0

            # Receive data from UDP
            data, addr = rx_sock.recvfrom(65535)  # Maximum UDP packet size
            print(f"Received {len(data)} bytes from {addr}")
            print(data)

            # Relay message back out to the multicast group
            tx_sock.sendto(data, (MULTICAST_GROUP, TX_PORT))

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
