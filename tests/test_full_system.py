#!/usr/bin/env python3
"""
Full system test: Simulated agent → C relay → AVRO + multicast
"""
import socket
import struct
import time
import subprocess
import signal
import os
import math
import io
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lib/python'))

import avro.schema
import avro.io
import avro.datafile


RELAY_PORT = 26000
MCAST_FULL = ("239.1.1.1", 6000)
SCHEMA_PATH = "config/agents/example.avsc"
DATA_DIR = "./data"


def create_test_record(counter: int) -> dict:
    """Create test record matching example.avsc schema"""
    t = counter * 0.1  # 10 Hz simulation
    return {
        'time': int(time.time() * 1_000_000_000),  # nanoseconds
        'message': f'test_record_{counter}',
        'counter': counter,
        'sine_wave': math.sin(t),
        'ramp': (counter % 100) / 100.0,
        'square_wave': 1.0 if (counter % 20) < 10 else -1.0,
        'noise': (hash(counter) % 1000) / 1000.0
    }


def serialize_record(schema, record) -> bytes:
    """Serialize record to AVRO binary"""
    writer = avro.io.DatumWriter(schema)
    bytes_io = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_io)
    writer.write(record, encoder)
    return bytes_io.getvalue()


def send_agent_packet(schema, record):
    """Send AVRO packet to relay via UDP"""
    data = serialize_record(schema, record)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, ('127.0.0.1', RELAY_PORT))
    sock.close()

    return data


def listen_multicast_packets(group, port, count, timeout=10):
    """Listen for multiple multicast packets"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))

    # Join multicast group
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    sock.settimeout(timeout)
    packets = []

    try:
        for _ in range(count):
            data, addr = sock.recvfrom(65535)
            packets.append(data)
    except socket.timeout:
        pass
    finally:
        sock.close()

    return packets


def verify_avro_files():
    """Verify AVRO files were created and contain data"""
    data_path = Path(DATA_DIR)
    avro_files = list(data_path.glob("*.avro"))

    if not avro_files:
        return False, "No AVRO files created"

    # Check latest file
    latest = max(avro_files, key=lambda p: p.stat().st_mtime)

    if latest.stat().st_size == 0:
        return False, f"AVRO file is empty: {latest.name}"

    # Verify sync marker
    with open(latest, 'rb') as f:
        content = f.read()

    sync_marker = bytes([
        0xa4, 0x8a, 0x1e, 0x90, 0x05, 0x04, 0x24, 0x78,
        0x0a, 0x68, 0x33, 0x7f, 0xc2, 0x50, 0x95, 0x63
    ])

    if sync_marker not in content:
        return False, "AVRO sync marker not found"

    return True, f"AVRO file OK: {latest.name} ({latest.stat().st_size} bytes)"


def test_full_system():
    """Test complete data flow"""
    print("=== Full System Test ===\n")
    print("Testing: Simulated Agent → C Relay → AVRO + Multicast\n")

    # Check prerequisites
    relay_bin = Path("relay/c/build/relay")
    if not relay_bin.exists():
        print(f"ERROR: Relay binary not found: {relay_bin}")
        print("Run 'make' in relay/c directory")
        return False

    # Load schema
    schema = avro.schema.parse(open(SCHEMA_PATH, 'r').read())

    # Clear data directory
    data_path = Path(DATA_DIR)
    data_path.mkdir(exist_ok=True)
    for f in data_path.glob("*.avro"):
        f.unlink()

    # Start relay
    print("Starting C relay...")
    relay_env = os.environ.copy()
    relay_env['RELAY_RX_PORT'] = str(RELAY_PORT)
    relay_env['RELAY_OUTPUT_DIR'] = DATA_DIR
    relay_env['RELAY_DECIMATION_ENABLED'] = 'false'  # Disable for simpler test

    relay_proc = subprocess.Popen(
        [str(relay_bin), "example"],
        env=relay_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(1)

    # Start multicast listener in background
    print("Starting multicast listener...")
    listener_proc = subprocess.Popen(
        ['python3', '-c', f'''
import socket, struct, sys
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', {MCAST_FULL[1]}))
mreq = struct.pack("4sl", socket.inet_aton("{MCAST_FULL[0]}"), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
sock.settimeout(10)
count = 0
try:
    while count < 10:
        data, addr = sock.recvfrom(65535)
        count += 1
        sys.stdout.write(f"{{count}}\\n")
        sys.stdout.flush()
except:
    pass
sys.stdout.write(f"FINAL:{{count}}\\n")
'''],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(0.5)

    # Send test packets
    print("Sending 10 test packets...")
    for i in range(10):
        record = create_test_record(i)
        send_agent_packet(schema, record)
        print(f"  Sent packet {i + 1}: counter={record['counter']}, sine={record['sine_wave']:.3f}")
        time.sleep(0.1)

    print("\nWaiting for processing...")
    time.sleep(2)

    # Check results
    print("\n=== Results ===\n")

    # 1. Check multicast
    listener_proc.wait(timeout=3)
    listener_output = listener_proc.stdout.read()
    mcast_count = 0
    for line in listener_output.split('\n'):
        if line.startswith('FINAL:'):
            mcast_count = int(line.split(':')[1])

    if mcast_count == 10:
        print(f"✓ Multicast: Received all {mcast_count} packets")
    else:
        print(f"✗ Multicast: Expected 10 packets, received {mcast_count}")

    # 2. Check AVRO files
    avro_ok, avro_msg = verify_avro_files()
    if avro_ok:
        print(f"✓ AVRO: {avro_msg}")
    else:
        print(f"✗ AVRO: {avro_msg}")

    # 3. Check relay process
    relay_return = relay_proc.poll()
    if relay_return is None:
        print("✓ Relay: Process running")
        relay_ok = True
    else:
        print(f"✗ Relay: Process exited with code {relay_return}")
        relay_ok = False

    # Cleanup
    print("\nCleaning up...")
    if relay_proc.poll() is None:
        relay_proc.send_signal(signal.SIGTERM)
        relay_proc.wait(timeout=2)

    # Print relay output
    stdout, stderr = relay_proc.communicate()
    if stdout:
        print("\nRelay STDOUT:")
        print(stdout[-500:])  # Last 500 chars

    # Summary
    print("\n=== Test Summary ===")
    tests_passed = (mcast_count == 10) and avro_ok and relay_ok
    if tests_passed:
        print("✓ Full system test PASSED")
        return True
    else:
        print("✗ Full system test FAILED")
        return False


if __name__ == '__main__':
    success = test_full_system()
    sys.exit(0 if success else 1)
