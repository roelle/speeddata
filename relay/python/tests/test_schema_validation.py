"""Tests for AVRO schema validation"""
import json
import tempfile
import os
import pytest


def test_valid_schema():
    """Test that example schema is valid JSON"""

    schema_path = os.path.join(
        os.path.dirname(__file__),
        '../../../config/agents/example.avsc'
    )

    # Should load without error
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    # Verify required fields
    assert 'type' in schema
    assert schema['type'] == 'record'
    assert 'fields' in schema
    assert len(schema['fields']) > 0


def test_schema_has_required_structure():
    """Test that schema follows AVRO record structure"""

    schema_path = os.path.join(
        os.path.dirname(__file__),
        '../../../config/agents/example.avsc'
    )

    with open(schema_path, 'r') as f:
        schema = json.load(f)

    # Each field should have name and type
    for field in schema['fields']:
        assert 'name' in field
        assert 'type' in field


def test_invalid_schema_rejected():
    """Test that invalid JSON is rejected"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.avsc', delete=False) as tmp:
        tmp.write('{ invalid json }')
        tmp_path = tmp.name

    try:
        with pytest.raises(json.JSONDecodeError):
            with open(tmp_path, 'r') as f:
                json.load(f)
    finally:
        os.unlink(tmp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
