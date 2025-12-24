#!/usr/bin/env python3
"""
Channel Registry Database Module
SQLite backend for dynamic channel registration
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class RegistryDB:
    """SQLite database for channel registration state"""

    def __init__(self, db_path: str = "data/registry.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                name TEXT PRIMARY KEY,
                port INTEGER UNIQUE NOT NULL,
                schema_path TEXT NOT NULL,
                config_json TEXT,
                status TEXT DEFAULT 'registered',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pid INTEGER,
                last_heartbeat TIMESTAMP
            )
        """)

        # Index for fast port availability queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_port ON channels(port)
        """)

        # Index for status queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON channels(status)
        """)

        conn.commit()
        conn.close()

    def register_channel(self, name: str, port: int, schema_path: str,
                        config: Optional[Dict] = None) -> bool:
        """
        Register a new channel
        Returns True on success, False if port/name already exists
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            config_json = json.dumps(config) if config else None

            cursor.execute("""
                INSERT INTO channels (name, port, schema_path, config_json)
                VALUES (?, ?, ?, ?)
            """, (name, port, schema_path, config_json))

            conn.commit()
            conn.close()
            return True

        except sqlite3.IntegrityError:
            # Port or name already exists
            return False

    def deregister_channel(self, name: str) -> bool:
        """
        De-register a channel
        Returns True if channel was deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM channels WHERE name = ?", (name,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return deleted

    def get_channel(self, name: str) -> Optional[Dict]:
        """Get channel details by name"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM channels WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()

        if row:
            channel = dict(row)
            if channel['config_json']:
                channel['config'] = json.loads(channel['config_json'])
            return channel
        return None

    def list_channels(self, status: Optional[str] = None) -> List[Dict]:
        """List all channels, optionally filtered by status"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM channels WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM channels")

        rows = cursor.fetchall()
        conn.close()

        channels = []
        for row in rows:
            channel = dict(row)
            if channel['config_json']:
                channel['config'] = json.loads(channel['config_json'])
            channels.append(channel)

        return channels

    def is_port_available(self, port: int) -> bool:
        """Check if a port is available (not registered)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM channels WHERE port = ?", (port,))
        exists = cursor.fetchone() is not None

        conn.close()
        return not exists

    def get_available_ports(self, start: int = 26000, end: int = 27000) -> List[int]:
        """Get list of available ports in range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT port FROM channels WHERE port BETWEEN ? AND ?",
                      (start, end))
        used_ports = {row[0] for row in cursor.fetchall()}
        conn.close()

        return [port for port in range(start, end + 1) if port not in used_ports]

    def update_process_info(self, name: str, pid: int, status: str = "active"):
        """Update channel with relay process PID and status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE channels
            SET pid = ?, status = ?, last_heartbeat = CURRENT_TIMESTAMP
            WHERE name = ?
        """, (pid, status, name))

        conn.commit()
        conn.close()

    def clear_process_info(self, name: str):
        """Clear process info when relay stops"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE channels
            SET pid = NULL, status = 'registered'
            WHERE name = ?
        """, (name,))

        conn.commit()
        conn.close()

    def load_yaml_baseline(self, yaml_channels: List[Dict]) -> int:
        """
        Load baseline channels from YAML config
        Only inserts channels that don't already exist (DB takes precedence)
        Returns count of channels inserted
        """
        inserted = 0
        for channel in yaml_channels:
            success = self.register_channel(
                name=channel['name'],
                port=channel['port'],
                schema_path=channel.get('schema', ''),
                config=channel
            )
            if success:
                inserted += 1
        return inserted
