# Agent Schema Configuration

This directory contains AVRO schema files for data channels sent by remote agents.

## File Structure

Each agent has its own schema file: `{agent_id}.avsc`

Schema files are JSON-formatted AVRO schema definitions.

## Example Schema

See `example.avsc` for a reference schema with:
- Timestamp field (long with timestamp-nanos logical type)
- Message field (string)
- Number field (int)

## Adding a New Channel

1. Create new `.avsc` file with agent ID
2. Define schema fields matching agent's data structure
3. Assign UDP port in relay configuration
4. Restart relay to load new schema

## Schema Evolution

AVRO supports schema evolution with default values. When modifying schemas:
- Add new fields with default values
- Avoid removing or renaming existing fields
- Coordinate schema updates with agent firmware updates

## Validation

Run `make validate-schemas` to check schema files for errors.
