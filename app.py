"""
Kenya Coordination Cascade — demonstration of how drought signals
flow through East Africa's coordination infrastructure.

Problem: A drought alert from wapimaji-mcp currently reaches no one else.
         This tool shows what should happen when coordination is connected.
"""
import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="Kenya Coordination Cascade",
    page_icon="🇰🇪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Mobile-first CSS ──────────────────────────────────────────
st.markdown("""
<style>
  .block-container { max-width: 600px; padding: 1rem; }
  .stButton > button { width: 100%; min-height: 44px; font-size: 1rem; }
  div[data-testid="stSelectbox"] { font-size: 1rem; }
  .cascade-box {
    background: #f0f8ff; border-left: 4px solid #2563eb;
    border-radius: 6px; padding: 12px 16px; margin: 8px 0;
    font-size: 0.9rem;
  }
  .alert-box {
    background: #fff7ed; border-left: 4px solid #ea580c;
    border-radius: 6px; padding: 12px 16px; margin: 8px 0;
  }
  .success-box {
    background: #f0fdf4; border-left: 4px solid #16a34a;
    border-radius: 6px; padding: 12px 16px; margin: 8px 0;
  }
</style>
""", unsafe_allow_html=True)

# ── Routing table (mirrors africa-coord-bus) ──────────────────
CASCADES = {
    "drought_alert": {
        "label": "🌵 Drought Alert",
        "source": "wapimaji-mcp",
        "description": "NDVI anomaly + SPI threshold crossed. Drought predicted 6-8 weeks ahead.",
        "min_severity": "warning",
        "actions": [
            {"tool": "bima-mcp", "action": "evaluate_parametric_payout",
             "description": "Checks insurance contract triggers. If SPI < -1.5, initiates payout.",
             "severity": "warning"},
            {"tool": "kilimo-mcp", "action": "issue_drought_advisory",
             "description": "Sends SMS advisory to registered farmers: crop calendar, drought-resistant varieties.",
             "severity": "warning"},
            {"tool": "soko-mcp", "action": "price_alert",
             "description": "Monitors maize price — drought typically causes 20-40% price spike in 4-6 weeks.",
             "severity": "warning"},
            {"tool": "afya-mcp", "action": "activate_malnutrition_watch",
             "description": "Activates CHW malnutrition surveillance. Drought → malnutrition in 6-10 weeks.",
             "severity": "alert"},
            {"tool": "county-mcp", "action": "alert_county_health",
             "description": "County health officer notified. Early procurement of nutrition supplements.",
             "severity": "alert"},
        ]
    },
    "flood_alert": {
        "label": "🌊 Flood Alert",
        "source": "wapimaji-mcp",
        "description": "Flash flood risk detected from rainfall accumulation and terrain data.",
        "min_severity": "warning",
        "actions": [
            {"tool": "afya-mcp", "action": "waterborne_watch",
             "description": "Activates cholera/typhoid surveillance. Flood → disease risk in 2-4 weeks.",
             "severity": "warning"},
            {"tool": "county-mcp", "action": "flood_response",
             "description": "County disaster management office notified. Evacuation routes reviewed.",
             "severity": "warning"},
        ]
    },
    "disease_outbreak": {
        "label": "🏥 Disease Outbreak",
        "source": "afya-mcp",
        "description": "CHW reports above-threshold disease cases in a sub-county.",
        "min_severity": "warning",
        "actions": [
            {"tool": "wapimaji-mcp", "action": "flag_water_risk",
             "description": "Water quality inspection triggered (cholera/typhoid are waterborne).",
             "severity": "alert", "condition": "cholera or typhoid"},
            {"tool": "county-mcp", "action": "health_alert",
             "description": "County health officer notified with case count and location.",
             "severity": "warning"},
            {"tool": "fomu-mcp", "action": "emergency_procurement",
             "description": "Emergency medicine procurement request generated.",
             "severity": "alert"},
        ]
    },
    "price_spike": {
        "label": "📈 Maize Price Spike",
        "source": "soko-mcp",
        "description": "Market price >30% above seasonal mean — food security stress signal.",
        "min_severity": "warning",
        "actions": [
            {"tool": "afya-mcp", "action": "food_security_watch",
             "description": "CHWs asked to track household food security in market-connected areas.",
             "severity": "warning"},
            {"tool": "bima-mcp", "action": "food_security_eval",
             "description": "Evaluates food security insurance triggers if contract exists.",
             "severity": "warning"},
        ]
    }
}

COUNTIES = [
    "Turkana (23)", "Marsabit (22)", "Wajir (37)", "Mandera (29)", "Garissa (9)",
    "Tana River (28)", "Kilifi (25)", "Kwale (17)", "Embu (8)", "Meru (12)",
    "Kitui (15)", "Machakos (10)", "Makueni (11)", "Kajiado (21)", "Narok (33)",
    "Kisumu (19)", "Homa Bay (14)", "Siaya (32)", "Migori (30)", "Kisii (20)",
    "Nakuru (32)", "Nyandarua (7)", "Nyeri (6)", "Kirinyaga (4)", "Laikipia (24)",
]

SEVERITY_COLORS = {
    "info":     "🔵",
    "warning":  "🟡",
    "alert":    "🔴",
    "critical": "🚨",
}

# ── UI ────────────────────────────────────────────────────────
st.title("🇰🇪 Kenya Coordination Cascade")
st.caption(
    "Shows how a coordination signal from one domain flows to all others "
    "that need to respond. The problem this solves: 31 AI tools for Kenya "
    "currently operate in isolation."
)

st.divider()

col1, col2 = st.columns([3, 2])
with col1:
    event_key = st.selectbox(
        "Signal type",
        options=list(CASCADES.keys()),
        format_func=lambda k: CASCADES[k]["label"]
    )
with col2:
    severity = st.selectbox(
        "Severity",
        ["warning", "alert", "critical"],
        index=1
    )

county_raw = st.selectbox("County", COUNTIES, index=0)
county = county_raw.split(" (")[0]

cascade = CASCADES[event_key]

with st.expander("Signal details", expanded=True):
    st.markdown(f"**Source tool:** `{cascade['source']}`")
    st.markdown(f"**Event:** `{event_key}`")
    st.markdown(f"**Description:** {cascade['description']}")

if st.button("▶ Run coordination cascade", type="primary"):
    st.divider()
    st.markdown(f"### Cascade: {cascade['label']} in {county}")
    st.markdown(f"*{datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC · Severity: {SEVERITY_COLORS.get(severity, '⚪')} {severity.upper()}*")

    severity_rank = ["info", "warning", "alert", "critical"]

    triggered = [a for a in cascade["actions"]
                 if severity_rank.index(severity) >= severity_rank.index(a["severity"])]
    deferred  = [a for a in cascade["actions"]
                 if severity_rank.index(severity) < severity_rank.index(a["severity"])]

    st.markdown(f"**{len(triggered)} tools triggered · {len(deferred)} waiting for higher severity**")
    st.markdown("")

    for a in triggered:
        condition = f" *(if {a['condition']})*" if "condition" in a else ""
        st.markdown(
            f'<div class="cascade-box">'
            f'<b>{a["tool"]}</b> → <code>{a["action"]}</code>{condition}<br>'
            f'<span style="color:#555">{a["description"]}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    if deferred:
        st.markdown("")
        st.caption(f"⏸ {len(deferred)} additional actions trigger at higher severity:")
        for a in deferred:
            st.caption(f"  • `{a['tool']}.{a['action']}` — requires {a['severity']}")

    st.divider()
    st.markdown(
        '<div class="success-box">'
        '<b>Coordination complete.</b> In production, each action above calls '
        'the corresponding MCP server. All tools are live at '
        '<a href="https://pypi.org/user/gmahia/">pypi.org/user/gmahia</a>. '
        'Coordination routing via '
        '<a href="https://pypi.org/project/africa-coord-bus/">africa-coord-bus</a>.'
        '</div>',
        unsafe_allow_html=True
    )

st.divider()
with st.expander("About this tool"):
    st.markdown("""
East Africa's coordination infrastructure has 31 AI tools — for water, health,
agriculture, insurance, land, education, and more. They don't talk to each other.

**The gap:** A drought signal six weeks before visible crop failure is actionable.
Insurance should trigger. Farmers should receive advisories. Health workers should
prepare for malnutrition. None of this currently happens automatically.

**This demonstration** shows the coordination cascade that should fire. The routing
logic runs on [africa-coord-bus](https://github.com/gabrielmahia/africa-coord-bus) —
the open-source coordination event bus connecting the MCP server ecosystem.

All source code: [github.com/gabrielmahia](https://github.com/gabrielmahia)
""")
