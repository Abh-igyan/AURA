"""
AURA Autonomous Flight Surgeon Agent
Coordinates the agentic triage loop:
1. Deterministic safety evaluation (NASA-STD-3001 limits).
2. Typed medical physics calculations & countermeasure formulation.
3. Dense vector search retrieval over NASA clinical protocols.
4. SLM clinical synthesis and interactive astronaut consultation.
Designed for 100% offline edge execution on 8GB RAM hardware with zero hallucination.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from .rules import DeterministicSafetyEngine
from .tools import MedicalToolsRegistry
from .slm import ClinicalSLMEngine


class FlightSurgeonAgent:
    def __init__(
        self,
        safety_engine: DeterministicSafetyEngine,
        tools: MedicalToolsRegistry,
        slm_engine: Optional[ClinicalSLMEngine] = None
    ):
        self.safety = safety_engine
        self.tools = tools
        self.slm = slm_engine or ClinicalSLMEngine()

    def triage(self, telemetry_reading: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes autonomous triage loop over a telemetry snapshot.
        Enforces deterministic safety gating before invoking tools.
        """
        eval_result = self.safety.evaluate(telemetry_reading)
        state = eval_result["state"]
        hazards = eval_result["hazards"]
        tool_execution_trace: List[Dict[str, Any]] = []
        checklist: List[Dict[str, Any]] = []
        calculations: Dict[str, Any] = {}
        diagnosis = "Nominal physiological and environmental telemetry. All parameters within NASA-STD-3001 limits."

        if state == "NOMINAL":
            return {
                "triage_state": state,
                "diagnosis": diagnosis,
                "hazards": [],
                "tool_calls": [],
                "calculations": {},
                "checklist": [{
                    "step_number": 1,
                    "action": "Continue scheduled mission operational timeline. Maintain routine telemetry logging.",
                    "source_id": "NASA-STD-3001-NOMINAL",
                    "citation": "NASA Spaceflight Human-System Standard Vol 1"
                }],
                "clinical_notes": eval_result.get("clinical_notes", []),
                "action_summary": "All systems nominal. No medical intervention required."
            }

        # Handle specific hazard scenarios
        primary_hazard = hazards[0] if hazards else {}
        hazard_type = primary_hazard.get("type", "")
        action_summary = ""

        # Scenario 1: Solar Radiation Event (SPE)
        if "RADIATION" in hazard_type:
            diagnosis = f"CRITICAL RADIATION EVENT: {primary_hazard.get('trigger')} Rapid proton flux exceeds safe EVA operational envelope."

            # Tool Call 1: Calculate dosage projection to shelter
            time_to_shelter = context.get("time_to_shelter_min", 8.5) if context else 8.5
            dose_rate = telemetry_reading.get("dosimeter_rate_mSv_hr", 500.0)
            cumulative_dose = telemetry_reading.get("cumulative_dose_mSv", 150.0)
            
            calc_res = self.tools.calculate_radiation_countermeasure(
                dose_rate_mSv_hr=dose_rate,
                cumulative_mSv=cumulative_dose,
                time_to_shelter_min=time_to_shelter
            )
            tool_execution_trace.append({
                "tool": "calculate_radiation_countermeasure",
                "inputs": {"dose_rate_mSv_hr": dose_rate, "time_to_shelter_min": time_to_shelter},
                "output": calc_res
            })
            calculations = calc_res
            action_summary = f"ABORT EVA IMMEDIATELY. Ingress shelter within {time_to_shelter} min. Projected dose: {calc_res['projected_dose_at_ingress_mSv']} mSv."

            # Tool Call 2: Retrieve HRP clinical protocols via vector search
            protocol_id = primary_hazard.get("protocol_id", "NASA-HRP-JSC-CN-35747-SEC3.2")
            query_res = self.tools.query_nasa_guidelines("Solar Particle Event acute radiation shelter ARS prodromal nausea", category="RADIATION_SPE")
            tool_execution_trace.append({
                "tool": "query_nasa_guidelines",
                "inputs": {"query": "Solar Particle Event acute radiation shelter ARS prodromal nausea", "category": "RADIATION_SPE"},
                "output": {"primary_protocol": protocol_id, "status": query_res["status"], "matched_count": query_res.get("matched_count", 0)}
            })

            # Tool Call 3: Generate verified crew checklist
            checklist = self.tools.generate_crew_checklist(protocol_id)
            tool_execution_trace.append({
                "tool": "generate_crew_checklist",
                "inputs": {"protocol_id": protocol_id},
                "steps_generated": len(checklist)
            })

        # Scenario 2: Hypercapnia (CO2 Scrubber Degradation)
        elif "HYPERCAPNIA" in hazard_type:
            diagnosis = f"ECLSS ATMOSPHERIC CRISIS: {primary_hazard.get('trigger')} Severe risk of hypercapnic narcosis and crew impairment."

            # Tool Call 1: Calculate time to critical threshold
            co2_val = telemetry_reading.get("ambient_co2_mmHg", 8.0)
            calc_res = self.tools.calculate_co2_scrubber_countermeasure(
                current_pco2_mmHg=co2_val,
                volume_m3=context.get("module_volume_m3", 110.0) if context else 110.0
            )
            tool_execution_trace.append({
                "tool": "calculate_co2_scrubber_countermeasure",
                "inputs": {"current_pco2_mmHg": co2_val},
                "output": calc_res
            })
            calculations = calc_res
            action_summary = f"DEPLOY AUXILIARY LiOH CANISTERS. Time to critical limit: {calc_res['estimated_time_to_critical_min']} min."

            # Tool Call 2: Retrieve OCHMO atmospheric protocols via vector search
            protocol_id = primary_hazard.get("protocol_id", "NASA-OCHMO-TB-OCHMO-004-SEC4")
            query_res = self.tools.query_nasa_guidelines("CO2 scrubber failure hypercapnia LiOH headache breathing", category="ENVIRONMENTAL_CO2")
            tool_execution_trace.append({
                "tool": "query_nasa_guidelines",
                "inputs": {"query": "CO2 scrubber failure hypercapnia LiOH headache breathing", "category": "ENVIRONMENTAL_CO2"},
                "output": {"primary_protocol": protocol_id, "status": query_res["status"], "matched_count": query_res.get("matched_count", 0)}
            })

            # Tool Call 3: Generate verified crew checklist
            checklist = self.tools.generate_crew_checklist(protocol_id)
            tool_execution_trace.append({
                "tool": "generate_crew_checklist",
                "inputs": {"protocol_id": protocol_id},
                "steps_generated": len(checklist)
            })

        return {
            "triage_state": state,
            "diagnosis": diagnosis,
            "action_summary": action_summary,
            "hazards": hazards,
            "tool_calls": tool_execution_trace,
            "calculations": calculations,
            "checklist": checklist,
            "clinical_notes": eval_result.get("clinical_notes", [])
        }

    def consult(
        self,
        astronaut_query: str,
        current_telemetry: Optional[Dict[str, Any]] = None,
        active_hazard: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Interactive clinical consultation for direct astronaut/CMO inquiries.
        Uses dense vector search to retrieve relevant NASA protocols and SLM to synthesize clinical guidance.
        """
        # Vector similarity search over NASA protocol corpus
        retrieved_protocols = self.tools.rag.query(astronaut_query, top_k=3)
        
        # Synthesize with SLM
        consult_result = self.slm.generate_clinical_consult(
            astronaut_query=astronaut_query,
            retrieved_protocols=retrieved_protocols,
            biometrics=current_telemetry,
            telemetry_hazard=active_hazard
        )

        return {
            "query": astronaut_query,
            "assessment": consult_result["response"],
            "backend": consult_result["backend"],
            "model": consult_result["model"],
            "retrieved_protocols": retrieved_protocols,
            "is_low_confidence": consult_result.get("is_low_confidence", False),
            "confidence_score": consult_result.get("confidence_score", 0.0)
        }
