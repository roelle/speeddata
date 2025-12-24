import socket
import struct
import io
from pathlib import Path
import avro.schema
import avro.io

# Resolve paths relative to project root (not script location)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Configuration
# Subscribe to decimated multicast stream (matches config/global.yaml)
MULTICAST_GROUP = "239.1.1.2"
PORT = 6001
SCHEMA_FILE = str(PROJECT_ROOT / "config/agents/example.avsc")

# Load the Avro schema
with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    schema = avro.schema.parse(f.read())

def subscribe_and_decode():
    """
    Subscribes to a multicast group, receives UDP packets, decodes Avro data, and prints it to the screen.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to the multicast group and port
    sock.bind(("", PORT))

    # Join the multicast group
    group = socket.inet_aton(MULTICAST_GROUP)
    mreq = struct.pack("4sL", group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Listening for multicast messages on {MULTICAST_GROUP}:{PORT}...")

    try:
        while True:
            # Receive UDP message
            data, addr = sock.recvfrom(65535)  # Max UDP packet size
            print(f"Received data from {addr}")

            # Decode Avro data
            try:
                bytes_reader = io.BytesIO(data)
                decoder = avro.io.BinaryDecoder(bytes_reader)
                reader = avro.io.DatumReader(schema)
                decoded_message = reader.read(decoder)
                print(f"Decoded message: {decoded_message}")
            except Exception as e:
                print(f"Failed to decode message: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        sock.close()

# Call the function to start listening
if __name__ == "__main__":
    subscribe_and_decode()
