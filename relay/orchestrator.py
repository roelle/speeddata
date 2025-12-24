#!/usr/bin/env python3
"""
SpeedData Relay Orchestrator v0.5
Manages fleet of C relay processes (one per channel)
With embedded Flask REST API for dynamic channel registration
"""
import subprocess
import time
import signal
import sys
import os
import threading
from pathlib import Path
from typing import Dict, List, Optional

# Add lib to path for config access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lib/python'))
from speeddata_config import load_config

# Add relay directory to path for API imports
sys.path.insert(0, os.path.dirname(__file__))
from registry_db import RegistryDB
from api import create_app


class RelayProcess:
    """Manages a single relay process for one channel"""

    def __init__(self, channel_config: dict, relay_binary: str, global_config: dict):
        self.name = channel_config['name']
        self.port = channel_config['port']
        self.relay_binary = relay_binary
        self.process: Optional[subprocess.Popen] = None
        self.restart_count = 0
        self.last_start_time = 0

        # Extract config for environment variables
        self.env = os.environ.copy()
        self.env['RELAY_RX_PORT'] = str(self.port)

        # Global storage config
        storage = global_config.get('storage', {})
        self.env['RELAY_OUTPUT_DIR'] = storage.get('avro_path', './data')

    def start(self):
        """Start relay process"""
        if self.process and self.process.poll() is None:
            print(f"[{self.name}] Already running (PID: {self.process.pid})")
            return

        print(f"[{self.name}] Starting relay on port {self.port}...")

        self.process = subprocess.Popen(
            [self.relay_binary, self.name],
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.last_start_time = time.time()
        print(f"[{self.name}] Started (PID: {self.process.pid})")

    def stop(self):
        """Stop relay process gracefully"""
        if not self.process or self.process.poll() is not None:
            return

        print(f"[{self.name}] Stopping (PID: {self.process.pid})...")

        try:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait(timeout=5)
            print(f"[{self.name}] Stopped")
        except subprocess.TimeoutExpired:
            print(f"[{self.name}] Force killing (SIGKILL)...")
            self.process.kill()
            self.process.wait()

    def check_health(self) -> bool:
        """Check if process is healthy"""
        if not self.process:
            return False

        return_code = self.process.poll()
        if return_code is not None:
            # Process has exited
            stdout, stderr = self.process.communicate()
            print(f"[{self.name}] Process exited with code {return_code}")
            if stderr:
                print(f"[{self.name}] STDERR:\n{stderr}")
            return False

        return True

    def should_restart(self, max_restarts: int = 5, backoff: float = 5.0) -> bool:
        """Check if process should be restarted"""
        if self.restart_count >= max_restarts:
            print(f"[{self.name}] Max restart limit reached ({max_restarts})")
            return False

        # Backoff: don't restart too quickly
        time_since_start = time.time() - self.last_start_time
        if time_since_start < backoff:
            return False

        return True

    def restart(self):
        """Restart relay process"""
        print(f"[{self.name}] Restarting...")
        self.stop()
        self.restart_count += 1
        time.sleep(1)
        self.start()


class RelayOrchestrator:
    """Orchestrates fleet of relay processes with REST API"""

    def __init__(self, config_path: str = 'config', relay_binary: str = 'relay/c/build/relay',
                 enable_api: bool = True, api_port: int = 8080):
        self.config = load_config('relay', config_path)
        self.global_config = self._load_global_config(config_path)
        self.relay_binary = relay_binary
        self.processes: Dict[str, RelayProcess] = {}
        self.running = True
        self.enable_api = enable_api
        self.api_port = api_port
        self.api_thread = None
        self.process_lock = threading.Lock()  # Thread-safe process management

        # Initialize registry database
        self.db = RegistryDB("data/registry.db")

        # Initialize Flask app if API enabled
        if self.enable_api:
            self.app = create_app(self.db, self)

        # Verify relay binary exists
        if not Path(self.relay_binary).exists():
            raise FileNotFoundError(
                f"Relay binary not found: {self.relay_binary}\n"
                f"Build it with: cd relay/c && make"
            )

    def _load_global_config(self, config_path: str) -> dict:
        """Load global.yaml"""
        import yaml
        global_file = Path(config_path) / 'global.yaml'
        if global_file.exists():
            with open(global_file) as f:
                return yaml.safe_load(f) or {}
        return {}

    def _merge_config_with_db(self):
        """
        Merge YAML baseline with database state
        1. Load channels from relay.yaml as baseline
        2. Insert into DB (only if not already registered)
        3. Load final channel list from DB (DB is source of truth)
        """
        yaml_channels = self.config.get('channels', [])

        if yaml_channels:
            print(f"Loading {len(yaml_channels)} baseline channels from relay.yaml...")
            inserted = self.db.load_yaml_baseline(yaml_channels)
            print(f"  {inserted} new channels added to registry")
            print(f"  {len(yaml_channels) - inserted} channels already registered (DB takes precedence)\n")

        # Load all channels from DB
        db_channels = self.db.list_channels()
        return db_channels

    def start_all(self):
        """Start all configured channel relays from merged config"""
        # Merge YAML + DB, DB wins
        channels = self._merge_config_with_db()

        if not channels:
            print("WARNING: No channels configured (check relay.yaml or registry.db)")
            return

        print(f"Starting {len(channels)} relay process(es)...\n")

        for channel in channels:
            name = channel['name']
            try:
                # Build channel config from DB record
                channel_config = {
                    'name': name,
                    'port': channel['port'],
                    'schema': channel['schema_path']
                }
                # Merge with stored config JSON if exists
                if channel.get('config'):
                    channel_config.update(channel['config'])

                with self.process_lock:
                    relay = RelayProcess(channel_config, self.relay_binary, self.global_config)
                    self.processes[name] = relay
                    relay.start()

                    # Update DB with PID
                    self.db.update_process_info(name, relay.process.pid, "active")

                time.sleep(0.5)  # Stagger starts
            except Exception as e:
                print(f"[{name}] ERROR: Failed to start: {e}")

        print(f"\n✓ {len(self.processes)}/{len(channels)} relay processes started")

    def stop_all(self):
        """Stop all relay processes"""
        print("\nStopping all relay processes...")

        with self.process_lock:
            for name, relay in self.processes.items():
                relay.stop()
                # Clear PID from DB
                self.db.clear_process_info(name)

        print("✓ All relay processes stopped")

    def spawn_relay(self, channel_config: dict) -> int:
        """
        Spawn a new relay process for a channel (called by API)
        Returns PID of spawned process
        """
        name = channel_config['name']

        with self.process_lock:
            if name in self.processes:
                raise ValueError(f"Relay already running for channel '{name}'")

            relay = RelayProcess(channel_config, self.relay_binary, self.global_config)
            relay.start()
            self.processes[name] = relay

            return relay.process.pid

    def stop_relay(self, name: str):
        """
        Stop a specific relay process (called by API)
        """
        with self.process_lock:
            if name not in self.processes:
                raise ValueError(f"No relay running for channel '{name}'")

            relay = self.processes[name]
            relay.stop()
            del self.processes[name]

            # Clear PID from DB
            self.db.clear_process_info(name)

    def monitor_loop(self, check_interval: float = 2.0):
        """Monitor and restart failed processes"""
        print(f"\nMonitoring relay processes (check interval: {check_interval}s)")
        print("Press Ctrl+C to stop\n")

        try:
            while self.running:
                for name, relay in list(self.processes.items()):
                    if not relay.check_health():
                        if relay.should_restart():
                            relay.restart()
                        else:
                            print(f"[{name}] Not restarting (limit reached or too soon)")

                time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n\nReceived shutdown signal")
            self.running = False

    def status(self):
        """Print status of all relay processes"""
        print("\n=== Relay Fleet Status ===")
        for name, relay in self.processes.items():
            if relay.check_health():
                print(f"[{name}] RUNNING (PID: {relay.process.pid}, restarts: {relay.restart_count})")
            else:
                print(f"[{name}] STOPPED")

    def _run_api_server(self):
        """Run Flask API in background thread"""
        print(f"Starting REST API on port {self.api_port}...")
        self.app.run(host='0.0.0.0', port=self.api_port, threaded=True, debug=False)

    def run(self):
        """Main orchestrator run loop with API server"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, lambda s, f: None)  # Handle in monitor_loop
        signal.signal(signal.SIGTERM, self._shutdown_handler)

        try:
            # Start Flask API in background thread
            if self.enable_api:
                self.api_thread = threading.Thread(target=self._run_api_server, daemon=True)
                self.api_thread.start()
                print(f"✓ REST API started on http://0.0.0.0:{self.api_port}/api/v1\n")
                time.sleep(1)  # Let API server start

            # Start relay fleet
            self.start_all()
            self.status()

            # Monitor loop
            self.monitor_loop()
        finally:
            self.stop_all()

    def _shutdown_handler(self, sig, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {sig}, shutting down...")
        self.running = False


def main():
    import argparse

    parser = argparse.ArgumentParser(description='SpeedData Relay Orchestrator v0.5')
    parser.add_argument(
        '--config',
        default='config',
        help='Configuration directory (default: config)'
    )
    parser.add_argument(
        '--binary',
        default='relay/c/build/relay',
        help='Path to relay binary (default: relay/c/build/relay)'
    )
    parser.add_argument(
        '--check-interval',
        type=float,
        default=2.0,
        help='Health check interval in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--api-port',
        type=int,
        default=8080,
        help='REST API port (default: 8080)'
    )
    parser.add_argument(
        '--no-api',
        action='store_true',
        help='Disable REST API'
    )

    args = parser.parse_args()

    print("=== SpeedData Relay Orchestrator v0.5 ===")
    print("With embedded REST API for channel registration\n")

    try:
        orchestrator = RelayOrchestrator(
            args.config,
            args.binary,
            enable_api=not args.no_api,
            api_port=args.api_port
        )
        orchestrator.run()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
