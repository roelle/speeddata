#!/usr/bin/env python3
"""
Integration tests for channel registration REST API
Tests API → DB → Orchestrator integration
"""
import pytest
import json
import tempfile
from pathlib import Path
import sys
import os

# Add relay module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../relay'))

from registry_db import RegistryDB
from api import create_app


class MockOrchestrator:
    """Mock orchestrator for testing API without spawning real processes"""

    def __init__(self):
        self.spawned = []
        self.stopped = []
        self.next_pid = 1000

    def spawn_relay(self, channel_config):
        """Mock spawn - just record what was requested"""
        self.spawned.append(channel_config)
        pid = self.next_pid
        self.next_pid += 1
        return pid

    def stop_relay(self, name):
        """Mock stop - just record what was stopped"""
        self.stopped.append(name)


@pytest.fixture
def test_db():
    """Create temporary test database"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_registry.db"
        yield RegistryDB(str(db_path))


@pytest.fixture
def test_schema(tmpdir):
    """Create test AVRO schema file"""
    schema = {
        "namespace": "test.sensor",
        "type": "record",
        "name": "data",
        "fields": [
            {"name": "time", "type": "long"},
            {"name": "value", "type": "double"}
        ]
    }
    schema_path = Path(tmpdir) / "test_schema.avsc"
    with open(schema_path, 'w') as f:
        json.dump(schema, f)
    return str(schema_path)


@pytest.fixture
def client(test_db, test_schema, tmpdir):
    """Create Flask test client with mock orchestrator"""
    mock_orch = MockOrchestrator()
    app = create_app(test_db, mock_orch)
    app.config['TESTING'] = True

    with app.test_client() as client:
        # Attach mock orchestrator for assertions
        client.mock_orch = mock_orch
        # Attach test schema path
        client.test_schema = test_schema
        yield client


def test_health_check(client):
    """Test /health endpoint"""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'service' in data


def test_list_channels_empty(client):
    """Test listing channels when none registered"""
    response = client.get('/api/v1/channels')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['channels'] == []


def test_register_channel_success(client):
    """Test successful channel registration"""
    payload = {
        "name": "sensor1",
        "port": 26001,
        "schema": client.test_schema,
        "config": {"decimation": 5}
    }

    response = client.post('/api/v1/channels',
                          json=payload,
                          content_type='application/json')

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['name'] == 'sensor1'
    assert data['port'] == 26001
    assert 'pid' in data

    # Verify orchestrator was called
    assert len(client.mock_orch.spawned) == 1
    assert client.mock_orch.spawned[0]['name'] == 'sensor1'


def test_register_channel_port_conflict(client):
    """Test port conflict detection"""
    # Register first channel
    payload1 = {
        "name": "sensor1",
        "port": 26001,
        "schema": client.test_schema
    }
    client.post('/api/v1/channels', json=payload1)

    # Try to register second channel with same port
    payload2 = {
        "name": "sensor2",
        "port": 26001,
        "schema": client.test_schema
    }
    response = client.post('/api/v1/channels', json=payload2)

    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'Port already in use' in data['error']
    assert data['used_by'] == 'sensor1'


def test_register_channel_missing_fields(client):
    """Test validation of required fields"""
    payload = {"name": "sensor1"}  # Missing port and schema

    response = client.post('/api/v1/channels', json=payload)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Missing required fields' in data['error']


def test_get_channel(client):
    """Test retrieving specific channel details"""
    # Register channel first
    payload = {
        "name": "sensor1",
        "port": 26001,
        "schema": client.test_schema
    }
    client.post('/api/v1/channels', json=payload)

    # Retrieve it
    response = client.get('/api/v1/channels/sensor1')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'sensor1'
    assert data['port'] == 26001
    assert 'pid' in data


def test_get_channel_not_found(client):
    """Test retrieving non-existent channel"""
    response = client.get('/api/v1/channels/nonexistent')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'not found' in data['error'].lower()


def test_deregister_channel(client):
    """Test channel de-registration"""
    # Register channel first
    payload = {
        "name": "sensor1",
        "port": 26001,
        "schema": client.test_schema
    }
    client.post('/api/v1/channels', json=payload)

    # De-register it
    response = client.delete('/api/v1/channels/sensor1')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'

    # Verify orchestrator stop was called
    assert 'sensor1' in client.mock_orch.stopped

    # Verify channel is gone
    response = client.get('/api/v1/channels/sensor1')
    assert response.status_code == 404


def test_get_channel_schema(client):
    """Test retrieving AVRO schema"""
    # Register channel
    payload = {
        "name": "sensor1",
        "port": 26001,
        "schema": client.test_schema
    }
    client.post('/api/v1/channels', json=payload)

    # Get schema
    response = client.get('/api/v1/channels/sensor1/schema')

    assert response.status_code == 200
    schema = json.loads(response.data)
    assert schema['namespace'] == 'test.sensor'
    assert schema['type'] == 'record'


def test_validate_schema_match(client):
    """Test schema validation when schemas match"""
    # Register channel
    payload = {
        "name": "sensor1",
        "port": 26001,
        "schema": client.test_schema
    }
    client.post('/api/v1/channels', json=payload)

    # Load matching schema
    with open(client.test_schema) as f:
        schema = json.load(f)

    # Validate
    response = client.post('/api/v1/channels/sensor1/validate-schema',
                          json={"schema": schema})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] is True


def test_validate_schema_mismatch(client):
    """Test schema validation when schemas don't match"""
    # Register channel
    payload = {
        "name": "sensor1",
        "port": 26001,
        "schema": client.test_schema
    }
    client.post('/api/v1/channels', json=payload)

    # Different schema
    wrong_schema = {
        "namespace": "wrong",
        "type": "record",
        "name": "data",
        "fields": [{"name": "foo", "type": "int"}]
    }

    response = client.post('/api/v1/channels/sensor1/validate-schema',
                          json={"schema": wrong_schema})

    assert response.status_code == 409
    data = json.loads(response.data)
    assert data['valid'] is False


def test_list_available_ports(client):
    """Test listing available ports"""
    response = client.get('/api/v1/ports/available?start=26000&end=26010')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['available']) == 11  # Inclusive range


def test_check_port_status_available(client):
    """Test checking if specific port is available"""
    response = client.get('/api/v1/ports/26001/status')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['available'] is True
    assert data['status'] == 'free'


def test_check_port_status_in_use(client):
    """Test checking port that's in use"""
    # Register channel
    payload = {
        "name": "sensor1",
        "port": 26001,
        "schema": client.test_schema
    }
    client.post('/api/v1/channels', json=payload)

    # Check port
    response = client.get('/api/v1/ports/26001/status')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['available'] is False
    assert data['status'] == 'in_use'
    assert data['channel'] == 'sensor1'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
