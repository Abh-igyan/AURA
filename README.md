# AURA: Autonomous Universal Rescue & Astronaut-Health Agent
**NASA International Space Apps Challenge Prototype**  
*Target:* **NASA ExMC Gap Med10 — Computed Medical Decision Support**

---

## 🚀 Overview

AURA is an onboard autonomous clinical decision-support and triage system engineered for deep-space exploration missions (e.g. Artemis lunar surface EVA and Mars transit). Under communication blackouts or round-trip transmission latencies of 4 to 24 minutes, real-time consultation with flight surgeons at NASA Johnson Space Center is impossible. 

AURA solves this by running an **agentic, offline, deterministic-first medical triage and consultation system** designed to run comfortably on edge devices and **standard laptops with 8 GB RAM**.

---

## 🧠 Architecture & 8 GB RAM Optimization

### 1. Deterministic Safety Core (NASA-STD-3001)
- Evaluates real-time astronaut biometrics (HR, HRV, SpO2) and habitat environment (ambient PCO2, dosimeter mSv/hr, cumulative radiation).
- Transitions strictly across `NOMINAL` → `WATCH` → `ALERT` → `EMERGENCY` states using hard-coded NASA thresholds.
- Zero reliance on LLMs for safety-critical state switches or physics math.

### 2. True Vector Similarity Search (`engine/vector_store.py`)
- Indexes authoritative NASA spaceflight clinical protocols:
  1. `NASA-HRP-JSC-CN-35747-SEC3.2`: Solar Particle Events & Acute Radiation Syndrome (ARS).
  2. `NASA-OCHMO-TB-OCHMO-004-SEC4`: Spacecraft Cabin Atmospheric Quality & CO2 Scrubber Degradation.
  3. `NASA-HRP-SANS-EVIDENCE-2022`: Spaceflight-Associated Neuro-ocular Syndrome (SANS) & Cephalad Fluid Shifts.
  4. `NASA-EVA-FLIGHT-RULE-B13-104`: In-Suit Decompression Sickness (DCS) & Bends.
  5. `NASA-HRP-BEHAVIORAL-HEALTH-2021`: Long-Duration Confinement, Sleep Debt & Cognitive Fatigue.
- Calculates subword/n-gram vector space embeddings and cosine similarity (0.0 to 1.0) with zero external server dependencies and negligible RAM footprint (< 20 MB).
- Automatically upgrades to dense neural embeddings (`sentence-transformers/all-MiniLM-L6-v2`) if installed.

### 3. Edge-First SLM Engine (`engine/slm.py`)
- Engineered specifically for **8 GB RAM machines**:
  - **Option A (Local Ollama Neural SLM):** Integrates with `llama3.2:1b` (~1.3 GB RAM) or `qwen2.5:1.5b` (~1.6 GB RAM) running locally via Ollama (`http://localhost:11434`). Fast, 100% offline, zero disk thrashing.
  - **Option B (Resilient Local Clinical Synthesizer):** If Ollama is not running, AURA operates via a built-in offline Flight Surgeon Synthesizer that runs with **0 MB extra RAM** and zero latency. The app never crashes or hangs!
  - **Option C (Cloud API Bridge):** Supports Groq (`GROQ_API_KEY`) or OpenAI if an API key is provided for instant cloud inference.

### 4. Astronaut-Centric Ergonomics
- High-contrast, dark-mode cockpit designed for astronauts under acute stress.
- Immediate **Mandatory Flight Surgeon Directives** and clean metric cards instead of raw developer JSON traces.
- Interactive step-by-step verified action checklist with explicit document citations.
- **"Ask AURA" Natural Language Intercom**: Direct query console where crew can type complaints or click preset mission emergency chips.

---

## 🛠️ Quickstart

### 1. Run the Dashboard
```powershell
cd C:\Users\Abhigyan\Documents\vs_code\AURA
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 2. (Optional) Run Local Neural SLM via Ollama
If you want to run a local neural SLM on your 8 GB RAM laptop:
1. Download Ollama from [ollama.ai](https://ollama.ai).
2. Open PowerShell and run:
   ```powershell
   ollama run llama3.2:1b
   ```
   *(Only 1.3 GB download; uses ~1.3 GB of RAM, leaving plenty of headroom for Windows + Chrome).*
3. Refresh `http://localhost:8501`. AURA will automatically detect Ollama and display `Ollama Local (llama3.2:1b)` in the sidebar!

---

## 🧪 Running Integration Tests

Run the comprehensive core test suite:
```powershell
python tests/test_aura_core.py
```
All 6 test suites verify:
1. Vector Store cosine retrieval precision across all 5 NASA emergency categories.
2. NASA-STD-3001 deterministic safety rule thresholds.
3. Physics countermeasure formulas (SPE shelter ingress time, CO2 scrubber time-to-critical).
4. SLM offline resilience and citation grounding.
5. Autonomous Flight Surgeon full agent triage loop.
6. Sensor telemetry validation and quality gating.
