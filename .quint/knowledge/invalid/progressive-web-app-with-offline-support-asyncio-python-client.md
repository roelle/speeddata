---
scope: Modern browsers with Service Worker support, Python 3.8+ with async. Offline-first architecture.
kind: system
content_hash: d394d6bbd3906081214f903f219feb3f
---

# Hypothesis: Progressive Web App with Offline Support + AsyncIO Python Client

Modern PWA with full offline capabilities.

**Frontend (PWA):**
- Service Worker for offline caching
- IndexedDB for local channel registry cache
- Offline mode: queue registrations, sync when online
- Install as desktop app (manifest.json)
- Vanilla JS + lightweight state management (Zustand or similar, 1KB)
- Push notifications for channel status changes

**Python Client (AsyncIO):**
- async/await API: async def register_channel()
- httpx for async HTTP
- Batch operations with asyncio.gather()
- Progress bars (tqdm integration)
- Webhook support: notify on registration events
- ~500 lines

**Architecture:**
```
Browser → Service Worker → IndexedDB (offline cache)
Browser → Fetch → REST API (when online)
Browser → WebSocket → Live data

JupyterLab → async speeddata client → httpx
JupyterLab → await register_many() → parallel uploads
```

**Schema Handling:**
- IndexedDB schema cache (avoid re-downloads)
- Offline schema validation
- Sync queue for pending uploads
- Delta updates: only upload schema changes

## Rationale
{"anomaly": "Need UI + library for registration API", "approach": "PWA for offline support, async Python for performance", "alternatives_rejected": ["Electron (too heavy)", "Cordova (mobile not needed)"]}