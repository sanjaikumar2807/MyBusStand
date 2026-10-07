let map = L.map('map').setView([13.0827, 80.2707], 13); // Default Chennai

L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, HERE, DeLorme, USGS, Intermap',
    maxZoom: 19
}).addTo(map);

let busMarker = null;
let userMarker = null;
let trackingInterval = null;

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
        const uLat = pos.coords.latitude;
        const uLng = pos.coords.longitude;
        userMarker = L.marker([uLat, uLng]).addTo(map)
            .bindPopup("<b>Your Location</b>").openPopup();
        map.setView([uLat, uLng], 14);
    }, (err) => console.log(err), { enableHighAccuracy: true });
}

const trackBtn = document.getElementById('track-btn');
const busIdInput = document.getElementById('bus-id-input');

trackBtn.addEventListener('click', () => {
    const busId = busIdInput.value;
    if (!busId) {
        alert("Please enter a Bus ID");
        return;
    }

    if (trackingInterval) clearInterval(trackingInterval);

    // Initial Fetch
    updateBusLocation(busId);

    // Poll every 5 seconds
    trackingInterval = setInterval(() => {
        updateBusLocation(busId);
    }, 5000);
});

async function updateBusLocation(busId) {
    try {
        const response = await fetch(`/api/buses/${busId}/location/`);
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            clearInterval(trackingInterval);
            return;
        }

        const lat = data.lat;
        const lng = data.lng;

        if (!busMarker) {
            busMarker = L.marker([lat, lng]).addTo(map)
                .bindPopup(`Bus ${data.bus_id} - Live Location`).openPopup();
            map.setView([lat, lng], 15);
        } else {
            busMarker.setLatLng([lat, lng]);
            map.panTo([lat, lng]);
        }
    } catch (err) {
        console.error("Tracking error:", err);
    }
}
