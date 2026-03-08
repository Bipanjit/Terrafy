import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import json
import time

# =========================
# ⚙️ PAGE CONFIG & CSS
# =========================
st.set_page_config(
    page_title="AgriVue | Equipment Exchange",
    page_icon="🚜",
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
    
    h1, h2, h3 {
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
        font-size: 2.2rem !important;
        font-family: 'Playfair Display', serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9ba8a0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Custom Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #d4af37, #b8860b) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        padding: 0.75rem !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4) !important;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(0,0,0,0.5) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        color: #fff !important;
        border-radius: 6px;
    }
    
    /* Cards */
    .dashboard-card {
        background: rgba(20, 30, 22, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# 🔐 GEMINI CONFIG
# =========================
GEMINI_API_KEY = "AIzaSyCNT1doxoqbi8xJYFUn1c1a95jSovW_oHk"
MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# 🛠️ SAFE JSON EXTRACTOR
# =========================
def safe_json_from_text(text: str):
    if not text:
        raise ValueError("Empty AI response")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON found")
    json_str = text[start:end + 1]
    return json.loads(json_str)

# =========================
# 🧠 AI MARKETPLACE BRAIN
# =========================
def gemini_marketplace_brain(context):
    prompt = f"""
    You are an elite Agricultural Economist and Logistics AI powering the AgriVue Equipment Exchange.

    Context Parameters:
    {context}

    Your responsibilities:
    1. Determine the optimal strategic action (e.g., EXECUTE RENTAL, HOLD, NEGOTIATE).
    2. Analyze hyper-local equipment demand based on the season and crop.
    3. Generate a dynamically optimized rental price that maximizes ROI without exploiting the renter.
    4. Calculate the financial impact of the farmer's Trust/Reputation Score (discounts or premiums).
    5. Provide a hard financial breakdown (Estimated Cost, Projected Benefit, Net Impact in INR).
    6. Assign a system confidence score (0-100).

    Rules:
    - You must output ONLY valid JSON. No markdown formatting, no preambles.
    - Be highly analytical and use professional financial terminology.

    Required JSON format:
    {{
      "best_decision": "Short Actionable Command (e.g., PROCEED WITH RENTAL)",
      "price_reasoning": "Detailed economic justification for the price.",
      "demand_level": "Surge / Stable / Low",
      "optimized_price": "Numeric value only (e.g., 1250)",
      "reputation_effect": "Explanation of how the score affected the price.",
      "estimated_cost": "Numeric value only (total cost)",
      "estimated_benefit": "Numeric value only (projected return)",
      "net_impact": "Numeric value only (benefit - cost)",
      "confidence_score": 95,
      "one_line_advice": "High-impact executive summary."
    }}
    """
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])]
        )
        return response.text
    except Exception as e:
        return None

# =========================
# 🌍 MAIN UI DASHBOARD
# =========================
st.markdown("<h1>AgriVue | Equipment Exchange</h1>", unsafe_allow_html=True)
st.caption("AI-POWERED DYNAMIC PRICING • TRUST-BASED LOGISTICS • ROI OPTIMIZATION")
st.markdown("---")

# ---------------- INPUT PANEL ----------------
st.markdown("### 🎛️ Asset & Contract Parameters")
with st.container(border=True):
    in_col1, in_col2, in_col3, in_col4 = st.columns(4)
    with in_col1:
        equipment = st.selectbox("Asset Type", ["Tractor (50HP+)", "Rotavator", "Boom Sprayer", "Combine Harvester", "Seed Drill"])
        crop = st.selectbox("Target Commodity", ["Wheat", "Rice", "Maize", "Cotton", "Sugarcane"])
    with in_col2:
        season = st.selectbox("Current Phase", ["Land Preparation", "Sowing", "Crop Maintenance", "Harvesting"])
        urgency = st.selectbox("Demand Velocity", ["Standard", "Urgent (Within 24h)", "Critical (Immediate)"])
    with in_col3:
        base_price = st.number_input("Market Baseline (₹/Hr)", min_value=100, value=800, step=50)
        hours = st.number_input("Contract Duration (Hrs)", min_value=1, value=8)
    with in_col4:
        st.markdown("<br>", unsafe_allow_html=True)
        reputation_score = st.slider("Counterparty Trust Score", 0, 100, 85, help="Based on past AgriVue transactions")

st.markdown("<br>", unsafe_allow_html=True)
execute_btn = st.button("INITIALIZE DYNAMIC PRICING ENGINE", use_container_width=True)

# =========================
# 🚀 AI EXECUTION & OUTPUT
# =========================
if execute_btn:
    context = f"""
    Crop: {crop} | Phase: {season} | Asset: {equipment}
    Market Baseline: ₹{base_price}/hour | Duration: {hours} hours
    Velocity: {urgency} | Counterparty Trust Score: {reputation_score}/100
    Current Month: {datetime.now().strftime('%B')}
    """

    with st.spinner("Quantum algorithms optimizing asset logistics and pricing..."):
        time.sleep(1) # Artificial delay for premium feel
        raw = gemini_marketplace_brain(context)
        
        try:
            data = safe_json_from_text(raw)
            
            # Format numbers safely
            opt_price = float(data.get("optimized_price", base_price))
            est_cost = float(data.get("estimated_cost", 0))
            est_benefit = float(data.get("estimated_benefit", 0))
            net_impact = float(data.get("net_impact", 0))
            
            st.markdown("---")
            st.markdown("<h2>Intelligence Readout</h2>", unsafe_allow_html=True)
            
            # Top Metric Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("System Directive", data.get("best_decision", "N/A"))
            m2.metric("Optimized Rate", f"₹ {opt_price:,.0f} / hr", f"{(opt_price - base_price):+,.0f} from baseline")
            m3.metric("Projected Net ROI", f"₹ {net_impact:,.0f}")
            m4.metric("Algorithm Confidence", f"{data.get('confidence_score', 0)}%")

            # Detailed Breakdown Columns
            r1, r2 = st.columns([2, 1])
            
            with r1:
                st.markdown(f"""
                <div class="dashboard-card">
                    <h3 style="margin-top:0; border-bottom:1px solid rgba(212,175,55,0.2); padding-bottom:10px;">Market Economics</h3>
                    <p><strong style="color:#d4af37;">Demand Velocity:</strong> {data.get('demand_level', 'N/A')}</p>
                    <p><strong style="color:#d4af37;">Pricing Rationale:</strong> {data.get('price_reasoning', 'N/A')}</p>
                    <p><strong style="color:#d4af37;">Trust Score Adjustment:</strong> {data.get('reputation_effect', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.info(f"**Executive Summary:** {data.get('one_line_advice', 'N/A')}")
                
            with r2:
                st.markdown(f"""
                <div class="dashboard-card">
                    <h3 style="margin-top:0; border-bottom:1px solid rgba(212,175,55,0.2); padding-bottom:10px;">Contract Ledger</h3>
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <span>Total Duration:</span> <strong>{hours} Hrs</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <span>Gross Liability:</span> <strong style="color:#ff4c4c;">₹ {est_cost:,.0f}</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <span>Gross Yield:</span> <strong style="color:#4CAF50;">₹ {est_benefit:,.0f}</strong>
                    </div>
                    <hr style="border-color: rgba(255,255,255,0.1);">
                    <div style="display:flex; justify-content:space-between; font-size:1.2rem;">
                        <span style="color:#d4af37;">NET IMPACT:</span> <strong style="color:#d4af37;">₹ {net_impact:,.0f}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Progress bar for confidence visually styled
                st.caption("AI Confidence Level")
                st.progress(int(data.get("confidence_score", 50)) / 100)
                
        except Exception as e:
            st.error(f"Marketplace Neural Engine Offline. Please verify API uplink. Error: {str(e)}")

# =========================
# FOOTER
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("AGRIVUE LOGISTICS • The data presented is generated by AI models and should be cross-referenced with local physical market conditions prior to finalizing financial contracts.")