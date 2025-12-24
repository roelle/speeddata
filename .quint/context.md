# Bounded Context

## Vocabulary

- **Dark**: black background + yellow lines.
- **Light**: white background + blue lines.

**WebSocket Data Stream**: Server.js broadcasts AVRO-decoded JSON packets to browser clients. Frontend consumes these for live updates.

**Multi-Chart Page**: HTML page can contain multiple independent stripchart components, positioned via CSS.

**Data Buffer**: Client-side storage of recent signal samples within time window (sliding window/circular buffer).

**Current State (v0.2)**: Simple text display of latest WebSocket data (`<span id="field">` updated with latest value). No charting yet.

**AVRO Schema**: Defines channel structure (fields = signals).
- **Example**: `{time: long, voltage: double, current: double}`.

**Multicast Stream**: UDP multicast carrying AVRO-encoded samples. Server.js subscribes and decodes.

## Invariants

1. **HTML/CSS Convention Adherence**: Chart component must use standard HTML attributes and CSS classes, not custom non-standard syntax like `<span signals=[...]>`.
2. **WebSocket as Data Source**: Charts consume data from existing WebSocket connection (ws://localhost:8080). No direct UDP access from browser.
3. **Signal Naming**: Use dot notation `channel.signal` to identify data (e.g., `example.voltage`). Channel corresponds to AVRO schema, signal to field.
4. **Time Window FIFO**: Fixed-duration window (configurable per chart). Oldest data drops when window full. No infinite accumulation.
5. **Newest Data on Right**: Time axis orientation: right edge = now (t=0), left edge = t-window_duration. Data scrolls left over time.
6. **CSS Theming**: Dark mode (black bg, yellow lines) and light mode (white bg, blue lines) via CSS, respecting user/system preference or explicit class.
7. **Multi-Chart Support**: Multiple independent charts on single HTML page. Each chart can plot different signals with different window durations.
8. **CSS Positioning**: Charts positioned via standard CSS (flexbox, grid, absolute, etc.). No custom layout engine.
9. **No Server Changes**: Existing server.js broadcasts all fields in JSON. Frontend filters which signals to plot. Server doesn't need per-chart customization.
10. **Existing Architecture (v0.2)**:
    - Node.js server.js: UDP multicast → WebSocket JSON broadcast
    - Browser frontend.js: WebSocket client updating `<span>` elements by id
    - AVRO schema defines channel structure
11. **Rendering Technology**: Decision needed - Canvas, SVG, or WebGL for chart rendering. Must support real-time updates (60fps desirable).
12. **Performance**: Must handle typical workload (5000 Hz → decimated to ~100 Hz, multiple signals, multiple charts on page).
13. **Browser Compatibility**: Modern browsers (Chrome, Firefox, Safari). No IE11 support required.
