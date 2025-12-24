#!/usr/bin/env python3
"""
SpeedData Relay Orchestrator
Manages fleet of C relay processes (one per channel)
"""
import subprocess
import time
import signal
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

# Add lib to path for config access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lib/python'))
from speeddata_config import load_config


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
    """Orchestrates fleet of relay processes"""

    def __init__(self, config_path: str = 'config', relay_binary: str = 'relay/c/build/relay'):
        self.config = load_config('relay', config_path)
        self.global_config = self._load_global_config(config_path)
        self.relay_binary = relay_binary
        self.processes: Dict[str, RelayProcess] = {}
        self.running = True

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

    def start_all(self):
        """Start all configured channel relays"""
        channels = self.config.get('channels', [])
        if not channels:
            print("WARNING: No channels configured in relay.yaml")
            return

        print(f"Starting {len(channels)} relay process(es)...\n")

        for channel in channels:
            name = channel['name']
            relay = RelayProcess(channel, self.relay_binary, self.global_config)
            self.processes[name] = relay
            relay.start()
            time.sleep(0.5)  # Stagger starts

        print(f"\n✓ All {len(self.processes)} relay processes started")

    def stop_all(self):
        """Stop all relay processes"""
        print("\nStopping all relay processes...")

        for relay in self.processes.values():
            relay.stop()

        print("✓ All relay processes stopped")

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

    def run(self):
        """Main orchestrator run loop"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, lambda s, f: None)  # Handle in monitor_loop
        signal.signal(signal.SIGTERM, self._shutdown_handler)

        try:
            self.start_all()
            self.status()
            self.monitor_loop()
        finally:
            self.stop_all()

    def _shutdown_handler(self, sig, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {sig}, shutting down...")
        self.running = False


def main():
    import argparse

    parser = argparse.ArgumentParser(description='SpeedData Relay Orchestrator')
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

    args = parser.parse_args()

    print("=== SpeedData Relay Orchestrator ===\n")

    try:
        orchestrator = RelayOrchestrator(args.config, args.binary)
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
