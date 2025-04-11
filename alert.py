import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
recv=""
with open('config.json') as file:
    data = json.load(file)
    recv=(data['notification_email'])

def send_email(subject, body):
    sender_email = "ids.detection.in007@gmail.com"
    receiver_email = recv
    password = "asvtsrbghsznnbyb"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)
        server.quit()
        print("[EMAIL] Alert sent successfully.")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {e}")
