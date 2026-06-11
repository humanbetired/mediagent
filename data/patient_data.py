from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class VitalSigns:
    heart_rate: float           # BPM
    systolic_bp: float          # mmHg
    diastolic_bp: float         # mmHg
    spo2: float                 # %
    temperature: float          # Celsius
    respiratory_rate: float     # breaths/min
    blood_glucose: float        # mg/dL
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

@dataclass
class PatientProfile:
    patient_id: str
    name: str
    age: int
    conditions: list            # ["diabetes", "hypertension", etc]
    vitals: Optional[VitalSigns] = None

# ── Simulasi Data Pasien ─────────────────────────────────

def get_sample_patients():
    return [
        PatientProfile(
            patient_id="P001",
            name="Budi Santoso",
            age=68,
            conditions=["diabetes", "hypertension"],
            vitals=VitalSigns(
                heart_rate=112,
                systolic_bp=175,
                diastolic_bp=95,
                spo2=93,
                temperature=38.6,
                respiratory_rate=22,
                blood_glucose=285
            )
        ),
        PatientProfile(
            patient_id="P002",
            name="Siti Rahma",
            age=45,
            conditions=["asthma"],
            vitals=VitalSigns(
                heart_rate=88,
                systolic_bp=118,
                diastolic_bp=75,
                spo2=97,
                temperature=36.8,
                respiratory_rate=16,
                blood_glucose=95
            )
        ),
        PatientProfile(
            patient_id="P003",
            name="Ahmad Yusuf",
            age=55,
            conditions=["COPD", "cardiac"],
            vitals=VitalSigns(
                heart_rate=38,
                systolic_bp=85,
                diastolic_bp=55,
                spo2=84,
                temperature=35.2,
                respiratory_rate=32,
                blood_glucose=110
            )
        ),
    ]