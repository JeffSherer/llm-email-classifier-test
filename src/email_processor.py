# src/email_processor.py

import os
import logging
from typing import Dict, Optional
from openai import OpenAI

from src.prompting import build_classification_prompt, build_response_prompt
from src.openai_helpers import safe_chat_completion

logger = logging.getLogger(__name__)


class EmailProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.valid_categories = {
            "complaint",
            "inquiry",
            "feedback",
            "support_request",
            "other",
        }

    def classify_email(self, email: Dict) -> Optional[str]:
        if not all(field in email and email[field] for field in ["id", "subject", "body"]):
            logger.error(f"Missing field in email: {email}")
            return None

        prompt = build_classification_prompt(email["subject"], email["body"])
        logger.info(f"Classifying email {email['id']}...")

        response = safe_chat_completion(self.client, prompt, temperature=0)
        if not response:
            return None

        category = None
        confidence = 0
        for line in response.lower().splitlines():
            if line.startswith("category:"):
                category = line.split("category:")[1].strip()
            elif line.startswith("confidence:"):
                try:
                    confidence = int(line.split("confidence:")[1].strip())
                except ValueError:
                    confidence = 0

        self.last_confidence = confidence

        if category not in self.valid_categories or confidence < 3:
            logger.warning(f"Low confidence for email {email['id']} ({confidence}/5). Using fallback.")
            return "other"

        logger.info(f"Email {email['id']} classified as '{category}' ({confidence}/5)")
        return category

    def generate_response(self, email: Dict, classification: str) -> Optional[str]:
        if not all(field in email and email[field] for field in ["id", "subject", "body"]):
            logger.error(f"Missing field in email: {email}")
            return None

        sender = email.get("from", "unknown@example.com")
        prompt = build_response_prompt(email["subject"], email["body"], classification, sender)
        logger.info(f"Generating response for email {email['id']} ({classification})...")

        response = safe_chat_completion(self.client, prompt, temperature=0.5)
        if not response:
            return None

        if "Drafted Response:" in response:
            return response.split("Drafted Response:")[1].strip()

        logger.warning(f"Unexpected response format: {response}")
        return None
