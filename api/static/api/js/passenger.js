// Passenger logic for handling bus selection and tracking redirection

document.addEventListener('DOMContentLoaded', () => {
    const trackBtn = document.getElementById('track-btn');
    const busIdInput = document.getElementById('bus-id-input');

    if (trackBtn) {
        trackBtn.addEventListener('click', () => {
            const busId = busIdInput.value.trim();

            if (!busId) {
                alert('Please enter a valid Bus ID (e.g., 1)');
                return;
            }

            // 1. Save the selected bus ID to localStorage so the tracking page can use it
            localStorage.setItem('selectedBusId', busId);

            // 2. To make it look professional, we'll also store a dummy bus object
            // so the tracking page header doesn't show "Loading..."
            const dummyBus = {
                number: 'Bus ID: ' + busId,
                route: 'Calculating route...'
            };
            localStorage.setItem('selectedBus', JSON.stringify(dummyBus));

            // 3. Redirect to the Live Tracking module
            // We use the path that matches the Render/Django setup
            window.location.href = '/live bus tracking module.html';
        });
    }
});
