import os
import logging
from typing import Dict, Optional, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from src.openai_helpers import safe_chat_completion
from src.validation import validate_email_data
from src.prompting import build_classification_prompt, build_response_prompt
from src.email_history import fetch_history, append_to_history

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
        self.last_confidence: int = 0

    def classify_email(self, email: Dict) -> Optional[str]:
        email_obj = validate_email_data(email)
        if not email_obj:
            logger.error(f"Invalid email data: {email}")
            return None

        prompt = build_classification_prompt(email_obj.subject, email_obj.body)
        logger.info(f"[CLASSIFY] Prompt:\n{prompt[:300]}...")

        messages = [{"role": "user", "content": prompt}]
        response = safe_chat_completion(self.client, messages, temperature=0)

        if not response:
            logger.error("No response from API.")
            return None

        logger.info(f"[CLASSIFY] Raw Response:\n{response}\n")

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
            logger.warning(f"Low confidence ({confidence}/5) or unknown category. Fallback to 'other'.")
            return "other"

        logger.info(f"Email classified as '{category}' with confidence {confidence}/5")
        return category

    def generate_response(self, email: Dict, classification: str, history: Optional[List[Dict]] = None) -> Optional[str]:
        email_obj = validate_email_data(email)
        if not email_obj:
            logger.error(f"Invalid email data: {email}")
            return None

        history = fetch_history(email_obj.from_)

        prompt = build_response_prompt(
            email_obj.subject,
            email_obj.body,
            classification,
            email_obj.from_,
            history=history,
        )
        logger.info(f"[RESPOND] Prompt:\n{prompt[:300]}...")

        messages = [{"role": "user", "content": prompt}]
        response = safe_chat_completion(self.client, messages, temperature=0.5)

        if not response:
            logger.error("No response from API.")
            return None

        logger.info(f"[RESPOND] Raw Response:\n{response[:300]}...\n")

        final_response = None
        for key in ["Drafted Response:", "Response:"]:
            if key in response:
                final_response = response.split(key)[1].strip()
                break

        if final_response:
            append_to_history(
                email_obj.from_,
                email_obj.subject,
                email_obj.body,
                classification,
                final_response
            )

        return final_response
