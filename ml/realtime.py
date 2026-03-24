from pynput import keyboard
import time
import pandas as pd
import joblib
import os
import json

TARGET_TEXT = "greyc laboratory"

press_times = {}
typed_keys = []
window_data = []

ANOMALY_COUNT = 0
THRESHOLD = 3

def load_user(username):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(base_dir, "profiles", f"{username}.json")

    with open(profile_path) as f:
        profile = json.load(f)

    model = joblib.load(profile["model"])
    scaler = joblib.load(profile["scaler"])

    return model, scaler

username = input("Enter username: ")
model, scaler = load_user(username)

print("Real-time monitoring started...")

def on_press(key):
    try:
        k = key.char
    except:
        return

    press_times[k] = time.time()
    typed_keys.append((k, "press", time.time()))

def on_release(key):
    global ANOMALY_COUNT

    try:
        k = key.char
    except:
        return

    typed_keys.append((k, "release", time.time()))

    if len(typed_keys) >= 20:
        features = extract_features()

        df = pd.DataFrame([features])
        X_scaled = scaler.transform(df)

        prediction = model.predict(X_scaled)

        if prediction[0] == -1:
            ANOMALY_COUNT += 1
            print(f"⚠️ anomaly detected ({ANOMALY_COUNT})")

            if ANOMALY_COUNT >= THRESHOLD:
                print("🚨 INTRUDER ALERT!")
        else:
            ANOMALY_COUNT = 0
            print("✅ normal typing")

        typed_keys.clear()

def extract_features():
    dwell = []
    flight = []

    last_release = None

    for i in range(len(typed_keys)):
        key, action, t = typed_keys[i]

        if action == "press":
            press_t = t

        elif action == "release":
            release_t = t

            dwell.append(release_t - press_t)

            if last_release is not None:
                flight.append(press_t - last_release)

            last_release = release_t

    return dwell + flight

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()