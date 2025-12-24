# SpeedData Channel Registration API (v0.5)

REST API for dynamic channel registration and management.

## Base URL

```
http://localhost:8080/api/v1
```

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "service": "speeddata-registration-api",
  "version": "0.5.0"
}
```

---

### List Channels

```http
GET /channels?status={status}
```

**Query Parameters:**
- `status` (optional): Filter by status (`registered`, `active`)

**Response:**
```json
{
  "channels": [
    {
      "name": "sensor1",
      "port": 26001,
      "schema_path": "config/agents/sensor1.avsc",
      "status": "active",
      "pid": 12345,
      "created_at": "2025-12-24T10:00:00",
      "config": {"decimation": 5}
    }
  ]
}
```

---

### Get Channel Details

```http
GET /channels/{name}
```

**Response:**
```json
{
  "name": "sensor1",
  "port": 26001,
  "schema_path": "config/agents/sensor1.avsc",
  "status": "active",
  "pid": 12345,
  "created_at": "2025-12-24T10:00:00",
  "config": {"decimation": 5}
}
```

**Errors:**
- `404` - Channel not found

---

### Register Channel

```http
POST /channels
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "sensor1",
  "port": 26001,
  "schema": "config/agents/sensor1.avsc",
  "config": {
    "decimation": 5,
    "rotation": 3600
  }
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "name": "sensor1",
  "port": 26001,
  "pid": 12345,
  "message": "Channel 'sensor1' registered and relay started"
}
```

**Errors:**
- `400` - Missing required fields or invalid schema
- `409` - Port or name already in use
- `500` - Failed to start relay process

---

### De-register Channel

```http
DELETE /channels/{name}
```

**Response:**
```json
{
  "status": "success",
  "name": "sensor1",
  "message": "Channel 'sensor1' de-registered and relay stopped"
}
```

**Errors:**
- `404` - Channel not found
- `500` - Failed to stop relay process

---

### Get Channel Schema

```http
GET /channels/{name}/schema
```

**Response:**
```json
{
  "namespace": "speeddata.sensor1",
  "type": "record",
  "name": "data",
  "fields": [
    {"name": "time", "type": "long", "logicalType": "timestamp-nanos"},
    {"name": "temperature", "type": "double"},
    {"name": "pressure", "type": "double"}
  ]
}
```

**Errors:**
- `404` - Channel or schema file not found
- `500` - Failed to read schema

---

### Validate Schema

```http
POST /channels/{name}/validate-schema
Content-Type: application/json
```

**Request Body:**
```json
{
  "schema": {
    "namespace": "speeddata.sensor1",
    "type": "record",
    "name": "data",
    "fields": [...]
  }
}
```

**Response (schema matches):**
```json
{
  "valid": true,
  "message": "Schema matches registered schema"
}
```

**Response (schema mismatch - 409):**
```json
{
  "valid": false,
  "message": "Schema does not match",
  "registered_schema": {...},
  "provided_schema": {...}
}
```

**Errors:**
- `404` - Channel not found
- `400` - Missing 'schema' field in request

---

### List Available Ports

```http
GET /ports/available?start={start}&end={end}
```

**Query Parameters:**
- `start` (default: 26000): Range start (inclusive)
- `end` (default: 27000): Range end (inclusive)

**Response:**
```json
{
  "range": {"start": 26000, "end": 27000},
  "available": [26000, 26002, 26003, ...],
  "count": 998
}
```

**Errors:**
- `400` - Invalid range (start >= end)

---

### Check Port Status

```http
GET /ports/{port}/status
```

**Response (port available):**
```json
{
  "port": 26001,
  "available": true,
  "status": "free"
}
```

**Response (port in use):**
```json
{
  "port": 26001,
  "available": false,
  "status": "in_use",
  "channel": "sensor1"
}
```

---

## Usage Examples

### Register a new channel (remote device)

```bash
curl -X POST http://localhost:8080/api/v1/channels \
  -H "Content-Type: application/json" \
  -d '{
    "name": "remote-sensor-1",
    "port": 26050,
    "schema": "config/agents/temperature.avsc",
    "config": {"decimation": 10}
  }'
```

### Check if port is available before registering

```bash
curl http://localhost:8080/api/v1/ports/26050/status
```

### Validate schema matches before sending data

```bash
curl -X POST http://localhost:8080/api/v1/channels/remote-sensor-1/validate-schema \
  -H "Content-Type: application/json" \
  -d @my_schema.json
```

### List all active channels

```bash
curl http://localhost:8080/api/v1/channels?status=active
```

### De-register when shutting down

```bash
curl -X DELETE http://localhost:8080/api/v1/channels/remote-sensor-1
```

---

## Configuration Storage

**Hybrid Model:**
- **Static baseline:** `config/relay.yaml` (git-tracked, defaults)
- **Dynamic state:** `data/registry.db` (SQLite, runtime registrations)
- **Precedence:** Database overrides YAML

**Startup Flow:**
1. Load `relay.yaml` baseline
2. Insert into `registry.db` (if not already registered)
3. Spawn relays from merged state (DB is source of truth)

**Benefits:**
- Git-managed defaults
- Runtime registration without config file edits
- Rollback to baseline by deleting DB

---

## Authentication & Security

**Current:** None (LAN-only, trusted network assumption per project invariants)

**Future Considerations:**
- API keys for remote devices
- TLS/HTTPS for external deployments
- Rate limiting for abuse prevention

---

## Error Handling

All endpoints return JSON error responses with structure:

```json
{
  "error": "Descriptive error message",
  "field": "optional-context",
  "details": "optional-detailed-info"
}
```

**Standard HTTP Status Codes:**
- `200` - Success
- `201` - Created (registration)
- `400` - Bad Request (validation failure)
- `404` - Not Found
- `409` - Conflict (port/name in use)
- `500` - Internal Server Error
