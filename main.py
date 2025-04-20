# main.py 
import os
from collections import deque
import cv2
import time
import json
import requests
import smtplib
import datetime
from datetime import datetime
import imutils
from threading import Thread
from utils import get_timestamp, ensure_dirs, send_email_alert,load_config
from config import *

import threading

lock = threading.Lock()
shared_frame = None

ensure_dirs([RECORDINGS_PATH, LOG_PATH])

FRAME_BUFFER_SIZE = 100  # ~10 seconds of video at 10 FPS

def record_video(buffered_frames, filename, callback_on_finish):
    if not buffered_frames:
        print("[WARN] No frames to record.")
        callback_on_finish()
        return

    height, width = buffered_frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, 10.0, (width, height))

    for frame in buffered_frames:
        out.write(frame)
        time.sleep(0.1)  # simulate real-time recording

    out.release()
    callback_on_finish()

def main():
    print("[INFO] Starting camera...")
    cap = cv2.VideoCapture(CAMERA_SOURCE)
    time.sleep(2.0)

    first_frame = None
    recording = False
    frame_buffer = deque(maxlen=FRAME_BUFFER_SIZE)

    def reset_recording():
        nonlocal recording
        recording = False
        print("[INFO] Recording finished.")

    while True:
        ret, frame = cap.read()
        global shared_frame
        with lock:
            shared_frame = frame.copy()

        if not ret:
            print("[WARN] Failed to grab frame.")
            continue

        frame = imutils.resize(frame, width=500)
        frame_buffer.append(frame.copy())
        # Add timestamp to frame
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if first_frame is None:
            first_frame = gray
            continue

        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False

        for c in contours:
            if cv2.contourArea(c) < MOTION_SENSITIVITY:
                continue
            motion_detected = True
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if motion_detected and not recording:
            timestamp = get_timestamp()
            video_file = f"{RECORDINGS_PATH}/motion_{timestamp}.avi"
            image_file = f"{SNAPSHOT_PATH}/snapshot_{timestamp}.jpg"

            # Save snapshot image
            cv2.imwrite(image_file, frame)

            print(f"[INFO] Motion detected. Recording video: {video_file}")
            config = load_config()
            if config.get("alerts_enabled", True):
                send_email_alert(config.get("alert_email", EMAIL_RECEIVER),timestamp, image_path=image_file)

            try:
                requests.post(DASHBOARD_URL, json={"motion_detected": True}, timeout=1)
            except:
                print("[WARN] Could not update dashboard motion status.")

            recording = True
            Thread(
                target=record_video,
                # args=(frame, VIDEO_DURATION, video_file, cap, reset_recording),
                args=(list(frame_buffer), video_file, reset_recording),
                daemon=True
            ).start()
        else:
            try:
                requests.post(DASHBOARD_URL, json={"motion_detected": False}, timeout=1)
            except:
                pass


        cv2.imshow("Security Feed", frame)
        key = cv2.waitKey(1) & 0xFF

        # Update first_frame every 100 frames for background adaptation
        if int(time.time()) % 10 == 0:
            first_frame = gray

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
