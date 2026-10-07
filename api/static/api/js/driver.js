let watchId = null;

const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const statusText = document.getElementById('status-text');
const coordsText = document.getElementById('coords-text');
const busIdInput = document.getElementById('bus-id');

startBtn.addEventListener('click', () => {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser");
        return;
    }

    const busId = busIdInput.value;
    if (!busId) {
        alert("Please enter a Bus ID");
        return;
    }

    statusText.innerText = "Sharing Location...";
    startBtn.style.display = 'none';
    stopBtn.style.display = 'block';

    watchId = navigator.geolocation.watchPosition(
        (position) => {
            const { latitude, longitude } = position.coords;
            coordsText.innerText = `Latitude: ${latitude.toFixed(6)} | Longitude: ${longitude.toFixed(6)}`;

            // Send to Django Backend
            fetch('/api/buses/' + busId + '/location/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    bus_id: busId,
                    lat: latitude,
                    lng: longitude
                })
            })
            .then(response => response.json())
            .then(data => console.log("Location updated:", data))
            .catch(err => console.error("Error updating location:", err));
        },
        (error) => {
            console.error("Geolocation Error:", error);
            statusText.innerText = "GPS Error: " + error.message;
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
});

stopBtn.addEventListener('click', () => {
    if (watchId) {
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
    }
    statusText.innerText = "Location sharing stopped.";
    startBtn.style.display = 'block';
    stopBtn.style.display = 'none';
});
