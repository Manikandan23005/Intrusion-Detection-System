import requests
import json
import datetime
from scapy.all import sniff, IP, TCP, UDP

SUSPICIOUS_PORTS = {23, 2323, 4444, 5555, 6667, 8080, 31337}
SUSPICIOUS_IPS = {"192.168.1.100"}
import subprocess

def block_ip(ip_address):
    try:
        # Construct the UFW command
        command = ['sudo', 'ufw', 'deny', 'from', ip_address]
        # Run the command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"[+] Blocked IP {ip_address} via UFW.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to block IP {ip_address}. Error:\n{e.stderr}")
API_URL = "http://localhost:5000/receive_data"  # Change this to your actual API

def send_to_api(alert_type, src_ip, dst_ip, dst_port=None):
    data = {
        "alert_type": alert_type,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "dst_port": dst_port
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        print(f" Sent to API: {data} | Response: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API Error: {e}")

def log_alert(message, src_ip, dst_ip, dst_port=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry, end="") 

    with open("intrusion_logs.txt", "a") as log_file:
        log_file.write(log_entry)

    # Send to API
    send_to_api(message, src_ip, dst_ip, dst_port)
def process_packet(packet):
    print(f"📡 Packet Captured: {packet.summary()}")  # Debugging output
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        if TCP in packet or UDP in packet:
            dst_port = packet[TCP].dport if TCP in packet else packet[UDP].dport
            
            if dst_port in SUSPICIOUS_PORTS:
                log_alert(f"⚠️ Suspicious Port Access: {src_ip} -> {dst_ip}:{dst_port}", src_ip, dst_ip, dst_port)
            
            if src_ip in SUSPICIOUS_IPS:
                log_alert(f"⚠️ Known Malicious IP Detected: {src_ip} -> {dst_ip}", src_ip, dst_ip)

def start_ids():
    print(" Starting IDS... Monitoring Traffic & Sending Alerts to API...")
    sniff(prn=process_packet, store=False, filter="ip")

if __name__ == "__main__":
    start_ids()

