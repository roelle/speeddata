---
kind: system
scope: SpeedData v0.3 Pivot API. Small to medium queries (≤20 channels, ≤5 minutes). JupyterLab interactive analysis, ad-hoc scripting. Assumes single-user or trusted network deployment.
content_hash: eb88bfc2eaef2a7b63c2401c98df6f99
---

# Hypothesis: Simple Synchronous REST API with Query Parameters

Minimalist REST API design optimized for JupyterLab interactive use. Single synchronous endpoint that returns HDF5 file directly.

**Endpoint:**
```
GET /api/v1/pivot/export?start=<ISO8601>&end=<ISO8601>&channels=<list>&signals=<list>
```

**Time Specification (Query Params):**
- `start`: ISO 8601 timestamp (required)
- `end`: ISO 8601 timestamp (optional, defaults to "now")
- Alternative: `duration`: ISO 8601 duration (e.g., "PT30S" for 30 seconds)
- Supports: start+end, start+duration, end+duration (backward)
- Relative: `duration` only → backward from "now"

**Selection (Query Params):**
- `channels`: Comma-separated list (e.g., "ch1,ch2,ch3")
- `signals`: Comma-separated, optional (defaults to all signals in selected channels)
- No glob patterns (explicit lists only)
- No exclusion filters

**Response:**
- Success: HTTP 200, Content-Type: application/x-hdf5, HDF5 file in body
- Error: HTTP 4xx/5xx with JSON error response
- Timeout: 60 seconds max, return 408 if pivot takes longer

**Authentication:**
- None (v0.3 - trusted network assumption)
- Future: API key via header (v0.4+)

**File Naming:**
- Server-side: `export_<timestamp>.h5`
- Client receives as attachment with Content-Disposition header

**Constraints:**
- Max 20 channels per request
- Max 5 minute time range
- No job queueing - immediate execution or timeout

**Example:**
```bash
curl "http://localhost:8000/api/v1/pivot/export?start=2025-01-23T14:30:00Z&duration=PT1M&channels=ch1,ch2" \
  -o output.h5
```

**Python Client (JupyterLab):**
```python
import requests
from lib.python.dataset import read_hdf5

response = requests.get('http://localhost:8000/api/v1/pivot/export', params={
    'start': '2025-01-23T14:30:00Z',
    'duration': 'PT1M',
    'channels': 'ch1,ch2'
})
with open('export.h5', 'wb') as f:
    f.write(response.content)

data = read_hdf5('export.h5')
```

## Rationale
{"anomaly": "Need REST API for pivot data export", "approach": "Minimize complexity - single synchronous endpoint, query params, direct file response. Optimized for interactive use.", "alternatives_rejected": ["POST with JSON body (unnecessary complexity for simple queries)", "Async job pattern (over-engineered for small queries)", "Streaming response (HDF5 requires random access during write)"]}