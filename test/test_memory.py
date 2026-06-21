from data.patient_data import get_sample_patients
from agents.orchestrator import MediAgentOrchestrator

orchestrator = MediAgentOrchestrator()
patients     = get_sample_patients()
budi         = patients[0]   # P001 — kasus paling menarik

print("\n" + "="*60)
print("SESSION 1 — First visit")
print("="*60)
result1 = orchestrator.run(budi)
print(f"Status   : {result1['vital_analysis']['overall_status']}")
print(f"Memory   : {result1['memory_context']}")

print("\n" + "="*60)
print("SESSION 2 — Same patient, agent now has memory")
print("="*60)
result2 = orchestrator.run(budi)
print(f"Status   : {result2['vital_analysis']['overall_status']}")
print(f"Memory   : {result2['memory_context']}")

# Cek semua pasien aktif di Redis
print("\n[Memory] Active patients in Redis:")
print(orchestrator.memory.get_all_active_patients())

# Cek alert log
print("\n[Memory] Alerts for P001:")
for alert in orchestrator.memory.get_alerts("P001"):
    print(f"  {alert}")