# AURA Project: Complete Conversation & Strategic Research Archive
**Migrated Session History | NASA Space Apps Challenge 2026**  
*Archive Date:* November 14, 2026  
*Project Location:* `c:\Users\Abhigyan\Documents\vs_code\AURA`

---

## Table of Contents
1. [Executive Trajectory & Key Pivots](#1-executive-trajectory--key-pivots)
2. [NASA Space Apps Challenge: Official Rules & Strategic Decisions](#2-nasa-space-apps-challenge-official-rules--strategic-decisions)
   - [The China Restriction (Wolf Amendment Compliance)](#the-china-restriction-wolf-amendment-compliance)
   - [Location Arbitrage: The Gangtok Decision](#location-arbitrage-the-gangtok-decision)
   - [Solo Participation Eligibility](#solo-participation-eligibility)
   - [Competition Round Structure & Timeline](#competition-round-structure--timeline)
3. [Problem Statements Evaluation (The 14 Challenges)](#3-problem-statements-evaluation-the-14-challenges)
   - [Why Challenge #1 ("Astronaut Health Monitoring") Was Selected](#why-challenge-1-astronaut-health-monitoring-was-selected)
   - [Why Vanilla RAG (#6) Was Rejected](#why-vanilla-rag-6-was-rejected)
4. [AURA System Architecture & NASA Alignment](#4-aura-system-architecture--nasa-alignment)
   - [The Core Problem: Deep Space Latency (4–24 min)](#the-core-problem-deep-space-latency-424-min)
   - [The Golden Pitch Citation: NASA ExMC Gap Med10](#the-golden-pitch-citation-nasa-exmc-gap-med10)
   - [The Safety Architecture: Solving Hallucinations](#the-safety-architecture-solving-hallucinations)
5. [NASA Open Data Provenance & Grounded Corpus](#5-nasa-open-data-provenance--grounded-corpus)
6. [The Two Demonstration Scenarios](#6-the-two-demonstration-scenarios)
7. [Submission Deliverables & 30-Second Video Script](#7-submission-deliverables--30-second-video-script)
8. [Earlier Research Notes](#8-earlier-research-notes)
   - [Apple Robotics (Siyuan Hu & HALO)](#apple-robotics-siyuan-hu--halo)
   - [AIxNET 2026 Conference](#aixnet-2026-conference)
   - [Neuralink & OpenBCI Systems Roadmap](#neuralink--openbci-systems-roadmap)

---

## 1. Executive Trajectory & Key Pivots

* **Initial Goal:** Reviewing engineering opportunities in embodied/physical AI (Apple Robotics / HALO) and BCI (Neuralink/OpenBCI), before deciding to compete in the **NASA International Space Apps Challenge 2026**.
* **Hackathon Strategy:** Selected virtual participation in **Gangtok Local Chapter** due to low participant density (17 participants), maximizing the statistical probability of becoming a **NASA Global Nominee** (~50–70% vs <2% in metro hubs).
* **Teaming Decision:** Decided on a **solo execution model** (fully permitted for Local Events, eliminating coordination lag).
* **Challenge Selection:** Picked *"Create Health Monitoring Software for Astronauts on Space Missions"*.
* **Technical Innovation:** Rejected standard "Fitbit for Space" charts or toy "Chat with PDF" bots. Built **AURA** (*Autonomous Universal Rescue & Astronaut-Health Agent*): an edge-first, on-device autonomous Flight Surgeon combining real-time streaming telemetry, deterministic safety rules (NASA-STD-3001), typed medical tools, and grounded clinical RAG (NASA HRP JSC-CN-35747).

---

## 2. NASA Space Apps Challenge: Official Rules & Strategic Decisions

### The China Restriction (Wolf Amendment Compliance)
* **The Rule:** Under U.S. federal law (the Wolf Amendment) and NASA statutory funding policies, NASA cannot engage in bilateral activities or fund projects with "China or Chinese-owned entities" (including PRC government bodies, state-owned companies, and universities in mainland China, Hong Kong, or Macau).
* **Decision:** Avoiding co-registration or collaboration with individuals affiliated with Chinese institutions was mandatory. Any team failing the automated PRC Bilateral Compliance Review prior to Global Judging is instantly disqualified.

### Location Arbitrage: The Gangtok Decision
* **Registration Count:** Only 17 registered participants in Gangtok.
* **The Funnel:** 17 participants yields roughly 3 to 5 teams. In hackathons, 30–50% fail to submit a completed project before the deadline. Gangtok will likely see only 2 to 4 completed submissions.
* **The Quota:** Every active local chapter (even with 1–10 submissions) gets **at least 1 Global Nominee slot** to advance directly to NASA's international judging panel.
* **Verdict:** Entering Gangtok virtually provides a massive statistical advantage in Round 1. NASA treats all ~1,200 Global Nominees equally in Round 2 regardless of which chapter nominated them.

### Solo Participation Eligibility
* **Local Event Rule:** Local Event teams can have **1 to 6 members**. Solo teams are 100% eligible for local awards, Global Nomination, and Global Awards.
* *(Note: The Universal Event requires at least 2 members; Gangtok, as a local event, permits solo).*

### Competition Round Structure & Timeline
```
Round 1: Local Event Judging (Gangtok)
   └── Judges select Global Nominees (Top 1-2 teams per chapter; ~1,250 globally)
Round 2: Global Review (October – November)
   └── NASA & Space Agency Subject Matter Experts evaluate all Global Nominees
   └── Narrowed to ~40–45 Global Finalists + Honorable Mentions
Round 3: Executive Judging (December – January)
   └── Senior NASA leadership selects the 10 Global Winners (1 per award track)
Prize: Invitation to NASA Headquarters / Kennedy Space Center for rocket launch & presentation
```

---

## 3. Problem Statements Evaluation (The 14 Challenges)

### Why Challenge #1 ("Astronaut Health Monitoring") Was Selected
* High stakes, tangible human mission relevance (Artemis Lunar Base & Mars transit).
* Naturally requires systems engineering, low-latency telemetry processing, and intelligent decision support.
* Direct target for the **"Best Use of Technology"** and **"Best Mission Concept"** Global Awards.

### Why Vanilla RAG (#6 Space Biology Knowledge Engine) Was Rejected
* "Uploading PDFs to a vector database and chatting with them" is an overdone hackathon cliché.
* Lacks systems depth, provides no immediate operational feedback loop, and does not demonstrate real-time telemetry processing.

---

## 4. AURA System Architecture & NASA Alignment

### The Core Problem: Deep Space Latency (4–24 min)
On Mars and lunar exploration missions, communication round-trip latency to Earth is between **4 to 24 minutes**. When acute physiological emergencies occur (hypoxia, acute radiation, hypercapnia), real-time telemedicine consultation with Houston flight surgeons is physically impossible. The crew needs on-device autonomy.

### The Golden Pitch Citation: NASA ExMC Gap Med10
In NASA’s Exploration Medical Capability (ExMC) roadmap:
> *"NASA ExMC Gap Med10 explicitly states: **'We do not have the capability to provide computed medical decision support during exploration missions.'** AURA is an edge-first prototype engineered to address Gap Med10."* *(NTRS 20200000567)*

### The Safety Architecture: Solving Hallucinations
To defend against harsh scrutiny from spaceflight physicians:
1. **The LLM Does Not Make Clinical Decisions:** A deterministic Python rules engine computes triage states based on hardcoded **NASA-STD-3001** thresholds.
2. **Deterministic Tool Gating:** All math (time-to-shelter, radiation dose accumulation, CO₂ buildup rates) executes in typed Python functions, never in language model text generation.
3. **Traceable Citations:** Every step in the generated action checklist displays an exact NASA Document ID and section reference.
4. **Human-in-the-Loop:** AURA recommends $\to$ Crew Medical Officer (CMO) confirms $\to$ logs are queued for ground review upon comms re-acquisition.

---

## 5. NASA Open Data Provenance & Grounded Corpus

| Resource | Official Document / Identifier | Role in AURA |
| :--- | :--- | :--- |
| **NASA CCMC DONKI** | `SEP-2024-05-11T02:15:00-SEP-001` | Real S3 Solar Radiation Storm event trigger |
| **NASA-STD-3001 Vol 1 & 2** | *Spaceflight Human-System Standard* | Hardcoded 250 mSv single-event limit & SMAC CO₂ thresholds |
| **NASA HRP Evidence Report** | `JSC-CN-35747` | Clinical management of Solar Particle Events & Acute Radiation Syndrome |
| **NASA OCHMO Tech Brief** | `TB-OCHMO-004` | Spacecraft atmospheric quality & hypercapnia protocols |
| **NASA OSDR / RadLab** | *Ames Life Sciences Data Archive* | Baseline environmental & radiation time-series |

---

## 6. The Two Demonstration Scenarios

### Scenario 1: Solar Particle Event (SPE) during Lunar EVA
* **Location:** Shackleton Crater Rim (EVA-3), CDR Marcus Vance.
* **Progression:** Real DONKI SEP notification $\to$ dosimeter spikes to 820 mSv/hr $\to$ cumulative dose crosses 250 mSv limit (268 mSv) $\to$ HR climbs to 124 bpm, nausea reported.
* **Agent Actions:** Calls `calculate_radiation_countermeasure()` (dose at ingress: 272 mSv) $\to$ queries guidelines $\to$ generates immediate shelter-in-place and antiemetic checklist citing `NASA-HRP-JSC-CN-35747-SEC3.2`.

### Scenario 2: ECLSS Carbon Dioxide Scrubber Failure (Deep Space Transit)
* **Location:** Deep Space Transit Habitat, Dr. Elena Rostova.
* **Progression:** CDRA valve failure $\to$ ambient CO₂ ramps from 2.9 to 13.6 mmHg (exceeds 10.0 mmHg emergency limit) $\to$ HR climbs to 110 bpm $\to$ **SpO₂ remains steady at 98%**.
* **Clinical Differential:** Preserved SpO₂ with elevated PCO₂ confirms pure environmental hypercapnia, ruling out primary respiratory failure.
* **Agent Actions:** Calls `calculate_co2_scrubber_countermeasure()` $\to$ orders cessation of exercise, deployment of backup LiOH canisters, and 100% O₂ masks citing `NASA-OCHMO-TB-OCHMO-004-SEC4`.

---

## 7. Submission Deliverables & 30-Second Video Script

### 30-Second NASA Video Script:
```
[0:00 - 0:06] (Visual: Cockpit dashboard showing comms delay warning)
"On missions to Mars, communication delay is 20 minutes. If an astronaut faces a medical crisis, Houston can't answer in time."

[0:06 - 0:15] (Visual: Triggering Scenario 1, telemetry graphs spiking into red)
"Meet AURA. Built to address NASA ExMC Gap Med10, AURA is an on-device autonomous flight surgeon running 100% offline."

[0:15 - 0:24] (Visual: Highlighting tool-calling trace and deterministic calculations)
"When a Solar Particle Event or CO₂ scrubber fails, AURA's deterministic rules engine detects the crisis and executes verified medical tools."

[0:24 - 0:30] (Visual: Showing step-by-step checklist with NASA document citations)
"Zero hallucinations. Every action step is grounded in NASA-STD-3001 and HRP clinical guidelines. AURA: Autonomous care beyond Earth."
```

---

## 8. Earlier Research Notes

### Apple Robotics (Siyuan Hu & HALO)
* **Profile:** Siyuan Hu is a Lead Researcher and Engineering Manager at Apple AI/ML Research (robotics team led by Vladlen Koltun and Matthias Müller).
* **Flagship Project:** **HALO** (*Humanoid Autonomy, Learned in simulation, running Onboard*).
  - Hardware: Unitree G1 humanoid robot powered by an onboard **Mac mini M4 Pro** wired directly to the robot's battery bus.
  - ML Stack: Local edge vision-language-action models running locally on **Apple MLX**; zero-shot sim-to-real transfer trained in **NVIDIA Isaac Sim**.
* **Outreach Strategy:** Avoid sending generic student/hackathon links (can undersell systems capabilities). Instead, lead with low-level systems engineering (Go, Linux internals, deterministic IPC, low-latency data pipelines, eBPF / system observability).

### AIxNET 2026 Conference
* **What it is:** 1st International Conference on Interconnected AI and NETworks (IEEE ComSoc, Paris, Nov 23–25, 2026).
* **Verdict:** Do NOT travel or register (in-person only, academic telco focus). Track online slides for two relevant presentations:
  1. Walid Saad’s Keynote: *"Why AI Still Can’t Handle the Physical World: AGI-Native Wireless Systems for Physical AI"*.
  2. The Panel: *"Agents for Networks, Networks for Agents"*.

### Neuralink & OpenBCI Systems Roadmap
* **Domain:** Brain-Computer Interfaces (BCI).
* **Core Insight:** Neuralink is ~80% systems engineering (custom ASIC, low-power BLE telemetry, <15ms real-time Kalman/RNN neural decoders, sub-micron surgical robotics).
* **Open Source Ecosystem to Build Proof-of-Work:**
  - **OpenBCI** (Cyton/Ganglion open-source biosensing hardware).
  - **BrainFlow** (high-performance C++/Python data acquisition SDK).
  - **NeuroTechX** (global community).
  - **MNE-Python & PhysioNet BCI Motor Imagery Dataset** (free EEG data to build thought-to-cursor decoders without hardware).

---

*End of Migrated Session Context. All code and dashboard files are active in this workspace directory.*
