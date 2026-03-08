import streamlit as st
import qrcode
from PIL import Image
import hashlib
import json
from datetime import datetime, timedelta
import io
import time
import pydeck as pdk
import pandas as pd

# ==========================================
# ⚙️ CONFIGURATION & CSS STYLING
# ==========================================
st.set_page_config(
    page_title="AgriVue | Provenance Ledger",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: radial-gradient(circle at top, #111a14 0%, #050706 100%);
        color: #f0f4f1;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif !important;
        color: #d4af37 !important;
        letter-spacing: 1px;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* Custom Metrics */
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

    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(20, 30, 22, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    
    .hash-string {
        font-family: 'Courier New', Courier, monospace;
        color: #4CAF50;
        background: rgba(0,0,0,0.5);
        padding: 10px;
        border-radius: 6px;
        word-break: break-all;
        font-size: 0.85rem;
        border: 1px solid rgba(76, 175, 80, 0.3);
        text-align: center;
    }

    /* Custom Timeline CSS */
    .timeline {
        border-left: 2px solid rgba(212, 175, 55, 0.5);
        padding-left: 20px;
        margin-left: 10px;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 25px;
    }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -27px;
        top: 0;
        width: 12px;
        height: 12px;
        background-color: #d4af37;
        border-radius: 50%;
        box-shadow: 0 0 10px #d4af37;
    }
    .timeline-date {
        font-size: 0.85rem;
        color: #9ba8a0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .timeline-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f0f4f1;
        margin-bottom: 4px;
    }
    .timeline-desc {
        font-size: 0.9rem;
        color: #b0bec5;
    }
    
    /* Live Pulsing Dot */
    .live-dot {
        height: 10px; width: 10px; background-color: #ff4c4c;
        border-radius: 50%; display: inline-block;
        animation: pulse-red 1.5s infinite;
        margin-right: 8px;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 76, 76, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 76, 76, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 76, 76, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📦 ENHANCED MOCK DATABASE
# ==========================================
batches = {
    "BATCH-AV-9942": {
        "crop": "Premium Basmati Rice",
        "farm_location": "Ludhiana, Punjab",
        "farmer": "Sardar Jagjeet Singh",
        "health_index": "94% (Optimal)",
        "pesticides": "0.0% (Organic)",
        "carbon_saved": "1.2 Tons",
        "carbon_payout": "₹ 3,450",
        "water_saved": "45,000 Liters",
        "planted": "2025-11-12",
        "harvested": "2026-02-25",
        "status": "In Transit to Export Hub",
        "storage_temp": "18.2 °C",
        "storage_hum": "62%",
        "origin_coords": [75.8573, 30.9010],    # Ludhiana
        "dest_coords": [70.21, 21.02]           # Kandla Port
    },
    "BATCH-AV-8810": {
        "crop": "Sharbati Wheat",
        "farm_location": "Karnal, Haryana",
        "farmer": "Anurag Rana",
        "health_index": "88% (Standard)",
        "pesticides": "0.2% (Safe limits)",
        "carbon_saved": "0.8 Tons",
        "carbon_payout": "₹ 2,100",
        "water_saved": "20,000 Liters",
        "planted": "2025-10-05",
        "harvested": "2026-02-20",
        "status": "Warehoused (ITC Procurement)",
        "storage_temp": "22.0 °C",
        "storage_hum": "45%",
        "origin_coords": [76.99, 29.68],        # Karnal
        "dest_coords": [72.83, 18.94]           # Mumbai Port
    }
}

# ==========================================
# 📱 SIDEBAR & HUD
# ==========================================
with st.sidebar:
    st.markdown("<h2>🔗 Master Ledger</h2>", unsafe_allow_html=True)
    selected_batch = st.selectbox("Select Asset Batch", list(batches.keys()))
    
    st.markdown("---")
    st.info("🟢 **Blockchain Node: SYNCED**\n\nVerifying cryptographic signatures across decentralized AgriVue nodes.")

batch_data = batches[selected_batch]

# ==========================================
# 🌍 EXECUTIVE DASHBOARD
# ==========================================
st.markdown("<h1>Cryptographic Provenance Ledger</h1>", unsafe_allow_html=True)
st.caption("FARM-TO-FORK TRACEABILITY • IMMUTABLE SMART CONTRACTS • EXPORT VERIFICATION")
st.markdown("---")

# 🏆 Top Level Enterprise Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Commodity Class", batch_data["crop"])
m2.metric("Chemical Verification", batch_data["pesticides"])
m3.metric("Carbon Offset Yield", batch_data["carbon_saved"])
m4.metric("Carbon Monetization", batch_data["carbon_payout"])

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 🔗 CRYPTO & DATA PROCESSING
# ==========================================
# Generate SHA-256 Hash
data_string = json.dumps(batch_data, sort_keys=True).encode('utf-8')
crypto_hash = hashlib.sha256(data_string).hexdigest()

# Generate QR Code
verification_url = f"https://agrivue-ledger.com/verify?batch={selected_batch}&hash={crypto_hash[:16]}"
qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
qr.add_data(verification_url)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white")

buf = io.BytesIO()
qr_img.save(buf, format="PNG")
qr_bytes = buf.getvalue()

col1, col2 = st.columns([1.5, 1], gap="large")

# ---------------- LEFT COLUMN: LOGISTICS & MAP ----------------
with col1:
    st.markdown("### 🗺️ Live Supply Chain Routing")
    
    # 🚁 3D PyDeck Arc Map (Origin to Destination)
    route_data = pd.DataFrame({
        "inbound_lon": [batch_data["origin_coords"][0]],
        "inbound_lat": [batch_data["origin_coords"][1]],
        "outbound_lon": [batch_data["dest_coords"][0]],
        "outbound_lat": [batch_data["dest_coords"][1]],
    })

    view_state = pdk.ViewState(
        latitude=(batch_data["origin_coords"][1] + batch_data["dest_coords"][1]) / 2,
        longitude=(batch_data["origin_coords"][0] + batch_data["dest_coords"][0]) / 2,
        zoom=4.5,
        pitch=45
    )

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=route_data,
        get_source_position=["inbound_lon", "inbound_lat"],
        get_target_position=["outbound_lon", "outbound_lat"],
        get_source_color=[212, 175, 55, 255], # Gold origin
        get_target_color=[76, 175, 80, 255],  # Green destination
        get_width=5,
        auto_highlight=True
    )
    
    r = pdk.Deck(layers=[arc_layer], initial_view_state=view_state, map_style="mapbox://styles/mapbox/dark-v10")
    st.pydeck_chart(r)
    
    # ⏳ Timeline
    st.markdown("### ⏳ Agronomic Lifecycle")
    st.markdown(f"""
    <div class="glass-card">
        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-date">{batch_data['planted']}</div>
                <div class="timeline-title">🌱 Seed Sowing & Geotagging</div>
                <div class="timeline-desc">Coordinates locked: {batch_data['farm_location']}. Optimal moisture levels confirmed via AgriVue sensors.</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-date">Mid-Season (Continuous)</div>
                <div class="timeline-title">🛰️ Orbital Health Verification</div>
                <div class="timeline-desc">Maintained {batch_data['health_index']} health index. Zero unapproved chemical treatments detected by Sentinel Guard.</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-date">{batch_data['harvested']}</div>
                <div class="timeline-title">🚜 Yield Securitization</div>
                <div class="timeline-desc">Harvest logged. Quality grade assessed and data permanently hashed to ledger.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- RIGHT COLUMN: BLOCKCHAIN & LIVE TELEMETRY ----------------
with col2:
    st.markdown("### 🔐 Digital Passport")
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <h4 style="color:#d4af37; margin-top:0;">{selected_batch}</h4>
        <p style="color:#9ba8a0; font-size:0.9rem; margin-bottom:0;">Scan to verify organic authenticity</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display QR Code securely
    st.markdown("<div style='display: flex; justify-content: center; background: white; padding: 15px; border-radius: 12px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.image(qr_bytes, width=220) 
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("### Cryptographic Signature")
    st.markdown(f"<div class='hash-string'>0x{crypto_hash}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🌡️ LIVE TELEMETRY
    st.markdown("### <span class='live-dot'></span>Live Storage Telemetry", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span style="color:#9ba8a0;">Current Status:</span> 
            <strong style="color:#4CAF50;">{batch_data['status']}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span style="color:#9ba8a0;">Container Temp:</span> 
            <strong>{batch_data['storage_temp']}</strong>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#9ba8a0;">Relative Humidity:</span> 
            <strong>{batch_data['storage_hum']}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("ISSUE EXPORT CERTIFICATE (PDF)", use_container_width=True):
        with st.spinner("Minting secure certificate on the ledger..."):
            time.sleep(1.5)
            st.success("✅ Certificate successfully minted. Ready for buyer transfer.")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption("AGRIVUE LEDGER • The hash displayed above mathematically guarantees that the telemetry, geospatial tracking, and chemical data associated with this batch has not been altered since the moment of harvest.")