# SpeedData Changelog

## v0.2 - February 2025

### Architecture
- Implemented service-oriented architecture with process isolation
- Independent services: relay, stripchart, pivot
- Clear separation of concerns per DRR decisions

### Directory Structure
- Created organized folder hierarchy:
  - `config/agents/` - AVRO schema files
  - `relay/python/` - Relay service
  - `stripchart/server/` - WebSocket server
  - `stripchart/frontend/` - Web frontend
  - `pivot/python/` - Row-to-column transformer
  - `lib/python/` - Roelle DataSet library
  - `examples/sender/` - Example data sources
  - `tests/` - Integration tests

### Build System
- Added Makefile with targets:
  - `make install` - Install dependencies
  - `make test` - Run all tests (8 passing)
  - `make validate-schemas` - Validate AVRO schemas
  - `make clean` - Remove build artifacts
  - `make start/stop` - Service lifecycle
  - `make help` - Show available targets

### Testing
- Added pytest test framework
- Created test suites:
  - Dataset HDF5 loading (4 tests)
  - AVRO schema validation (3 tests)
  - Pivot basic functionality (1 test)
- All tests passing

### Roelle DataSet Integration
- Added HDF5 loader: `read_hdf5(file_path)`
- Added `Set.from_hdf5()` static method
- Added `Channel.from_hdf5_group()` for channel loading
- Supports SpeedData pivot output format:
  - Signal → HDF5 dataset
  - Channel → HDF5 group
  - Set → HDF5 file

### Configuration
- Centralized AVRO schemas in `config/agents/`
- Updated all services to use config paths
- Added schema validation tooling

### Dependencies
- Added pandas==2.2.3 (for DataFrame support)
- Added pytest==8.0.0 (testing framework)
- Existing: avro, h5py, numpy, supervisor

### Documentation
- Updated README with v0.2 structure
- Added config/agents/README.md for schema documentation
- Created this CHANGELOG

### Migration Notes
- File paths updated to reference new directory structure
- Supervisor config updated for new working directories
- `index.html` moved to `stripchart/frontend/`
- Example schemas in `config/agents/example.avsc`

## v0.1 - January 2025

### Initial Release
- Proof-of-concept implementation
- Basic UDP relay (rowdog.py)
- AVRO wire encoding
- WebSocket stripchart server
- Simple web frontend
- Row-to-column pivot (catcol.py)
- Example sender/receiver
