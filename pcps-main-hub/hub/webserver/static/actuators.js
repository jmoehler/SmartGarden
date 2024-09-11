console.log("Getting led status");
getLedStatus();
setInterval(getLedStatus, 5000);

function getLedStatus() {
    console.log("Fetching led status");
    var led = document.getElementById("ledSwitch");

    fetch('/get_led_status')
        .then(response => response.json())
        .then(data => {
            if (data.status == "on") {
                led.disabled = false;
                led.checked = true;
            } else if (data.status == "off") {
                led.disabled = false;
                led.removeAttribute("checked");
            } else {
                led.disabled = true;
                console.log(data);
                throw new Error("Error fetching led status");
            }
        })
        .catch(error => {
            led.disabled = true;
            console.log("Error fetching led status: ",error);
        });
}

function toggleLed() {
    var checkbox = document.getElementById("ledSwitch");
    var status = checkbox.checked ? "on" : "off";

    fetch('/toggle_led', {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({toggle: status})})
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status == "on") {
                checkbox.setAttribute("checked", "checked");
            } else if (data.status == "off") {
                checkbox.removeAttribute("checked");
            } else {
                throw new Error("Error toggling led");
            }
        })
        .catch(error => {
            console.log("Error toggling led: ",error);
        });
}