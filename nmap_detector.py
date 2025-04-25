from scapy.all import sniff, IP, TCP, UDP
from alert import send_email
from collections import defaultdict
import time
from client_api import add_log
from user import block_ip
import json

# Initialize configuration
uid = 0
try:
    with open('config.json') as file:
        data = json.load(file)
        uid = data.get('user_id', 0)
except FileNotFoundError:
    print("Config file not found.")
except json.JSONDecodeError:
    print("Error decoding config file.")

# Tracking variables
sessions = defaultdict(lambda: {'bytes': 0, 'packets': 0, 'start_time': time.time()})
scan_tracker = defaultdict(list)
SIZE_THRESHOLD = 500 * 1024  # Example: 500 KB
PACKET_THRESHOLD = 5         # Example: Minimum 5 packets
SCAN_THRESHOLD = 10          # Port scan threshold
TIME_WINDOW = 10             # Time window for tracking (in seconds)

# File transfer detection function
def detect_file_transfer(packet):
    if IP in packet and (TCP in packet or UDP in packet):
        src = packet[IP].src
        dst = packet[IP].dst
        key = (src, dst)

        pkt_len = len(packet)
        now = time.time()

        # Reset sessions if time window expired
        if now - sessions[key]['start_time'] > TIME_WINDOW:
            sessions[key] = {'bytes': 0, 'packets': 0, 'start_time': now}

        sessions[key]['bytes'] += pkt_len
        sessions[key]['packets'] += 1

        # If file transfer threshold exceeded
        if sessions[key]['bytes'] > SIZE_THRESHOLD and sessions[key]['packets'] > PACKET_THRESHOLD:
            print(f"[ALERT] Possible file transfer from {src} to {dst} - "
                  f"{sessions[key]['bytes'] / (1024*1024):.2f} MB in {sessions[key]['packets']} packets.")
            sessions[key] = {'bytes': 0, 'packets': 0, 'start_time': now} 
            
            try:
                send_email("File Transfer Detected:", f"possible file transfer from {src} to {dst}")
                add_log(uid, "File Transfer Detected", dst, f"possible file transfer detected from {src} to {dst}","medium")
            except Exception as e:
                print(f"Error: {e}")

# Nmap/Port scan detection function
def detect_nmap(pkt):
    if pkt.haslayer(IP) and pkt.haslayer(TCP):
        src_ip = pkt[IP].src
        dst_port = pkt[TCP].dport
        timestamp = time.time()

        scan_tracker[src_ip].append((dst_port, timestamp))

        # Filter scan history for the last TIME_WINDOW seconds
        scan_tracker[src_ip] = [(p, t) for p, t in scan_tracker[src_ip] if timestamp - t <= TIME_WINDOW]

        # Port scan detection based on threshold
        if len(set(p for p, _ in scan_tracker[src_ip])) > SCAN_THRESHOLD:
            msg = f"⚠ Potential port scan detected from {src_ip}"
            print(msg)
            try:
                send_email("Nmap/Port Scan Detected", msg)
                add_log(uid, "Nmap/Port Scan Detected", "Unknown", msg, "high")
                block_ip(src_ip)
            except Exception as e:
                print(f"Error: {e}")
            scan_tracker[src_ip] = []  

# Combined sniffing function
def combined_detection(packet):
    detect_nmap(packet)
    detect_file_transfer(packet)

# Start sniffing
def start_sniffing():
    print("[INFO] Starting network monitor for port scans and file transfers...")
    sniff(filter="tcp", prn=combined_detection, store=0)

# Call start_sniffing to begin packet sniffing

