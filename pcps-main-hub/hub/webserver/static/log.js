
function reverseTableRows() {
    var tbody = document.getElementById("logTable");
    var rows = tbody.getElementsByTagName("tr");
    
    // convert NodeList to array and reverse it
    var reversedRows = Array.from(rows).reverse();
    
    // clear existing rows
    tbody.innerHTML = "";
    
    // append reversed rows to tbody
    reversedRows.forEach(row => { tbody.appendChild(row); });
}

async function getLogData(){
    fetch('/get_all_logs')
        .then(response => response.json())
        .then(data => {
            // delete all rows in table except the header
            var logTable = document.getElementById("logTable");
            for (var i = logTable.rows.length - 1; i >= 0; i--) {
                logTable.deleteRow(i);
            }

            const activatedFilterSensors = [...document.querySelectorAll('input[name=sensor-filter-checkboxes]:checked')];
            const activatedSensors = activatedFilterSensors.map(checkbox => {
                console.log(checkbox.value);
                return parseInt(checkbox.value);
            });
            
            const selector = document.getElementById('log-select')
            const selectorState = selector.value;
            
            for (var i = 0; i < data.log.length; i++) {
                var log = data.log[i];
                var logTable = document.getElementById("logTable");
                criticalFlag = 0
                
                // if `descending` is selected put now entries at the top, else append them at the bottom
                var row = selectorState === 'descending' ? logTable.insertRow(0) : logTable.insertRow(-1);  
                
                var statuscodeCell = row.insertCell(0);
                var timestampCell = row.insertCell(1);
                var messageCell = row.insertCell(2);
                var actionCell = row.insertCell(3);
                
                statuscodeCell.innerHTML = log.statuscode;
                timestampCell.innerHTML = log.timestamp;
                var message = "";
                var action = "Action taken!";
                
                var statuscode = parseInt(log.statuscode);
                var statuscodeFirstDigit = Math.floor(statuscode / 100);
                var statuscodeLastTwoDigits = statuscode % 100;
                
                // skip unchecked sensors
                if (!activatedSensors.includes(statuscodeFirstDigit)){
                    if(selectorState === 'descending')
                        logTable.deleteRow(0)
                    else 
                        logTable.deleteRow(-1);  
                    continue;
                }

                switch (statuscodeFirstDigit) {
                    case 1:
                        message += "The EC-value is ";
                        break;
                    case 2:
                        message += "The pH-value is ";
                        break;
                    case 3:
                        message += "The temperature is ";
                        break;
                    case 4:
                        message += "The humidity is ";
                        break;
                    case 5:
                        message = "The water level is ";
                        break;
                    default:
                        message = "error unknown";
                        action = "error unkown";
                }

                switch (statuscodeLastTwoDigits) {
                    case 2:
                        message += "too high.";
                        break;
                    case 4:
                        message += "too high.";
                        break;
                    case 3:
                        message += "too low.";
                        break;
                    case 6:
                        message += "too low.";
                        break;
                    case 1:
                        message += "just right.";
                        break;
                    case 5:
                        message += "just right";
                        break;
                    case 7:
                        criticalFlag = 1;
                        message += "too low.";
                        action = "CRITICAL: Action has been taken 5 times, but no improvement!";
                        row.classList.add("critical-event");
                        break;
                    case 8:
                        criticalFlag = 1;
                        message += "too high.";
                        action = "CRITICAL: Action has been taken 5 times, but no improvement!";
                        row.classList.add("critical-event");
                        break;
                    default:
                        message = "error unknown";
                        action = "error unkown";
                }


                messageCell.innerHTML = message;
                
                actionCell.innerHTML = action;
                if (criticalFlag) actionCell.classList.add('text-danger');
            }

        })
        .catch(error => {
            console.log("Error fetching log data: ",error);
        });

        
}


function clearLogHistory() {
    document.getElementById('clear-log-form').submit();
    const logBody = document.getElementById('logTable');
    logBody.innerHTML = ''
}


function exportToCSV(){
    let csv = []
    let rows = document.getElementsByTagName('tr'); // all rows
    for (let i = 0; i < rows.length; i++){
        let cols = rows[i].querySelectorAll('td, th'); // get all cells of current row.
        let csvrow = [];
        for (let j = 0; j < cols.length; j++) {
            let col = cols[j].innerHTML;
            
            // check if column contains a `,` and remove it.
            if (col.includes(','))
                csvrow.push(col.replace(',', ''));
            else 
                csvrow.push(col);
        }
        
        csv.push(csvrow.join(','));
    }

    csv = csv.join('\n');

    // file-like object of immutable, raw data
    CSVFile = new Blob([csv], {type: 'text/csv'});

    // temporal, unvisible link to initiat download process
    let tmp = Object.assign( document.createElement('a'),  { download: 'SimplePlant_log.csv', href: window.URL.createObjectURL(CSVFile), display: 'none' });
    document.body.appendChild(tmp);
    tmp.click();
    document.body.removeChild(tmp);
}

getLogData();
setInterval(getLogData, 5000);