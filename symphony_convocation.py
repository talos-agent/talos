# symphony_convocation.py
from datetime import datetime


def generate_convocation():
    return {
        "event_id": "SYMPHONY-001",
        "date": datetime.utcnow().isoformat(),
        "pilot_countries": ["Brazil", "UN-Virtual"],
        "status": "CONVOKED",
    }
