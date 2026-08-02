import requests
import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import FASTAPI_URL, DASHBOARD_URL

st.set_page_config(page_title="Password Risk Intelligence System", page_icon="🔐", layout="centered")

# Custom CSS (unchanged : this is the look & feel, not logic)

st.markdown(
    """
    <style>
        :root {
            --bg-main: #050805;
            --bg-card: #0b140f;
            --green-main: #00ff88;
            --text-main: #e6fff3;
            --text-muted: #8fbfa6;
        }
        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="block-container"] {
            margin: 0;
            background: radial-gradient(circle at top, #0f1f14, var(--bg-main)) !important;
            color: var(--text-main);
            font-family: 'Neo Sans', cursive, sans-serif;
        }
        #MainMenu, footer, header { visibility: hidden; }
        .dash-btn-wrap { text-align: center; margin-top: 90px; margin-bottom: 10px; }
        .dash-btn {
            display: inline-block; padding: 8px 15px; font-weight: bold; font-size: 12px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #04120a !important; border-radius: 999px; text-decoration: none !important;
            letter-spacing: 1px; transition: all 0.3s ease;
        }
        .dash-btn:hover { transform: translateY(-3px); box-shadow: 0 0 25px rgba(0,255,136,.8); }
        .pw-card {
            width: 520px; max-width: 92%; margin: 0 auto 60px auto; padding: 36px 40px;
            background: linear-gradient(180deg, #0e1c13, var(--bg-card));
            border-radius: 16px; border: 1px solid rgba(0, 255, 136, 0.18);
            box-shadow: 0 18px 50px rgba(0,0,0,.75), 0 0 24px rgba(0,255,136,.07);
        }
        .pw-title {
            text-align: center; color: var(--green-main); letter-spacing: 1px; margin-bottom: 26px;
            text-shadow: 0 0 10px rgba(0,255,136,.5); font-size: 1.3rem; font-weight: 700;
        }
        .pw-output {
            margin-top: 20px; padding: 20px; background: #07140e; border-radius: 12px;
            border: 1px solid rgba(0,255,136,.15); animation: fadeIn .4s ease;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
        .pw-output h3 { margin-top: 0; color: #fffffb; padding-bottom: 1px; }
        .pw-output p { font-size: .92rem; line-height: 1.6; color: var(--text-muted); margin: 10px 0; text-align: justify; }
        .risk-wrap { margin-top: 16px; padding: 14px 16px; border-radius: 12px; display: flex; flex-direction: column; gap: 8px; }
        .risk-label { align-self: flex-start; padding: 6px 14px; font-size: .75rem; font-weight: 700; letter-spacing: 1px; border-radius: 999px; text-transform: uppercase; }
        .sev-CRITICAL { border: 1px solid #ff2b2b; box-shadow: 0 0 18px rgba(255,43,43,.4); }
        .sev-CRITICAL .risk-label { background: #ff2b2b; color: #120202; animation: pulseCritical 1s infinite; }
        @keyframes pulseCritical { 0% { transform: translateX(0) scale(1); } 50% { transform: translateX(4px) scale(1.05); } 100% { transform: translateX(0) scale(1); } }
        .sev-HIGH { border: 1px solid #ff5a3d; }
        .sev-HIGH .risk-label { background: #ff5a3d; color: #1a0704; animation: slideWarn 1.5s ease-in-out infinite; }
        @keyframes slideWarn { 0% { transform: translateX(0); } 50% { transform: translateX(6px); } 100% { transform: translateX(0); } }
        .sev-MEDIUM { border: 1px solid #ffb84d; }
        .sev-MEDIUM .risk-label { background: #ffb84d; color: #1a1204; animation: floatSoft 3s ease-in-out infinite; }
        @keyframes floatSoft { 0% { transform: translateY(0); } 50% { transform: translateY(-2px); } 100% { transform: translateY(0); } }
        .sev-LOW { border: 1px solid var(--green-main); }
        .sev-LOW .risk-label { background: var(--green-main); color: #04120a; }
        .sev-UNKNOWN { border: 1px solid #ff9f43; }
        .sev-UNKNOWN .risk-label { background: #ff9f43; color: #1a0e02; }
        .scan-bar { height: 10px; background: #04130b; border-radius: 6px; overflow: hidden; margin: 2px 0; padding-top: 5px; }
        .scan-fill { height: 100%; width: 100%; background: linear-gradient(90deg, #00ff88, #00cc6a, #00ff88); background-size: 200% 100%; animation: scanGlow 3s linear infinite; }
        @keyframes scanGlow { from { background-position: 0% 0; } to { background-position: 200% 0; } }
        .metric-explain { font-size: .9rem; line-height: 1.65; color: #fffffb; margin: 8px 0 14px; opacity: .95; border-left: 2px solid #fffffb; padding-left: 12px; font-weight: bold; }
        [data-testid="stTextInput"] input { background: #07110c !important; border: 1px solid rgba(0,255,136,.3) !important; border-radius: 8px !important; color: var(--text-main) !important; padding: 12px !important; }
        [data-testid="stTextInput"] input:focus { outline: none !important; border-color: var(--green-main) !important; box-shadow: 0 0 10px rgba(0,255,136,.4) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

def risk_badge(severity: str, label: str, body: str) -> str:
    """Return the HTML for one coloured badge row."""
    return f"""
    <div class="risk-wrap sev-{severity}">
        <span class="risk-label">{label}</span>
        <span style="color:#c8e6d8; font-size:.88rem;">{body}</span>
    </div>
    """


SCAN_BAR = '<div class="scan-bar"><div class="scan-fill"></div></div>'


def metric_label(text: str) -> str:
    return f'<p class="metric-explain">{text}</p>'


def show(html: str) -> None:
    """Shortcut so we don't repeat unsafe_allow_html=True everywhere."""
    st.markdown(html, unsafe_allow_html=True)


RULE_SCORE_BUCKETS = [
    (3, "CRITICAL", "LOW", "Password meets very few security rules. Increase complexity significantly."),
    (5, "MEDIUM", "MODERATE", "Password meets basic security requirements. Further complexity recommended."),
    (7, "LOW", "GOOD", "Password follows most recommended security rules. Nearly optimal."),
    (8, "LOW", "EXCELLENT", "Password follows all recommended security rules. Well done."),
]

ENTROPY_BUCKETS = [
    (40, "CRITICAL", "VERY WEAK", "Entropy is critically low. Increase randomness urgently."),
    (60, "HIGH", "WEAK", "Entropy provides limited resistance to guessing attacks."),
    (80, "MEDIUM", "MODERATE", "Entropy is reasonable but not ideal for long-term security."),
    (float("inf"), "LOW", "STRONG", "Entropy is high under theoretical attack models."),
]


def pick_bucket(value: float, buckets: list[tuple]) -> tuple:
    """Return the first bucket whose upper bound is >= value."""
    for upper_bound, severity, label, text in buckets:
        if value <= upper_bound:
            return severity, label, text
    return buckets[-1][1:]  # fallback: last bucket


# Render one full result card

def render_results(r: dict) -> None:
    breaches = r["breaches"]
    rules = r["rules"]
    entropy = r["entropy"]
    risk = r["risk"]
    message = r["message"]

    header = "RESULTS (!Assessing Without Breach Data!)" if breaches == -1 else "RESULTS"
    show(f'<div class="pw-output"><h3>{header}</h3>')

    # Breach status
    if breaches == -1:
        show(risk_badge("UNKNOWN", "UNKNOWN", "Breach data unavailable (network or API failure)."))
    elif breaches > 0:
        show(risk_badge("CRITICAL", "BREACHES FOUND", f"Password has appeared {breaches:,} times in known breaches."))
    else:
        show(risk_badge("LOW", "NO BREACHES", "Password has not appeared in any known breaches."))
    show(SCAN_BAR)

    # Rule score
    show(metric_label(f"RULE SCORE: {rules} / 8"))
    severity, label, text = pick_bucket(rules, RULE_SCORE_BUCKETS)
    show(risk_badge(severity, label, text))
    show(SCAN_BAR)

    # Entropy
    show(metric_label(f"ENTROPY: {entropy} bits"))
    severity, label, text = pick_bucket(entropy, ENTROPY_BUCKETS)
    show(risk_badge(severity, label, text))
    show(SCAN_BAR)

    # Overall risk (comes from the backend)
    show(risk_badge(risk, f"{risk} RISK", message))
    show(SCAN_BAR)

    show("</div>")  # close .pw-output


# Page layout

show(f"""
<div class="dash-btn-wrap">
    <a href="{DASHBOARD_URL}" target="_blank" class="dash-btn">
        Telemetry and Analytics Dashboard
    </a>
</div>
""")

show('<div class="pw-title">PASSWORD RISK INTELLIGENCE SYSTEM</div>')

password = st.text_input(
    label="Password",
    type="password",
    placeholder="Enter password & press Enter…",
    label_visibility="collapsed",
)

# Call backend to render the result

if password:
    result = None
    with st.spinner("Analysing…"):
        try:
            response = requests.post(f"{FASTAPI_URL}/api/check-password", data={"password": password}, timeout=15)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.ConnectionError:
            st.error(f"⚠ Cannot reach the backend at **{FASTAPI_URL}**. Make sure FastAPI is running.")
        except requests.exceptions.Timeout:
            st.error("⚠ The request timed out. The breach API may be slow — try again.")
        except requests.exceptions.HTTPError as exc:
            detail = exc.response.json().get("detail", str(exc))
            st.error(f"⚠ Backend error: {detail}")
        except Exception as exc:
            st.error(f"⚠ Unexpected error: {exc}")

    if result:
        render_results(result)

show("</div>")  # close
