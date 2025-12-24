#!/usr/bin/env python3
"""
Integration test for C relay
Tests end-to-end UDP receive → AVRO write → multicast relay
"""
import socket
import struct
import time
import os
import subprocess
import signal
from pathlib import Path

# Test configuration
TEST_PORT = 27000
MCAST_FULL = ("239.1.1.1", 6000)
MCAST_DEC = ("239.1.1.2", 6001)
TEST_DATA_DIR = "/tmp/relay_integration_test"
RELAY_BIN = "relay/c/build/relay"


def setup_test_env():
    """Setup test environment"""
    # Create test data directory
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)

    # Set environment variables for relay
    os.environ['RELAY_RX_PORT'] = str(TEST_PORT)
    os.environ['RELAY_OUTPUT_DIR'] = TEST_DATA_DIR
    os.environ['RELAY_DECIMATION_ENABLED'] = 'true'
    os.environ['RELAY_DECIMATION_FACTOR'] = '3'


def cleanup_test_env():
    """Cleanup test artifacts"""
    import shutil
    if Path(TEST_DATA_DIR).exists():
        shutil.rmtree(TEST_DATA_DIR)


def send_udp_packet(data):
    """Send UDP packet to relay"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, ('127.0.0.1', TEST_PORT))
    sock.close()


def listen_multicast(group, port, timeout=2):
    """Listen for multicast packet"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))

    # Join multicast group
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    sock.settimeout(timeout)
    try:
        data, addr = sock.recvfrom(65535)
        sock.close()
        return data
    except socket.timeout:
        sock.close()
        return None


def check_avro_files():
    """Check if AVRO files were created"""
    avro_files = list(Path(TEST_DATA_DIR).glob("*.avro"))
    return len(avro_files) > 0, avro_files


def test_basic_relay():
    """Test basic relay functionality"""
    print("Test 1: Basic UDP relay...")

    # Start relay process
    relay_proc = subprocess.Popen(
        [RELAY_BIN, "test"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for relay to start
    time.sleep(0.5)

    # Setup multicast listener for full-rate
    full_listener = subprocess.Popen(
        ['python3', '-c', f'''
import socket, struct
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', {MCAST_FULL[1]}))
mreq = struct.pack("4sl", socket.inet_aton("{MCAST_FULL[0]}"), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
sock.settimeout(2)
try:
    data, addr = sock.recvfrom(65535)
    print(f"RECEIVED:{{len(data)}}")
except:
    pass
'''],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(0.5)

    # Send test packet
    test_data = b"Hello from integration test"
    send_udp_packet(test_data)

    # Wait for processing
    time.sleep(0.5)

    # Check multicast received
    full_listener.wait(timeout=3)
    output = full_listener.stdout.read().decode()

    # Cleanup
    relay_proc.send_signal(signal.SIGTERM)
    relay_proc.wait(timeout=2)

    if "RECEIVED:" in output:
        print("✓ Full-rate multicast received")
    else:
        print("✗ Full-rate multicast NOT received")
        return False

    # Check AVRO file created
    has_files, files = check_avro_files()
    if has_files:
        print(f"✓ AVRO file created: {files[0].name}")
    else:
        print("✗ AVRO file NOT created")
        return False

    return True


def test_decimation():
    """Test decimation logic"""
    print("\nTest 2: Decimation (factor=3)...")

    # Start relay
    relay_proc = subprocess.Popen(
        [RELAY_BIN, "test"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(0.5)

    # Send 6 packets (should get 2 decimated packets)
    packets_sent = 6
    for i in range(packets_sent):
        send_udp_packet(f"Packet {i}".encode())
        time.sleep(0.1)

    # Wait for processing
    time.sleep(1)

    # Cleanup
    relay_proc.send_signal(signal.SIGTERM)
    relay_proc.wait(timeout=2)

    # Check stdout for decimation messages
    stdout = relay_proc.stdout.read().decode()
    decimation_count = stdout.count("decimated multicast")

    print(f"  Sent {packets_sent} packets")
    print(f"  Decimated packets: {decimation_count}")

    # With factor=3, expect 2 decimated (3rd and 6th packet)
    if decimation_count == 2:
        print("✓ Decimation working correctly")
        return True
    else:
        print(f"✗ Expected 2 decimated packets, got {decimation_count}")
        return False


def test_file_content():
    """Test AVRO file content structure"""
    print("\nTest 3: AVRO file content...")

    # Start relay
    relay_proc = subprocess.Popen(
        [RELAY_BIN, "test"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(0.5)

    # Send test packet
    test_data = b"\x01\x02\x03\x04\x05"
    send_udp_packet(test_data)

    time.sleep(0.5)

    # Cleanup
    relay_proc.send_signal(signal.SIGTERM)
    relay_proc.wait(timeout=2)

    # Read AVRO file
    has_files, files = check_avro_files()
    if not has_files:
        print("✗ No AVRO file found")
        return False

    avro_file = files[0]
    with open(avro_file, 'rb') as f:
        content = f.read()

    # Check for sync marker
    sync_marker = bytes([
        0xa4, 0x8a, 0x1e, 0x90, 0x05, 0x04, 0x24, 0x78,
        0x0a, 0x68, 0x33, 0x7f, 0xc2, 0x50, 0x95, 0x63
    ])

    if sync_marker in content:
        print("✓ AVRO sync marker found")
    else:
        print("✗ AVRO sync marker NOT found")
        return False

    # Check test data is in file
    if test_data in content:
        print("✓ Test data found in AVRO file")
    else:
        print("✗ Test data NOT found in AVRO file")
        return False

    print(f"  File size: {len(content)} bytes")
    return True


def main():
    print("=== C Relay Integration Tests ===\n")

    # Check if relay binary exists
    if not Path(RELAY_BIN).exists():
        print(f"ERROR: Relay binary not found: {RELAY_BIN}")
        print("Run 'make' in relay/c directory first")
        return 1

    setup_test_env()

    try:
        results = []
        results.append(test_basic_relay())
        cleanup_test_env()
        setup_test_env()

        results.append(test_decimation())
        cleanup_test_env()
        setup_test_env()

        results.append(test_file_content())

        # Summary
        print("\n=== Test Summary ===")
        passed = sum(results)
        total = len(results)
        print(f"Passed: {passed}/{total}")

        if all(results):
            print("\n✓ All integration tests passed!")
            return 0
        else:
            print("\n✗ Some tests failed")
            return 1

    finally:
        cleanup_test_env()


if __name__ == '__main__':
    exit(main())
