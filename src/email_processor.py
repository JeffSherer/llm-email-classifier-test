import os
import logging
from typing import Dict, Optional
from openai import OpenAI

from src.openai_helpers import safe_chat_completion
from src.validation import validate_email_data
from src.prompting import build_classification_prompt, build_response_prompt

# Set up logging
logging.basicConfig(level=logging.INFO)
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
        email_obj = validate_email_data(email)
        if not email_obj:
            print(f"[ERROR] Invalid email data: {email}")
            return None

        prompt = build_classification_prompt(email_obj.subject, email_obj.body)
        print(f"\n📤 [CLASSIFY] Prompt:\n{prompt[:300]}...")

        messages = [{"role": "user", "content": prompt}]
        response = safe_chat_completion(self.client, messages, temperature=0)

        if not response:
            print("[ERROR] No response from API.")
            return None

        print(f"📥 [CLASSIFY] Raw Response:\n{response}\n")

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
            print(f"[WARN] Low confidence ({confidence}/5) or unknown category. Fallback to 'other'.")
            return "other"

        print(f"[SUCCESS] Email classified as '{category}' with confidence {confidence}/5")
        return category

    def generate_response(self, email: Dict, classification: str) -> Optional[str]:
        email_obj = validate_email_data(email)
        if not email_obj:
            print(f"[ERROR] Invalid email data: {email}")
            return None

        prompt = build_response_prompt(
            email_obj.subject, email_obj.body, classification, email_obj.from_
        )
        print(f"\n📤 [RESPOND] Prompt:\n{prompt[:300]}...")

        messages = [{"role": "user", "content": prompt}]
        response = safe_chat_completion(self.client, messages, temperature=0.5)

        if not response:
            print("[ERROR] No response from API.")
            return None

        print(f"📥 [RESPOND] Raw Response:\n{response[:300]}...\n")

        if "Drafted Response:" in response:
            return response.split("Drafted Response:")[1].strip()
        elif "Response:" in response:
            return response.split("Response:")[1].strip()

        print(f"[WARN] Unexpected response format:\n{response}")
        return None
