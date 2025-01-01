const ws = new WebSocket("ws://localhost:8080");

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);

    // Find all elements with the class `data` (or a specific channel name)
    const elements = document.querySelectorAll(".data"); //TOTO: Change to a specific channel name or make configurable

    // All elements would like data signals, but not all data needs to be
    // displayed. So, rather than iterating over all the data keys, we iterate
    // over the desired elements and update them with the corresponding data.
    elements.forEach((element) => {
        // Use the id attribute to determine the data key
        const key = element.getAttribute("id");
        if (data[key] !== undefined) {
            // Update the element with the corresponding value
            element.textContent = data[key];
        }
    });
};
