import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

# ==========================================
# ⚙️ CONFIGURATION & CSS STYLING
# ==========================================
st.set_page_config(
    page_title="AgriVue | Market Intelligence",
    page_icon="📊",
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
    
    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(0,0,0,0.5) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        color: #fff !important;
        border-radius: 6px;
    }
    
    .arbitrage-card {
        background: rgba(20, 30, 22, 0.6);
        border: 1px solid #4CAF50;
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        border-left: 5px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# 🔑 CREDENTIALS
# -------------------------------
MANDI_API_KEY = "579b464db66ec23bdd0000013489abd871054a72531e1063c7f40b73"
OPENROUTER_API_KEY = "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"

# =====================================================
# 📍 LOCATION & TARGETING
# =====================================================
st.markdown("<h1>Commodities Exchange Terminal</h1>", unsafe_allow_html=True)
st.caption("HIGH-FREQUENCY MANDI TRACKING • SPATIAL ARBITRAGE • PREDICTIVE SENTIMENT")
st.markdown("---")

with st.sidebar:
    st.markdown("<h2>Targeting Parameters</h2>", unsafe_allow_html=True)
    st.info("Bypassing auto-geolocation for Hackathon Demo stability.")
    district = st.text_input("Enter District Name (e.g., Ludhiana, Pune, Bhopal)", value="Ludhiana")
    
    if not district:
        st.stop()

# =====================================================
# 📊 FETCH MANDI DATA (SAFE CACHED)
# =====================================================
@st.cache_data(ttl=300)
def fetch_mandi(district_name):
    url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={MANDI_API_KEY}&format=json&filters[district]={district_name.title()}&limit=1000"
    response = requests.get(url, headers={"User-Agent": "AgriVue"}, timeout=15)
    response.raise_for_status()
    return response.json()

with st.spinner(f"Establishing uplink with {district} wholesale markets..."):
    try:
        data = fetch_mandi(district)
    except Exception as e:
        st.error("Terminal offline. Unable to reach government market databases.")
        st.stop()

if "records" not in data or len(data["records"]) == 0:
    st.warning(f"No active trading data found for {district} in the current window.")
    st.stop()

df = pd.DataFrame(data["records"])
df["modal_price"] = pd.to_numeric(df["modal_price"], errors="coerce")
df["arrival_date"] = pd.to_datetime(df["arrival_date"], format="%d/%m/%Y", errors="coerce")
df = df.dropna(subset=["modal_price", "arrival_date"])

# =====================================================
# 📌 COMMODITY FILTER & GLOBAL METRICS
# =====================================================
commodity = st.sidebar.selectbox("Select Asset Class (Crop)", sorted(df["commodity"].unique()))
df_crop = df[df["commodity"] == commodity]

if df_crop.empty:
    st.warning("Insufficient liquidity for this asset class.")
    st.stop()

current_avg_price = df_crop['modal_price'].mean()
max_price = df_crop['modal_price'].max()
min_price = df_crop['modal_price'].min()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Asset Class", commodity)
m2.metric("Current Regional Avg", f"₹ {current_avg_price:,.0f} / Qtl")
m3.metric("30-Day High", f"₹ {max_price:,.0f} / Qtl")
m4.metric("Active Market Hubs", df_crop["market"].nunique())

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# 🚨 KILLER FEATURE 1: THE ARBITRAGE ENGINE
# =====================================================
st.markdown("### 🗺️ Spatial Arbitrage Scanner")
st.caption("Identifies price discrepancies between local markets to maximize farmer profit margins.")

market_stats = df_crop.groupby('market')['modal_price'].mean().reset_index()
best_market = market_stats.loc[market_stats['modal_price'].idxmax()]
worst_market = market_stats.loc[market_stats['modal_price'].idxmin()]
arbitrage_spread = best_market['modal_price'] - worst_market['modal_price']

if arbitrage_spread > 0:
    st.markdown(f"""
    <div class="arbitrage-card">
        <h3 style="margin-top:0; color:#4CAF50;">Arbitrage Opportunity Detected</h3>
        <p style="font-size: 1.1rem;">Divert transport of <strong>{commodity}</strong> to <strong style="color:#d4af37;">{best_market['market']} Mandi</strong>.</p>
        <div style="display:flex; justify-content:space-between; margin-top: 15px;">
            <div>
                <small style="color:#9ba8a0;">Max Sell Price</small><br>
                <strong style="font-size:1.5rem;">₹ {best_market['modal_price']:,.0f}</strong> ({best_market['market']})
            </div>
            <div>
                <small style="color:#9ba8a0;">Min Sell Price</small><br>
                <strong style="font-size:1.5rem; color:#ff4c4c;">₹ {worst_market['modal_price']:,.0f}</strong> ({worst_market['market']})
            </div>
            <div>
                <small style="color:#9ba8a0;">Potential Profit Margin</small><br>
                <strong style="font-size:1.5rem; color:#4CAF50;">+ ₹ {arbitrage_spread:,.0f} / Qtl</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Market prices are currently uniformly distributed. No significant arbitrage opportunities detected.")

# =====================================================
# 📈 KILLER FEATURE 2: VOLATILITY FORECASTING
# =====================================================
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### 📈 Price Volatility & Trend Forecast")
    
    trend_df = df_crop.groupby("arrival_date")["modal_price"].mean().reset_index().sort_values("arrival_date")
    
    if len(trend_df) > 5:
        # Linear Regression for trend
        X = np.arange(len(trend_df)).reshape(-1, 1)
        y = trend_df["modal_price"].values
        model = LinearRegression().fit(X, y)
        
        # Predict future trajectory
        future_X = np.arange(len(trend_df), len(trend_df) + 15).reshape(-1, 1)
        future_y = model.predict(future_X)
        future_dates = [trend_df["arrival_date"].iloc[-1] + timedelta(days=int(i)) for i in range(1, 16)]
        
        # Calculate simulated volatility (confidence interval)
        std_dev = np.std(y) * 0.5 
        upper_bound = future_y + std_dev
        lower_bound = future_y - std_dev

        fig = go.Figure()
        
        # Historical Data
        fig.add_trace(go.Scatter(x=trend_df["arrival_date"], y=trend_df["modal_price"], mode='lines+markers', name='Historical Rate', line=dict(color='#d4af37', width=2)))
        
        # Predictive Corridor (Shaded area)
        fig.add_trace(go.Scatter(x=future_dates + future_dates[::-1], y=list(upper_bound) + list(lower_bound)[::-1], fill='toself', fillcolor='rgba(76, 175, 80, 0.2)', line=dict(color='rgba(255,255,255,0)'), hoverinfo="skip", showlegend=True, name='Volatility Corridor'))
        
        # Future Trend Line
        fig.add_trace(go.Scatter(x=future_dates, y=future_y, mode='lines', name='AI Projection', line=dict(color='#4CAF50', width=2, dash='dot')))
        
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient historical data to generate predictive models.")

# =====================================================
# 🧭 KILLER FEATURE 3: MARKET SENTIMENT GAUGE
# =====================================================
with c2:
    st.markdown("### 🧭 Market Sentiment")
    
    # Calculate if price is currently high or low relative to its recent extremes
    if max_price > min_price:
        sentiment_score = ((current_avg_price - min_price) / (max_price - min_price)) * 100
    else:
        sentiment_score = 50

    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = sentiment_score,
        title = {'text': "Sell Favorability", 'font': {'color': '#9ba8a0'}},
        number = {'suffix': "%", 'font': {'color': '#d4af37'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#d4af37"},
            'steps': [
                {'range': [0, 33], 'color': "rgba(255, 76, 76, 0.3)"},   # Red (Bad time to sell)
                {'range': [33, 66], 'color': "rgba(255, 152, 0, 0.3)"},  # Orange (Hold)
                {'range': [66, 100], 'color': "rgba(76, 175, 80, 0.3)"}  # Green (Strong Sell)
            ],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': sentiment_score}
        }
    ))
    fig_gauge.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

# =====================================================
# 🤖 AI FINANCIAL STRATEGIST
# =====================================================
st.markdown("---")
st.markdown("### 🧠 AI Commodities Strategist")

if st.button("GENERATE EXECUTIVE BRIEFING", use_container_width=True):
    prompt = f"""
    Act as an elite commodities trader advising a farmer.
    District: {district}
    Asset: {commodity}
    Current Regional Avg: ₹{int(current_avg_price)}
    Identified Arbitrage: Sell at {best_market['market']} for ₹{int(best_market['modal_price'])}

    Provide a highly professional, 4-bullet-point executive summary. 
    1. Financial Sentiment (Bullish/Bearish).
    2. Arbitrage Action (What they should do with the spatial price difference).
    3. Storage Advice (Should they sell now or warehouse it?).
    4. Macro Risk Factor.
    Do not use generic AI introductions. Be direct and authoritative.
    """

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "google/gemini-2.0-flash-lite-preview-02-05:free", "messages": [{"role": "user", "content": prompt}]}

    with st.spinner("Compiling quantitative financial briefing..."):
        try:
            ai_response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
            if ai_response.status_code == 200:
                explanation = ai_response.json()["choices"][0]["message"]["content"]
                st.info(explanation)
            else:
                st.error(f"Quant Engine Offline. HTTP {ai_response.status_code}")
        except Exception:
            st.error("Connection timeout. Quantitative engines unreachable.")