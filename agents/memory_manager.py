import redis
import json
from datetime import datetime
import os

class AgentMemoryManager:

    def __init__(
        self,
        host: str = None,
        port: int = None,
        ttl_seconds: int = 86400   
    ):
        host = host or os.getenv("REDIS_HOST", "localhost")
        port = port or int(os.getenv("REDIS_PORT", "6379"))

        self.client = redis.Redis(
            host=host,
            port=port,
            decode_responses=True
        )
        self.ttl = ttl_seconds

        try:
            self.client.ping()
            print("[Memory] Redis connected")
        except redis.ConnectionError:
            print("[Memory] WARNING: Redis not available — memory disabled")
            self.client = None

    # ── Session History ──────────────────────────────────

    def save_session(self, patient_id: str, session_data: dict):
        """Simpan satu session analisis ke history pasien."""
        if not self.client:
            return

        key          = f"patient:{patient_id}:history"
        session_data["timestamp"] = datetime.now().isoformat()

        existing_raw = self.client.get(key)
        history      = json.loads(existing_raw) if existing_raw else []
        history.append(session_data)

        history = history[-10:]

        self.client.set(key, json.dumps(history), ex=self.ttl)
        print(f"[Memory] Session saved for {patient_id} (total: {len(history)})")

    def get_history(self, patient_id: str) -> list:
        """Ambil semua history session pasien."""
        if not self.client:
            return []

        key = f"patient:{patient_id}:history"
        raw = self.client.get(key)
        return json.loads(raw) if raw else []

    def get_last_session(self, patient_id: str) -> dict | None:
        """Ambil session terakhir saja."""
        history = self.get_history(patient_id)
        return history[-1] if history else None

    # ── Alert Tracking ───────────────────────────────────

    def save_alert(self, patient_id: str, alert: dict):
        """Simpan alert CRITICAL/WARNING ke log terpisah."""
        if not self.client:
            return

        key   = f"patient:{patient_id}:alerts"
        alert["timestamp"] = datetime.now().isoformat()

        existing_raw = self.client.get(key)
        alerts       = json.loads(existing_raw) if existing_raw else []
        alerts.append(alert)
        alerts = alerts[-20:]   # max 20 alert

        self.client.set(key, json.dumps(alerts), ex=self.ttl)

    def get_alerts(self, patient_id: str) -> list:
        if not self.client:
            return []
        key = f"patient:{patient_id}:alerts"
        raw = self.client.get(key)
        return json.loads(raw) if raw else []

    # ── Context Builder untuk LLM ────────────────────────

    def build_context_summary(self, patient_id: str) -> str:
        """
        Buat ringkasan history untuk dimasukkan ke LLM prompt.
        Ini yang bikin agent 'ingat' pasien sebelumnya.
        """
        history = self.get_history(patient_id)
        if not history:
            return "No previous sessions recorded."

        lines = [f"Patient {patient_id} — last {len(history)} session(s):"]
        for i, session in enumerate(history[-3:], 1):   # 3 session terakhir
            ts      = session.get("timestamp", "unknown")[:16]
            status  = session.get("overall_status", "?")
            risk    = session.get("risk_level", "?")
            crits   = session.get("critical_params", [])
            warns   = session.get("warning_params", [])

            lines.append(
                f"  Session {i} [{ts}]: Status={status}, Risk={risk}"
                + (f", Critical={crits}" if crits else "")
                + (f", Warning={warns}"  if warns  else "")
            )

        alerts = self.get_alerts(patient_id)
        if alerts:
            lines.append(f"  Total alerts on record: {len(alerts)}")

        return "\n".join(lines)

    # ── Utils ────────────────────────────────────────────

    def clear_patient(self, patient_id: str):
        if not self.client:
            return
        self.client.delete(f"patient:{patient_id}:history")
        self.client.delete(f"patient:{patient_id}:alerts")
        print(f"[Memory] Cleared all data for {patient_id}")

    def get_all_active_patients(self) -> list:
        if not self.client:
            return []
        keys = self.client.keys("patient:*:history")
        return [k.split(":")[1] for k in keys]