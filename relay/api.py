#!/usr/bin/env python3
"""
Channel Registration REST API
Flask blueprint for dynamic channel management
"""
from flask import Flask, Blueprint, request, jsonify
from pathlib import Path
import json
from typing import Optional

from registry_db import RegistryDB


# Create blueprint
api = Blueprint('registration_api', __name__)

# Database instance (set by orchestrator)
db: Optional[RegistryDB] = None
orchestrator = None  # Reference to orchestrator for relay management


def init_api(database: RegistryDB, orch):
    """Initialize API with database and orchestrator references"""
    global db, orchestrator
    db = database
    orchestrator = orch


@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "speeddata-registration-api",
        "version": "0.5.0"
    })


@api.route('/channels', methods=['GET'])
def list_channels():
    """List all registered channels"""
    status_filter = request.args.get('status')
    channels = db.list_channels(status=status_filter)

    # Remove internal fields
    for ch in channels:
        ch.pop('config_json', None)

    return jsonify({"channels": channels})


@api.route('/channels/<name>', methods=['GET'])
def get_channel(name: str):
    """Get specific channel details"""
    channel = db.get_channel(name)

    if not channel:
        return jsonify({"error": "Channel not found", "name": name}), 404

    channel.pop('config_json', None)
    return jsonify(channel)


@api.route('/channels', methods=['POST'])
def register_channel():
    """
    Register a new channel
    Request body: {"name": "...", "port": ..., "schema": "...", "config": {...}}
    """
    data = request.get_json()

    # Validation
    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get('name')
    port = data.get('port')
    schema_path = data.get('schema')

    if not all([name, port, schema_path]):
        return jsonify({
            "error": "Missing required fields",
            "required": ["name", "port", "schema"]
        }), 400

    # Validate port is integer
    try:
        port = int(port)
    except (ValueError, TypeError):
        return jsonify({"error": "Port must be an integer"}), 400

    # Check if port is available
    if not db.is_port_available(port):
        existing = db.get_channel(name)
        if existing and existing['port'] == port:
            return jsonify({
                "error": "Port already in use",
                "port": port,
                "used_by": name
            }), 409
        else:
            # Find which channel is using the port
            channels = db.list_channels()
            for ch in channels:
                if ch['port'] == port:
                    return jsonify({
                        "error": "Port already in use",
                        "port": port,
                        "used_by": ch['name']
                    }), 409

    # Validate schema file exists
    schema_file = Path(schema_path)
    if not schema_file.exists():
        return jsonify({
            "error": "Schema file not found",
            "path": schema_path
        }), 400

    # Validate schema is valid JSON
    try:
        with open(schema_file) as f:
            schema_json = json.load(f)
    except json.JSONDecodeError as e:
        return jsonify({
            "error": "Invalid schema file (not valid JSON)",
            "path": schema_path,
            "details": str(e)
        }), 400

    # Register in database
    config = data.get('config', {})
    success = db.register_channel(name, port, schema_path, config)

    if not success:
        return jsonify({
            "error": "Channel name already registered",
            "name": name
        }), 409

    # Spawn relay process via orchestrator
    try:
        channel_config = {
            'name': name,
            'port': port,
            'schema': schema_path,
            **config
        }
        pid = orchestrator.spawn_relay(channel_config)

        # Update database with PID
        db.update_process_info(name, pid, "active")

        return jsonify({
            "status": "success",
            "name": name,
            "port": port,
            "pid": pid,
            "message": f"Channel '{name}' registered and relay started"
        }), 201

    except Exception as e:
        # Rollback registration if spawn fails
        db.deregister_channel(name)
        return jsonify({
            "error": "Failed to start relay process",
            "name": name,
            "details": str(e)
        }), 500


@api.route('/channels/<name>', methods=['DELETE'])
def deregister_channel(name: str):
    """De-register a channel and stop its relay"""
    channel = db.get_channel(name)

    if not channel:
        return jsonify({"error": "Channel not found", "name": name}), 404

    # Stop relay process via orchestrator
    try:
        orchestrator.stop_relay(name)
    except Exception as e:
        return jsonify({
            "error": "Failed to stop relay process",
            "name": name,
            "details": str(e)
        }), 500

    # Remove from database
    db.deregister_channel(name)

    return jsonify({
        "status": "success",
        "name": name,
        "message": f"Channel '{name}' de-registered and relay stopped"
    })


@api.route('/channels/<name>/schema', methods=['GET'])
def get_channel_schema(name: str):
    """Retrieve the full AVRO schema for a channel"""
    channel = db.get_channel(name)

    if not channel:
        return jsonify({"error": "Channel not found", "name": name}), 404

    schema_path = Path(channel['schema_path'])
    if not schema_path.exists():
        return jsonify({
            "error": "Schema file not found",
            "path": str(schema_path)
        }), 404

    try:
        with open(schema_path) as f:
            schema = json.load(f)
        return jsonify(schema)
    except Exception as e:
        return jsonify({
            "error": "Failed to read schema",
            "details": str(e)
        }), 500


@api.route('/channels/<name>/validate-schema', methods=['POST'])
def validate_schema(name: str):
    """
    Validate if provided schema matches registered schema
    Request body: {"schema": {...}}
    """
    channel = db.get_channel(name)

    if not channel:
        return jsonify({"error": "Channel not found", "name": name}), 404

    data = request.get_json()
    if not data or 'schema' not in data:
        return jsonify({"error": "Request body must contain 'schema' field"}), 400

    provided_schema = data['schema']

    # Load registered schema
    schema_path = Path(channel['schema_path'])
    try:
        with open(schema_path) as f:
            registered_schema = json.load(f)
    except Exception as e:
        return jsonify({
            "error": "Failed to load registered schema",
            "details": str(e)
        }), 500

    # Simple equality check (can be enhanced with AVRO schema compatibility)
    if provided_schema == registered_schema:
        return jsonify({
            "valid": True,
            "message": "Schema matches registered schema"
        })
    else:
        return jsonify({
            "valid": False,
            "message": "Schema does not match",
            "registered_schema": registered_schema,
            "provided_schema": provided_schema
        }), 409


@api.route('/ports/available', methods=['GET'])
def list_available_ports():
    """List available ports in range"""
    start = int(request.args.get('start', 26000))
    end = int(request.args.get('end', 27000))

    if start >= end:
        return jsonify({"error": "Invalid range: start must be < end"}), 400

    available = db.get_available_ports(start, end)

    return jsonify({
        "range": {"start": start, "end": end},
        "available": available,
        "count": len(available)
    })


@api.route('/ports/<int:port>/status', methods=['GET'])
def check_port_status(port: int):
    """Check if a specific port is available"""
    available = db.is_port_available(port)

    if available:
        return jsonify({
            "port": port,
            "available": True,
            "status": "free"
        })
    else:
        # Find which channel is using it
        channels = db.list_channels()
        for ch in channels:
            if ch['port'] == port:
                return jsonify({
                    "port": port,
                    "available": False,
                    "status": "in_use",
                    "channel": ch['name']
                })


def create_app(database: RegistryDB, orch) -> Flask:
    """Create Flask app with registration API"""
    # Determine static folder path relative to api.py
    api_dir = Path(__file__).parent
    static_folder = api_dir.parent / 'registration' / 'frontend'

    app = Flask(__name__,
                static_folder=str(static_folder),
                static_url_path='')

    init_api(database, orch)
    app.register_blueprint(api, url_prefix='/api/v1')

    # Serve registration frontend at root
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app
