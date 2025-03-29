/* script.js */
fetch("http://localhost:5000/api/stats")
.then(response => response.json())
.then(data => {
    document.getElementById("users").innerText = `${data.users} Active Users`;
    document.getElementById("sales").innerText = `$${data.sales} This Month`;
    document.getElementById("performance").innerText = `${data.performance}% Efficiency`;
})
.catch(error => console.error("Error fetching data:", error));
