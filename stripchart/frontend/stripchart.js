/**
 * Lightweight Canvas Stripchart - Vanilla JavaScript
 * Zero dependencies, ~5KB implementation
 * Real-time scrolling time-series visualization
 */

class Stripchart {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Parse configuration from data attributes
        this.signals = (canvas.dataset.signals || '').split(',').map(s => s.trim()).filter(s => s);
        this.window = parseFloat(canvas.dataset.window) || 30; // seconds
        this.height = parseInt(canvas.dataset.height) || 300;
        this.theme = canvas.dataset.theme || 'auto';
        this.yMin = canvas.dataset.ymin ? parseFloat(canvas.dataset.ymin) : null;
        this.yMax = canvas.dataset.ymax ? parseFloat(canvas.dataset.ymax) : null;

        // Set canvas size
        this.canvas.width = canvas.clientWidth;
        this.canvas.height = this.height;

        // Data buffers: Map<signalName, Array<{time, value}>>
        this.buffers = new Map();
        this.signals.forEach(sig => this.buffers.set(sig, []));

        // Colors (must be set BEFORE assignSignalColors)
        this.colors = this.getThemeColors();

        // Parse custom colors or use defaults (after this.colors is set)
        const customColors = canvas.dataset.colors ?
            canvas.dataset.colors.split(',').map(c => c.trim()) : null;
        this.signalColors = this.assignSignalColors(customColors);

        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());

        // Start animation loop
        this.animate();
    }

    getThemeColors() {
        let theme = this.theme;

        if (theme === 'auto') {
            // Detect system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            theme = prefersDark ? 'dark' : 'light';
        }

        if (theme === 'dark') {
            return {
                background: '#000000',
                grid: '#333333',
                text: '#CCCCCC',
                palette: ['#FFFF00', '#00FFFF', '#FF00FF', '#00FF00', '#FFA500', '#FF6B6B']
                // Yellow, Cyan, Magenta, Green, Orange, Light Red
            };
        } else {
            return {
                background: '#FFFFFF',
                grid: '#DDDDDD',
                text: '#333333',
                palette: ['#0000FF', '#FF0000', '#00AA00', '#FF8000', '#8000FF', '#008080']
                // Blue, Red, Green, Orange, Purple, Teal
            };
        }
    }

    assignSignalColors(customColors) {
        // Map signal names to colors
        const colorMap = new Map();
        const palette = customColors || this.colors.palette;

        this.signals.forEach((sig, idx) => {
            colorMap.set(sig, palette[idx % palette.length]);
        });

        return colorMap;
    }

    handleResize() {
        this.canvas.width = this.canvas.clientWidth;
        this.canvas.height = this.height;
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

        // Y axis scaling: use explicit range if provided, otherwise auto-scale
        let yMin, yMax;

        if (this.yMin !== null && this.yMax !== null) {
            // Use explicit Y-axis range
            yMin = this.yMin;
            yMax = this.yMax;
        } else {
            // Auto-scale based on data
            const allValues = Array.from(this.buffers.values())
                .flat()
                .map(d => d.value)
                .filter(v => v !== undefined);

            if (allValues.length === 0) {
                this.drawNoData();
                return;
            }

            yMin = Math.min(...allValues);
            yMax = Math.max(...allValues);
        }

        const yRange = yMax - yMin || 1;

        // Draw each signal with its assigned color
        this.signals.forEach((sig, idx) => {
            const buffer = this.buffers.get(sig);
            if (!buffer || buffer.length === 0) return;

            ctx.strokeStyle = this.signalColors.get(sig);
            ctx.lineWidth = 2;
            ctx.beginPath();

            buffer.forEach((point, i) => {
                // X: right edge = now (time 0), left edge = -window
                const x = width - ((now - point.time) / (this.window * 1000)) * width;

                // Y: bottom = yMin, top = yMax
                const y = height - ((point.value - yMin) / yRange) * height * 0.9 + height * 0.05;

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
        ctx.font = '12px monospace';

        // Y-axis labels
        ctx.fillText(yMax.toFixed(2), 5, 15);
        ctx.fillText(yMin.toFixed(2), 5, height - 5);

        // X-axis labels (time)
        ctx.fillText('now', width - 40, height - 5);
        ctx.fillText(`-${this.window}s`, 5, height - 20);

        // Signal legend with colors
        if (this.signals.length > 0) {
            let legendX = 5;
            const legendY = 30;
            ctx.font = '12px monospace';

            this.signals.forEach((sig, idx) => {
                // Draw colored line segment
                ctx.strokeStyle = this.signalColors.get(sig);
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(legendX, legendY - 5);
                ctx.lineTo(legendX + 15, legendY - 5);
                ctx.stroke();

                // Draw signal name
                ctx.fillStyle = this.colors.text;
                ctx.fillText(sig, legendX + 20, legendY);

                // Move to next position
                legendX += ctx.measureText(sig).width + 40;
            });
        }
    }

    drawNoData() {
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;

        ctx.fillStyle = this.colors.text;
        ctx.font = '16px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Waiting for data...', width / 2, height / 2);
        ctx.textAlign = 'left';
    }
}

// Global chart registry
const stripcharts = [];

// Initialize all stripcharts on page load
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('canvas.stripchart').forEach(canvas => {
        const chart = new Stripchart(canvas);
        stripcharts.push(chart);
        console.log(`Initialized stripchart for signals: ${chart.signals.join(', ')}`);
    });
});

// Export for WebSocket integration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Stripchart, stripcharts };
}
