---
scope: SpeedData v0.3 stripchart. Modern browsers with SVG support. Best for scenarios prioritizing DOM inspectability and smooth animations over raw performance. Moderate data rates (~100 Hz). Acceptable for <5 charts per page.
kind: system
content_hash: b953b86d21054a7537f9b4506eeef221
---

# Hypothesis: SVG-Based Stripchart with D3.js for Data Management

Hybrid approach using SVG rendering with D3.js for data binding and axis management, custom scrolling logic.

**HTML Structure:**
```html
<div class="stripchart-container"
     data-signals="example.voltage,example.current"
     data-window="30"
     data-theme="auto">
</div>
```

**D3.js Implementation:**
```javascript
class StripchartManager {
  constructor(container) {
    this.container = container;
    this.signals = container.dataset.signals.split(',');
    this.window = parseFloat(container.dataset.window) || 30;
    this.theme = container.dataset.theme || 'auto';
    
    this.data = new Map(); // signal -> [{time, value}]
    
    // Create SVG
    this.svg = d3.select(container)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%');
    
    this.setupScales();
    this.setupAxes();
    this.setupLines();
  }
  
  setupScales() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    
    this.xScale = d3.scaleTime()
      .domain([Date.now() - this.window * 1000, Date.now()])
      .range([0, width]);
    
    this.yScale = d3.scaleLinear()
      .domain([0, 100]) // Auto-scale based on data
      .range([height, 0]);
  }
  
  setupAxes() {
    this.xAxis = d3.axisBottom(this.xScale);
    this.yAxis = d3.axisLeft(this.yScale);
    
    this.svg.append('g')
      .attr('class', 'x-axis')
      .call(this.xAxis);
    
    this.svg.append('g')
      .attr('class', 'y-axis')
      .call(this.yAxis);
  }
  
  setupLines() {
    this.line = d3.line()
      .x(d => this.xScale(d.time))
      .y(d => this.yScale(d.value))
      .curve(d3.curveLinear);
    
    this.signals.forEach(sig => {
      this.svg.append('path')
        .attr('class', `line-${sig}`)
        .attr('stroke', this.getColor(sig))
        .attr('fill', 'none');
    });
  }
  
  onWebSocketData(data) {
    const now = Date.now();
    const cutoff = now - this.window * 1000;
    
    this.signals.forEach(sig => {
      const [channel, signal] = sig.split('.');
      if (data[signal] !== undefined) {
        if (!this.data.has(sig)) this.data.set(sig, []);
        
        const buffer = this.data.get(sig);
        buffer.push({time: now, value: data[signal]});
        
        // Remove old data outside window
        while (buffer.length > 0 && buffer[0].time < cutoff) {
          buffer.shift();
        }
      }
    });
    
    this.render();
  }
  
  render() {
    // Update x-axis domain to scroll
    this.xScale.domain([Date.now() - this.window * 1000, Date.now()]);
    this.svg.select('.x-axis').call(this.xAxis);
    
    // Update y-axis domain based on data range
    const allValues = Array.from(this.data.values()).flat().map(d => d.value);
    this.yScale.domain([d3.min(allValues), d3.max(allValues)]);
    this.svg.select('.y-axis').call(this.yAxis);
    
    // Update line paths
    this.signals.forEach(sig => {
      this.svg.select(`.line-${sig}`)
        .datum(this.data.get(sig) || [])
        .attr('d', this.line);
    });
    
    requestAnimationFrame(() => this.render());
  }
}

// Initialize all charts
document.querySelectorAll('.stripchart-container').forEach(container => {
  new StripchartManager(container);
});
```

**CSS Theming:**
```css
.stripchart-container {
  width: 100%;
  height: 300px;
}

.stripchart-container[data-theme="dark"] {
  background: black;
}

.stripchart-container[data-theme="dark"] path {
  stroke: yellow;
}

.stripchart-container[data-theme="light"] {
  background: white;
}

.stripchart-container[data-theme="light"] path {
  stroke: blue;
}

.stripchart-container .x-axis,
.stripchart-container .y-axis {
  font-size: 12px;
}
```

**Features:**
- SVG vector graphics (sharp scaling, inspectable DOM)
- D3.js handles data binding, scales, axes
- Custom scrolling logic (not relying on plugin)
- Auto-scaling Y axis based on data range
- Smooth animations possible

**Performance Considerations:**
- SVG slower than Canvas for high-frequency updates
- DOM manipulation overhead
- Suitable for moderate data rates (~100 Hz with careful optimization)
- Can optimize with virtual DOM or selective updates

**Dependencies:**
- D3.js (~250 KB minified, or ~70 KB for d3-scale + d3-axis + d3-shape)

## Rationale
{"anomaly": "Need real-time scrolling charts with standard HTML, CSS theming, multi-chart support", "approach": "SVG provides vector graphics with inspectable DOM. D3.js handles complex data binding and axis management. Hybrid approach: D3 for scaffolding, custom code for scrolling.", "alternatives_rejected": ["Pure D3 with enter/update/exit (too complex for simple scrolling)", "SVG without D3 (manual axis/scale management tedious)", "Canvas (loses DOM inspectability)"]}