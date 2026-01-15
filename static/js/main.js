document.addEventListener('DOMContentLoaded', function() {
    // Update Clock in Header if it exists
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        // Use an element with id="header-clock" if you add one
        // For this app, we might just update "Day 5/60" logic if we had real dates.
    }

    // Example: Poll for battery status or connection (Simulation)
    setInterval(() => {
        const onlineBadge = document.querySelector('.status-online');
        if(onlineBadge) {
            // Toggle text for fun simulation or just keep it static
            // onlineBadge.textContent = 'Online'; 
        }
    }, 5000);
});

async function fetchSensorData() {
    try {
        const response = await fetch('/api/sensor-data');
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

function updateDashboard(data) {
    // This function will be called by the monitor page
    // Map data keys to element IDs
    for (const [key, value] of Object.entries(data)) {
        const element = document.getElementById(`val-${key}`);
        if (element) {
            element.innerText = typeof value === 'number' ? value.toFixed(1) : value;
            updateCardColor(key, value);
        }
    }
}

function updateCardColor(sensorType, value) {
    const card = document.getElementById(`card-${sensorType}`);
    const indicator = document.getElementById(`ind-${sensorType}`);
    if (!card || !indicator) return;

    // Simple logic example - this should be driven by the Plant Profile limits ideally
    // For now we hardcode some basic range checks or just leave it green
    // Real logic would compare value vs plant.min and plant.max
    
    // Reset classes
    indicator.classList.remove('indicator-green', 'indicator-yellow', 'indicator-red');
    
    // Example Thresholds (These should come from the backend/template data attributes)
    let status = 'green';
    
    // Simple demo logic
    if (sensorType === 'temperature') {
        if (value < 15 || value > 35) status = 'red';
        else if (value < 20 || value > 30) status = 'yellow';
    }
    
    indicator.classList.add(`indicator-${status}`);
}
