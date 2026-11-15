# 🛰️ AURA: Autonomous Universal Rescue & Astronaut-Health Agent
### *An Onboard "Robot Flight Surgeon" for Deep Space & Lunar Missions*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aura-flight-surgeon.streamlit.app/)
[![NASA Space Apps Challenge](https://img.shields.io/badge/NASA%20Space%20Apps-2026%20Global%20Challenge-blue.svg)](https://www.spaceappschallenge.org/)
[![NASA Standard](https://img.shields.io/badge/NASA--STD--3001-Compliant%20Triage-green.svg)](https://www.nasa.gov/)
[![Offline First](https://img.shields.io/badge/Offline%20First-0--RAM%20Fallback-orange.svg)](https://github.com/Abh-igyan/AURA)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

### 🌐 **Live Interactive Mission Cockpit**
> **Experience the live deployment directly in your browser:**  
> 👉 **[https://aura-flight-surgeon.streamlit.app/](https://aura-flight-surgeon.streamlit.app/)**  
*(No installation or GPU required — runs directly on Streamlit Community Cloud!)*

---

## 🧒 Explain It Like I'm Five: *What is AURA?*

> **Imagine you are an astronaut floating in a tiny spacecraft on your way to Mars, 140 million miles away from home.** 🚀
>
> If you catch a fever or scrape your arm on Earth, you can call 911 or visit a doctor in five minutes. 
> 
> But in deep space, there is **no hospital nearby**. Even worse: a radio message to Earth takes **20 minutes** to get there, and another **20 minutes** for Houston to answer back! If a giant solar storm suddenly erupts from the Sun or your oxygen recycler starts acting up, **you cannot wait 40 minutes for Earth to reply.**
>
> **Enter AURA.** 🤖✨
> 
> AURA is a super-smart **Robot Flight Surgeon** that lives right inside your spaceship's computer. It watches your heartbeat, monitors the air inside your cabin, detects cosmic radiation storms, and gives you instant medical answers in less than one second — **completely offline, with zero internet connection!**

---

## 🌟 AURA's Three Superpowers

```
      +-----------------------------------------------------------+
      |               AURA CORE ARCHITECTURE                     |
      +-----------------------------------------------------------+
                                    |
      +-----------------------------+-----------------------------+
      |                             |                             |
      v                             v                             v
[ 🛡️ SUPERPOWER 1 ]          [ ⚡ SUPERPOWER 2 ]          [ 📚 SUPERPOWER 3 ]
Deterministic Safety Core    100% Offline Edge SLM        Vector Memory (RAG)
NASA-STD-3001 Rule Engine    Ollama 1B or 0-RAM Fallback  NASA Clinical Protocols
   (Zero Guessing)             (Works Without Cloud)        (Exact Citations)
```

### 🛡️ Superpower 1: The Deterministic Safety Shield *(Zero Guessing!)*
In space medicine, **AI hallucinations can be fatal**. A medical AI cannot "guess" or "hallucinate" dosages when an astronaut is in danger.
- AURA uses a hard-coded **Deterministic Safety Core** built on **NASA-STD-3001** flight standards.
- Evaluates real-time astronaut vitals (Heart Rate, HRV Autonomic Strain, SpO2) and habitat environment (CO2 levels, radiation dosimeter flux).
- Transitions across **`NOMINAL` → `WATCH` → `ALERT` → `EMERGENCY`** with mathematical certainty.
- Computes real physics countermeasures, such as exact shelter ingress deadlines during Solar Particle Events (SPE) and cabin evacuation limits.

### ⚡ Superpower 2: 100% Offline & 0-RAM Fallback *(Deep Space Ready)*
Deep space has no Wi-Fi or cellular towers. AURA is engineered to run on compact spacecraft flight hardware and **standard laptops with 8 GB RAM**:
- **Local Neural SLM:** Runs Small Language Models (e.g. `llama3.2:1b` ~1.3 GB RAM or `qwen2.5:1.5b`) completely offline via Ollama.
- **Resilient 0-RAM Clinical Synthesizer:** If no neural engine is loaded, AURA automatically shifts into an ultra-lean local synthesizer running with **0 MB extra RAM** and zero latency. The app **never hangs, never crashes, and never gives up.**
- **Cloud API Bridge:** Seamlessly connects with Groq or OpenAI if connectivity is available.

### 📚 Superpower 3: Instant Space Medicine Library *(Vector RAG Intercom)*
AURA includes a subword-vector similarity engine indexing NASA's most critical deep-space medical guidelines:
1. `NASA-HRP-JSC-CN-35747-SEC3.2`: Solar Particle Events & Acute Radiation Syndrome (ARS).
2. `NASA-OCHMO-TB-OCHMO-004-SEC4`: Spacecraft Cabin Atmospheric Quality & CO2 Scrubber Degradation.
3. `NASA-HRP-SANS-EVIDENCE-2022`: Spaceflight-Associated Neuro-ocular Syndrome (SANS) & Cephalad Fluid Shifts.
4. `NASA-EVA-FLIGHT-RULE-B13-104`: In-Suit Decompression Sickness (DCS) & Bends Prevention.
5. `NASA-HRP-BEHAVIORAL-HEALTH-2021`: Confinement Stress, Sleep Debt & Circadian Resets.

Astronauts can ask questions via the **"Ask AURA" Natural Language Intercom** and receive grounded advice with exact NASA document and section citations.

---

## 🕹️ Cockpit Interface & Mission Scenarios

AURA includes a high-contrast, military-grade dark HUD designed for astronauts operating under extreme stress, microgravity disorientation, and heavy vibration:

- **🚨 Mandatory Clinical Directives:** High-visibility directive banners displaying clear, decisive actions (e.g., *"ABORT EVA IMMEDIATELY. Ingress storm shelter within 8.5 min"*).
- **📈 Real-Time Multivariate Telemetry Stream:** Dynamic visual graphs tracking radiation dose curves, heart rate spikes, and cabin CO2 levels against NASA safety ceilings.
- **✅ Verified Crew Action Protocol:** Interactive step-by-step checklist ensuring no critical medical action is missed during an emergency.
- **🎙️ Natural Language Intercom:** Interactive Q&A console with preset emergency simulation chips (*"Radiation Flash"*, *"CO2 Scrubber Warning"*, *"Eye Blurriness / SANS"*).

---

## 🚀 Quickstart & Local Installation

You can run AURA locally on any Windows, macOS, or Linux machine in two minutes:

### 1. Clone the Repository
```bash
git clone https://github.com/Abh-igyan/AURA.git
cd AURA
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Mission Cockpit
```bash
streamlit run app.py
```
Your browser will open automatically at `http://localhost:8501`.

---

## 🧠 (Optional) Run 100% Offline with Local SLM (Ollama)

To experience full local neural intelligence with zero cloud dependencies:
1. Download Ollama from [ollama.ai](https://ollama.ai).
2. Run the ultra-light 1-billion parameter model in your terminal:
   ```bash
   ollama run llama3.2:1b
   ```
   *(Download size is only ~1.3 GB and uses ~1.3 GB RAM, running effortlessly on 8 GB RAM systems).*
3. Refresh `http://localhost:8501`. AURA will automatically detect your local neural engine and display `Ollama Local (llama3.2:1b)` in the mission control sidebar!

---

## 🧪 Integration Test Suite

Verify all deterministic rules, vector retrieval precision, and physics calculations:
```bash
python tests/test_aura_core.py
```
The test suite validates:
- [x] **NASA-STD-3001 Rule Engine:** Accurate gating across all alert tiers.
- [x] **Physics Formulas:** Solar radiation shelter ingress and CO2 scrubber degradation timers.
- [x] **Vector Store Cosine Precision:** Grounded retrieval across all 5 NASA clinical protocol categories.
- [x] **SLM Offline Resilience:** Automatic 0-RAM fallback and citation enforcement.
- [x] **Autonomous Triage Pipeline:** End-to-end telemetry ingestion and clinical directive synthesis.

---

## 📜 NASA Standards & Technical References
- **NASA-STD-3001**: Space Flight Human-System Standard (Volume 1: Crew Health; Volume 2: Human Factors, Habitability, and Environmental Health).
- **NASA ExMC Gap Med10**: Exploration Medical Capability — Autonomous Medical Decision Support.
- **JSC-CN-35747**: Radiation Protection and Acute Radiation Syndrome Protocols for Deep Space EVA.
- **TB-OCHMO-004**: Spacecraft Internal Atmosphere Technical Brief (CO2 Limits and Scrubbing Dynamics).

---

## 👨‍🚀 Mission Team

Developed for the **NASA International Space Apps Challenge 2026**  
- **Team:** `AURAstronaut`  
- **Team Members:** Abhigyan Tiwari, Dhruba Kumar Agarwalla  
- **Target Category:** *Create Health Monitoring Software for Astronauts on Space Missions*  

---
*Ad Astra Per Aspera* 🚀
