from data.patient_data import PatientProfile
from agents.vital_monitor import VitalSignsMonitorAgent
from agents.risk_analysis import RiskAnalysisAgent
from agents.medical_rag import MedicalRAGAgent, init_settings
from agents.memory_manager import AgentMemoryManager

class MediAgentOrchestrator:

    def __init__(self):
        print("\n[MediAgent] Initializing Multi-Agent System...")
        init_settings()
        self.vital_monitor   = VitalSignsMonitorAgent()
        self.risk_analyzer   = RiskAnalysisAgent()
        self.rag_agent       = MedicalRAGAgent()
        self.memory          = AgentMemoryManager()
        print("[MediAgent] All agents ready ✓\n")

    def run(self, patient: PatientProfile) -> dict:
        print(f"[Orchestrator] Processing: {patient.name} ({patient.patient_id})")

        # ── Ambil Memory / History ───────────────────────
        history_context = self.memory.build_context_summary(patient.patient_id)
        has_history     = "No previous" not in history_context
        if has_history:
            print(f"[Memory] History found for {patient.patient_id}")
        else:
            print(f"[Memory] First session for {patient.patient_id}")

        # ── Agent 1: Vital Signs Monitor ────────────────
        print("[Agent 1] Vital Signs Monitor...")
        vital_result = self.vital_monitor.analyze(patient)
        print(f"[Agent 1] → {vital_result['overall_status']}")

        # ── Agent 2: Risk Analysis (dengan memory context) ─
        print("[Agent 2] Risk Analysis...")
        risk_result = self.risk_analyzer.analyze(
            patient,
            vital_result,
            history_context=history_context   # ← inject memory ke LLM
        )

        # ── Agent 3: RAG (conditional) ───────────────────
        rag_result = None
        if vital_result["overall_status"] in ["WARNING", "CRITICAL"]:
            print("[Agent 3] Medical RAG...")
            problem_params = (
                vital_result["critical_params"] +
                vital_result["warning_params"]
            )
            rag_query  = (
                f"Patient has {patient.conditions}. "
                f"Abnormal vitals: {', '.join(problem_params)}. "
                f"What are the clinical protocols and monitoring guidelines?"
            )
            rag_result = self.rag_agent.query(rag_query)
        else:
            print("[Agent 3] Skipped — vitals NORMAL")

        # ── Simpan ke Memory ─────────────────────────────
        session_data = {
            "overall_status" : vital_result["overall_status"],
            "risk_level"     : risk_result["risk_level"],
            "critical_params": vital_result["critical_params"],
            "warning_params" : vital_result["warning_params"],
        }
        self.memory.save_session(patient.patient_id, session_data)

        # Save alert kalau WARNING/CRITICAL
        if vital_result["overall_status"] != "NORMAL":
            self.memory.save_alert(patient.patient_id, {
                "status" : vital_result["overall_status"],
                "params" : vital_result["critical_params"] + vital_result["warning_params"]
            })

        # ── Final Report ─────────────────────────────────
        return {
            "patient"        : patient.name,
            "patient_id"     : patient.patient_id,
            "age"            : patient.age,
            "conditions"     : patient.conditions,
            "vital_analysis" : vital_result,
            "risk_analysis"  : risk_result,
            "rag_guidance"   : rag_result,
            "memory_context" : history_context,
        }