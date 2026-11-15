"""
AURA Telemetry Ingestion & Quality Gate Engine
Simulates onboard sensor telemetry feeds and enforces data validation gates.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class TelemetryStream:
    def __init__(self, scenario_path: Path | str):
        self.scenario_path = Path(scenario_path)
        with open(self.scenario_path, "r", encoding="utf-8") as f:
            self.metadata: Dict[str, Any] = json.load(f)
        self.records: List[Dict[str, Any]] = self.metadata.get("time_series", [])
        self.cursor: int = 0

    def total_steps(self) -> int:
        return len(self.records)

    def get_current(self) -> Dict[str, Any]:
        if not self.records:
            return {}
        idx = min(self.cursor, len(self.records) - 1)
        return self.records[idx]

    def seek(self, step_index: int) -> Dict[str, Any]:
        self.cursor = max(0, min(step_index, len(self.records) - 1))
        return self.get_current()

    def step(self) -> Optional[Dict[str, Any]]:
        if self.cursor < len(self.records) - 1:
            self.cursor += 1
            return self.get_current()
        return None

    def get_history(self, up_to_current: bool = True) -> List[Dict[str, Any]]:
        if up_to_current:
            return self.records[: self.cursor + 1]
        return self.records


class SensorQualityGate:
    """
    Validates physical sanity of biometric and environmental telemetry
    to prevent sensor noise or flatlines from triggering false alarms.
    """
    @staticmethod
    def validate(reading: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        hr = reading.get("heart_rate_bpm", 0)
        spo2 = reading.get("spo2_pct", 0)
        co2 = reading.get("ambient_co2_mmHg", 0)
        dose = reading.get("cumulative_dose_mSv", 0)

        if hr < 20 or hr > 220:
            issues.append(f"Heart rate out-of-bounds: {hr} bpm")
        if spo2 < 50 or spo2 > 100:
            issues.append(f"SpO2 out-of-bounds: {spo2}%")
        if co2 < 0 or co2 > 50:
            issues.append(f"Cabin CO2 reading irrational: {co2} mmHg")
        if dose < 0:
            issues.append(f"Negative cumulative radiation: {dose} mSv")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "reading": reading
        }
