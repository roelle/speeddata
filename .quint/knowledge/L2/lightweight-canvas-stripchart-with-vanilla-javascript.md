---
scope: SpeedData v0.3 stripchart. All modern browsers with Canvas support. Optimized for minimal dependencies and maximum performance. Best for simple stripcharts without advanced features (zoom, pan, annotations). Handles high data rates (100-1000 Hz).
kind: system
content_hash: f817045cdfca42aa8def30d59667daf5
---

# Hypothesis: Lightweight Canvas Stripchart with Vanilla JavaScript

Minimal dependency approach using raw Canvas API and vanilla JavaScript with data attributes.

**HTML Structure:**
```html
<canvas class="stripchart"
        data-signals="example.voltage,example.current"
        data-window="30"
        data-height="300"
        data-theme="auto">
</canvas>
```

**Vanilla JavaScript Implementation:**
```javascript
class Stripchart {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.signals = canvas.dataset.signals.split(',');
    this.window = parseFloat(canvas.dataset.window) || 30; // seconds
    this.height = parseInt(canvas.dataset.height) || 300;
    this.theme = canvas.dataset.theme || 'auto';
    
    // Set canvas size
    this.canvas.width = canvas.clientWidth;
    this.canvas.height = this.height;
    
    // Data buffers: Map<signalName, Array<{time, value}>>
    this.buffers = new Map();
    this.signals.forEach(sig => this.buffers.set(sig, []));
    
    // Colors
    this.colors = this.getThemeColors();
    
    // Start animation loop
    this.animate();
  }
  
  getThemeColors() {
    const theme = this.theme === 'auto' 
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : this.theme;
    
    if (theme === 'dark') {
      return {
        background: '#000000',
        line: '#FFFF00',
        grid: '#333333',
        text: '#CCCCCC'
      };
    } else {
      return {
        background: '#FFFFFF',
        line: '#0000FF',
        grid: '#DDDDDD',
        text: '#333333'
      };
    }
  }
  
  addDataPoint(signal, value) {
    const buffer = this.buffers.get(signal);
    if (!buffer) return;
    
    const now = Date.now();
    const cutoff = now - (this.window * 1000);
    
    buffer.push({time: now, value: value});
    
    // Remove old data (FIFO)
    while (buffer.length > 0 && buffer[0].time < cutoff) {
      buffer.shift();
    }
  }
  
  animate() {
    this.draw();
    requestAnimationFrame(() => this.animate());
  }
  
  draw() {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    // Clear canvas
    ctx.fillStyle = this.colors.background;
    ctx.fillRect(0, 0, width, height);
    
    // Draw grid
    this.drawGrid();
    
    // Calculate scales
    const now = Date.now();
    const timeStart = now - (this.window * 1000);
    
    // Auto-scale Y axis based on all data
    const allValues = Array.from(this.buffers.values())
      .flat()
      .map(d => d.value)
      .filter(v => v !== undefined);
    
    const yMin = Math.min(...allValues, 0);
    const yMax = Math.max(...allValues, 100);
    const yRange = yMax - yMin || 1;
    
    // Draw each signal
    this.signals.forEach((sig, idx) => {
      const buffer = this.buffers.get(sig);
      if (!buffer || buffer.length === 0) return;
      
      ctx.strokeStyle = this.colors.line;
      ctx.lineWidth = 2;
      ctx.beginPath();
      
      buffer.forEach((point, i) => {
        // X: right edge = now (time 0), left edge = -window
        const x = width - ((now - point.time) / (this.window * 1000)) * width;
        
        // Y: bottom = yMin, top = yMax
        const y = height - ((point.value - yMin) / yRange) * height;
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      
      ctx.stroke();
    });
    
    // Draw axes
    this.drawAxes(yMin, yMax);
  }
  
  drawGrid() {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    ctx.strokeStyle = this.colors.grid;
    ctx.lineWidth = 1;
    
    // Vertical grid lines (time divisions)
    for (let i = 0; i <= 10; i++) {
      const x = (i / 10) * width;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    
    // Horizontal grid lines (value divisions)
    for (let i = 0; i <= 5; i++) {
      const y = (i / 5) * height;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
  }
  
  drawAxes(yMin, yMax) {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    ctx.fillStyle = this.colors.text;
    ctx.font = '12px sans-serif';
    
    // Y-axis labels
    ctx.fillText(yMax.toFixed(2), 5, 15);
    ctx.fillText(yMin.toFixed(2), 5, height - 5);
    
    // X-axis labels (time)
    ctx.fillText('now', width - 40, height - 5);
    ctx.fillText(`-${this.window}s`, 5, height - 5);
  }
}

// Global WebSocket handler
const charts = [];

// Initialize all stripcharts on page load
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('canvas.stripchart').forEach(canvas => {
    charts.push(new Stripchart(canvas));
  });
});

// WebSocket integration
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  charts.forEach(chart => {
    chart.signals.forEach(sig => {
      const [channel, signal] = sig.split('.');
      if (data[signal] !== undefined) {
        chart.addDataPoint(sig, data[signal]);
      }
    });
  });
};
```

**CSS Styling:**
```css
canvas.stripchart {
  display: block;
  width: 100%;
  border: 1px solid #ccc;
  margin: 10px 0;
}
```

**Features:**
- Zero dependencies (vanilla JS + Canvas API)
- Minimal bundle size (~5 KB for stripchart code)
- Direct Canvas control (maximum performance)
- Auto-scaling Y axis
- Simple grid rendering
- Theme support via data attribute

**Performance:**
- Canvas 2D optimal for real-time updates
- requestAnimationFrame for smooth 60fps
- Efficient FIFO buffer management
- Handles 100+ Hz data with multiple signals

**Limitations:**
- No built-in zoom/pan (can add if needed)
- No legends (can add as separate div)
- Manual axis/grid rendering
- Limited styling (Canvas vs CSS)

## Rationale
{"anomaly": "Need real-time scrolling charts with standard HTML, CSS theming, multi-chart support, minimal dependencies", "approach": "Vanilla JavaScript with Canvas API. No library dependencies. Direct rendering control for performance. Simple but complete implementation.", "alternatives_rejected": ["jQuery + plugins (outdated pattern)", "React/Vue components (overkill for static HTML page)", "WebGL (complexity not justified for 2D charts)"]}