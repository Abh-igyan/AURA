"""
AURA Deterministic Safety Rules Engine
Anchored directly in NASA-STD-3001 Volume 1 & Volume 2 spaceflight limits.
Enforces deterministic medical state transitions without relying on LLM decisions.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List


class DeterministicSafetyEngine:
    def __init__(self, thresholds_path: Path | str):
        with open(thresholds_path, "r", encoding="utf-8") as f:
            self.standards: Dict[str, Any] = json.load(f)

        self.rad_limits = self.standards["radiation_limits"]["operational_rules"]
        self.co2_limits = self.standards["atmospheric_co2_limits"]
        self.vital_limits = self.standards["vital_signs_thresholds"]

    def evaluate(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pure deterministic evaluation of biometric & environmental state.
        Returns state level, triggered hazards, and NASA-STD-3001 violations.
        """
        hazards: List[Dict[str, Any]] = []
        state = "NOMINAL"

        dose = reading.get("cumulative_dose_mSv", 0.0)
        dose_rate = reading.get("dosimeter_rate_mSv_hr", 0.0)
        co2 = reading.get("ambient_co2_mmHg", 0.0)
        hr = reading.get("heart_rate_bpm", 75)
        spo2 = reading.get("spo2_pct", 98.0)
        hrv = reading.get("hrv_rmssd_ms", 45.0)

        # 1. Radiation Evaluation (NASA-STD-3001 Vol 1 Crew Limits)
        if dose >= self.rad_limits["emergency_abort_eva_mSv"]:
            state = "EMERGENCY"
            hazards.append({
                "type": "HAZARD_RADIATION_ACUTE_SPE",
                "severity": "CRITICAL",
                "trigger": f"Cumulative dose {dose:.1f} mSv exceeds NASA-STD-3001 Single-Event Limit (250.0 mSv)",
                "document": "NASA-STD-3001 Vol 1 Rev B",
                "protocol_id": "NASA-HRP-JSC-CN-35747-SEC3.2"
            })
        elif dose >= self.rad_limits["alert_threshold_cumulative_mSv"] or dose_rate > 500.0:
            if state != "EMERGENCY":
                state = "ALERT"
            hazards.append({
                "type": "HAZARD_RADIATION_SPE_APPROACHING",
                "severity": "HIGH",
                "trigger": f"Accumulated {dose:.1f} mSv (Rate {dose_rate:.1f} mSv/hr). Rapid flux detected.",
                "document": "NASA-STD-3001 Vol 2",
                "protocol_id": "NASA-HRP-JSC-CN-35747-SEC3.2"
            })
        elif dose >= self.rad_limits["watch_threshold_cumulative_mSv"] or dose_rate > 50.0:
            if state == "NOMINAL":
                state = "WATCH"
            hazards.append({
                "type": "HAZARD_RADIATION_WATCH",
                "severity": "MODERATE",
                "trigger": f"Dose accumulation {dose:.1f} mSv exceeds nominal baseline.",
                "document": "NASA-STD-3001 Vol 2",
                "protocol_id": "NASA-HRP-JSC-CN-35747-SEC3.2"
            })

        # 2. Environmental CO2 Evaluation (Spacecraft SMAC Limits)
        if co2 >= self.co2_limits["emergency_evacuation_partial_pressure_mmHg"]:
            state = "EMERGENCY"
            hazards.append({
                "type": "HAZARD_HYPERCAPNIA_CRITICAL",
                "severity": "CRITICAL",
                "trigger": f"Ambient CO2 {co2:.1f} mmHg exceeds emergency evacuation threshold (10.0 mmHg)",
                "document": "NASA Spacecraft Maximum Allowable Concentrations (SMAC)",
                "protocol_id": "NASA-OCHMO-TB-OCHMO-004-SEC4"
            })
        elif co2 >= self.co2_limits["alert_partial_pressure_mmHg"]:
            if state != "EMERGENCY":
                state = "ALERT"
            hazards.append({
                "type": "HAZARD_HYPERCAPNIA_ALERT",
                "severity": "HIGH",
                "trigger": f"Ambient CO2 {co2:.1f} mmHg exceeds alert threshold (7.5 mmHg)",
                "document": "NASA-STD-3001 Vol 2 Rev C",
                "protocol_id": "NASA-OCHMO-TB-OCHMO-004-SEC4"
            })
        elif co2 >= self.co2_limits["caution_partial_pressure_mmHg"]:
            if state == "NOMINAL":
                state = "WATCH"
            hazards.append({
                "type": "HAZARD_HYPERCAPNIA_CAUTION",
                "severity": "MODERATE",
                "trigger": f"Ambient CO2 {co2:.1f} mmHg elevated above nominal (3.0 mmHg)",
                "document": "NASA-STD-3001 Vol 2 Rev C",
                "protocol_id": "NASA-OCHMO-TB-OCHMO-004-SEC4"
            })

        # 3. Physiological Triage Differential (H-4, H-5 fixes)
        clinical_notes = []
        spo2_limits = self.vital_limits["oxygen_saturation_pct"]
        hr_limits = self.vital_limits["heart_rate_bpm"]

        # SpO2 / Hypoxia — was completely absent; now generates hazards (H-4 fix)
        if spo2 < spo2_limits["critical_hypoxia"]:
            state = "EMERGENCY"
            hazards.append({
                "type": "HAZARD_HYPOXIA_CRITICAL",
                "severity": "CRITICAL",
                "trigger": f"SpO2 {spo2:.1f}% below critical hypoxia threshold ({spo2_limits['critical_hypoxia']}%). Immediate supplemental O2 required.",
                "document": "NASA-STD-3001 Vol 1 Rev B",
                "protocol_id": "NASA-HRP-JSC-CN-35747-SEC3.2"
            })
        elif spo2 < spo2_limits["caution_low"]:
            if state not in ("EMERGENCY", "ALERT"):
                state = "ALERT"
            hazards.append({
                "type": "HAZARD_HYPOXIA_ALERT",
                "severity": "HIGH",
                "trigger": f"SpO2 {spo2:.1f}% below caution threshold ({spo2_limits['caution_low']}%). Supplemental oxygen and monitoring required.",
                "document": "NASA-STD-3001 Vol 1 Rev B",
                "protocol_id": "NASA-HRP-JSC-CN-35747-SEC3.2"
            })
        elif spo2 < spo2_limits["nominal_min"]:
            if state == "NOMINAL":
                state = "WATCH"
            clinical_notes.append(f"SpO2 {spo2:.1f}% below nominal minimum ({spo2_limits['nominal_min']}%). Monitor closely.")

        # Bradycardia — was never checked (H-5 fix)
        if hr < hr_limits["nominal_min"]:
            if state not in ("EMERGENCY",):
                state = "ALERT" if hr < 40 else ("ALERT" if state == "NOMINAL" else state)
            hazards.append({
                "type": "HAZARD_BRADYCARDIA",
                "severity": "HIGH" if hr < 40 else "MODERATE",
                "trigger": f"Bradycardia detected: {hr} bpm (nominal min {hr_limits['nominal_min']} bpm). Risk of cardiac compromise.",
                "document": "NASA-STD-3001 Vol 1 Rev B",
                "protocol_id": "NASA-HRP-JSC-CN-35747-SEC3.2"
            })

        # Tachycardia & HRV — escalate to WATCH when isolated vital-sign findings
        if hr >= hr_limits["tachycardia_caution"]:
            if state == "NOMINAL":
                state = "WATCH"
            clinical_notes.append(f"Tachycardia detected ({hr} bpm) secondary to physiological strain.")
        if hrv <= self.vital_limits["heart_rate_variability_rmssd_ms"]["stress_autonomic_strain"]:
            if state == "NOMINAL":
                state = "WATCH"
            clinical_notes.append(f"Depressed HRV ({hrv:.1f} ms) confirms acute autonomic nervous system stress.")

        if co2 > 5.0 and spo2 >= spo2_limits["nominal_min"]:
            clinical_notes.append("Environmental hypercapnia confirmed: elevated PCO2 with preserved SpO2 rules out primary respiratory failure.")

        return {
            "state": state,
            "hazards": hazards,
            "clinical_notes": clinical_notes,
            "metrics": {
                "heart_rate_bpm": hr,
                "spo2_pct": spo2,
                "ambient_co2_mmHg": co2,
                "cumulative_dose_mSv": dose,
                "dosimeter_rate_mSv_hr": dose_rate,
                "hrv_rmssd_ms": hrv
            }
        }
