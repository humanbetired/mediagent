from data.patient_data import VitalSigns, PatientProfile

class VitalSignsMonitorAgent:

    THRESHOLDS = {
        "heart_rate"       : {"normal": (60, 100),  "warning": (40, 150),  "unit": "BPM"},
        "systolic_bp"      : {"normal": (90, 130),  "warning": (80, 180),  "unit": "mmHg"},
        "diastolic_bp"     : {"normal": (60, 85),   "warning": (50, 110),  "unit": "mmHg"},
        "spo2"             : {"normal": (95, 100),  "warning": (88, 94),   "unit": "%"},
        "temperature"      : {"normal": (36.1, 37.5), "warning": (35.0, 39.0), "unit": "°C"},
        "respiratory_rate" : {"normal": (12, 20),   "warning": (10, 30),   "unit": "brpm"},
        "blood_glucose"    : {"normal": (70, 140),  "warning": (54, 300),  "unit": "mg/dL"},
    }

    def analyze(self, patient: PatientProfile) -> dict:
        vitals   = patient.vitals
        findings = []
        flags    = []

        checks = {
            "heart_rate"       : vitals.heart_rate,
            "systolic_bp"      : vitals.systolic_bp,
            "diastolic_bp"     : vitals.diastolic_bp,
            "spo2"             : vitals.spo2,
            "temperature"      : vitals.temperature,
            "respiratory_rate" : vitals.respiratory_rate,
            "blood_glucose"    : vitals.blood_glucose,
        }

        for param, value in checks.items():
            threshold = self.THRESHOLDS[param]
            unit      = threshold["unit"]
            normal    = threshold["normal"]
            warning   = threshold["warning"]

            # SpO2 — lower is worse
            if param == "spo2":
                if value < 88:
                    status = "CRITICAL"
                elif value < 95:
                    status = "WARNING"
                else:
                    status = "NORMAL"
            else:
                lo_n, hi_n = normal
                lo_w, hi_w = warning
                if value < lo_w or value > hi_w:
                    status = "CRITICAL"
                elif value < lo_n or value > hi_n:
                    status = "WARNING"
                else:
                    status = "NORMAL"

            findings.append({
                "parameter" : param,
                "value"     : value,
                "unit"      : unit,
                "status"    : status
            })
            flags.append(status)

        # Overall status — worst flag wins
        if "CRITICAL" in flags:
            overall = "CRITICAL"
        elif "WARNING" in flags:
            overall = "WARNING"
        else:
            overall = "NORMAL"

        critical_params = [f["parameter"] for f in findings if f["status"] == "CRITICAL"]
        warning_params  = [f["parameter"] for f in findings if f["status"] == "WARNING"]

        return {
            "patient_id"      : patient.patient_id,
            "patient_name"    : patient.name,
            "overall_status"  : overall,
            "findings"        : findings,
            "critical_params" : critical_params,
            "warning_params"  : warning_params,
        }