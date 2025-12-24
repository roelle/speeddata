---
kind: system
scope: SpeedData v0.3 stripchart. Modern browsers. Suitable for moderate data rates (~100 Hz decimated). Trade-off: library bundle size (~300 KB total) for feature completeness and maturity.
content_hash: dc7d97db458f8ed90bafb004d34d1a29
---

# Hypothesis: Chart.js with Data Attribute Configuration

Use Chart.js library with custom wrapper for data attribute-based configuration.

**HTML Structure:**
```html
<div class="stripchart" 
     data-signals="example.voltage,example.current"
     data-window="30"
     data-theme="auto">
</div>
```

**JavaScript Initialization:**
```javascript
// Initialize all stripcharts on page load
document.querySelectorAll('.stripchart').forEach(container => {
  const signals = container.dataset.signals.split(',');
  const window = parseFloat(container.dataset.window) || 30;
  const theme = container.dataset.theme || 'auto';
  
  const canvas = document.createElement('canvas');
  container.appendChild(canvas);
  
  const chart = new Chart(canvas, {
    type: 'line',
    data: {
      datasets: signals.map(sig => ({
        label: sig,
        data: [],
        borderColor: getColorForSignal(sig, theme),
        borderWidth: 2,
        fill: false,
        pointRadius: 0 // No point markers for performance
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false, // Disable for real-time performance
      scales: {
        x: {
          type: 'realtime',
          realtime: {
            duration: window * 1000, // milliseconds
            refresh: 100, // refresh rate in ms
            delay: 0,
            onRefresh: chart => updateChartData(chart)
          }
        },
        y: {
          beginAtZero: false
        }
      }
    }
  });
  
  container.chartInstance = chart;
});
```

**WebSocket Integration:**
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  document.querySelectorAll('.stripchart').forEach(container => {
    const chart = container.chartInstance;
    const signals = container.dataset.signals.split(',');
    
    signals.forEach((sig, idx) => {
      const [channel, signal] = sig.split('.');
      if (data[signal] !== undefined) {
        chart.data.datasets[idx].data.push({
          x: Date.now(),
          y: data[signal]
        });
      }
    });
  });
};
```

**Chart.js Realtime Plugin:**
- Use chartjs-plugin-streaming for scrolling time axis
- Automatic window management (drops old data)
- Built-in zoom/pan support
- Responsive canvas sizing

**CSS Theming:**
```css
.stripchart {
  width: 100%;
  height: 300px;
  position: relative;
}

.stripchart[data-theme="dark"] {
  background: black;
  --grid-color: #333;
  --text-color: #ccc;
}

.stripchart[data-theme="light"] {
  background: white;
  --grid-color: #ddd;
  --text-color: #333;
}
```

**Features:**
- Mature library (Chart.js 4.x)
- Plugin ecosystem (streaming, zoom, annotation)
- Built-in legends, tooltips, axis labels
- Canvas-based rendering (good performance)
- Responsive by default

**Dependencies:**
- Chart.js (~200 KB minified)
- chartjs-plugin-streaming (~30 KB)
- moment.js or luxon for time handling (~60 KB)

## Rationale
{"anomaly": "Need real-time scrolling charts with standard HTML, CSS theming, multi-chart support", "approach": "Leverage mature Chart.js library with streaming plugin. Wrapper code maps data attributes to Chart.js config. Avoids custom rendering code.", "alternatives_rejected": ["Highcharts (proprietary license for commercial use)", "D3.js (lower-level, more code required)", "Plotly.js (larger bundle, overkill for simple stripcharts)"]}