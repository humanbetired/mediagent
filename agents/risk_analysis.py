from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
import os
from data.patient_data import PatientProfile

LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class RiskAnalysisAgent:

    def __init__(self):
        self.llm = Ollama(
            model=LLM_MODEL,
            base_url = OLLAMA_BASE_URL,
            request_timeout=120.0
        )

    def analyze(
            self,
            patient: PatientProfile,
            vital_findings: dict,
            history_context: str = "No previous sessions recorded."
        ) -> dict:

            findings_text = "\n".join([
                f"- {f['parameter']}: {f['value']} {f['unit']} [{f['status']}]"
                for f in vital_findings["findings"]
            ])

            prompt = f"""You are a clinical risk analysis AI assistant.

        Patient: {patient.name}, Age: {patient.age}
        Known conditions: {', '.join(patient.conditions)}

        PATIENT HISTORY:
        {history_context}

        Current Vital Signs:
        {findings_text}

        Overall Status: {vital_findings['overall_status']}
        Critical parameters: {vital_findings['critical_params'] or 'None'}
        Warning parameters:  {vital_findings['warning_params']  or 'None'}

        Based on the patient profile, history, and current vitals, provide:
        1. RISK LEVEL: (LOW / MODERATE / HIGH / CRITICAL)
        2. PRIMARY CONCERN: Most urgent issue in one sentence
        3. IMMEDIATE ACTIONS: 2-3 specific actions for nursing staff
        4. MONITORING: What to watch in the next hour
        5. TREND NOTE: Any pattern from history worth noting (if history exists)

        Be concise and clinical. No disclaimers."""

            response = self.llm.complete(prompt)

            return {
                "patient_id"     : patient.patient_id,
                "risk_level"     : vital_findings["overall_status"],
                "llm_assessment" : str(response),
                "critical_params": vital_findings["critical_params"],
                "warning_params" : vital_findings["warning_params"],
            }