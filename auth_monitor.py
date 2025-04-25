# auth_monitor.py

import subprocess
import re
from alert import send_email
from client_api import add_log
ip=""
import json
from user import block_ip
uid=0
from collections import defaultdict

failed_attempts = defaultdict(int)

with open('config.json') as file:
    data = json.load(file)
    uid=(data['user_id'])

class AuthLogMonitor:
    def __init__(self):
        self.journalctl = subprocess.Popen(
            ['journalctl', '-f', '-n', '0'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def start(self):
        print("[INFO] Starting journalctl auth monitor...")
        for line in self.journalctl.stdout:
            self.parse_log(line.strip())

    def parse_log(self, log_line):
        # ✅ SSH login successful (local or remote)
        if "Accepted password for" in log_line:
            match = re.search(r"Accepted password for (\w+) from ([\d\.]+)", log_line)
            ip=""
            if match:
                user, ip = match.group(1), match.group(2)
                msg = f"SSH login successful: user '{user}' from {ip}"
            else:
                match = re.search(r"Accepted password for (\w+)", log_line)
                if match:
                    user = match.group(1)
                    msg = f"SSH login successful: user '{user}' (local or IP not found)"
                else:
                    return
            print(msg)
            failed_attempts[ip] = 0
            send_email("SSH Login Successful", msg)
            add_log(uid,"Login Attempt","Unknown or Local" if ip=="" else ip ,msg,"medium")
            return

        # ❌ SSH login failed (local or remote)
        if "Failed password for" in log_line:
            ip=""
            match = re.search(r"Failed password for (invalid user )?(\w+) from ([\d\.]+)", log_line)
            if match:
                invalid = match.group(1) or ""
                user, ip = match.group(2), match.group(3)
                msg = f"❌ SSH login failed: {invalid.strip()}user '{user}' from {ip}"
            else:
                fallback = re.search(r"Failed password for (invalid user )?(\w+)", log_line)
                if fallback:
                    user = fallback.group(2)
                    msg = f"❌ SSH login failed: user '{user}' (IP not found)"
                else:
                    return
            print(msg)
            failed_attempts[ip] += 1
            if failed_attempts[ip] > 5:
                print(f"🚨 Too many failed login attempts from {ip}, blocking the IP...")
                block_ip(ip)  
                failed_attempts[ip] = 0  
            send_email("SSH Login Failed", msg)
            add_log(uid,"Login Attempt","Unknown or Local" if ip=="" else ip ,msg,"high")
            return

        # ⚙️ Root shell accessed via sudo -i
        if "sudo" in log_line and "COMMAND=/usr/bin/zsh" in log_line:
            user = re.search(r'^.*sudo\[\d+\]: (\w+)', log_line)
            if user:
                msg = f"⚙️ Root shell accessed by user {user.group(1)}"
                print(msg)
                send_email("Root Shell Access", msg)
                add_log(uid,"Root Shell Access","Unknown" ,msg,"high")
            return
        

        # 👤 New user added
        if "adduser" in log_line and "home directory" in log_line:
            user = re.search(r'adduser:.*user (\w+)', log_line)
            if user:
                msg = f"👤 New user created: {user.group(1)}"
                print(msg)
                send_email("User Created", msg)
                add_log(uid,"User Created","Unknown",msg,"low")
            return

        # ❌ User deleted
        if "deluser" in log_line and "remove user" in log_line:
            user = re.search(r"remove user '(\w+)'", log_line)
            if user:
                msg = f"❌ User deleted: {user.group(1)}"
                print(msg)
                send_email("User Deleted", msg)
                add_log(uid,"User Deleted","Unknown",msg,"medium")
            return

        # 🔑 Password changed
        if "passwd" in log_line and ("password changed" in log_line or "password updated" in log_line):
            user = re.search(r'passwd.*user (\w+)', log_line)
            if user:
                msg = f"🔑 Password changed for user {user.group(1)}"
                print(msg)
                send_email("Password Changed", msg)
                add_log(uid,"Password Changed","Unknown",msg,"medium")
            return

        # 🔄 User modified
        if "usermod" in log_line:
            user = re.search(r'usermod.*user (\w+)', log_line)
            if user:
                msg = f"🔄 User modified: {user.group(1)}"
                print(msg)
                send_email("User Modified", msg)
                add_log(uid,"User Modified","Unknown" ,msg,"low")
            return

        # 👥 Group change
        if "add '" in log_line and "to group" in log_line:
            user = re.search(r"add '(\w+)' to group '(\w+)'", log_line)
            if user:
                msg = f"👥 User '{user.group(1)}' added to group '{user.group(2)}'"
                print(msg)
                send_email("User Group Change", msg)
                add_log(uid,"User Group Changed","Unknown" ,msg,"low")
            return

        # 🚫 Ignore unrelated logs
        return
