# SpeedData Relay (v0.4)

High-performance compiled relay for SpeedData channels. Receives UDP packets, writes AVRO files, and multicasts data streams.

## Architecture

**Per-Channel Process Model:**
- One C relay process per channel (fault isolation)
- Python orchestrator manages process fleet
- 5Gbps per-channel throughput (50x headroom over 1Gbps Pi ethernet)

**Data Flow:**
```
UDP Receive (127.0.0.1:port)
    ↓
AVRO File Write (./data/data_<timestamp>.avro)
    ↓
Multicast Relay
    ├─→ Full-rate (239.1.1.1:6000)
    └─→ Decimated (239.1.1.2:6001) [optional]
```

**Design Decision:** C99 + stdio chosen over Rust/Zig (see `.quint/decisions/DRR-2025-12-24-v0-4-relay-architecture-c-stdio-per-channel-revised.md`)

## Build

```bash
cd relay/c
make clean && make
```

Binary: `relay/c/build/relay`

## Usage

### Single Channel (Manual)

```bash
# Set configuration via environment
export RELAY_RX_PORT=26000
export RELAY_OUTPUT_DIR=./data
export RELAY_DECIMATION_ENABLED=true
export RELAY_DECIMATION_FACTOR=5

# Run relay
./relay/c/build/relay example
```

### Fleet Management (Orchestrator)

```bash
# Start all channels from relay.yaml
python3 relay/orchestrator.py

# Custom config directory
python3 relay/orchestrator.py --config /etc/speeddata

# Custom relay binary
python3 relay/orchestrator.py --binary /usr/local/bin/relay
```

**Orchestrator Features:**
- Automatic process spawning (one per channel)
- Health monitoring and automatic restart
- Graceful shutdown (SIGTERM handling)
- Per-channel configuration from `relay.yaml`

## Configuration

**relay.yaml:**
```yaml
channels:
  - name: "example"
    port: 26000
    schema: "config/agents/example.avsc"
  - name: "sensor_1"
    port: 26001
    schema: "config/agents/sensor.avsc"

decimation:
  enabled: true
  factor: 5
  algorithm: "downsample"

rotation:
  mode: "size"
  threshold: 52428800  # 50MB

storage:
  avro_path: "./data"
```

**global.yaml:**
```yaml
multicast:
  full_rate:
    address: "239.1.1.1"
    port: 6000
  decimated:
    address: "239.1.1.2"
    port: 6001
```

## Testing

### Unit Tests

Tests AVRO encoding, decimation logic, writer components:

```bash
cd relay/c/tests
make test
```

**Coverage:**
- `test_utils`: AVRO long encoding (zigzag + varint)
- `test_decimator`: Downsampling logic (factor=1,3,5)
- `test_avro_writer`: File creation, block writes, rotation, sync marker

### Integration Tests

End-to-end UDP → AVRO → multicast flow:

```bash
cd /path/to/speeddata
python3 tests/test_relay_integration.py
```

**Tests:**
1. Basic relay (UDP in → multicast out + AVRO)
2. Decimation (factor=3, verify 2 of 6 packets decimated)
3. AVRO format (sync marker, data integrity)

### Full System Test

Complete data flow with AVRO-serialized packets:

```bash
source bin/activate  # For avro-python3
python3 tests/test_full_system.py
```

**Validates:**
- AVRO serialization (matching example.avsc schema)
- All 10 packets multicast and written to disk
- Process stability

## Performance

| Platform | Ethernet | Per-Channel Ceiling | Headroom |
|----------|----------|-------------------|----------|
| Raspberry Pi 4 | 1 Gbps | 5 Gbps | 5x |
| Mid-range server | 10 Gbps | 5 Gbps | 20 channels |
| High-end Xeon | 100 Gbps | 5 Gbps | 20 channels |

**Actual bottlenecks (v0.4):**
- Pi: 1Gbps ethernet (not relay)
- Mid: Network/disk I/O (not relay)
- Xeon: Consider io_uring upgrade if approaching 5Gbps per channel

## Implementation Notes

### AVRO Block Format

Matches Python `avro.datafile.DataFileWriter` raw block writes:
```
[object_count: varint] (always 1)
[byte_count: varint]   (length of data)
[data: bytes]
[sync_marker: 16 bytes] (fixed: 0xa48a1e90...)
```

**Why not full AVRO library?**
- Python relay uses raw block writes for performance
- C implementation must match byte-for-byte for compatibility
- Avoids apache-avro-c dependency

### Decimation

Simple downsampling (every Nth packet):
```c
count++;
if (count >= factor) {
    count = 0;
    send_to_decimated_multicast();
}
```

**Future:** Could implement averaging/minmax/RMS (requires AVRO deserialization)

### File Rotation

Currently size-based only (50MB default). Time-based rotation planned for v0.5.

## Migration from Python

1. Build C relay: `cd relay/c && make`
2. Test with orchestrator: `python3 relay/orchestrator.py`
3. Verify AVRO files compatible with existing pivot/stripchart
4. Once stable, deprecate `relay/python/rowdog.py`

**Compatibility:** AVRO files are byte-compatible with Python implementation (tested with identical sync markers).

## Troubleshooting

**"Relay binary not found"**
```bash
cd relay/c && make
```

**"No channels configured"**
- Check `relay.yaml` has `channels:` section
- Verify config path: `--config /path/to/config`

**Multicast not received**
- Check firewall: `sudo iptables -L`
- Verify multicast routing: `route -n`
- Test on localhost first (127.0.0.1 works)

**Process crashes immediately**
- Check port not in use: `netstat -tuln | grep <port>`
- Verify write permissions on output directory
- Check logs: orchestrator prints stderr

## Development

**Add new test:**
```c
// relay/c/tests/test_myfeature.c
#include "../include/relay.h"
void test_myfeature() { /* ... */ }

// relay/c/tests/Makefile
TESTS += $(BUILD_DIR)/test_myfeature
```

**Add new component:**
```c
// relay/c/include/relay.h
int my_function(int arg);

// relay/c/src/mycomponent.c
#include "relay.h"
int my_function(int arg) { /* ... */ }

// relay/c/Makefile
SOURCES += $(SRC_DIR)/mycomponent.c
```

## Future Enhancements

**v0.5+ Possibilities:**
- io_uring upgrade for >40Gbps per-channel (Linux 5.10+ only)
- Time-based rotation (in addition to size)
- Proper AVRO averaging/minmax/RMS decimation
- Compression (Snappy/Zstandard)
- Remote monitoring API

**See:** `.quint/knowledge/L2/` for architectural alternatives evaluated during design.
