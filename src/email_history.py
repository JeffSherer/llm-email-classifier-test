import os
import json
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "email_logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_path(email: str) -> str:
    filename = email.replace("@", "_at_").replace(".", "_dot_")
    return os.path.join(LOG_DIR, f"{filename}.json")

def append_to_history(email: str, subject: str, body: str, classification: str, response: str):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "subject": subject,
        "body": body,
        "category": classification,
        "response": response
    }

    path = get_log_path(email)
    history = []

    if os.path.exists(path):
        with open(path, "r") as f:
            history = json.load(f)

    history.append(entry)

    with open(path, "w") as f:
        json.dump(history, f, indent=2)

def fetch_history(email: str, limit: int = 3):
    path = get_log_path(email)
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        history = json.load(f)

    return history[-limit:]
