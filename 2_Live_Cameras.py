import streamlit as st
import cv2
import time
import numpy as np
from datetime import datetime
from google import genai
from google.genai import types
from PIL import Image, ImageDraw
import io
import json
import streamlit.components.v1 as components
from twilio.rest import Client

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AgriVue Live Cameras",
    page_icon="📡",
    layout="wide"
)

# ---------------- CUSTOM CSS (LUXURY AESTHETIC) ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: radial-gradient(circle at top, #111a14 0%, #050706 100%);
        color: #f0f4f1;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #d4af37 !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-size: 2rem !important;
        font-family: 'Playfair Display', serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9ba8a0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    hr {
        border-color: rgba(212, 175, 55, 0.2);
    }
</style>
""", unsafe_allow_html=True)

API_KEY = "AIzaSyCNT1doxoqbi8xJYFUn1c1a95jSovW_oHk"
MODEL = "gemini-2.5-flash"
client = genai.Client(api_key=API_KEY)

# ---------------- TWILIO WHATSAPP ----------------
TWILIO_SID = "AC5fc5c6ad85fb57f5318b0fd5c537d8ff"
TWILIO_TOKEN = "57d050eff73a193bf70e2861625b45ec"
WHATSAPP_FROM = "whatsapp:+14155238886"   # Twilio sandbox
WHATSAPP_TO = "whatsapp:+918872862277"    # user number

twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)

# ---------------- CAMERA STREAMS ----------------
CAMERAS = {
    "🌧 Sky Node (Rain)": "http://10.73.234.171:8080/video",
    "🌬 Wind Node (Movement)": "http://10.73.234.34:8080/video",
    "🌱 Soil Node": "http://10.73.234.96:8080/video",
    "🍃 Leaf Node (Stress)": "http://10.51.2.163:8080/video",
}

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙ Live Controls")
FPS = st.sidebar.slider("Refresh FPS", 1, 10, 3)
SNAPSHOT_INTERVAL_MIN = st.sidebar.slider("Snapshot interval (minutes)", 1, 30, 5)
MOTION_THRESHOLD = st.sidebar.slider("Motion sensitivity", 1000, 10000, 3500)
st.sidebar.info("📡 Live Feed • 🌬 Motion • 🧠 Gemini AI • 📲 WhatsApp")

# ---------------- UI ----------------
st.title("📡 AgriVue Live Farm Intelligence")
st.caption("Live Camera • Motion Detection • AI Alerts")

cols = st.columns(2)
cols += st.columns(2)

video_boxes = {}
motion_boxes = {}
ai_status_boxes = {}
ai_render_boxes = {}

for i, name in enumerate(CAMERAS.keys()):
    with cols[i]:
        st.subheader(name)
        video_boxes[name] = st.empty()
        motion_boxes[name] = st.empty()
        ai_status_boxes[name] = st.empty()
        ai_render_boxes[name] = st.empty()

# ---------------- HELPERS ----------------
def add_watermark(frame, text="AgriVue"):
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    draw.text(
        (10, img.height - 30),
        f"{text} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        fill=(255, 255, 255)
    )
    return np.array(img)

def analyze_with_gemini(image_bytes, node):
    prompt = (
        "You are an agricultural AI assistant. "
        f"Analyze this image from node: {node}. "
        "Return ONLY valid JSON with keys: "
        '{"rain_likelihood":"Low|Medium|High",'
        '"wind_level":"Calm|Moderate|Strong",'
        '"crop_stress":"Low|Medium|High",'
        '"summary":"short farmer-friendly sentence"}'
    )

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/jpeg"
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt, image_part]
    )

    text = response.text.strip()
    start, end = text.find("{"), text.rfind("}") + 1
    return json.loads(text[start:end])

# ---------------- UI CARD (UPDATED STYLING) ----------------
def render_ai_card(result):
    return f"""
    <div style="background: rgba(20, 30, 22, 0.6); border: 1px solid rgba(212, 175, 55, 0.3); 
                border-radius: 12px; padding: 16px; margin-top: 10px; backdrop-filter: blur(10px);">
        <div style="font-family: 'Playfair Display', serif; color: #d4af37; font-size: 1.1rem; margin-bottom: 12px; border-bottom: 1px solid rgba(212,175,55,0.2); padding-bottom: 5px;">
            Intelligence Report
        </div>
        <div style="display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap;">
            <span style="background: rgba(0,0,0,0.5); border: 1px solid #4CAF50; color: #4CAF50; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem;">
                🌧 Rain: {result.get('rain_likelihood', 'N/A')}
            </span>
            <span style="background: rgba(0,0,0,0.5); border: 1px solid #2196F3; color: #2196F3; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem;">
                🌬 Wind: {result.get('wind_level', 'N/A')}
            </span>
            <span style="background: rgba(0,0,0,0.5); border: 1px solid #FF9800; color: #FF9800; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem;">
                🌱 Stress: {result.get('crop_stress', 'N/A')}
            </span>
        </div>
        <div style="color: #9ba8a0; font-size: 0.9rem; line-height: 1.5;">
            <strong style="color: #f0f4f1;">Analysis:</strong> {result.get('summary', 'N/A')}
        </div>
    </div>
    """

# ---------------- WHATSAPP MESSAGE ----------------
def send_whatsapp(node, result):
    message = (
        f"📡 AgriVue Alert\n\n"
        f"📍 {node}\n"
        f"🌧 Rain: {result['rain_likelihood']}\n"
        f"🌬 Wind: {result['wind_level']}\n"
        f"🌱 Stress: {result['crop_stress']}\n\n"
        f"🧠 {result['summary']}"
    )

    twilio_client.messages.create(
        from_=WHATSAPP_FROM,
        to=WHATSAPP_TO,
        body=message
    )

# ---------------- STATE ----------------
last_snapshot = {k: 0.0 for k in CAMERAS}
prev_gray = {}
snapshot_interval_sec = SNAPSHOT_INTERVAL_MIN * 60

# ---------------- MAIN LOOP ----------------
while True:
    for node, url in CAMERAS.items():

        with video_boxes[node]:
            components.html(f'<img src="{url}" width="100%">', height=320)

        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = add_watermark(frame, node)

        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        motion = 0
        if node in prev_gray:
            motion = int(np.sum(cv2.absdiff(prev_gray[node], gray)))
        prev_gray[node] = gray

        motion_boxes[node].metric("🌬 Motion", min(100, motion // 500))

        now = time.time()
        if now - last_snapshot[node] > snapshot_interval_sec or motion > MOTION_THRESHOLD:
            last_snapshot[node] = now

            buf = io.BytesIO()
            Image.fromarray(frame).save(buf, format="JPEG")

            ai_status_boxes[node].info("🧠 AI analysing snapshot…")
            result = analyze_with_gemini(buf.getvalue(), node)

            # ✅ SHOW CLEAN UI
            ai_render_boxes[node].markdown(
                render_ai_card(result),
                unsafe_allow_html=True
            )

            # ✅ SEND WHATSAPP (NO JSON SHOWN)
            send_whatsapp(node, result)

    time.sleep(1 / FPS)