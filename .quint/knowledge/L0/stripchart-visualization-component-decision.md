---
scope: SpeedData v0.3 stripchart frontend. Applies to real-time visualization of WebSocket-streamed signal data. Modern browsers (Chrome, Firefox, Safari). Multi-chart pages with independent time windows.
kind: episteme
content_hash: 84177347abe99d544d9d9a338acf3c43
---

# Hypothesis: Stripchart Visualization Component Decision

Parent decision node grouping competing approaches for implementing scrolling time-series stripchart visualization in SpeedData frontend.

Must determine:
- HTML component pattern (custom elements, data attributes, div containers)
- Rendering technology (Canvas, SVG, or charting library)
- Signal selector syntax (how to specify channel.signal in HTML)
- Data buffer management (circular buffer, sliding window)
- Chart update mechanism (animation loop, requestAnimationFrame)
- Theming approach (CSS variables, class-based, prefers-color-scheme)

## Rationale
{"anomaly": "Current frontend only displays latest values as text. Need scrolling time-series charts (stripcharts) showing historical data within configurable time windows.", "approach": "Systematically evaluate component patterns, rendering technologies, and data management strategies for real-time charting", "alternatives_rejected": ["Server-side rendering (not real-time)", "Proprietary dashboard tools (vendor lock-in)", "Desktop app (need web-based)"]}