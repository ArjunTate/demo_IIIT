let map;
let currentMarker = null;
let currentInfo = null;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 20, lng: 0 },
    zoom: 2
  });

  const input = document.getElementById("searchBox");

  const autocomplete = new google.maps.places.Autocomplete(input);

  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();

    if (!place.geometry) {
      alert("No location found");
      return;
    }

    const location = place.geometry.location;
    const lat = location.lat();
    const lng = location.lng();

    map.setCenter(location);
    map.setZoom(6);

    calculateRisk(lat, lng).then(data => {
      showRisk(lat, lng, place.name, data);
    });
  });
}

//////////////////////////////////////////////////////////
// 🔥 REAL WEATHER + RISK ENGINE
//////////////////////////////////////////////////////////

async function calculateRisk(lat, lng) {
  const API_KEY = "2d1ebeda3cb4bbe7a2fe15e7cf8ca5fe"; // ← PUT YOUR KEY HERE

  const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lng}&appid=${API_KEY}&units=metric`;

  try {
    const res = await fetch(url);
    const data = await res.json();

    if (data.cod !== 200) throw new Error("API error");

    const temp = data.main.temp;
    const wind = data.wind.speed;
    const humidity = data.main.humidity;
    const pressure = data.main.pressure;

    const risk = calculateRiskScore(temp, wind, humidity, pressure);

    return {
      temperature: temp.toFixed(1),
      wind: wind.toFixed(1),
      humidity,
      pressure,
      risk
    };

  } catch (err) {
    console.error(err);

    return {
      temperature: "N/A",
      wind: "N/A",
      humidity: "N/A",
      pressure: "N/A",
      risk: "UNKNOWN"
    };
  }
}

//////////////////////////////////////////////////////////
// 🧠 SMART RISK CALCULATION
//////////////////////////////////////////////////////////

function calculateRiskScore(temp, wind, humidity, pressure) {
  let score = 0;

  // 🌡 Temperature
  if (temp > 35) score += 3;
  else if (temp > 30) score += 2;
  else if (temp > 25) score += 1;

  // 💨 Wind
  if (wind > 10) score += 3;
  else if (wind > 7) score += 2;
  else if (wind > 4) score += 1;

  // 💧 Humidity
  if (humidity > 80) score += 2;
  else if (humidity > 60) score += 1;

  // 🌊 Pressure (LOW pressure = danger)
  if (pressure < 1000) score += 3;
  else if (pressure < 1010) score += 2;

  // FINAL RESULT
  if (score >= 7) return "HIGH";
  if (score >= 4) return "MEDIUM";
  return "LOW";
}

//////////////////////////////////////////////////////////
// 🎯 DISPLAY RESULT ON MAP
//////////////////////////////////////////////////////////

function showRisk(lat, lng, name, data) {

  // Remove old marker
  if (currentMarker) currentMarker.setMap(null);

  // Close old popup
  if (currentInfo) currentInfo.close();

  const color =
    data.risk === "HIGH" ? "red" :
    data.risk === "MEDIUM" ? "orange" :
    data.risk === "LOW" ? "green" :
    "gray";

  const marker = new google.maps.Marker({
    position: { lat, lng },
    map: map,
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      scale: 10,
      fillColor: color,
      fillOpacity: 1,
      strokeWeight: 1
    }
  });

  const info = new google.maps.InfoWindow({
    content: `
      <div style="min-width:200px">
        <h3>${name}</h3>
        <p>🌡 Temp: ${data.temperature}°C</p>
        <p>💨 Wind: ${data.wind} m/s</p>
        <p>💧 Humidity: ${data.humidity}%</p>
        <p>🌊 Pressure: ${data.pressure} hPa</p>
        <p><b style="color:${color}">⚠ Risk: ${data.risk}</b></p>
      </div>
    `
  });

  info.open(map, marker);

  currentMarker = marker;
  currentInfo = info;
}

window.onload = initMap;