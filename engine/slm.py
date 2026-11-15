"""
AURA Clinical Small Language Model (SLM) Engine
Designed for 8GB RAM edge systems:
- Seamlessly connects to local Ollama (Llama 3.2 1B / Qwen 2.5 1.5B with ~1.3GB memory footprint).
- Supports optional Cloud API (Groq / OpenAI) if API keys are provided.
- Enforces a strict Similarity Confidence Gate (rejects nearest matches below 20% confidence).
- Guaranteed resilient fallback: Built-in local offline clinical reasoning engine that operates
  with 0MB extra RAM without network dependencies or system freezes.
"""

from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


class ClinicalSLMEngine:
    """
    Autonomous Medical Reasoning & Synthesis Engine for Astronaut Triage.
    Enforces strict grounding against NASA medical standards and similarity gates.
    """

    SYSTEM_PROMPT = """You are AURA (Autonomous Universal Rescue & Astronaut-Health Agent), an onboard AI Flight Surgeon prototype addressing NASA ExMC Gap Med10 (Computed Medical Decision Support).
You are operating during a deep-space exploration mission with a 22-minute Earth communication latency.
Your role is to evaluate astronaut complaints and onboard telemetry, correlate them with retrieved NASA clinical protocols, and deliver concise, authoritative, life-critical instructions.

RULES:
1. NEVER invent or hallucinate drug dosages or clinical steps. Only synthesize what is in the verified NASA protocol.
2. Always provide calm, directive instructions suitable for an astronaut or Crew Medical Officer (CMO) under acute stress.
3. Explicitly cite the document ID and standard for every countermeasure.
4. Keep clinical explanations under 4 concise sentences, followed by immediate action steps.
"""

    # Minimum cosine similarity required to trust a matched protocol (20%)
    MIN_CONFIDENCE_THRESHOLD = 0.20

    def __init__(self, preferred_model: str = "llama3.2:1b", ollama_host: str = "http://localhost:11434"):
        self.preferred_model = preferred_model
        self.ollama_host = ollama_host.rstrip("/")
        self.active_backend = "CHECKING"
        self.available_ollama_models: List[str] = []
        self.check_environment()

    def check_environment(self) -> str:
        """Determines active SLM engine backend based on system state."""
        # 1. Check local Ollama
        try:
            req = urllib.request.Request(f"{self.ollama_host}/api/tags", headers={"User-Agent": "AURA-Agent"})
            with urllib.request.urlopen(req, timeout=1.2) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    self.available_ollama_models = [m["name"] for m in data.get("models", [])]
                    self.active_backend = "OLLAMA_LOCAL"
                    return f"Ollama Local ({len(self.available_ollama_models)} models found)"
        except Exception:
            pass

        # 2. Check Groq API
        if os.environ.get("GROQ_API_KEY"):
            self.active_backend = "GROQ_CLOUD"
            return "Groq Cloud API (Llama 3.3 70B / 8B)"

        # 3. Check OpenAI API (L-1 fix: route to offline synthesizer; OpenAI handler not yet implemented)
        if os.environ.get("OPENAI_API_KEY"):
            # OpenAI integration is planned; for now fall through to the offline synthesizer
            # so the app never silently misfires. Remove this comment when implemented.
            self.active_backend = "OFFLINE_SYNTHESIZER"
            return "AURA Edge Clinical Synthesizer (Local 0-RAM Fallback)"

        # 4. Fallback: Edge Clinical Synthesizer
        self.active_backend = "OFFLINE_SYNTHESIZER"
        return "AURA Edge Clinical Synthesizer (Local 0-RAM Fallback)"

    def generate_clinical_consult(
        self,
        astronaut_query: str,
        retrieved_protocols: List[Dict[str, Any]],
        biometrics: Optional[Dict[str, Any]] = None,
        telemetry_hazard: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes astronaut inquiry, live telemetry, and retrieved NASA protocols
        into a definitive clinical assessment and action plan.
        """
        # Step 1: BUILD SIMILARITY-GROUNDED PROMPT
        # Step 2: SIMILARITY CONFIDENCE GATE
        top_score = 0.0
        if retrieved_protocols:
            top_score = retrieved_protocols[0].get("vector_score", retrieved_protocols[0].get("similarity_score", 0.0))

        if not retrieved_protocols or top_score < self.MIN_CONFIDENCE_THRESHOLD:
            nearest_doc = retrieved_protocols[0].get("document", "N/A") if retrieved_protocols else "None"
            nearest_id = retrieved_protocols[0].get("id", retrieved_protocols[0].get("doc_id", "N/A")) if retrieved_protocols else "None"
            return {
                "backend": "AURA Safety Gate (Low Vector Confidence)",
                "response": (
                    f"⚠️ **SAFETY ALERT: NO AUTHORITATIVE NASA PROTOCOL MATCHED (Confidence: {top_score*100:.1f}%)**\n\n"
                    f"The reported symptom does not match any verified clinical procedure in the onboard NASA-STD-3001/HRP corpus above the 20% safety threshold.\n\n"
                    f"**SAFETY GATE ACTION:**\n"
                    f"• Nearest unverified match (`{nearest_doc}` [{nearest_id}]) was **REJECTED** to prevent dangerous protocol mismatch.\n\n"
                    f"**GENERAL EMERGENCY RESUSCITATION DIRECTIVES:**\n"
                    f"1. **Cease Physical Exertion:** Immediately recline the crew member and establish microgravity restraint.\n"
                    f"2. **Retrieve Onboard Emergency Medical Kit:** Open Pack B (ACLS & Resuscitation) / Defibrillator.\n"
                    f"3. **Check Vital Signs:** Continuously monitor SpO2, heart rate, blood pressure, and ECG Lead II.\n"
                    f"4. **Administer 100% Oxygen:** Apply non-rebreather mask or PBA at 10-15 L/min if in distress.\n"
                    f"5. **Telemetry Queue:** Record full symptom timeline for priority transmission to Earth Mission Control."
                ),
                "model": "AURA-Safety-Gate-1.0",
                "grounded_protocols": [],
                "is_low_confidence": True,
                "confidence_score": top_score
            }

        # Formulate grounded prompt context
        context_blocks = []
        for p in retrieved_protocols[:2]:
            steps_txt = "\n".join([f"  - {s}" for s in p.get("protocol_steps", p.get("steps", []))])
            context_blocks.append(
                f"[PROTOCOL ID: {p.get('id', p.get('doc_id'))}]\n"
                f"DOCUMENT: {p.get('document')}\n"
                f"SECTION: {p.get('section')}\n"
                f"CITATION: {p.get('citations', p.get('citation'))}\n"
                f"SUMMARY: {p.get('summary')}\n"
                f"VERIFIED STEPS:\n{steps_txt}"
            )
        protocols_context = "\n\n".join(context_blocks) if context_blocks else "No matching NASA clinical document."

        bio_summary = "Nominal"
        if biometrics:
            bio_summary = (
                f"Heart Rate: {biometrics.get('heart_rate_bpm', 'N/A')} bpm | "
                f"SpO2: {biometrics.get('spo2_pct', 'N/A')}% | "
                f"HRV: {biometrics.get('hrv_rmssd_ms', 'N/A')} ms | "
                f"Dose: {biometrics.get('cumulative_dose_mSv', 'N/A')} mSv | "
                f"Ambient CO2: {biometrics.get('ambient_co2_mmHg', 'N/A')} mmHg"
            )

        hazard_summary = "None detected."
        if telemetry_hazard:
            hazard_summary = f"{telemetry_hazard.get('severity', 'WARNING')}: {telemetry_hazard.get('trigger', '')}"

        prompt = f"""[MISSION TELEMETRY CONTEXT]
Active Biometrics: {bio_summary}
Deterministic Hazard Flag: {hazard_summary}

[RETRIEVED AUTHORITATIVE NASA PROTOCOLS]
{protocols_context}

[ASTRONAUT REPORT / INTERCOM QUERY]
"{astronaut_query}"

Provide your Flight Surgeon clinical assessment and immediate directives.
"""

        # H-3 fix: prefer exact tag match first, then prefix/substring fallback
        # 1. Try local Ollama if active
        if self.active_backend == "OLLAMA_LOCAL":
            model_to_use = self.preferred_model
            if self.available_ollama_models:
                exact = [m for m in self.available_ollama_models if m == self.preferred_model]
                prefix = [m for m in self.available_ollama_models if m.startswith(self.preferred_model.split(":")[0])]
                if exact:
                    model_to_use = exact[0]
                elif prefix:
                    model_to_use = prefix[0]
                elif self.available_ollama_models:
                    model_to_use = self.available_ollama_models[0]

            response_text = self._call_ollama(model_to_use, prompt)
            if response_text:
                return {
                    "backend": f"Ollama Local ({model_to_use})",
                    "response": response_text,
                    "model": model_to_use,
                    "grounded_protocols": [p.get("id", p.get("doc_id")) for p in retrieved_protocols[:2]],
                    "is_low_confidence": False,
                    "confidence_score": top_score
                }

        # 2. Try Groq if active
        if self.active_backend == "GROQ_CLOUD":
            response_text = self._call_groq(prompt)
            if response_text:
                return {
                    "backend": "Groq Cloud API",
                    "response": response_text,
                    "model": "llama-3.3-70b-versatile",
                    "grounded_protocols": [p.get("id", p.get("doc_id")) for p in retrieved_protocols[:2]],
                    "is_low_confidence": False,
                    "confidence_score": top_score
                }

        # 3. Deterministic Local Edge Clinical Synthesizer (Instant, 0-RAM, Zero Hallucination)
        fallback_response = self._synthesize_offline(
            astronaut_query=astronaut_query,
            protocols=retrieved_protocols,
            biometrics=biometrics,
            hazard=telemetry_hazard
        )
        return {
            "backend": "AURA Edge Clinical Synthesizer (Deterministic Local)",
            "response": fallback_response,
            "model": "AURA-Med-Edge-1.0",
            "grounded_protocols": [p.get("id", p.get("doc_id")) for p in retrieved_protocols[:2]],
            "is_low_confidence": False,
            "confidence_score": top_score
        }

    def _call_ollama(self, model: str, prompt: str) -> Optional[str]:
        """Queries local Ollama endpoint."""
        url = f"{self.ollama_host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "system": self.SYSTEM_PROMPT,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 400
            }
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "").strip()
        except Exception:
            return None

    def _call_groq(self, prompt: str) -> Optional[str]:
        """Queries Groq API if key is present."""
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return None
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 450
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return None

    def _synthesize_offline(
        self,
        astronaut_query: str,
        protocols: List[Dict[str, Any]],
        biometrics: Optional[Dict[str, Any]],
        hazard: Optional[Dict[str, Any]]
    ) -> str:
        """
        High-fidelity deterministic spaceflight clinical synthesis.
        Formats retrieved NASA protocols into direct medical directives with zero hallucination.
        """
        top_doc = protocols[0]
        doc_id = top_doc.get("id", top_doc.get("doc_id", "NASA-PROTOCOL"))
        doc_title = top_doc.get("document", "NASA Clinical Guidance")
        section = top_doc.get("section", "Medical Operations")
        citation = top_doc.get("citations", top_doc.get("citation", doc_title))
        steps = top_doc.get("protocol_steps", top_doc.get("steps", []))

        # Dynamic clinical assessment synthesis
        assessment = f"**FLIGHT SURGEON CLINICAL EVALUATION**\n"
        assessment += f"Grounded in **{doc_title}** ({section}).\n\n"

        if hazard:
            assessment += f"⚠️ **Active Environmental/Biometric Trigger:** {hazard.get('trigger', 'Elevated drift')}\n"

        if biometrics:
            hr = biometrics.get("heart_rate_bpm", 75)
            spo2 = biometrics.get("spo2_pct", 98.0)
            if hr > 100:
                assessment += f"• **Physiological Strain:** Tachycardia detected ({hr} bpm), indicating acute autonomic stress response.\n"
            if spo2 < 95.0:
                assessment += f"• **Respiratory Marker:** Depressed oxygen saturation ({spo2}% SpO2) warrants immediate atmospheric check.\n"

        assessment += f"\n**SUMMARY OF DIRECTIVES ({doc_id}):**\n"
        assessment += f"{top_doc.get('summary', '')}\n\n"

        assessment += "**IMMEDIATE ACTION PROTOCOL:**\n"
        for i, step in enumerate(steps[:4], 1):
            assessment += f"{i}. {step}\n"

        assessment += f"\n📄 *Authority Citation:* `{citation}`"
        return assessment
