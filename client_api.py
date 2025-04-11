import requests
import json 
def add_user(username):
    url = "http://127.0.0.1:5000/add_user"
    headers = {"Content-Type": "application/json"}
    payload = {"username": username}

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print(f"User added successfully with ID {response.json()['user_id']}")
    else:
        print(f"Failed to add user: {response.json()['error']}")

# Function to send log data to the API (from client or script)
def add_log(user_id, event_type, source_ip, message, severity):
    url = "http://127.0.0.1:5000/add_log"
    headers = {"Content-Type": "application/json"}
    payload = {
        "user_id": user_id,
        "event_type": event_type,
        "source_ip": source_ip,
        "message": message,
        "severity": severity
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print(f"Log added successfully with ID {response.json()['log_id']}")
    else:
        print(f"Failed to add log: {response.json()['error']}")

