import streamlit as st
import io
import json
import random
from PIL import Image
from datetime import datetime
from google import genai
from google.genai import types
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import alerts

# ==============================
# ⚙️ PAGE CONFIGURATION
# ==============================
st.set_page_config(
    page_title="AgriVue | Loss Adjustment",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# 🎨 LUXURY TECH STYLING
# ==============================
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
        font-size: 2rem !important;
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
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4) !important;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input {
        background: rgba(0,0,0,0.5) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        color: #fff !important;
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 🔐 SYSTEM CREDENTIALS
# ==============================
API_KEY = "AIzaSyC3KJotknWSN2_gYCL2wI_nCzgSehtM648"
client = genai.Client(api_key=API_KEY)

# ==============================
# 📱 SIDEBAR & HUD
# ==============================
st.sidebar.markdown("<h2>Claim Parameters</h2>", unsafe_allow_html=True)

DEMO_MODE = st.sidebar.toggle("Simulated Assessor Mode", value=False)

st.sidebar.markdown("### Asset Details")
crop_name = st.sidebar.text_input("Commodity Type", value="Wheat")
total_area_ha = st.sidebar.number_input("Total Insured Area (Hectares)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)

st.sidebar.markdown("### Financial Baselines")
expected_yield_q_per_ha = st.sidebar.number_input("Expected Yield (Quintal/Ha)", min_value=1.0, max_value=200.0, value=35.0, step=1.0)
expected_price_rs_per_q = st.sidebar.number_input("Market Rate (₹/Quintal)", min_value=100.0, max_value=10000.0, value=2200.0, step=50.0)

# ==============================
# 🌍 MAIN DASHBOARD
# ==============================
st.markdown("<h1>Automated Loss Adjustment</h1>", unsafe_allow_html=True)
st.caption("AI DAMAGE QUANTIFICATION • FINANCIAL IMPACT MODELING • PMFBY COMPLIANCE")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. Pre-Event Baseline")
    before_img = st.file_uploader("Upload BEFORE Damage Image", type=["jpg", "jpeg", "png"], key="before")

with col2:
    st.markdown("### 2. Post-Event Assessment")
    after_img = st.file_uploader("Upload AFTER Damage Image", type=["jpg", "jpeg", "png"], key="after")

# Helper for UI layout
def metric_row(label, value, help_text=None):
    st.markdown(f"**{label}:** <span style='color:#d4af37;'>{value}</span>", unsafe_allow_html=True)
    if help_text:
        st.caption(help_text)

# ==============================
# 🧠 AI PROCESSING ENGINE
# ==============================
if before_img and after_img:
    before_bytes = before_img.getvalue()
    after_bytes = after_img.getvalue()

    # PIL Images to pass directly to Gemini
    before_image = Image.open(io.BytesIO(before_bytes))
    after_image = Image.open(io.BytesIO(after_bytes))

    st.markdown("---")
    st.subheader("Visual Evidence Verification")
    c1, c2 = st.columns(2)
    c1.image(before_image, caption="Verified Baseline", use_container_width=True)
    c2.image(after_image, caption="Reported Damage", use_container_width=True)

    with st.spinner("Executing structural damage analysis via AgriVue AI..."):

        if DEMO_MODE:
            damage_pct = random.randint(30, 85)
            damage_data = {
                "damage_type": "Severe Waterlogging/Lodging",
                "damage_severity_pct": damage_pct,
                "salvageable": damage_pct < 55,
                "estimated_area_affected_ha": round(total_area_ha * damage_pct / 100.0, 2),
                "likely_cause": "Intense localized precipitation leading to structural crop failure.",
                "risk_of_secondary_issues": "High risk of fungal rot due to prolonged moisture exposure.",
                "recommended_farmer_actions": [
                    "Isolate the affected area by digging temporary drainage trenches.",
                    "Document all angles of the field using the AgriVue mobile application.",
                    "Do not harvest or clear the field until the official adjuster physically verifies the claim."
                ],
                "required_documents_for_claim": [
                    "Aadhaar Card & Bank Passbook",
                    "Khasra/Khatauni (Land Ownership Records)",
                    "Crop Sowing Certificate (Issued by Patwari)",
                    "Premium Deduction Receipt (Bank Statement)"
                ],
                "followup_next_7_days": "Monitor root integrity. If soil remains saturated for 72+ hours, assume 100% yield loss in affected sectors.",
                "summary": "Critical structural failure detected in crop canopy. High probability of yield loss exceeding insurance thresholds."
            }
        else:
            try:
                schema = {
                    "type": "object",
                    "properties": {
                        "damage_type": {"type": "string"},
                        "damage_severity_pct": {"type": "number"},
                        "salvageable": {"type": "boolean"},
                        "estimated_area_affected_ha": {"type": "number"},
                        "likely_cause": {"type": "string"},
                        "risk_of_secondary_issues": {"type": "string"},
                        "recommended_farmer_actions": {"type": "array", "items": {"type": "string"}},
                        "required_documents_for_claim": {"type": "array", "items": {"type": "string"}},
                        "followup_next_7_days": {"type": "string"},
                        "summary": {"type": "string"}
                    },
                    "required": ["damage_type", "damage_severity_pct", "salvageable", "estimated_area_affected_ha", "likely_cause", "risk_of_secondary_issues", "recommended_farmer_actions", "required_documents_for_claim", "followup_next_7_days", "summary"]
                }

                prompt = f"""
                You are a senior, highly analytical Crop Insurance Adjuster for the PMFBY (Pradhan Mantri Fasal Bima Yojana).
                The asset is {crop_name} spanning {total_area_ha} hectares.

                Compare the BEFORE (baseline) and AFTER (post-event) images.
                Provide a highly professional, clinical assessment of the damage. 
                Estimate the severity percentage strictly based on visual canopy/structural degradation.
                Your tone must be objective, financial, and executive. Ensure recommendations are legally and agriculturally sound.
                """

                # THE FIX: Pass prompt and raw PIL Images directly in the list
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        prompt,
                        before_image,
                        after_image
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema
                    ),
                )
                
                # Strip Markdown backticks so JSON loads perfectly every time
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                damage_data = json.loads(clean_json)

            except Exception as e:
                st.error(f"Neural processing failure: {e}")
                st.stop()

    # ---------------- YIELD & FINANCIAL CALCULATIONS ----------------
    damage_pct = float(damage_data.get("damage_severity_pct", 0))
    damage_fraction = max(0.0, min(damage_pct / 100.0, 1.0))
    damaged_area_ha = min(damage_data.get("estimated_area_affected_ha", total_area_ha * damage_fraction), total_area_ha)

    normal_yield_q = total_area_ha * expected_yield_q_per_ha
    expected_income_rs = normal_yield_q * expected_price_rs_per_q
    estimated_yield_loss_q = normal_yield_q * damage_fraction
    estimated_income_loss_rs = estimated_yield_loss_q * expected_price_rs_per_q

    if damage_pct < 20:
        insurance_eligible = "Unlikely (Below Threshold)"
        claim_urgency = "Standard Monitoring"
        suggested_claim_window_days = 7
    elif damage_pct < 50:
        insurance_eligible = "Probable (Requires Physical Audit)"
        claim_urgency = "Elevated"
        suggested_claim_window_days = 3
    else:
        insurance_eligible = "Highly Probable (Exceeds Threshold)"
        claim_urgency = "CRITICAL"
        suggested_claim_window_days = 2

    # Inject variables into the dictionary so the PDF can find it
    damage_data.update({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estimated_income_loss_rs": estimated_income_loss_rs,
        "estimated_yield_loss_q": estimated_yield_loss_q,
        "insurance_eligible": insurance_eligible,
        "claim_urgency": claim_urgency,
        "damaged_area_ha_final": round(damaged_area_ha, 2) 
    })

    # ---------------- UI DASHBOARD RENDER ----------------
    st.markdown("---")
    st.markdown("<h2>Executive Damage Report</h2>", unsafe_allow_html=True)
    
    st.info(f"**AI Adjuster Summary:** {damage_data.get('summary', 'Analysis completed.')}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Structural Damage", f"{damage_pct}%")
    m2.metric("Affected Area", f"{damaged_area_ha:.2f} Ha")
    m3.metric("Est. Yield Loss", f"{estimated_yield_loss_q:.1f} Qtl")
    m4.metric("Financial Exposure", f"₹ {estimated_income_loss_rs:,.0f}")

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 📋 Claim Viability")
        metric_row("Event Classification", damage_data.get("damage_type", "Unknown"))
        metric_row("Salvage Potential", "Viable" if damage_data.get("salvageable", False) else "Non-Viable")
        metric_row("Claim Eligibility", insurance_eligible)
        metric_row("Filing Urgency", claim_urgency)
        metric_row("Mandatory Filing Window", f"Within {suggested_claim_window_days} Days")
        
        st.markdown("<br>### 📂 Required Compliance Documents", unsafe_allow_html=True)
        for d in damage_data.get("required_documents_for_claim", ["Standard KYC documents required."]):
            st.markdown(f"🔸 {d}")

    with col_b:
        st.markdown("### 🛡️ Mitigation Directives")
        st.markdown("**Immediate Actions:**")
        for a in damage_data.get("recommended_farmer_actions", ["Contact local authorities."]):
            st.markdown(f"🔹 {a}")
            
        st.markdown("<br>**Secondary Risks & Monitoring (7-Day Outlook):**", unsafe_allow_html=True)
        st.warning(damage_data.get("risk_of_secondary_issues", "Monitor field conditions continuously."))
        st.write(damage_data.get("followup_next_7_days", ""))

    # ---------------- PDF GENERATION (PROFESSIONAL FORMAT) ----------------
    # Bulletproofed PDF logic using .get() to prevent KeyErrors
    def generate_pdf(data: dict) -> str:
        filename = "AgriVue_Official_Loss_Report.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Safe extractions to prevent formatting crashes
        yield_loss = data.get('estimated_yield_loss_q', 0.0)
        income_loss = data.get('estimated_income_loss_rs', 0.0)
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 50, "AGRIVUE COMMAND CENTER")
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 65, "Official AI Loss Adjustment & Claim Report")
        c.drawString(40, height - 80, f"Generated: {data.get('timestamp', 'N/A')}")
        
        # Divider Line
        c.setLineWidth(1)
        c.line(40, height - 90, width - 40, height - 90)
        
        # Asset Details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, height - 120, "1. ASSET & LOCATION DETAILS")
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 140, f"Commodity: {crop_name}")
        c.drawString(40, height - 155, f"Total Insured Area: {total_area_ha} Hectares")
        
        # Financial Impact
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, height - 190, "2. FINANCIAL IMPACT ASSESSMENT")
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 210, f"Baseline Yield (Est.): {int(normal_yield_q)} Quintals")
        c.drawString(40, height - 225, f"Yield Loss (Est.): {yield_loss:.1f} Quintals")
        c.drawString(40, height - 240, f"Total Financial Exposure: INR {income_loss:,.2f}")
        
        # AI Damage
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, height - 275, "3. AI STRUCTURAL ANALYSIS")
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 295, f"Primary Cause: {data.get('damage_type', 'N/A')}")
        c.drawString(40, height - 310, f"Severity Assessment: {data.get('damage_severity_pct', 0)}% Structural Loss")
        c.drawString(40, height - 325, f"Affected Area: {data.get('damaged_area_ha_final', 'N/A')} Hectares")
        c.drawString(40, height - 340, f"Salvage Potential: {'Viable' if data.get('salvageable', False) else 'Non-Viable'}")
        
        # Claim Actions
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, height - 375, "4. CLAIM COMPLIANCE DIRECTIVES")
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 395, f"Eligibility Probability: {data.get('insurance_eligible', 'N/A')}")
        c.drawString(40, height - 410, f"Action Window: Must file within {suggested_claim_window_days} Days")
        
        y_pos = height - 435
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y_pos, "Required Documentation:")
        y_pos -= 15
        c.setFont("Helvetica", 10)
        for d in data.get("required_documents_for_claim", []):
            c.drawString(50, y_pos, f"- {d}")
            y_pos -= 15

        y_pos -= 15
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y_pos, "Executive Summary:")
        y_pos -= 15
        c.setFont("Helvetica", 10)
        
        # Word wrap for summary
        import textwrap
        wrapped_summary = textwrap.wrap(data.get("summary", "N/A"), width=90)
        for line in wrapped_summary:
            c.drawString(50, y_pos, line)
            y_pos -= 15
            
        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(40, 40, "This report is generated by AgriVue AI. Physical verification by an authorized adjuster is required for claim disbursement.")

        c.save()
        return filename

    st.markdown("<br>", unsafe_allow_html=True)
    pdf_file = generate_pdf(damage_data)

    c1, c2 = st.columns([1, 3])
    with c1:
        st.download_button(
            "📄 DOWNLOAD OFFICIAL PDF",
            data=open(pdf_file, "rb").read(),
            file_name="AgriVue_Loss_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # ---------------- WHATSAPP ALERT ----------------
    try:
        alerts.monitor_and_alert(
            "Loss Adjustment Module",
            {
                "rain_prob": "Low", # Bypassing weather alerts in alerts.py
                "wind_speed": "Calm",
                "moisture_pct": 50,
                "summary": (
                    f"CROP LOSS RECORDED.\n"
                    f"Commodity: {crop_name} | Damage: {damage_pct}%\n"
                    f"Financial Exposure: INR {estimated_income_loss_rs:,.0f}\n"
                    f"Eligibility: {insurance_eligible}\n"
                    f"Action: Submit official PDF report to local FPO."
                )
            }
        )
        st.success("📲 Executive summary successfully routed via Twilio Secure Network.")
    except Exception as e:
        st.error("Could not transmit WhatsApp alert. Ensure Twilio server is online.")