"""
AURA: Autonomous Universal Rescue & Astronaut-Health Agent
NASA International Space Apps Challenge Prototype
Target: NASA ExMC Gap Med10 — Computed Medical Decision Support

Avionics Glass-Cockpit & Tactical Flight Surgeon HUD
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engine.telemetry import TelemetryStream, SensorQualityGate
from engine.rules import DeterministicSafetyEngine
from engine.rag import GroundedMedicalRAG
from engine.tools import MedicalToolsRegistry
from engine.slm import ClinicalSLMEngine
from engine.agent import FlightSurgeonAgent

st.set_page_config(
    page_title="AURA // FLIGHT SURGEON HUD",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aerospace Glass-Cockpit Tactical HUD Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Global Dark Obsidian Palette */
    .stApp {
        background-color: #030712 !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* Monospace telemetry accents */
    .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Avionics HUD Metric Tile */
    .hud-tile {
        background: #0b0f19;
        border: 1px solid #1e293b;
        border-top: 2px solid #3b82f6;
        border-radius: 4px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .hud-tile-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 4px;
    }
    .hud-tile-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.1;
    }
    .hud-tile-delta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        margin-top: 4px;
    }
    .delta-alert { color: #f87171; }
    .delta-nominal { color: #34d399; }

    /* Tactical Alert Banners */
    .hud-alert-banner {
        font-family: 'JetBrains Mono', monospace;
        border-radius: 4px;
        padding: 14px 18px;
        margin-bottom: 16px;
        font-size: 0.88rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        line-height: 1.45;
        border: 1px solid transparent;
    }
    .hud-alert-emergency {
        background: rgba(127, 29, 29, 0.25);
        border-color: #ef4444;
        border-left: 5px solid #ef4444;
        color: #fecaca;
    }
    .hud-alert-watch {
        background: rgba(120, 53, 15, 0.25);
        border-color: #f59e0b;
        border-left: 5px solid #f59e0b;
        color: #fef3c7;
    }
    .hud-alert-nominal {
        background: rgba(6, 78, 59, 0.2);
        border-color: #10b981;
        border-left: 5px solid #10b981;
        color: #d1fae5;
    }

    /* Tactical Directive Card */
    .tactical-directive {
        background: #090d16;
        border: 1px solid #1e293b;
        border-left: 4px solid #38bdf8;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .tactical-directive-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #38bdf8;
    }
    .tactical-directive-msg {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 6px;
        line-height: 1.4;
    }

    /* Standardized Document Citation Pill */
    .doc-ref {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        background: #0f172a;
        color: #94a3b8;
        padding: 2px 7px;
        border-radius: 3px;
        border: 1px solid #334155;
        display: inline-block;
        margin-top: 3px;
    }

    /* Checklist Step Tile */
    .checklist-row {
        background: #0b0f19;
        border: 1px solid #1e293b;
        border-radius: 4px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }

    /* Streamlit widget tweaks */
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        padding: 8px 14px;
        border-radius: 4px 4px 0 0;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Core Engines
DATA_DIR = PROJECT_ROOT / "data"
thresholds_path = DATA_DIR / "nasa_std_3001_thresholds.json"
guidelines_path = DATA_DIR / "nasa_hrp_clinical_guidelines.json"

@st.cache_resource
def load_aura_engines():
    safety = DeterministicSafetyEngine(thresholds_path)
    rag = GroundedMedicalRAG(guidelines_path)
    tools = MedicalToolsRegistry(rag)
    slm = ClinicalSLMEngine()
    agent = FlightSurgeonAgent(safety, tools, slm)
    return safety, rag, tools, slm, agent

safety_engine, rag_engine, tools_registry, slm_engine, agent = load_aura_engines()

# ==========================================
# SIDEBAR: AVIONICS CONFIGURATION & LINK
# ==========================================
st.sidebar.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 1.15rem; font-weight: 800; letter-spacing: 0.08em; color: #f8fafc;">
    AURA // MISSION CONTROL
</div>
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; margin-bottom: 12px;">
    NASA SPACE APPS 2026 PROTOTYPE
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("**TARGET PROTOCOL:** `NASA ExMC Gap Med10 (Decision Support)`")

scenario_choice = st.sidebar.selectbox(
    "MISSION SCENARIO INGESTION",
    [
        "Scenario 1: Solar Particle Event (Lunar EVA)",
        "Scenario 2: ECLSS CO2 Scrubber Fault (Deep Space)",
        "Nominal Baseline Telemetry"
    ]
)

# Load Selected Scenario
if "Solar" in scenario_choice:
    scenario_file = DATA_DIR / "scenario_solar_radiation.json"
elif "CO2" in scenario_choice:
    scenario_file = DATA_DIR / "scenario_co2_hypercapnia.json"
else:
    scenario_file = DATA_DIR / "scenario_solar_radiation.json"

sim_stream = TelemetryStream(scenario_file)

# Telemetry Time Slider
max_step = sim_stream.total_steps() - 1
step_idx = st.sidebar.slider("TIMELINE STEP (MET INCREMENT)", 0, max_step, min(max_step, 6))
current_reading = sim_stream.seek(step_idx)
history = sim_stream.get_history(up_to_current=True)

st.sidebar.markdown("---")

# SLM Engine Status & 8GB RAM Configuration
st.sidebar.markdown("#### COMPUTATION NODE")
slm_status = slm_engine.check_environment()
st.sidebar.markdown(f"""
<div style="background: #090d16; border: 1px solid #1e293b; border-left: 3px solid #10b981; padding: 8px 10px; border-radius: 3px; font-family: 'JetBrains Mono', monospace; font-size: 0.76rem;">
    <div style="color: #64748b;">ACTIVE ENGINE:</div>
    <div style="color: #34d399; font-weight: 700;">{slm_status}</div>
    <div style="color: #94a3b8; font-size: 0.68rem; margin-top: 3px;">RAM FOOTPRINT: ≤ 1.4 GB (8GB SAFE)</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("#### UPLINK TELEMETRY STATUS")
st.sidebar.markdown("""
<div style="background: #090d16; border: 1px solid #1e293b; border-left: 3px solid #f59e0b; padding: 10px; border-radius: 3px; font-family: 'JetBrains Mono', monospace; font-size: 0.76rem;">
    <div style="color: #f59e0b; font-weight: 700;">SIGNAL LATENCY: 22m 14s</div>
    <div style="color: #94a3b8; margin-top: 3px;">Houston Telemedicine: OFFLINE</div>
    <div style="color: #38bdf8; font-weight: 700; margin-top: 3px;">EDGE AUTONOMOUS MODE: ARMED</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("#### FLIGHT DATA REPOSITORIES")
st.sidebar.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #64748b; line-height: 1.5;">
• NASA-STD-3001 Vol 1 & 2<br>
• HRP Evidence Report JSC-CN-35747<br>
• NASA OCHMO-TB-004<br>
• CCMC DONKI SEP Catalog<br>
• ISS CHeCS ACLS Clinical Set
</div>
""", unsafe_allow_html=True)

# ==========================================
# AVIONICS MASTER HEADER
# ==========================================
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
    <div style="display: flex; align-items: baseline; gap: 14px;">
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 900; letter-spacing: 0.05em; color: #f8fafc;">
            AURA // AUTONOMOUS FLIGHT SURGEON
        </span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #38bdf8; background: #0f172a; padding: 3px 8px; border: 1px solid #0284c7; border-radius: 3px;">
            LEVEL-IV AUTONOMY
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"OPERATIONAL SECTOR: {sim_stream.metadata.get('name', 'Deep Space Mission')} | LOC: {sim_stream.metadata.get('location', 'Lunar South Pole Shackleton Rim')}")
with col_h2:
    st.markdown(f"""
    <div style="text-align: right; font-family: 'JetBrains Mono', monospace;">
        <div style="font-size: 0.68rem; color: #64748b; text-transform: uppercase;">ASTRONAUT SUBJECT</div>
        <div style="font-size: 1.05rem; font-weight: 800; color: #f1f5f9;">{sim_stream.metadata.get('crew_member', 'CDR M. Vance')}</div>
    </div>
    """, unsafe_allow_html=True)

# Quality Gate Check
quality = SensorQualityGate.validate(current_reading)
if not quality["valid"]:
    st.markdown(f"""
    <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; padding: 8px 12px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #fca5a5; margin-bottom: 10px;">
        [SENSOR QUALITY FAULT] {', '.join(quality['issues'])}
    </div>
    """, unsafe_allow_html=True)

# Telemetry KPI Ribbon
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    hr = current_reading.get("heart_rate_bpm", 75)
    st.markdown(f"""
    <div class="hud-tile">
        <div class="hud-tile-label">HEART RATE</div>
        <div class="hud-tile-val">{hr} <span style="font-size: 0.85rem; color: #64748b;">BPM</span></div>
        <div class="hud-tile-delta {'delta-alert' if hr > 100 else 'delta-nominal'}">
            {'+' if hr > 72 else ''}{hr - 72} BPM REF
        </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    spo2 = current_reading.get("spo2_pct", 98.0)
    st.markdown(f"""
    <div class="hud-tile">
        <div class="hud-tile-label">SPO2 SATURATION</div>
        <div class="hud-tile-val">{spo2:.1f} <span style="font-size: 0.85rem; color: #64748b;">%</span></div>
        <div class="hud-tile-delta {'delta-alert' if spo2 < 95 else 'delta-nominal'}">
            {spo2 - 98.0:.1f}% BASELINE
        </div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    hrv = current_reading.get("hrv_rmssd_ms", 45.0)
    st.markdown(f"""
    <div class="hud-tile">
        <div class="hud-tile-label">AUTONOMIC STRAIN (HRV)</div>
        <div class="hud-tile-val">{hrv:.1f} <span style="font-size: 0.85rem; color: #64748b;">MS</span></div>
        <div class="hud-tile-delta {'delta-alert' if hrv < 25 else 'delta-nominal'}">
            RMSSD METRIC
        </div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    dose = current_reading.get("cumulative_dose_mSv", 2.0)
    st.markdown(f"""
    <div class="hud-tile" style="border-top-color: {'#ef4444' if dose >= 250 else ('#f59e0b' if dose >= 50 else '#3b82f6')};">
        <div class="hud-tile-label">CUMULATIVE DOSE</div>
        <div class="hud-tile-val">{dose:.1f} <span style="font-size: 0.85rem; color: #64748b;">mSv</span></div>
        <div class="hud-tile-delta {'delta-alert' if dose >= 250 else 'delta-nominal'}">
            LIMIT: 250 mSv
        </div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    co2 = current_reading.get("ambient_co2_mmHg", 1.2)
    st.markdown(f"""
    <div class="hud-tile" style="border-top-color: {'#ef4444' if co2 >= 10 else ('#f59e0b' if co2 >= 7.5 else '#3b82f6')};">
        <div class="hud-tile-label">CABIN PCO2</div>
        <div class="hud-tile-val">{co2:.1f} <span style="font-size: 0.85rem; color: #64748b;">mmHg</span></div>
        <div class="hud-tile-delta {'delta-alert' if co2 >= 10 else 'delta-nominal'}">
            SMAC: 10 mmHg
        </div>
    </div>
    """, unsafe_allow_html=True)

# Execute Autonomous Agent Triage
triage_result = agent.triage(current_reading, context=sim_stream.metadata)
state = triage_result["triage_state"]

# Tactical Triage State Banner
if state == "EMERGENCY":
    st.markdown(f"""
    <div class="hud-alert-banner hud-alert-emergency">
        [STATE: CRITICAL EMERGENCY ACTIVE] &mdash; NASA-STD-3001 BOUNDARY EXCEEDED<br>
        <span style="font-family: 'Inter', sans-serif; font-size: 0.95rem; font-weight: 500;">{triage_result['diagnosis']}</span>
    </div>
    """, unsafe_allow_html=True)
elif state in ("ALERT", "WATCH"):
    st.markdown(f"""
    <div class="hud-alert-banner hud-alert-watch">
        [STATE: {state} DETECTED] &mdash; ELEVATED ENVIRONMENTAL/PHYSIOLOGICAL DRIFT<br>
        <span style="font-family: 'Inter', sans-serif; font-size: 0.95rem; font-weight: 500;">{triage_result['diagnosis']}</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="hud-alert-banner hud-alert-nominal">
        [STATE: NOMINAL OPERATIONAL BASELINE] &mdash; ALL BIOMETRIC & ATMOSPHERIC PARAMETERS WITHIN SPEC
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# AVIONICS TABS
# ==========================================
tab_cockpit, tab_intercom, tab_guidelines = st.tabs([
    "MISSION COCKPIT & TRIAGE",
    "ASK AURA INTERCOM (SLM / VECTOR RAG)",
    "NASA CLINICAL REPOSITORY"
])

# ----------------------------------------------------
# TAB 1: COCKPIT & AUTONOMOUS ACTION STATION
# ----------------------------------------------------
with tab_cockpit:
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown("<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.82rem; font-weight: 700; color: #94a3b8; margin-bottom: 8px;'>TELEMETRY TRAJECTORY STREAM (MULTIVARIATE)</div>", unsafe_allow_html=True)
        df_history = pd.DataFrame(history)
        fig = go.Figure()

        if "cumulative_dose_mSv" in df_history.columns and df_history["cumulative_dose_mSv"].max() > 10.0:
            fig.add_trace(go.Scatter(x=df_history["minute"], y=df_history["cumulative_dose_mSv"], name="Absorbed Dose (mSv)", line=dict(color="#ef4444", width=2.5)))
            fig.add_hline(y=250.0, line_dash="dash", line_color="#ef4444", annotation_text="NASA-STD-3001 Single-Event Limit (250 mSv)", annotation_font=dict(color="#ef4444", size=10))
            fig.add_trace(go.Scatter(x=df_history["minute"], y=df_history["heart_rate_bpm"], name="Heart Rate (BPM)", yaxis="y2", line=dict(color="#38bdf8", width=1.8)))
            fig.update_layout(
                yaxis=dict(title="Dose (mSv)", title_font=dict(color="#ef4444", size=11), tickfont=dict(size=10)),
                yaxis2=dict(title="Heart Rate (BPM)", title_font=dict(color="#38bdf8", size=11), overlaying="y", side="right", tickfont=dict(size=10))
            )
        else:
            fig.add_trace(go.Scatter(x=df_history["minute"], y=df_history["ambient_co2_mmHg"], name="Cabin PCO2 (mmHg)", line=dict(color="#f59e0b", width=2.5)))
            fig.add_hline(y=10.0, line_dash="dash", line_color="#ef4444", annotation_text="SMAC Evacuation Limit (10.0 mmHg)", annotation_font=dict(color="#ef4444", size=10))
            fig.add_trace(go.Scatter(x=df_history["minute"], y=df_history["heart_rate_bpm"], name="Heart Rate (BPM)", yaxis="y2", line=dict(color="#38bdf8", width=1.8)))
            fig.update_layout(
                yaxis=dict(title="PCO2 (mmHg)", title_font=dict(color="#f59e0b", size=11), tickfont=dict(size=10)),
                yaxis2=dict(title="Heart Rate (BPM)", title_font=dict(color="#38bdf8", size=11), overlaying="y", side="right", tickfont=dict(size=10))
            )

        fig.update_layout(
            xaxis_title="Mission Elapsed Time (Minutes)",
            plot_bgcolor="#090d16",
            paper_bgcolor="#090d16",
            font=dict(color="#94a3b8", family="JetBrains Mono, monospace"),
            height=320,
            margin=dict(l=40, r=40, t=30, b=40),
            legend=dict(orientation="h", y=1.12, font=dict(size=10))
        )
        st.plotly_chart(fig, use_container_width=True)

        # Clinical Differential
        st.markdown("<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.82rem; font-weight: 700; color: #94a3b8; margin: 12px 0 6px 0;'>DIFFERENTIAL PHYSIOLOGICAL FINDINGS</div>", unsafe_allow_html=True)
        if triage_result["clinical_notes"]:
            for note in triage_result["clinical_notes"]:
                st.markdown(f"""
                <div style="background: #090d16; border-left: 3px solid #64748b; padding: 6px 10px; margin-bottom: 5px; font-size: 0.85rem; color: #cbd5e1;">
                    • {note}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size: 0.85rem; color: #64748b;'>No acute differential anomalies detected. Autonomic stability confirmed.</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown("<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.82rem; font-weight: 700; color: #94a3b8; margin-bottom: 8px;'>AUTONOMOUS FLIGHT SURGEON DIRECTIVES</div>", unsafe_allow_html=True)

        # Tactical Directive Card
        if triage_result.get("action_summary"):
            st.markdown(f"""
            <div class="tactical-directive">
                <div class="tactical-directive-tag">MANDATORY CLINICAL DIRECTIVE</div>
                <div class="tactical-directive-msg">{triage_result['action_summary']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Deterministic Physics & Countermeasure Metrics
        if triage_result["calculations"]:
            calc = triage_result["calculations"]
            st.markdown("<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.72rem; color: #64748b; margin-bottom: 6px;'>COMPUTED COUNTERMEASURE TELEMETRY</div>", unsafe_allow_html=True)
            if "projected_dose_at_ingress_mSv" in calc:
                c_a, c_b = st.columns(2)
                with c_a:
                    st.metric("Projected Ingress Dose", f"{calc['projected_dose_at_ingress_mSv']} mSv", delta="EXCEEDS LIMIT" if calc["exceeds_limit"] else "SAFE", delta_color="inverse")
                with c_b:
                    st.metric("Safe Time Margin", f"{calc['safe_margin_mSv']} mSv", delta="IMMEDIATE INGRESS" if calc["exceeds_limit"] else "NOMINAL", delta_color="inverse")
            elif "estimated_time_to_critical_min" in calc:
                c_a, c_b = st.columns(2)
                with c_a:
                    st.metric("Time to 10 mmHg Limit", f"{calc['estimated_time_to_critical_min']} min", delta="CRITICAL" if calc['estimated_time_to_critical_min'] < 30 else "MONITOR", delta_color="inverse")
                with c_b:
                    st.metric("Countermeasure", calc.get("recommendation", "RECYCLE_BED"))

        # Interactive Step-by-Step Action Checklist
        st.markdown("<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.82rem; font-weight: 700; color: #94a3b8; margin: 12px 0 6px 0;'>VERIFIED CREW ACTION PROTOCOL</div>", unsafe_allow_html=True)

        checklist = triage_result.get("checklist", [])
        for item in checklist:
            st.markdown(f"""
            <div class="checklist-row">
                <div style="font-weight: 600; color: #f1f5f9; font-size: 0.9rem;">
                    Step {item['step_number']}: {item['action']}
                </div>
                <div class="doc-ref">REF: {item['citation']} | ID: {item['source_id']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.checkbox(f"Acknowledge Step {item['step_number']} Executed by Crew", key=f"step_ck_{item['step_number']}")

        # Collapsible Engineering Audit Log for Ground Crew
        with st.expander("AUDITABLE TOOL EXECUTION LOG (GROUND SYNC)", expanded=False):
            st.caption("Deterministic tool call trace (NASA ExMC Gap Med10 verification)")
            if triage_result["tool_calls"]:
                for call in triage_result["tool_calls"]:
                    st.markdown(f"**⚡ Called Tool:** `{call['tool']}`")
                    st.json(call)
            else:
                st.write("Nominal operational profile. No emergency tool invocations.")

# ----------------------------------------------------
# TAB 2: INTERACTIVE ASTRONAUT INTERCOM (SLM + VECTOR SEARCH)
# ----------------------------------------------------
with tab_intercom:
    st.markdown("""
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">
        ASTRONAUT CLINICAL CONSULTATION INTERCOM
    </div>
    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 12px;">
        Direct natural language medical query engine. Retrieves verified NASA clinical flight rules via dense vector cosine similarity and synthesizes actionable clinical advisories offline.
    </div>
    """, unsafe_allow_html=True)

    # Clean Tactical Query Presets
    st.markdown("<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.72rem; color: #64748b; margin-bottom: 6px;'>PRESET MISSION CLINICAL QUERIES</div>", unsafe_allow_html=True)
    p_c1, p_c2, p_c3 = st.columns(3)
    preset_query = ""
    with p_c1:
        if st.button("EVA: Solar Storm Nausea & Vomiting"):
            preset_query = "Astronaut experiencing acute nausea and vomiting 2 hours after EVA solar particle flux."
        if st.button("ECLSS: PCO2 Buildup & Frontal Headache"):
            preset_query = "Crew member reports throbbing frontal headache and dyspnea. Scrubber alarm triggered."
    with p_c2:
        if st.button("Cardiac: Acute Chest Pain / Myocardial Infarction"):
            preset_query = "Astronaut experiencing crushing substernal chest pain, diaphoresis, and left arm numbness. Suspected heart attack / acute coronary syndrome."
        if p_c2.button("Vision: Right Eye Blurriness / SANS Optic Edema"):
            preset_query = "Vision in right eye is blurring during treadmill exercise. Suspecting papilledema or SANS."
    with p_c3:
        if st.button("EVA: Joint Bends / Suspected DCS"):
            preset_query = "Spacewalker reports sharp joint pain in right knee and shoulder after airlock repressurization. Decompression sickness suspected."
        if st.button("Behavioral: Circadian Fatigue / Reaction Lapse"):
            preset_query = "Crew member has 14 hours sleep debt over 3 days with cognitive reaction time lag on PVT."

    astronaut_input = st.text_input(
        "ASTRONAUT SYMPTOM REPORT / CLINICAL QUERY:",
        value=preset_query if preset_query else "",
        placeholder="e.g., Severe substernal chest pain radiating to jaw and left arm..."
    )

    if st.button("EXECUTE CLINICAL CONSULTATION", type="primary") or astronaut_input:
        if astronaut_input.strip():
            with st.spinner("Executing dense vector retrieval and clinical synthesis..."):
                consult = agent.consult(
                    astronaut_query=astronaut_input,
                    current_telemetry=current_reading,
                    active_hazard=triage_result["hazards"][0] if triage_result["hazards"] else None
                )

            st.markdown(f"""
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8; margin: 8px 0;">
                SYNTHESIS BACKEND: <span style="color: #38bdf8;">{consult['backend']}</span> | MODEL: <span style="color: #38bdf8;">{consult['model']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Display Clinical Advisory Card
            border_color = "#f59e0b" if consult.get("is_low_confidence") else "#38bdf8"
            advisory_title = "SAFETY GATE ALERT // UNINDEXED PROTOCOL QUERY" if consult.get("is_low_confidence") else "FLIGHT SURGEON CLINICAL EVALUATION"
            st.markdown(f"""
            <div style="background: #090d16; border: 1px solid #1e293b; border-left: 4px solid {border_color}; border-radius: 4px; padding: 18px; margin-top: 8px;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 800; color: {border_color}; letter-spacing: 0.08em; text-transform: uppercase;">{advisory_title}</div>
                <div style="white-space: pre-wrap; font-size: 0.95rem; line-height: 1.6; color: #f1f5f9; margin-top: 8px;">{consult['assessment']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Display Retrieved NASA Protocols & Cosine Scores
            st.markdown("<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.8rem; font-weight: 700; color: #94a3b8; margin: 16px 0 6px 0;'>GROUNDED NASA PROTOCOL VECTOR MATCHES</div>", unsafe_allow_html=True)
            for idx, p in enumerate(consult["retrieved_protocols"], 1):
                score = p.get("vector_score", 0.0)
                st.markdown(f"""
                <div style="background: #0b0f19; border: 1px solid #1e293b; border-radius: 4px; padding: 10px 14px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span style="font-weight: 700; color: #e2e8f0; font-size: 0.88rem;">{idx}. {p.get('document')}</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #38bdf8;">SCORE: {score:.4f}</span>
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; margin-top: 2px;">
                        SECTION: {p.get('section')} | CAT: {p.get('category')}
                    </div>
                    <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 4px;">{p.get('summary')}</div>
                    <div class="doc-ref">CITATION: {p.get('citations')}</div>
                </div>
                """, unsafe_allow_html=True)

# ----------------------------------------------------
# TAB 3: GROUNDED NASA EVIDENCE BASE
# ----------------------------------------------------
with tab_guidelines:
    st.markdown("""
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">
        NASA SPACE MEDICINE KNOWLEDGE REPOSITORY
    </div>
    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 12px;">
        Curated offline flight rule database addressing NASA ExMC Gap Med10 requirements.
    </div>
    """, unsafe_allow_html=True)

    for doc in rag_engine.corpus:
        with st.expander(f"DOC: {doc['document']} [{doc['id']}]", expanded=False):
            st.markdown(f"**Section:** `{doc['section']}`")
            st.markdown(f"**Category:** `{doc['category']}`")
            st.markdown(f"**Clinical Summary:** {doc['summary']}")
            st.markdown(f"**Authority Citation:** `{doc['citations']}`")
            st.markdown("**Authoritative Protocol Steps:**")
            for i, step in enumerate(doc["protocol_steps"], 1):
                st.markdown(f"{i}. {step}")

# Footer
st.markdown("---")
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.caption("AURA // AUTONOMOUS UNIVERSAL RESCUE & ASTRONAUT-HEALTH AGENT | NASA SPACE APPS 2026 | 100% OFFLINE EDGE ARCHITECTURE")
with col_f2:
    st.button("PACKAGE GROUND TELEMETRY BURST")
