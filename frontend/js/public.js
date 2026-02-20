fetch("http://127.0.0.1:5000/aqi/all")
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById("aqiCards");
        container.innerHTML = "";

        data.forEach(a => {
            let bg = "success";

            if (a.aqi > 300) bg = "danger";
            else if (a.aqi > 200) bg = "warning";
            else if (a.aqi > 100) bg = "info";

            const card = document.createElement("div");
            card.className = "col-md-4 mb-3";

            card.innerHTML = `
                <div class="card border-${bg}">
                    <div class="card-body">
                        <h5 class="card-title">${a.location_name || "GPS Area"}</h5>
                        <h2 class="text-${bg}">${a.aqi}</h2>
                        <p>${a.category}</p>
                        <small>${a.health_message}</small>
                    </div>
                </div>
            `;

            container.appendChild(card);
        });
    })
    .catch(err => console.error(err));

const searchInput = document.getElementById("citySearch");
const suggestionsBox = document.getElementById("suggestions");

searchInput.addEventListener("input", function () {
    const query = this.value.trim();

    if (query.length < 2) {
        suggestionsBox.innerHTML = "";
        return;
    }

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}&addressdetails=1&limit=5`)
        .then(res => res.json())
        .then(data => {
            suggestionsBox.innerHTML = "";

            data.forEach(place => {
                const option = document.createElement("div");
                option.style.padding = "8px";
                option.style.cursor = "pointer";
                option.style.borderBottom = "1px solid #eee";
                option.innerText = place.display_name;

                option.onclick = function () {
                    searchInput.value = place.display_name;
                    suggestionsBox.innerHTML = "";

                    const lat = parseFloat(place.lat);
                    const lon = parseFloat(place.lon);

                    moveToLocation(lat, lon);
                };

                suggestionsBox.appendChild(option);
            });
        })
        .catch(err => console.log("Geocoding error:", err));
});

// Load AQI Trend
fetch("http://127.0.0.1:5000/aqi/trend")
  .then(res => res.json())
  .then(data => {

    const labels = data.map(d => d.record_date);
    const values = data.map(d => d.avg_aqi);

    new Chart(document.getElementById("aqiChart"), {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "AQI",
          data: values,
          borderColor: "red",
          fill: false
        }]
      }
    });
  });

// Load Prediction
fetch("http://127.0.0.1:5000/aqi/predict")
  .then(res => res.json())
  .then(data => {
    document.getElementById("predictedAqi").innerText = "🔮 Tomorrow AQI Prediction in your city is " +
      data.predicted_aqi + " (" + data.category + ")";
  });