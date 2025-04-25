from monitor import IntrusionMonitor
from auth_monitor import AuthLogMonitor
from nmap_detector import start_sniffing
import threading
import time
import subprocess

def block_ip(ip_address):
    subprocess.run([ "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"])

def block_mac(mac_address):
    subprocess.run([ "ebtables", "-A", "INPUT", "-s", mac_address, "-j", "DROP"])

if __name__ == "__main__":
    print("[INFO] Starting journalctl auth monitor...")
    auth_monitor_thread = threading.Thread(target=AuthLogMonitor().start, daemon=True)
    auth_monitor_thread.start()

    print("[INFO] Starting file system monitor...")
    file_monitor = IntrusionMonitor(path="./")
    file_monitor_thread = threading.Thread(target=file_monitor.run, daemon=True)
    file_monitor_thread.start()

    print("[INFO] Starting network monitor...")
    sniff_thread = threading.Thread(target=start_sniffing, daemon=True)
    sniff_thread.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] IDS stopped by user.")
