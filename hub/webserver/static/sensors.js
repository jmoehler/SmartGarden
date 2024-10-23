function setFullOpacity(id) {
    var element = document.getElementById(id);
    element.style.opacity = "1";
}

function setLowOpacity(id) {
    var element = document.getElementById(id);
    element.style.opacity = "0.2";
}

function getPh() {
    fetch('/get_ph')
        .then(response => response.json())
        .then(data => {
            document.getElementById('ph-value').innerHTML = data.ph.entries[0].ph_value.toFixed(2);
            clearInterval(phIntervallId);
            updateTimeOfMeasurement("ph", data.ph.entries[0].time_of_measurement);
            phIntervallId = setInterval(updateTimeOfMeasurement, 1000, "ph", data.ph.entries[0].time_of_measurement);


            setFullOpacity("ph");
            
        })
        .catch(error => {
            document.getElementById('ph-value').innerHTML = "-";

            setLowOpacity("ph");
            
        });
}

function getEc() {
    fetch('/get_ec')
        .then(response => response.json())
        .then(data => {
            document.getElementById('ec-value').innerHTML = data.ec.entries[0].ec_value.toFixed(2);
            clearInterval(ecIntervallId);
            updateTimeOfMeasurement("ec", data.ec.entries[0].time_of_measurement);
            ecIntervallId = setInterval(updateTimeOfMeasurement, 1000, "ec", data.ec.entries[0].time_of_measurement);

            setFullOpacity("ec");
            
        })
        .catch(error => {
            document.getElementById('ec-value').innerHTML = "-";

            setLowOpacity("ec");
            
        });
}

function getWaterlevel() {
    fetch('/get_waterlevel')
        .then(response => response.json())
        .then(data => {
            if (data.waterlevel.entries[0].waterlevel_value < 1){
                document.getElementById('waterlevel-value').innerHTML = "Full";
            } else {
                document.getElementById('waterlevel-value').innerHTML = "Too low";
            }
            
            clearInterval(waterlevelIntervallId);
            updateTimeOfMeasurement("waterlevel", data.waterlevel.entries[0].time_of_measurement);
            waterlevelIntervallId = setInterval(updateTimeOfMeasurement, 1000, "waterlevel", data.waterlevel.entries[0].time_of_measurement);
            setFullOpacity("waterlevel");
            
        })
        .catch(error => {
            document.getElementById('waterlevel-value').innerHTML = "-";


            setLowOpacity("waterlevel");
            
        });
}

function getTemperature() {
    fetch('/get_temperature')
        .then(response => response.json())
        .then(data => {
            document.getElementById('temperature-value').innerHTML = data.temperature.entries[0].temperature_value.toFixed(2);
            clearInterval(temperatureIntervallId);
            updateTimeOfMeasurement("temperature", data.temperature.entries[0].time_of_measurement);    
            temperatureIntervallId = setInterval(updateTimeOfMeasurement, 1000, "temperature", data.temperature.entries[0].time_of_measurement);


            setFullOpacity("temperature");
            
        })
        .catch(error => {
            document.getElementById('temperature-value').innerHTML = "-";

            setLowOpacity("temperature");
            
        });
}

function getHumidity() {
    fetch('/get_humidity')
        .then(response => response.json())
        .then(data => {
            document.getElementById('humidity-value').innerHTML = data.humidity.entries[0].humidity_value.toFixed(2);
            clearInterval(humidityIntervallId);
            updateTimeOfMeasurement("humidity", data.humidity.entries[0].time_of_measurement);
            humidityIntervallId = setInterval(updateTimeOfMeasurement, 1000, "humidity", data.humidity.entries[0].time_of_measurement);


            setFullOpacity("humidity");
            
        })
        .catch(error => {
            document.getElementById('humidity-value').innerHTML = "-";

            setLowOpacity("humidity");
            
        });
}

function getLight() {
    fetch('/get_light')
        .then(response => response.json())
        .then(data => {
            document.getElementById('light-value').innerHTML = data.light.entries[0].visible_value.toFixed(2);
            clearInterval(lightIntervallId);
            updateTimeOfMeasurement("light", data.light.entries[0].time_of_measurement);
            lightIntervallId = setInterval(updateTimeOfMeasurement, 1000, "light", data.light.entries[0].time_of_measurement);

            setFullOpacity("light");
            
        })
        .catch(error => {
            document.getElementById('light-value').innerHTML = "-";

            setLowOpacity("light");
            
        });
}

let lastRefresh;

function refreshAllSensors() {
    lastRefresh = Date.now();
    getPh();
    getEc();
    getWaterlevel();
    getTemperature();
    getHumidity();
    getLight();
}


function updateTimeOfMeasurement(sensor, timestamp) {
    const timeOfMeasurementCard = document.getElementById(sensor + '-timestamp');

    const then = new Date(timestamp);
    const now = new Date();
    const delta = now - then;

    if (delta < 60000){
        document.getElementById(sensor+'-timestamp').innerHTML = "Measurement: <b>" + Math.floor(delta / 1000) + "</b> seconds ago";
    } else if (delta < 3600000){
        document.getElementById(sensor+'-timestamp').innerHTML = "measured <b>" + Math.floor(delta / 60000) + "</b> minutes ago";
    } else if (delta < 86400000){
        document.getElementById(sensor+'-timestamp').innerHTML = "measured <b>" + Math.floor(delta / 3600000) + "</b> hours ago";
    } else {
        document.getElementById(sensor+'-timestamp').innerHTML = "measured <b>" + Math.floor(delta / 86400000) + "</b> days ago";
    }
}


function updateLastRefreshTimer() {
    const lastUpdatedCard = document.getElementById('sensor-refresh');
    
    const now = Date.now();
    const delta = now - lastRefresh;

    if(delta < 60000){
        lastUpdatedCard.innerText = 'Last updated: ' + Math.floor(delta / 1000) + ' seconds ago';
    } else if (delta < 3600000){
        lastUpdatedCard.innerText = 'Last updated: ' + Math.floor(delta / 60000) + ' minutes ago';
    } else if (delta < 86400000){
        lastUpdatedCard.innerText = 'Last updated: ' + Math.floor(delta / 3600000) + ' hours ago';
    } else {
        lastUpdatedCard.innerText = 'Last updated: ' + Math.floor(delta / 86400000) + ' days ago';
    }

}

// refresh the sensors on page load
refreshAllSensors();

function getAnalysis() {
    fetch('/get_picture_analysis')
        .then(response => {
            if (!response.ok){
                const result = document.getElementById('analysis-result');
                const recommendation = document.getElementById('analysis-recommendation');
                result.innerHTML = "No analysis data available, since no analysis was performed yet.";
                recommendation.innerHTML = "No recommendations available, since no analysis was performed yet.";
            } else {
                response.json()
            }
        })
        .then(data => {
            const result = document.getElementById('analysis-result');
            const recommendation = document.getElementById('analysis-recommendation');
        })
        .catch(error => {
            document.getElementById('analysis-result').innerHTML = "Some error occured while fetching the analysis data";
            document.getElementById('analysis-recommendation').innerHTML = "Some error occured while fetching the analysis data";
        });
}


function toggleAutoReload(event) {
    clearInterval(intervallId); // stop currently running setIntervall 
    
    if (event.target.checked){
        intervallId = setInterval(refreshAllSensors, 3000);
        const lastUpdatedCard = document.getElementById('sensor-refresh');
        lastUpdatedCard.innerText = 'Auto-reload enabled.'
    } else {
        intervallId = setInterval(updateLastRefreshTimer, 1000, Date.now());
    }
}

getAnalysis();
//setInterval(getAnalysis, 1000); // every 5 minutes

// on startup auto-reload is enabled
let intervallId;
let phIntervallId;
let ecIntervallId;
let waterlevelIntervallId;
let temperatureIntervallId;
let humidityIntervallId;
let lightIntervallId;

intervallId = setInterval(refreshAllSensors, 3000)