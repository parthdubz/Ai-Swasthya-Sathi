import cv2
import time
import serial
import threading
from flask import Flask, jsonify, make_response, Response
from flask_cors import CORS
import mediapipe as mp

# ================= CONFIG =================
ALERT_HOLD_TIME = 10  # seconds
SERIAL_PORT = "COM5"
BAUD_RATE = 115200

# ================= STATE =================
alert_state = "normal"
alert_start_time = 0
gesture_cooldown = 5
last_gesture_time = 0

# ================= FLASK SERVER =================
app = Flask(__name__)
CORS(app)

@app.route("/status")
def status():
    resp = make_response(jsonify({"state": alert_state}))
    resp.headers["Cache-Control"] = "no-store"
    return resp

# ---------- VIDEO STREAM ROUTE ----------
def generate_frames():
    global cap
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Encode frame
        ret, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def run_server():
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

threading.Thread(target=run_server, daemon=True).start()
print("📡 Flask server running on port 5001")

# ================= SERIAL =================
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("🔌 ESP Connected")
except:
    ser = None
    print("⚠️ Serial connection failed")

# ================= MEDIAPIPE =================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ================= CAMERA =================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not found")
    exit()

print("📷 Camera started")
print("✌️ V sign → ALERT\n")

# ================= GESTURE FUNCTION =================
def is_v_sign(lm):
    return (
        lm[8].y  < lm[6].y and   # index up
        lm[12].y < lm[10].y and  # middle up
        lm[16].y > lm[14].y and  # ring down
        lm[20].y > lm[18].y      # pinky down
    )

# ================= MAIN LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # ---- Detect gesture ----
    if result.multi_hand_landmarks:
        lm = result.multi_hand_landmarks[0].landmark
        if time.time() - last_gesture_time >= gesture_cooldown:
            if is_v_sign(lm):
                alert_state = "alert"
                alert_start_time = time.time()
                last_gesture_time = time.time()

                print("🚨 ALERT TRIGGERED")

                if ser:
                    ser.write(b"ALERT\n")

    # ---- Hold alert ----
    if alert_state == "alert":
        if time.time() - alert_start_time >= ALERT_HOLD_TIME:
            alert_state = "normal"
            print("✅ ALERT CLEARED")

            if ser:
                ser.write(b"NORMAL\n")

    # Optional: show local window
    cv2.imshow("Gesture Detection - YETI", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# ================= CLEANUP =================
cap.release()
if ser:
    ser.close()
cv2.destroyAllWindows()
