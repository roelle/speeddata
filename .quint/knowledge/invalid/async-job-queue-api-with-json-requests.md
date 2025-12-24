---
kind: system
scope: SpeedData v0.3+ Pivot API. Large queries (100+ channels, hours of data). Production deployments with multiple users. Supports long-running exports without HTTP timeout issues.
content_hash: 4c6df5ccdb57e09b2763bd02ea2a059b
---

# Hypothesis: Async Job Queue API with JSON Requests

Production-grade API with async job execution for large export requests. Supports long-running queries without HTTP timeouts.

**Endpoints:**

**1. Create Export Job:**
```
POST /api/v1/pivot/jobs
Content-Type: application/json

{
  "time_range": {
    "type": "absolute",  // or "relative", "duration"
    "start": "2025-01-23T14:30:00Z",
    "end": "2025-01-23T15:30:00Z"
  },
  "channels": {
    "include": ["ch1", "ch2", "ch3"],
    "exclude": [],
    "pattern": null  // future: glob support
  },
  "signals": {
    "ch1": ["voltage", "current"],
    "ch2": "*",  // all signals
    "ch3": ["temperature"]
  },
  "options": {
    "decimation": null,  // future: export decimation
    "format": "hdf5",
    "metadata": {
      "description": "Analysis run #42",
      "user": "researcher@lab.com"
    }
  }
}

Response: 202 Accepted
{
  "job_id": "abc123",
  "status": "queued",
  "created_at": "2025-01-23T14:35:00Z"
}
```

**2. Poll Job Status:**
```
GET /api/v1/pivot/jobs/{job_id}

Response:
{
  "job_id": "abc123",
  "status": "completed",  // or "queued", "processing", "failed"
  "progress": 100,
  "created_at": "2025-01-23T14:35:00Z",
  "completed_at": "2025-01-23T14:37:23Z",
  "result": {
    "file_url": "/api/v1/pivot/jobs/abc123/download",
    "file_size": 12345678,
    "channels_exported": 3,
    "time_range_actual": {
      "start": "2025-01-23T14:30:00Z",
      "end": "2025-01-23T15:30:00Z"
    }
  },
  "error": null
}
```

**3. Download Result:**
```
GET /api/v1/pivot/jobs/{job_id}/download

Response: HDF5 file
```

**4. List Jobs:**
```
GET /api/v1/pivot/jobs?status=completed&limit=10

Response:
{
  "jobs": [...],
  "total": 42,
  "page": 1
}
```

**5. Cancel Job:**
```
DELETE /api/v1/pivot/jobs/{job_id}
```

**Job Management:**
- Job state stored in SQLite database (pivot/jobs.db)
- Background worker processes jobs from queue
- Job retention: 24 hours after completion, then auto-delete
- Max concurrent jobs: 3
- Job timeout: 1 hour max

**Authentication:**
- API key via header: `X-API-Key: <key>`
- Optional: per-user job quotas

**Time Specification Variants:**
```json
// Absolute
{"type": "absolute", "start": "...", "end": "..."}

// Start + duration
{"type": "start_duration", "start": "...", "duration": "PT30M"}

// End + duration (backward)
{"type": "end_duration", "end": "...", "duration": "PT30M"}

// Relative (backward from now)
{"type": "relative", "duration": "PT1H"}

// Named preset
{"type": "preset", "name": "last_hour"}
```

**Python Client:**
```python
import requests, time

# Submit job
resp = requests.post('http://localhost:8000/api/v1/pivot/jobs', json={
    'time_range': {'type': 'relative', 'duration': 'PT1H'},
    'channels': {'include': ['ch1', 'ch2']}
})
job_id = resp.json()['job_id']

# Poll until complete
while True:
    status = requests.get(f'http://localhost:8000/api/v1/pivot/jobs/{job_id}').json()
    if status['status'] == 'completed':
        break
    time.sleep(2)

# Download result
file_resp = requests.get(f'http://localhost:8000/api/v1/pivot/jobs/{job_id}/download')
with open('export.h5', 'wb') as f:
    f.write(file_resp.content)
```

## Rationale
{"anomaly": "Large pivot queries (hours of data, 100 channels) exceed HTTP timeout limits. Sync API would fail or require unreasonable timeout values.", "approach": "Async job queue pattern - submit request, poll status, download when ready. Standard pattern for long-running operations.", "alternatives_rejected": ["WebSocket streaming (doesn't solve timeout, adds complexity)", "Server-sent events (one-directional, doesn't fit request/response)", "Sync with infinite timeout (ties up connections, no progress visibility)"]}