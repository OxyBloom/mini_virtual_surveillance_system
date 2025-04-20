# utils.py

import os
from datetime import datetime
import smtplib
import json
import requests
from email.message import EmailMessage
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, CONFIG_PATH,DASHBOARD_URL

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def ensure_dirs(paths):
    for path in paths:
        os.makedirs(path, exist_ok=True)

def send_email_alert(receiver_email,timestamp, image_path=None):
    try:
        msg = EmailMessage()
        msg.set_content(f"Motion detected at {timestamp}")
        msg["Subject"] = "Security Alert - Motion Detected"
        msg["From"] = EMAIL_SENDER
        msg["To"] = receiver_email

        # Attach image if provided
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                img_data = f.read()
                msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=os.path.basename(image_path))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print(f"[INFO] Email alert sent at {timestamp} to {receiver_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

def notify_dashboard(motion):
    try:
        requests.post(DASHBOARD_URL, json={"motion_detected": motion})
    except Exception as e:
        print("Dashboard notification failed:", e)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"alerts_enabled": True, "alert_email": "example@example.com"}
