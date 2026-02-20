document.addEventListener("DOMContentLoaded", function () {

    if (!navigator.geolocation) {
        document.getElementById("headerAqi").innerText = "AQI: Location not supported";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        position => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            fetch(`http://127.0.0.1:5000/aqi/current?lat=${lat}&lng=${lng}`)
                .then(res => res.json())
                .then(data => {

                    const aqi = data.aqi ?? "N/A";
                    const category = data.category ?? "";

                    const badge = document.getElementById("headerAqi");
                    badge.innerText = `AQI: ${aqi} (${category})`;

                    // 🎨 Color based on AQI
                    if (aqi <= 50) {
                        badge.className = "badge bg-success fs-6";
                    } else if (aqi <= 100) {
                        badge.className = "badge bg-info fs-6";
                    } else if (aqi <= 200) {
                        badge.className = "badge bg-warning text-dark fs-6";
                    } else {
                        badge.className = "badge bg-danger fs-6";
                    }

                })
                .catch(() => {
                    document.getElementById("headerAqi").innerText = "AQI: Unavailable";
                });
        },
        () => {
            document.getElementById("headerAqi").innerText = "AQI: Location denied";
        }
    );
});
