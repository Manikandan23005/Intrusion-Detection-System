from scapy.all import sniff, IP, TCP, UDP
import datetime

SUSPICIOUS_PORTS = {23, 2323, 4444, 5555, 6667, 8080, 31337}
SUSPICIOUS_IPS = {"192.168.1.100"} 

def log_alert(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry, end="") 
    with open("intrusion_logs.txt", "a") as log_file:
        log_file.write(log_entry)

def process_packet(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        protocol = packet[IP].proto

        if TCP in packet or UDP in packet:
            dst_port = packet[TCP].dport if TCP in packet else packet[UDP].dport

            if dst_port in SUSPICIOUS_PORTS:
                log_alert(f"⚠️ Suspicious Port Access: {src_ip} -> {dst_ip}:{dst_port}")

            if src_ip in SUSPICIOUS_IPS:
                log_alert(f"⚠️ Known Malicious IP Detected: {src_ip} -> {dst_ip}")

def start_ids():
    print("✅ Starting Basic IDS... Monitoring Traffic...")
    sniff(prn=process_packet, store=False)

if __name__ == "__main__":
    start_ids()

