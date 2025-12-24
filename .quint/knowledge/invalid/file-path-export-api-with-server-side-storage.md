---
scope: SpeedData v0.3 Pivot API. Co-located deployments (JupyterLab on same host as pivot) or shared filesystem environments (NFS/SMB). Large exports (GB-scale) where HTTP download is bottleneck.
kind: system
content_hash: f9acd6d20fd3af82228b5f57c70ef4bf
---

# Hypothesis: File-Path Export API with Server-Side Storage

Alternative approach: API writes HDF5 to specified server-side path instead of HTTP download. Optimized for large files and shared filesystem deployments.

**Endpoint:**
```
POST /api/v1/pivot/export
Content-Type: application/json

{
  "time_range": {"start": "...", "end": "..."},
  "channels": ["ch1", "ch2"],
  "output": {
    "path": "/data/exports/my_analysis.h5",  // server filesystem path
    "overwrite": false,
    "permissions": "0644"
  }
}

Response: 201 Created
{
  "export_id": "xyz789",
  "output_path": "/data/exports/my_analysis.h5",
  "file_size": 45678901,
  "completed_at": "2025-01-23T14:37:45Z"
}
```

**Alternative: Auto-Generated Path:**
```json
{
  "time_range": {...},
  "channels": [...],
  "output": {
    "directory": "/data/exports",
    "filename_pattern": "export_{timestamp}_{channels}.h5"
  }
}

Response:
{
  "output_path": "/data/exports/export_20250123_143045_ch1-ch2-ch3.h5"
}
```

**List Exports:**
```
GET /api/v1/pivot/exports?directory=/data/exports&limit=10

Response:
{
  "exports": [
    {
      "path": "/data/exports/export_20250123_143045.h5",
      "size": 12345678,
      "created_at": "2025-01-23T14:30:45Z",
      "channels": ["ch1", "ch2"],
      "time_range": {"start": "...", "end": "..."}
    }
  ]
}
```

**Delete Export:**
```
DELETE /api/v1/pivot/exports?path=/data/exports/export_20250123_143045.h5
```

**Use Cases:**

**1. JupyterLab on Same Host:**
```python
# Pivot API creates file, Jupyter reads directly
import requests
from lib.python.dataset import read_hdf5

resp = requests.post('http://localhost:8000/api/v1/pivot/export', json={
    'time_range': {'duration': 'PT1H'},
    'channels': ['ch1', 'ch2'],
    'output': {'path': '/data/exports/analysis.h5'}
})

# File already on disk - no download needed
data = read_hdf5(resp.json()['output_path'])
```

**2. Network Filesystem (NFS/SMB):**
```python
# Pivot writes to network mount, client reads from same mount
resp = requests.post('http://pivot-server:8000/api/v1/pivot/export', json={
    'time_range': {...},
    'channels': [...],
    'output': {'path': '/mnt/shared/exports/run_42.h5'}
})

# Client mounts /mnt/shared, reads directly
data = read_hdf5('/mnt/shared/exports/run_42.h5')
```

**3. Batch Export Script:**
```python
# Export multiple time ranges in parallel
import concurrent.futures

def export_range(start, end):
    resp = requests.post('http://localhost:8000/api/v1/pivot/export', json={
        'time_range': {'start': start, 'end': end},
        'channels': ['ch1', 'ch2', 'ch3'],
        'output': {
            'directory': '/data/exports/batch',
            'filename_pattern': f'export_{start}_{end}.h5'
        }
    })
    return resp.json()['output_path']

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(export_range, s, e) for s, e in time_ranges]
    paths = [f.result() for f in futures]

# All files written to /data/exports/batch/
```

**Security Considerations:**
- Path validation: reject `..`, absolute paths outside allowed directories
- Allowed directories: configurable whitelist (e.g., `/data/exports`, `/tmp/pivot`)
- Permissions: configurable default (0644) or per-request
- Disk quota: per-user or per-directory limits

**Advantages:**
- No network transfer for large files (GB-scale exports)
- Parallel exports don't compete for HTTP bandwidth
- File persists on server (no ephemeral job cleanup)
- Natural integration with batch processing pipelines

**Disadvantages:**
- Requires shared filesystem or client access to server filesystem
- Path conflicts if multiple clients use same names
- Disk space management is manual (no auto-cleanup)
- Cannot use from remote clients without filesystem access

## Rationale
{"anomaly": "Large HDF5 files (GB-scale) are inefficient to transfer via HTTP. If client and server share filesystem, downloading via HTTP wastes time and bandwidth.", "approach": "Write HDF5 directly to server filesystem path, return path to client. Client reads via filesystem instead of HTTP. Optimizes for co-located deployments.", "alternatives_rejected": ["HTTP download for all queries (inefficient for large files on same host)", "Hybrid with optional path (API complexity)", "Separate file-based and HTTP-based endpoints (fragmentation)"]}