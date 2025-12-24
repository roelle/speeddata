---
scope: Frontend client (stripchart/frontend/). All channels displayed in browser charts. Requires modern browsers with Web Worker and SharedArrayBuffer support.
kind: system
content_hash: b6ebe8e369d5db24f314b7444204b755
---

# Hypothesis: Frontend Client-Side Decimation with Web Workers

Implement decimation in browser frontend using Web Workers to avoid blocking rendering thread. Stripchart server sends full-rate data over WebSocket. Frontend JavaScript spawns worker thread per channel to apply decimation before chart rendering.

Architecture:
- Main thread: WebSocket receiver, chart rendering
- Worker threads: decimation algorithms (downsample, average, min-max, RMS)
- SharedArrayBuffer: zero-copy communication between main/worker threads

Config in frontend HTML/JavaScript:
```javascript
const channelConfig = {
  high_rate: { algorithm: 'min-max', factor: 50 },
  medium_rate: { algorithm: 'average', factor: 10 }
};
```

Workers receive raw samples via postMessage, apply algorithm, return decimated samples. Chart libraries (Chart.js/Plotly) render decimated stream. Relay and server unchanged.

## Rationale
{"anomaly": "No decimation exists, chart rendering cannot keep up with 5000 Hz data", "approach": "Push decimation to edge (client), leverage browser parallelism, avoid server-side processing cost", "alternatives_rejected": ["Server decimation (wastes server CPU for per-client display preferences)", "Main thread decimation (blocks rendering, causes UI lag)"]}