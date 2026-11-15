"""
AURA Typed Medical Tools
Functions callable by the autonomous agent to execute verified medical calculations,
protocol lookups, and checklist generation.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .rag import GroundedMedicalRAG


class MedicalToolsRegistry:
    def __init__(self, rag_engine: GroundedMedicalRAG):
        self.rag = rag_engine

    def query_nasa_guidelines(self, query: str, category: str = "") -> Dict[str, Any]:
        """Tool: Query NASA space medicine protocols from the local grounded corpus."""
        docs = self.rag.query(query, category if category else None)
        if not docs:
            return {
                "status": "NOT_FOUND",
                "message": "No verified NASA protocol found in closed corpus. Escalate to ground telemetry log.",
                "protocols": []
            }
        return {
            "status": "SUCCESS",
            "matched_count": len(docs),
            "primary_protocol": docs[0]["id"],
            "protocols": docs
        }

    def calculate_radiation_countermeasure(self, dose_rate_mSv_hr: float, cumulative_mSv: float, time_to_shelter_min: float) -> Dict[str, Any]:
        """
        Tool: Deterministic physics calculation for EVA radiation exposure trajectory.
        Math runs in verified code, never in LLM hallucinations.
        """
        projected_additional_dose = (dose_rate_mSv_hr / 60.0) * time_to_shelter_min
        projected_total_dose = cumulative_mSv + projected_additional_dose
        limit_mSv = 250.0  # NASA-STD-3001 single event limit

        safe_margin = limit_mSv - projected_total_dose
        exceeds_limit = projected_total_dose >= limit_mSv

        return {
            "dose_rate_mSv_hr": dose_rate_mSv_hr,
            "cumulative_dose_mSv": cumulative_mSv,
            "time_to_shelter_min": time_to_shelter_min,
            "projected_dose_at_ingress_mSv": round(projected_total_dose, 1),
            "single_event_limit_mSv": limit_mSv,
            "exceeds_limit": exceeds_limit,
            "safe_margin_mSv": round(safe_margin, 1),
            "recommendation": "IMMEDIATE_SHELTER_INGRESS" if exceeds_limit or projected_total_dose > 150.0 else "PREPARE_TERMINATION"
        }

    def calculate_co2_scrubber_countermeasure(self, current_pco2_mmHg: float, volume_m3: float = 110.0, crew_count: int = 4) -> Dict[str, Any]:
        """
        Tool: Deterministic cabin atmospheric buildup calculation.
        Estimates time until critical hypercapnia (10.0 mmHg) without scrubbing.
        """
        # H-6 fix: corrected CO2 buildup physics.
        # Human CO2 production ≈ 200 mL/min = 0.012 m³/hr per person.
        # Volume fraction contribution per person per hour = 0.012 / volume_m3.
        # CO2 partial pressure rise rate (mmHg/hr) = volume_fraction_rate * 760 mmHg.
        # With scrubber fully failed, this gives the worst-case buildup rate.
        co2_production_m3_hr_per_person = 0.012  # standard metabolic rate
        co2_volume_fraction_rate = (crew_count * co2_production_m3_hr_per_person) / volume_m3
        co2_generation_rate_mmHg_hr = co2_volume_fraction_rate * 760.0
        limit_mmHg = 10.0
        delta_to_limit = max(0.0, limit_mmHg - current_pco2_mmHg)

        time_to_critical_min = (delta_to_limit / max(co2_generation_rate_mmHg_hr, 0.01)) * 60.0 if co2_generation_rate_mmHg_hr > 0 else 999.0

        return {
            "current_pco2_mmHg": current_pco2_mmHg,
            "emergency_limit_mmHg": limit_mmHg,
            "estimated_time_to_critical_min": round(time_to_critical_min, 1),
            "recommendation": "DEPLOY_AUXILIARY_LIOH" if current_pco2_mmHg >= 7.5 else "RECYCLE_PRIMARY_BED"
        }

    def generate_crew_checklist(self, protocol_id: str) -> List[Dict[str, Any]]:
        """Tool: Generate a step-by-step verified action checklist with explicit document ID."""
        doc = self.rag.get_by_id(protocol_id)
        if not doc:
            return [{
                "step_number": 1,
                "action": "Maintain crew stabilization. No specific NASA protocol matched for ID. Queue query for Mission Control.",
                "source_id": "NONE",
                "citation": "UNVERIFIED"
            }]
        return self.rag.format_checklist(doc)
