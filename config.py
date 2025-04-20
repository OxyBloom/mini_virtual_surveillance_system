# config.py
import os
import json


EMAIL_SENDER = "sender_email@gmail.com"
EMAIL_PASSWORD = "your app password"  # Use App Password if using Gmail
EMAIL_RECEIVER = "reciever@gmail.com"

MOTION_SENSITIVITY =5000  # Increase to reduce false alerts

VIDEO_DURATION = 10  # Seconds to record after motion
CAMERA_SOURCE = 0  # Use 0 for default webcam or Pi Camera

# RECORDINGS_PATH = "recordings"
RECORDINGS_PATH = "static/videos"
SNAPSHOT_PATH = "static/snapshots"
LOG_PATH = "logs"

CONFIG_PATH = "config.json"
VIDEO_DIR = "static/videos"
SNAPSHOT_DIR = "static/snapshots"
DASHBOARD_URL = "http://localhost:5000/update_motion_status"  # Update if hosted remotely


for path in [VIDEO_DIR, SNAPSHOT_DIR, LOG_PATH]:
    if not os.path.exists(path):
        os.makedirs(path)

# Load/save runtime config (email receiver, alerts toggle)
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {
        "alerts_enabled": True,
        "alert_email": EMAIL_RECEIVER
    }

def save_config(config_data):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config_data, f)


