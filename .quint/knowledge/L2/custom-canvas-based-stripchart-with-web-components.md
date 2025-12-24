---
scope: SpeedData v0.3 stripchart. Modern browsers with Web Components support (Chrome 54+, Firefox 63+, Safari 10.1+). Single-channel or explicitly channel-prefixed signals. Performance suitable for ~100 Hz decimated data, up to ~10 signals per chart.
kind: system
content_hash: 6b64e7dcbc3bf6e3e9bb26437ccae52c
---

# Hypothesis: Custom Canvas-Based Stripchart with Web Components

Custom implementation using Web Components (custom elements) and Canvas 2D API for rendering.

**HTML Structure:**
```html
<stripchart-plot 
  data-signals="example.voltage,example.current"
  data-window="30"
  data-theme="auto">
</stripchart-plot>
```

**Web Component Definition:**
```javascript
class StripchartPlot extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode: 'open'});
    this.buffer = new CircularBuffer(this.windowDuration * this.sampleRate);
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
  }
  
  connectedCallback() {
    const signals = this.dataset.signals.split(',');
    const window = parseFloat(this.dataset.window) || 30; // seconds
    const theme = this.dataset.theme || 'auto';
    
    this.render();
    this.subscribeToWebSocket(signals);
    requestAnimationFrame(() => this.animate());
  }
  
  onWebSocketData(data) {
    signals.forEach(sig => {
      const [channel, signal] = sig.split('.');
      if (data[signal] !== undefined) {
        this.buffer.push({time: Date.now(), value: data[signal]});
      }
    });
  }
  
  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.drawAxes();
    this.drawSignals();
    requestAnimationFrame(() => this.animate());
  }
}

customElements.define('stripchart-plot', StripchartPlot);
```

**Data Buffer:**
- Circular buffer per signal (fixed size based on window duration × sample rate)
- Ring buffer with head/tail pointers
- O(1) push, automatic oldest-data eviction

**Canvas Rendering:**
- 2D context with path drawing
- Double-buffering via requestAnimationFrame
- Time axis: right edge = now, left edge = t - window
- Auto-scaling Y axis based on signal range

**CSS Theming:**
```css
stripchart-plot {
  display: block;
  width: 100%;
  height: 300px;
}

stripchart-plot[data-theme="dark"] canvas {
  background: black;
  --line-color: yellow;
}

stripchart-plot[data-theme="light"] canvas {
  background: white;
  --line-color: blue;
}

@media (prefers-color-scheme: dark) {
  stripchart-plot[data-theme="auto"] canvas {
    background: black;
    --line-color: yellow;
  }
}
```

**WebSocket Integration:**
- Global WebSocket connection shared across all charts
- Each chart filters messages for its configured signals
- Signal mapping: `data[signal]` from JSON (assumes single channel currently)

**Performance:**
- Canvas 2D handles 60fps with moderate data rates
- Circular buffer prevents memory growth
- Optimized redraw: only clear/redraw changed regions (optional)

## Rationale
{"anomaly": "Need real-time scrolling charts, standard HTML conventions, CSS theming, multi-chart support", "approach": "Web Components provide encapsulation and standard HTML syntax. Canvas 2D offers performance and direct rendering control. Custom implementation avoids heavy library dependencies.", "alternatives_rejected": ["Non-standard HTML syntax (violates constraint)", "SVG (performance concerns for high-frequency updates)", "No component encapsulation (global namespace pollution)"]}