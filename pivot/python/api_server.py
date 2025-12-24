"""
Pivot REST API Server - Synchronous Design
Simple Flask-based API for AVRO-to-HDF5 export
"""
from flask import Flask, request, send_file, jsonify
from datetime import datetime, timedelta
import tempfile
import os
import sys

# Add lib to path for dataset access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib/python'))
from speeddata_config import load_config
import dataset

app = Flask(__name__)

# Load configuration
config = load_config('pivot')
api_config = config.get('api', {})
limits = api_config.get('limits', {})

# Configuration
MAX_CHANNELS = limits.get('max_channels', 20)
MAX_DURATION_MINUTES = limits.get('max_duration_minutes', 5)

# Storage configuration
storage_config = config.get('storage', {})
AVRO_PATH = storage_config.get('avro_path', '../../data')


def parse_iso8601_duration(duration_str):
    """Parse ISO 8601 duration like PT30S, PT5M, PT1H"""
    if not duration_str.startswith('PT'):
        raise ValueError(f"Invalid duration format: {duration_str}")

    duration_str = duration_str[2:]  # Remove 'PT'
    seconds = 0

    if 'H' in duration_str:
        hours, duration_str = duration_str.split('H')
        seconds += int(hours) * 3600
    if 'M' in duration_str:
        minutes, duration_str = duration_str.split('M')
        seconds += int(minutes) * 60
    if 'S' in duration_str:
        secs = duration_str.replace('S', '')
        if secs:
            seconds += int(secs)

    return timedelta(seconds=seconds)


def find_avro_files(channel_name: str, start: datetime, end: datetime):
    """Find AVRO files for a channel in the time range."""
    import glob
    from pathlib import Path

    avro_dir = Path(AVRO_PATH)
    if not avro_dir.exists():
        return []

    # Find all AVRO files (simple glob for now)
    # TODO: Implement smarter file selection based on timestamps in filenames
    pattern = str(avro_dir / "*.avro")
    files = glob.glob(pattern)

    return sorted(files)


def load_avro_data(channel_name: str, start: datetime, end: datetime, signals=None):
    """Load AVRO data from relay storage and filter by time range."""
    import avro.datafile
    import avro.io
    import numpy as np

    files = find_avro_files(channel_name, start, end)
    if not files:
        raise FileNotFoundError(f"No AVRO files found for channel {channel_name}")

    # Collect records from all files
    all_records = []
    for file_path in files:
        try:
            with open(file_path, 'rb') as f:
                reader = avro.datafile.DataFileReader(f, avro.io.DatumReader())
                for record in reader:
                    # Filter by time range if 'time' field exists
                    if 'time' in record:
                        # Assume time is Unix timestamp
                        record_time = datetime.fromtimestamp(record['time'])
                        if start <= record_time <= end:
                            all_records.append(record)
                    else:
                        all_records.append(record)
                reader.close()
        except Exception as e:
            print(f"Warning: Failed to read {file_path}: {e}")
            continue

    if not all_records:
        raise ValueError(f"No records found in time range for channel {channel_name}")

    # Extract signals
    time_data = []
    signal_data = {}

    for record in all_records:
        if 'time' in record:
            time_data.append(record['time'])

        for key, value in record.items():
            if key != 'time':
                # Filter signals if specified
                if signals and key not in signals:
                    continue

                if key not in signal_data:
                    signal_data[key] = []
                signal_data[key].append(value)

    return {
        'time': np.array(time_data) if time_data else None,
        'signals': {k: np.array(v) for k, v in signal_data.items()}
    }


@app.route('/api/v1/pivot/export', methods=['GET'])
def export():
    """
    Export AVRO data to HDF5 format

    Query Parameters:
    - start: ISO 8601 timestamp (required)
    - end: ISO 8601 timestamp (optional, defaults to now)
    - duration: ISO 8601 duration (alternative to end, e.g., PT30S)
    - channels: Comma-separated channel list (required)
    - signals: Comma-separated signal list (optional, defaults to all)

    Returns:
    - 200: HDF5 file
    - 400: Bad request (invalid parameters)
    - 413: Request too large (exceeds limits)
    - 500: Server error
    """
    try:
        # Parse time range
        start_str = request.args.get('start')
        if not start_str:
            return jsonify({"error": "Missing required parameter: start"}), 400

        try:
            start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        except ValueError as e:
            return jsonify({"error": f"Invalid start timestamp: {e}"}), 400

        # Determine end time
        end_str = request.args.get('end')
        duration_str = request.args.get('duration')

        if end_str:
            try:
                end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            except ValueError as e:
                return jsonify({"error": f"Invalid end timestamp: {e}"}), 400
        elif duration_str:
            try:
                duration = parse_iso8601_duration(duration_str)
                end = start + duration
            except ValueError as e:
                return jsonify({"error": f"Invalid duration: {e}"}), 400
        else:
            end = datetime.now()

        # Validate time range
        if start >= end:
            return jsonify({"error": "start must be before end"}), 400

        duration = end - start
        if duration > timedelta(minutes=MAX_DURATION_MINUTES):
            return jsonify({
                "error": f"Time range exceeds maximum ({MAX_DURATION_MINUTES} minutes)",
                "requested_minutes": duration.total_seconds() / 60
            }), 413

        # Parse channels
        channels_str = request.args.get('channels')
        if not channels_str:
            return jsonify({"error": "Missing required parameter: channels"}), 400

        channels = [c.strip() for c in channels_str.split(',')]
        if len(channels) > MAX_CHANNELS:
            return jsonify({
                "error": f"Channel count exceeds maximum ({MAX_CHANNELS})",
                "requested_channels": len(channels)
            }), 413

        # Parse signals (optional)
        signals_str = request.args.get('signals')
        signals = [s.strip() for s in signals_str.split(',')] if signals_str else None

        # Generate HDF5 file from AVRO data
        import h5py
        import numpy as np

        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as tmp:
            tmp_path = tmp.name

        with h5py.File(tmp_path, 'w') as f:
            for channel in channels:
                try:
                    # Load AVRO data for this channel
                    data = load_avro_data(channel, start, end, signals)

                    # Create HDF5 group for channel
                    grp = f.create_group(channel)

                    # Write time array
                    if data['time'] is not None:
                        grp.create_dataset('time', data=data['time'])

                    # Write signal datasets
                    for signal_name, signal_values in data['signals'].items():
                        grp.create_dataset(signal_name, data=signal_values)

                except FileNotFoundError as e:
                    # Channel has no data - create empty group
                    print(f"Warning: {e}")
                    grp = f.create_group(channel)
                except ValueError as e:
                    # No records in time range - create empty group
                    print(f"Warning: {e}")
                    grp = f.create_group(channel)

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'export_{timestamp}.h5'

        # Send file and clean up
        return send_file(
            tmp_path,
            mimetype='application/x-hdf5',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "pivot-api"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
