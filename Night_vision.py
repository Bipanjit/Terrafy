import streamlit as st
import cv2
import time
import numpy as np
import base64
from datetime import datetime
from ultralytics import YOLO

# ==========================================
# ⚙️ CONFIGURATION & CSS STYLING
# ==========================================
st.set_page_config(page_title="AgriVue | AI Sentinel", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: radial-gradient(circle at top, #0a0e0b 0%, #000000 100%);
        color: #f0f4f1;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #d4af37 !important;
        letter-spacing: 1px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-size: 2.5rem !important;
        font-family: 'Playfair Display', serif !important;
    }
    
    .threat-log {
        background: rgba(10, 14, 11, 0.9);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 8px;
        padding: 15px;
        height: 350px;
        overflow-y: auto;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
        color: #4CAF50;
    }

    @keyframes flash-critical {
        0% { background-color: rgba(255, 0, 0, 0.2); border: 2px solid #ff4c4c; box-shadow: 0 0 20px rgba(255,0,0,0.5); }
        50% { background-color: rgba(255, 0, 0, 0.6); border: 2px solid #ff0000; box-shadow: 0 0 40px rgba(255,0,0,0.8); }
        100% { background-color: rgba(255, 0, 0, 0.2); border: 2px solid #ff4c4c; box-shadow: 0 0 20px rgba(255,0,0,0.5); }
    }
    .alert-critical {
        animation: flash-critical 1s infinite;
        padding: 20px; border-radius: 12px; text-align: center;
        color: white; font-weight: 900; font-size: 1.5rem; letter-spacing: 2px;
    }

    @keyframes flash-elevated {
        0% { background-color: rgba(255, 152, 0, 0.2); border: 2px solid #FF9800; box-shadow: 0 0 20px rgba(255,152,0,0.3); }
        50% { background-color: rgba(255, 152, 0, 0.5); border: 2px solid #FF9800; box-shadow: 0 0 30px rgba(255,152,0,0.6); }
        100% { background-color: rgba(255, 152, 0, 0.2); border: 2px solid #FF9800; box-shadow: 0 0 20px rgba(255,152,0,0.3); }
    }
    .alert-elevated {
        animation: flash-elevated 1.5s infinite;
        padding: 20px; border-radius: 12px; text-align: center;
        color: white; font-weight: 800; font-size: 1.3rem; letter-spacing: 1px;
    }
    
    .alert-clear {
        background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50;
        padding: 20px; border-radius: 12px; text-align: center;
        color: #4CAF50; font-weight: 600; font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🧠 HIGH-ACCURACY AI INITIALIZATION
# ==========================================
@st.cache_resource
def load_model():
    # Upgraded to YOLOv8s (Small) for significantly better accuracy
    return YOLO("yolov8s.pt")

model = load_model()

# COCO Classes: 0: person, 15-24: animals (bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe)
HUMAN_CLASSES = [0]
ANIMAL_CLASSES = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
TARGET_CLASSES = HUMAN_CLASSES + ANIMAL_CLASSES

# ==========================================
# 🔊 STRICT AUDIO ENGINE
# ==========================================
if "last_human_alarm" not in st.session_state:
    st.session_state.last_human_alarm = 0
if "last_animal_alarm" not in st.session_state:
    st.session_state.last_animal_alarm = 0

def trigger_audio(threat_type, audio_placeholder):
    now = time.time()
    b64 = ""
    
    # 10-Second strict cooldown to prevent spam/overlap
    if threat_type == "HUMAN" and (now - st.session_state.last_human_alarm > 10):
        try:
            with open("human_sound.mp3", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            st.session_state.last_human_alarm = now
        except: pass
        
    elif threat_type == "ANIMAL" and (now - st.session_state.last_animal_alarm > 10):
        try:
            with open("animal_sound.mp3", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            st.session_state.last_animal_alarm = now
        except: pass

    if b64:
        audio_placeholder.markdown(
            f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
            unsafe_allow_html=True
        )

# ==========================================
# 🎨 MILITARY HUD DRAWING FUNCTION
# ==========================================
def draw_target_lock(img, x1, y1, x2, y2, color, label, track_id=""):
    thickness = 2
    length = 25
    
    # Sniper corners
    cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness)
    cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness)
    cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness)
    cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness)
    
    # Center Crosshair
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    cv2.drawMarker(img, (cx, cy), color, markerType=cv2.MARKER_CROSS, markerSize=15, thickness=1)
    
    # Label
    display_text = f"{label} ID:{track_id}" if track_id else label
    cv2.rectangle(img, (x1, y1 - 25), (x1 + len(display_text)*9, y1), color, -1)
    cv2.putText(img, display_text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

# ==========================================
# 📱 UI DASHBOARD & SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2>🛡️ Defense Matrix</h2>", unsafe_allow_html=True)
    camera_url = st.text_input("Camera Uplink URL/IP", value="http://192.168.29.154:8080/video")
    
    st.markdown("---")
    # Lower default threshold to catch more targets, the tracking algo will filter out noise
    conf_threshold = st.slider("Neural Confidence Threshold", 0.1, 1.0, 0.25)
    optics_mode = st.radio("Optics Filter", ["Standard RGB", "Thermal (FLIR)", "Night Vision (Green)"])
    
    st.markdown("---")
    col_start, col_stop = st.columns(2)
    start = col_start.button("🟢 ARM")
    stop = col_stop.button("🔴 DISARM")

if "system_armed" not in st.session_state:
    st.session_state.system_armed = False
if "incident_log" not in st.session_state:
    st.session_state.incident_log = []

if start: st.session_state.system_armed = True
if stop: st.session_state.system_armed = False

st.markdown("<h1>AI Sentinel Perimeter Guard</h1>", unsafe_allow_html=True)
st.caption("PERSISTENT OBJECT TRACKING • DYNAMIC GEOFENCING • AUTOMATED DETERRENTS")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Defense Status", "ARMED 🟢" if st.session_state.system_armed else "STANDBY 🟡")
m2.metric("Camera Feed", "ACTIVE" if st.session_state.system_armed else "OFFLINE")
m3.metric("Current Optics", optics_mode)
m4.metric("Recorded Incidents", len(st.session_state.incident_log))

feed_col, log_col = st.columns([2, 1])

with feed_col:
    frame_placeholder = st.empty()
    audio_placeholder = st.empty()

with log_col:
    st.markdown("### 🚨 Threat Status")
    alert_placeholder = st.empty()
    alert_placeholder.markdown("<div class='alert-clear'>🟢 PERIMETER SECURE</div>", unsafe_allow_html=True)
    
    st.markdown("### 📋 Security Event Log")
    log_placeholder = st.empty()

# ==========================================
# 🚀 CORE PROCESSING LOOP (TRACKING ENABLED)
# ==========================================
if "current_targets" not in st.session_state:
    st.session_state.current_targets = []

if st.session_state.system_armed:
    cap = cv2.VideoCapture(camera_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
    
    frame_skip = 2
    counter = 0
    prev_time = time.time()

    while st.session_state.system_armed:
        ret, frame = cap.read()
        if not ret:
            frame_placeholder.error("Uplink lost. Check camera IP.")
            time.sleep(1)
            continue

        frame = cv2.resize(frame, (800, 600))
        h, w, _ = frame.shape
        counter += 1
        
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # Define Geofence
        margin_x, margin_y = int(w * 0.15), int(h * 0.15)
        geo_x1, geo_y1, geo_x2, geo_y2 = margin_x, margin_y, w - margin_x, h - margin_y
        
        clean_ai_frame = frame.copy()

        if optics_mode == "Thermal (FLIR)":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)
        elif optics_mode == "Night Vision (Green)":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            zeros = np.zeros_like(gray)
            frame = cv2.merge([zeros, gray, zeros])

        threat_detected = None
        threat_level = "CLEAR"

        # --- YOLO PERSISTENT TRACKING ---
        if counter % frame_skip == 0:
            # Using model.track() instead of model(). It assigns IDs and tracks movement smoothly.
            results = model.track(clean_ai_frame, conf=conf_threshold, classes=TARGET_CLASSES, imgsz=640, persist=True, verbose=False)
            
            st.session_state.current_targets = []
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    track_id = int(box.id[0]) if box.id is not None else 0
                    st.session_state.current_targets.append((cls_id, x1, y1, x2, y2, track_id))

        # --- DRAW TARGETS & CHECK GEOFENCE ---
        for target in st.session_state.current_targets:
            cls_id, x1, y1, x2, y2, track_id = target
            
            # Improved Intersection Math: If ANY part of the bounding box touches the geofence
            in_zone = (x1 < geo_x2 and x2 > geo_x1 and y1 < geo_y2 and y2 > geo_y1)

            if in_zone:
                if cls_id in HUMAN_CLASSES:
                    threat_detected = "UNAUTHORIZED HUMAN"
                    threat_level = "CRITICAL"
                    color = (0, 0, 255) # Red
                else:
                    threat_detected = "WILDLIFE DETECTED"
                    threat_level = "ELEVATED"
                    color = (0, 165, 255) # Orange
                
                draw_target_lock(frame, x1, y1, x2, y2, color, threat_detected, str(track_id))
            else:
                # Target is outside the zone, draw it in grey so the user knows the AI sees it
                draw_target_lock(frame, x1, y1, x2, y2, (150, 150, 150), "APPROACHING ZONE", str(track_id))

        # Draw Geofence
        box_color = (0, 0, 255) if threat_detected else (0, 255, 0)
        cv2.rectangle(frame, (geo_x1, geo_y1), (geo_x2, geo_y2), box_color, 1)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"SYS: ACTIVE | OPTICS: {optics_mode.upper()} | FPS: {int(fps)}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"GEOFENCE: ARMED | TIME: {timestamp}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        frame_placeholder.image(frame, channels="BGR", use_container_width=True)

        # --- HANDLE ALERTS ---
        if threat_detected:
            audio_type = "HUMAN" if threat_level == "CRITICAL" else "ANIMAL"
            trigger_audio(audio_type, audio_placeholder)
            
            log_time = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{log_time}] {threat_level}: {threat_detected} breached Zone Alpha."
            if not st.session_state.incident_log or st.session_state.incident_log[0] != log_entry:
                st.session_state.incident_log.insert(0, log_entry)

            if threat_level == "CRITICAL":
                alert_placeholder.markdown(f"<div class='alert-critical'>🚨 CRITICAL BREACH: {threat_detected}<br><small>Deploying Security Measures</small></div>", unsafe_allow_html=True)
            else:
                alert_placeholder.markdown(f"<div class='alert-elevated'>⚠️ ELEVATED THREAT: {threat_detected}<br><small>Activating Repellent Protocols</small></div>", unsafe_allow_html=True)
        else:
            alert_placeholder.markdown("<div class='alert-clear'>🟢 PERIMETER SECURE<br><small>All nodes reporting normal</small></div>", unsafe_allow_html=True)
            audio_placeholder.empty()

        log_html = "<div class='threat-log'>" + "<br>".join(st.session_state.incident_log[:20]) + "</div>"
        log_placeholder.markdown(log_html, unsafe_allow_html=True)

    cap.release()
else:
    frame_placeholder.info("System Disarmed. Awaiting executive command.")