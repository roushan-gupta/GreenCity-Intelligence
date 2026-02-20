let map;

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        pos => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;

            initMap(lat, lng);
            loadMyAQI(lat, lng);
            loadAllAQI();
        },
        () => alert("Location permission required")
    );
}

function initMap(lat, lng) {
    map = L.map("map").setView([lat, lng], 11);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors"
    }).addTo(map);

    L.marker([lat, lng])
        .addTo(map)
        .bindPopup("You are here")
        .openPopup();
}

function loadMyAQI(lat, lng) {
    fetch(`http://127.0.0.1:5000/aqi/current?lat=${lat}&lng=${lng}`)
        .then(res => res.json())
        .then(data => {
            if (!data.aqi) {
                document.getElementById("myAqi").innerHTML = `
                    AQI: <b>${data.category}</b><br>
                    <small>${data.health_message}</small><br>
                    <small>Source: ${data.source}</small>
                `;
                return;
            }

            document.getElementById("myAqi").innerHTML = `
                Your Location AQI: 
                <b>${data.aqi}</b> (${data.category})<br>
                <small>${data.health_message}</small><br>
                <small>Source: ${data.source}</small>
            `;
        })
        .catch(() => {
            document.getElementById("myAqi").innerHTML =
                "Unable to fetch AQI data.";
        });
}


function getColor(aqi) {
    if (aqi <= 100) return "green";
    if (aqi <= 200) return "orange";
    return "red";
}

function loadAllAQI() {
    fetch("http://127.0.0.1:5000/aqi/all")
        .then(res => res.json())
        .then(data => {
            data.forEach(a => {
                if (!a.latitude || !a.longitude) return;

                L.circleMarker([a.latitude, a.longitude], {
                    radius: 8,
                    color: getColor(a.aqi),
                    fillOpacity: 0.7
                })
                .addTo(map)
                .bindPopup(`
                    AQI: ${a.aqi}<br>
                    ${a.category}<br>
                    <small>${a.health_message}</small>
                `);
            });
        });
}

function moveToLocation(lat, lon) {

    map.setView([lat, lon], 10);

    // Remove old marker (prevent stacking)
    if (window.currentMarker) {
        map.removeLayer(window.currentMarker);
    }

    window.currentMarker = L.marker([lat, lon]).addTo(map);

    fetch(`http://127.0.0.1:5000/aqi/current?lat=${lat}&lng=${lon}`)
        .then(res => res.json())
        .then(data => {

            document.getElementById("myAqi").innerHTML = `
                AQI: <b>${data.aqi ?? "N/A"}</b> (${data.category})<br>
                <small>${data.health_message}</small><br>
                <small>Source: ${data.source}</small>
            `;

            // Show AQI in marker popup properly
            window.currentMarker
                .bindPopup(`
                    <b>${data.aqi ?? "N/A"}</b> - ${data.category}<br>
                    <small>${data.source}</small>
                `)
                .openPopup();
        })
        .catch(() => {
            document.getElementById("myAqi").innerHTML =
                "Failed to fetch AQI.";
        });
}
