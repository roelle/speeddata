---
scope: SpeedData v0.3 Pivot API. All query sizes (small interactive to large batch). JupyterLab + production automation. Adapts to deployment scale (single-user → multi-user).
kind: system
content_hash: 57692b7a2204b61d74a8a49e2ef794f7
---

# Hypothesis: Hybrid Sync/Async API with Smart Routing

Adaptive API that automatically routes requests to sync or async execution based on estimated query size. Best of both worlds - simple for small queries, robust for large ones.

**Single Endpoint:**
```
POST /api/v1/pivot/export
Content-Type: application/json

{
  "time_range": {"start": "...", "end": "..."},
  "channels": ["ch1", "ch2"],
  "signals": {"ch1": ["voltage"], "ch2": "*"},
  "execution": "auto"  // or "sync", "async"
}
```

**Smart Routing Logic:**
```python
def estimate_query_size(time_range, channels):
    duration_sec = (end - start).total_seconds()
    num_channels = len(channels)
    estimated_samples = duration_sec * max_sample_rate * num_channels
    estimated_bytes = estimated_samples * avg_bytes_per_sample
    return estimated_bytes

size = estimate_query_size(request)
if size < 10_000_000:  # <10 MB
    return sync_export(request)  # HTTP 200 with file
else:
    job_id = queue_async_export(request)
    return {"job_id": job_id, "status": "queued"}  # HTTP 202
```

**Sync Response (Small Queries):**
```
HTTP 200 OK
Content-Type: application/x-hdf5
Content-Disposition: attachment; filename="export_20250123_143045.h5"

<HDF5 binary data>
```

**Async Response (Large Queries):**
```
HTTP 202 Accepted
Content-Type: application/json

{
  "job_id": "abc123",
  "status": "queued",
  "estimated_completion": "2025-01-23T14:45:00Z",
  "poll_url": "/api/v1/pivot/jobs/abc123",
  "websocket_url": "ws://localhost:8000/api/v1/pivot/jobs/abc123/stream"
}
```

**Job Status Endpoint (for async):**
```
GET /api/v1/pivot/jobs/{job_id}

Response:
{
  "status": "completed",
  "download_url": "/api/v1/pivot/jobs/{job_id}/download",
  "expires_at": "2025-01-24T14:37:00Z"
}
```

**Optional: WebSocket Progress Updates (for async):**
```
ws://localhost:8000/api/v1/pivot/jobs/{job_id}/stream

Messages:
{"type": "progress", "percent": 25, "message": "Processing channel ch1..."}
{"type": "progress", "percent": 50, "message": "Processing channel ch2..."}
{"type": "complete", "download_url": "/api/v1/pivot/jobs/{job_id}/download"}
```

**Thresholds (Configurable):**
- Sync cutoff: <10 MB estimated output
- Sync timeout: 30 seconds max
- If sync takes >30s, returns 503 with suggestion to retry with `execution=async`

**Python Client (Transparent Handling):**
```python
class PivotClient:
    def export(self, time_range, channels, signals=None):
        resp = self._post('/api/v1/pivot/export', {
            'time_range': time_range,
            'channels': channels,
            'signals': signals,
            'execution': 'auto'
        })
        
        if resp.status_code == 200:
            # Sync response - return file immediately
            return resp.content
        
        elif resp.status_code == 202:
            # Async response - poll until complete
            job_id = resp.json()['job_id']
            return self._wait_for_job(job_id)
        
    def _wait_for_job(self, job_id):
        while True:
            status = self._get(f'/api/v1/pivot/jobs/{job_id}').json()
            if status['status'] == 'completed':
                return self._get(status['download_url']).content
            time.sleep(2)

# Usage is same for both small and large queries
client = PivotClient()
data = client.export(
    time_range={'start': '...', 'duration': 'PT1H'},
    channels=['ch1', 'ch2']
)
```

**Time Specification (Unified):**
Supports all patterns in single structure:
```json
// Absolute
{"start": "2025-01-23T14:00:00Z", "end": "2025-01-23T15:00:00Z"}

// Start + duration
{"start": "2025-01-23T14:00:00Z", "duration": "PT1H"}

// End + duration (backward)
{"end": "2025-01-23T15:00:00Z", "duration": "PT1H"}

// Relative (backward from now)
{"duration": "PT30M"}

// Named preset
{"preset": "last_hour"}
```

**Error Handling:**
- 400: Invalid time range, malformed request
- 404: Requested channels not found
- 408: Sync query timeout (suggest async retry)
- 413: Query too large (exceeds max size limit)
- 429: Rate limit exceeded
- 503: Server overloaded (queue full)

## Rationale
{"anomaly": "Need API that works for both small interactive queries (JupyterLab) and large batch exports (automation). Pure sync is simple but fails on large queries. Pure async adds complexity for small queries.", "approach": "Hybrid pattern - smart routing based on estimated query size. Client code is simple (same interface for all queries), server adapts automatically.", "alternatives_rejected": ["Force users to choose sync vs async (bad UX, error-prone)", "Only sync with long timeout (ties up connections)", "Only async (unnecessary complexity for 90% of queries)"]}