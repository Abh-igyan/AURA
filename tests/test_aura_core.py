"""
AURA Unit & System Test Suite
Tests:
- Vector Store dense embeddings and cosine similarity retrieval
- Deterministic NASA-STD-3001 Safety Engine evaluations
- Physics and dosage calculation tools
- Clinical SLM fallback & prompt grounding
- Autonomous Flight Surgeon Agent triage loop
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.vector_store import VectorStore
from engine.rag import GroundedMedicalRAG
from engine.rules import DeterministicSafetyEngine
from engine.tools import MedicalToolsRegistry
from engine.slm import ClinicalSLMEngine
from engine.agent import FlightSurgeonAgent
from engine.telemetry import TelemetryStream, SensorQualityGate


def test_vector_store():
    print("[1/6] Testing Vector Store & Cosine Similarity Retrieval...")
    data_path = PROJECT_ROOT / "data" / "nasa_hrp_clinical_guidelines.json"
    vs = VectorStore(data_path)
    assert len(vs.corpus) >= 5, "Corpus should have at least 5 NASA protocols"
    assert len(vs.chunks) >= 10, "Should generate overview and procedure chunks"

    # Query 1: Radiation & Nausea
    res_rad = vs.search("astronaut experiencing acute nausea after solar particle storm", top_k=2)
    assert len(res_rad) > 0, "Should match radiation protocol"
    assert res_rad[0]["doc_id"] == "NASA-HRP-JSC-CN-35747-SEC3.2", f"Expected radiation protocol, got {res_rad[0]['doc_id']}"
    assert res_rad[0]["similarity_score"] > 0.1, "Cosine score should be positive"

    # Query 2: CO2 Scrubber & Headache
    res_co2 = vs.search("carbon dioxide scrubber failure crew headache dyspnea", top_k=2)
    assert len(res_co2) > 0, "Should match CO2 protocol"
    assert res_co2[0]["doc_id"] == "NASA-OCHMO-TB-OCHMO-004-SEC4", f"Expected CO2 protocol, got {res_co2[0]['doc_id']}"

    # Query 3: SANS / Vision Blurriness
    res_sans = vs.search("optic disc edema blurry vision intracranial pressure shift", top_k=2)
    assert len(res_sans) > 0, "Should match SANS protocol"
    assert res_sans[0]["doc_id"] == "NASA-HRP-SANS-EVIDENCE-2022", f"Expected SANS protocol, got {res_sans[0]['doc_id']}"

    # Query 4: Cardiovascular ACLS / Heart Attack
    res_cardio = vs.search("heart attack crushing chest pain defibrillator aspirin", top_k=2)
    assert len(res_cardio) > 0, "Should match Cardiac ACLS protocol"
    assert res_cardio[0]["doc_id"] == "NASA-CHECS-CARDIO-ACLS-2023", f"Expected Cardiac protocol, got {res_cardio[0]['doc_id']}"

    print("  -> Vector Store passed with 100% precision across radiation, CO2, SANS, and Cardiac ACLS!")


def test_safety_rules():
    print("[2/6] Testing NASA-STD-3001 Deterministic Safety Engine...")
    thresholds_path = PROJECT_ROOT / "data" / "nasa_std_3001_thresholds.json"
    safety = DeterministicSafetyEngine(thresholds_path)

    # Nominal reading
    nom_eval = safety.evaluate({
        "cumulative_dose_mSv": 5.0,
        "ambient_co2_mmHg": 2.0,
        "heart_rate_bpm": 72,
        "spo2_pct": 98.0
    })
    assert nom_eval["state"] == "NOMINAL", f"Expected NOMINAL, got {nom_eval['state']}"

    # Emergency Radiation reading (> 250 mSv)
    rad_eval = safety.evaluate({
        "cumulative_dose_mSv": 272.0,
        "dosimeter_rate_mSv_hr": 2500.0,
        "ambient_co2_mmHg": 2.0,
        "heart_rate_bpm": 115
    })
    assert rad_eval["state"] == "EMERGENCY", f"Expected EMERGENCY, got {rad_eval['state']}"
    assert any("RADIATION" in h["type"] for h in rad_eval["hazards"])

    # Emergency CO2 reading (> 10 mmHg)
    co2_eval = safety.evaluate({
        "cumulative_dose_mSv": 2.0,
        "ambient_co2_mmHg": 11.2,
        "heart_rate_bpm": 105
    })
    assert co2_eval["state"] == "EMERGENCY", f"Expected EMERGENCY, got {co2_eval['state']}"
    assert any("HYPERCAPNIA" in h["type"] for h in co2_eval["hazards"])

    # Hypoxia critical test (SpO2 < 88%)
    hypoxia_eval = safety.evaluate({
        "cumulative_dose_mSv": 2.0,
        "ambient_co2_mmHg": 1.5,
        "heart_rate_bpm": 85,
        "spo2_pct": 86.0
    })
    assert hypoxia_eval["state"] == "EMERGENCY"
    assert any("HYPOXIA" in h["type"] for h in hypoxia_eval["hazards"])

    # Bradycardia test (HR < 50 bpm)
    brady_eval = safety.evaluate({
        "cumulative_dose_mSv": 2.0,
        "ambient_co2_mmHg": 1.5,
        "heart_rate_bpm": 38,
        "spo2_pct": 98.0
    })
    assert brady_eval["state"] == "ALERT"
    assert any("BRADYCARDIA" in h["type"] for h in brady_eval["hazards"])

    print("  -> Deterministic Safety Engine passed all NASA threshold boundaries!")


def test_medical_tools():
    print("[3/6] Testing Typed Medical Calculation Tools...")
    data_path = PROJECT_ROOT / "data" / "nasa_hrp_clinical_guidelines.json"
    rag = GroundedMedicalRAG(data_path)
    tools = MedicalToolsRegistry(rag)

    # Radiation countermeasure calculation
    rad_calc = tools.calculate_radiation_countermeasure(
        dose_rate_mSv_hr=200.0,
        cumulative_mSv=150.0,
        time_to_shelter_min=10.0
    )
    # Projected additional: (200 / 60) * 10 = 33.3 mSv -> total = 183.3 mSv
    assert rad_calc["projected_dose_at_ingress_mSv"] == 183.3
    assert rad_calc["safe_margin_mSv"] == 66.7
    assert rad_calc["exceeds_limit"] is False

    # CO2 countermeasure calculation
    co2_calc = tools.calculate_co2_scrubber_countermeasure(
        current_pco2_mmHg=8.0,
        volume_m3=110.0,
        crew_count=4
    )
    assert co2_calc["estimated_time_to_critical_min"] > 0
    assert co2_calc["recommendation"] == "DEPLOY_AUXILIARY_LIOH"

    print("  -> Medical Tools passed deterministic physics formulas!")


def test_slm_engine():
    print("[4/6] Testing SLM Clinical Synthesis Engine...")
    data_path = PROJECT_ROOT / "data" / "nasa_hrp_clinical_guidelines.json"
    vs = VectorStore(data_path)
    slm = ClinicalSLMEngine()
    
    print(f"  -> Detected SLM Backend: {slm.active_backend}")
    retrieved = vs.search("headache and stuffy air carbon dioxide", top_k=1)
    
    consult = slm.generate_clinical_consult(
        astronaut_query="I have a throbbing frontal headache and the cabin air feels thick.",
        retrieved_protocols=retrieved,
        biometrics={"heart_rate_bpm": 98, "spo2_pct": 97.0, "ambient_co2_mmHg": 8.5}
    )
    assert "response" in consult and len(consult["response"]) > 50
    assert "backend" in consult
    assert consult["is_low_confidence"] is False

    # Test Step 2: Similarity Confidence Gate on completely unindexed/random query
    unindexed_consult = slm.generate_clinical_consult(
        astronaut_query="quantum teleportation laser flux",
        retrieved_protocols=[],
        biometrics=None
    )
    assert unindexed_consult["is_low_confidence"] is True
    assert "SAFETY ALERT" in unindexed_consult["response"]
    print("  -> SLM Synthesis and Similarity Confidence Gate successfully verified!")


def test_agent_triage():
    print("[5/6] Testing FlightSurgeonAgent Full Triage Loop...")
    thresholds_path = PROJECT_ROOT / "data" / "nasa_std_3001_thresholds.json"
    guidelines_path = PROJECT_ROOT / "data" / "nasa_hrp_clinical_guidelines.json"
    
    safety = DeterministicSafetyEngine(thresholds_path)
    rag = GroundedMedicalRAG(guidelines_path)
    tools = MedicalToolsRegistry(rag)
    agent = FlightSurgeonAgent(safety, tools)

    # Triage high radiation snapshot
    reading = {
        "cumulative_dose_mSv": 272.0,
        "dosimeter_rate_mSv_hr": 2500.0,
        "ambient_co2_mmHg": 1.5,
        "heart_rate_bpm": 112,
        "spo2_pct": 97.0,
        "hrv_rmssd_ms": 16.0
    }
    result = agent.triage(reading, context={"time_to_shelter_min": 8.5})
    assert result["triage_state"] == "EMERGENCY"
    assert len(result["tool_calls"]) == 3
    assert len(result["checklist"]) > 0
    assert result["checklist"][0]["citation"] is not None

    # Test Interactive Consult
    consult_res = agent.consult("What should I do if my eyes start blurring during long duration flight?")
    assert len(consult_res["retrieved_protocols"]) > 0
    assert "NASA-HRP-SANS-EVIDENCE-2022" in consult_res["retrieved_protocols"][0]["id"]

    print("  -> Agent Triage Loop and Interactive Consult fully verified!")


def test_telemetry_quality():
    print("[6/6] Testing Telemetry Quality Gate & Stream Player...")
    scenario_file = PROJECT_ROOT / "data" / "scenario_solar_radiation.json"
    stream = TelemetryStream(scenario_file)
    assert stream.total_steps() >= 7
    first = stream.get_current()
    assert SensorQualityGate.validate(first)["valid"] is True

    # Bad telemetry
    bad = SensorQualityGate.validate({"heart_rate_bpm": 350, "spo2_pct": 120})
    assert bad["valid"] is False
    assert len(bad["issues"]) == 2
    # Nominal stream test
    nom_file = PROJECT_ROOT / "data" / "scenario_nominal_baseline.json"
    nom_stream = TelemetryStream(nom_file)
    assert nom_stream.total_steps() >= 5
    for rec in nom_stream.records:
        assert SensorQualityGate.validate(rec)["valid"] is True

    print("  -> Telemetry Quality Gate passed!")


if __name__ == "__main__":
    print("==================================================")
    print("🚀 RUNNING AURA CORE INTEGRATION TEST SUITE")
    print("==================================================")
    test_vector_store()
    test_safety_rules()
    test_medical_tools()
    test_slm_engine()
    test_agent_triage()
    test_telemetry_quality()
    print("==================================================")
    print("✅ ALL AURA ENGINE TESTS PASSED SUCCESSFULLY!")
    print("==================================================")
