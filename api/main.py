from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

from data.patient_data import get_sample_patients, PatientProfile, VitalSigns
from agents.orchestrator import MediAgentOrchestrator

# ── App Init ─────────────────────────────────────────────
app = FastAPI(
    title="MediAgent API",
    description="AI-Powered Patient Health Monitoring System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Orchestrator ──────────────────────────────────
orchestrator: Optional[MediAgentOrchestrator] = None

@app.on_event("startup")
async def startup_event():
    global orchestrator
    print("[API] Initializing MediAgent Orchestrator...")
    orchestrator = MediAgentOrchestrator()
    print("[API] Ready ✓")

# ── Pydantic Models ──────────────────────────────────────
class VitalSignsInput(BaseModel):
    heart_rate: float
    systolic_bp: float
    diastolic_bp: float
    spo2: float
    temperature: float
    respiratory_rate: float
    blood_glucose: float

class PatientInput(BaseModel):
    patient_id: str
    name: str
    age: int
    conditions: list[str]
    vitals: VitalSignsInput

# ── Helpers ──────────────────────────────────────────────
def get_sample_patient_map():
    return {p.patient_id: p for p in get_sample_patients()}

# ── Endpoints ────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status"       : "ok",
        "orchestrator" : orchestrator is not None,
        "redis"        : orchestrator.memory.client is not None
                         if orchestrator else False
    }

@app.get("/api/patients")
async def list_patients():
    patients = get_sample_patients()
    return {
        "patients": [
            {
                "patient_id" : p.patient_id,
                "name"       : p.name,
                "age"        : p.age,
                "conditions" : p.conditions,
            }
            for p in patients
        ]
    }

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str):
    patient_map = get_sample_patient_map()
    if patient_id not in patient_map:
        raise HTTPException(status_code=404, detail="Patient not found")

    p = patient_map[patient_id]
    return {
        "patient_id" : p.patient_id,
        "name"       : p.name,
        "age"        : p.age,
        "conditions" : p.conditions,
        "vitals"     : p.vitals.__dict__ if p.vitals else None
    }

@app.get("/api/history/{patient_id}")
async def get_history(patient_id: str):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    history = orchestrator.memory.get_history(patient_id)
    return {"patient_id": patient_id, "history": history}

@app.get("/api/alerts/{patient_id}")
async def get_alerts(patient_id: str):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    alerts = orchestrator.memory.get_alerts(patient_id)
    return {"patient_id": patient_id, "alerts": alerts}

@app.post("/api/analyze/{patient_id}")
async def analyze_patient(patient_id: str):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")

    patient_map = get_sample_patient_map()
    if patient_id not in patient_map:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient = patient_map[patient_id]
    result  = orchestrator.run(patient)

    return {
        "patient_id"    : result["patient_id"],
        "patient_name"  : result["patient"],
        "overall_status": result["vital_analysis"]["overall_status"],
        "findings"      : result["vital_analysis"]["findings"],
        "risk_assessment": result["risk_analysis"]["llm_assessment"],
        "rag_guidance"  : result["rag_guidance"]["answer"]
                          if result["rag_guidance"] else None,
        "memory_context": result["memory_context"],
    }

@app.post("/api/patients/custom")
async def analyze_custom_patient(patient_input: PatientInput):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")

    vitals  = VitalSigns(**patient_input.vitals.dict())
    patient = PatientProfile(
        patient_id = patient_input.patient_id,
        name       = patient_input.name,
        age        = patient_input.age,
        conditions = patient_input.conditions,
        vitals     = vitals
    )

    result = orchestrator.run(patient)
    return {
        "patient_id"     : result["patient_id"],
        "patient_name"   : result["patient"],
        "overall_status" : result["vital_analysis"]["overall_status"],
        "findings"       : result["vital_analysis"]["findings"],
        "risk_assessment": result["risk_analysis"]["llm_assessment"],
        "rag_guidance"   : result["rag_guidance"]["answer"]
                           if result["rag_guidance"] else None,
    }

# ── SSE Streaming Endpoint ───────────────────────────────
@app.get("/api/stream/{patient_id}")
async def stream_analysis(patient_id: str):
    """
    Server-Sent Events — kirim analisis kata per kata ke client.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")

    patient_map = get_sample_patient_map()
    if patient_id not in patient_map:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient = patient_map[patient_id]

    async def event_generator():
        try:
            yield _sse_event("step", {"agent": "VitalMonitor", "status": "running"})
            await asyncio.sleep(0.1)

            vital_result = orchestrator.vital_monitor.analyze(patient)

            yield _sse_event("vital_result", {
                "overall_status" : vital_result["overall_status"],
                "findings"       : vital_result["findings"],
                "critical_params": vital_result["critical_params"],
                "warning_params" : vital_result["warning_params"],
            })

            yield _sse_event("step", {"agent": "RiskAnalysis", "status": "running"})
            await asyncio.sleep(0.1)

            history_context = orchestrator.memory.build_context_summary(patient.patient_id)

            findings_text = "\n".join([
                f"- {f['parameter']}: {f['value']} {f['unit']} [{f['status']}]"
                for f in vital_result["findings"]
            ])

            prompt = f"""You are a clinical risk analysis AI assistant.
                    Patient: {patient.name}, Age: {patient.age}
                    Conditions: {', '.join(patient.conditions)}
                    History: {history_context}
                    Vitals:
                    {findings_text}
                    Overall: {vital_result['overall_status']}

                    Provide risk level, primary concern, immediate actions, and monitoring plan.
                    Be concise and clinical."""

            from llama_index.llms.ollama import Ollama
            llm = Ollama(
                model=os.getenv("LLM_MODEL", "llama3.2:1b"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                request_timeout=120.0
            )

            full_response = ""
            for token in llm.stream_complete(prompt):
                chunk = token.delta
                if chunk:
                    full_response += chunk
                    yield _sse_event("token", {"text": chunk})
                    await asyncio.sleep(0)   # yield control ke event loop

            if vital_result["overall_status"] in ["WARNING", "CRITICAL"]:
                yield _sse_event("step", {"agent": "MedicalRAG", "status": "running"})
                await asyncio.sleep(0.1)

                problem_params = (
                    vital_result["critical_params"] +
                    vital_result["warning_params"]
                )
                rag_query  = (
                    f"Patient has {patient.conditions}. "
                    f"Abnormal vitals: {', '.join(problem_params)}. "
                    f"Clinical protocols and monitoring guidelines?"
                )
                rag_result = orchestrator.rag_agent.query(rag_query)

                yield _sse_event("rag_result", {
                    "answer"  : rag_result["answer"],
                    "sources" : rag_result["sources"]
                })

            orchestrator.memory.save_session(patient.patient_id, {
                "overall_status" : vital_result["overall_status"],
                "risk_level"     : vital_result["overall_status"],
                "critical_params": vital_result["critical_params"],
                "warning_params" : vital_result["warning_params"],
            })

            yield _sse_event("done", {"message": "Analysis complete"})

        except Exception as e:
            yield _sse_event("error", {"message": str(e)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control"              : "no-cache",
            "X-Accel-Buffering"          : "no",
            "Access-Control-Allow-Origin": "*",
        }
    )

def _sse_event(event_type: str, data: dict) -> str:
    """Format SSE message."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"