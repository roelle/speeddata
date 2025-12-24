const ws = new WebSocket("ws://localhost:8080");

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);

    // Update text displays
    const elements = document.querySelectorAll(".data");
    elements.forEach((element) => {
        const key = element.getAttribute("id");
        if (data[key] !== undefined) {
            element.textContent = data[key];
        }
    });

    // Update stripcharts
    if (typeof stripcharts !== 'undefined') {
        stripcharts.forEach(chart => {
            chart.signals.forEach(sig => {
                // Parse signal name: channel.signal or just signal
                const parts = sig.split('.');
                const signalName = parts.length > 1 ? parts[1] : sig;

                if (data[signalName] !== undefined) {
                    chart.addDataPoint(sig, data[signalName]);
                }
            });
        });
    }
};
