/* script.js */
fetch("http://localhost:5000/api/ids-stats")
.then(response => response.json())
.then(data => {
    document.getElementById("alerts").innerText = `${data.alerts} Total Alerts`;
    document.getElementById("high-severity").innerText = `${data.highSeverity} High Severity Alerts`;
    document.getElementById("traffic").innerText = `${data.traffic} MB/s Traffic`;
    document.getElementById("system-health").innerText = `${data.systemHealth} System Health`;
    document.getElementById("recent-threats").innerText = `${data.recentThreats}`;
})
.catch(error => console.error("Error fetching data:", error));
