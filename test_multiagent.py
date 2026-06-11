from data.patient_data import get_sample_patients
from agents.orchestrator import MediAgentOrchestrator
import json

orchestrator = MediAgentOrchestrator()
patients     = get_sample_patients()

for patient in patients:
    print("\n" + "="*70)
    result = orchestrator.run(patient)

    print(f"\n📋 PATIENT: {result['patient']} | ID: {result['patient_id']}")
    print(f"   Age: {result['age']} | Conditions: {result['conditions']}")

    print(f"\n🔴 VITAL STATUS: {result['vital_analysis']['overall_status']}")
    for f in result["vital_analysis"]["findings"]:
        icon = "🔴" if f["status"] == "CRITICAL" else "🟡" if f["status"] == "WARNING" else "🟢"
        print(f"   {icon} {f['parameter']:20s}: {f['value']} {f['unit']}")

    print(f"\n⚠️  RISK ASSESSMENT:")
    print(result["risk_analysis"]["llm_assessment"])

    if result["rag_guidance"]:
        print(f"\n📚 CLINICAL GUIDANCE (from RAG):")
        print(result["rag_guidance"]["answer"][:500] + "...")

    print("="*70)