# src/config.py

OPENAI_MODEL = "gpt-3.5-turbo-0125"
TEMPERATURE_CLASSIFY = 0.0
TEMPERATURE_RESPOND = 0.5
RETRY_ATTEMPTS = 2

VALID_CATEGORIES = {
    "complaint",
    "inquiry",
    "feedback",
    "support_request",
    "other",
}

LOG_LEVEL = "INFO"

