from flask import Flask, render_template, Response, send_from_directory, request, redirect, url_for
import cv2
import os
import json

app = Flask(__name__)

VIDEO_DIR = "static/videos"
SNAPSHOT_DIR = "static/snapshots"
CONFIG_PATH = "config.json"

# Default motion status
motion_status = {"motion_detected": False}

# Load or initialize config
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"alerts_enabled": True, "alert_email": ""}

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)

config = load_config()

@app.route('/', methods=['GET'])
def index():
    videos = sorted(os.listdir(VIDEO_DIR), reverse=True)
    snapshots = sorted(os.listdir(SNAPSHOT_DIR), reverse=True)
    selected_snapshot = request.args.get("snapshot")
    selected_video = request.args.get("video")
    return render_template("index.html",
                           videos=videos,
                           snapshots=snapshots,
                           selected_snapshot=selected_snapshot,
                           selected_video=selected_video,
                           alerts_enabled=config.get("alerts_enabled", True),
                           alert_email=config.get("alert_email", ""),
                           motion_detected=motion_status["motion_detected"])


@app.route('/videos/<filename>')
def get_video(filename):
    return send_from_directory(VIDEO_DIR, filename)

@app.route('/snapshots/<filename>')
def get_snapshot(filename):
    return send_from_directory(SNAPSHOT_DIR, filename)

@app.route('/view_snapshot', methods=['GET'])
def view_snapshot():
    snapshot = request.args.get("snapshot")
    return redirect(url_for('index', snapshot=snapshot))

@app.route('/view_video', methods=['GET'])
def view_video():
    video = request.args.get("video")
    return redirect(url_for('index', video=video))

@app.route('/set_config', methods=['POST'])
def set_config():
    alerts_enabled = 'alerts_enabled' in request.form
    alert_email = request.form.get('alert_email', '')
    config['alerts_enabled'] = alerts_enabled
    config['alert_email'] = alert_email
    save_config(config)
    return redirect(url_for('index'))

# Simulate motion detection status update from main.py (to be integrated)
@app.route('/update_motion_status', methods=['POST'])
def update_motion():
    data = request.get_json()
    motion_status["motion_detected"] = data.get("motion_detected", False)
    return {"status": "ok"}

@app.route('/motion_status')
def motion_status_api():
    return {"motion_detected": motion_status["motion_detected"]}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
