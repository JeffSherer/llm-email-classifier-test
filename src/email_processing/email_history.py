import os
import json
from datetime import datetime
import aiofiles  # Async file handling

LOG_DIR = os.path.join(os.path.dirname(__file__), "email_logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_path(email: str) -> str:
    filename = email.replace("@", "_at_").replace(".", "_dot_")
    return os.path.join(LOG_DIR, f"{filename}.json")

async def append_to_history(email: str, subject: str, body: str, classification: str, response: str):
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
        try:
            async with aiofiles.open(path, "r") as f:
                content = await f.read()
                history = json.loads(content) if content else []
        except json.JSONDecodeError:
            history = []

    history.append(entry)

    async with aiofiles.open(path, "w") as f:
        await f.write(json.dumps(history, indent=2))

async def fetch_history(email: str, limit: int = 3):
    path = get_log_path(email)
    if not os.path.exists(path):
        return []

    try:
        async with aiofiles.open(path, "r") as f:
            content = await f.read()
            history = json.loads(content) if content else []
        return history[-limit:]
    except json.JSONDecodeError:
        return []
