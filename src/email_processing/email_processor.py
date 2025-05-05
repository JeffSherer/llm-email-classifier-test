import logging
from typing import Dict, Optional, List
from src.config import API_KEY, MODEL_NAME, TEMPERATURE
from src.helpers.openai_helpers import async_safe_chat_completion
from src.helpers.validation import validate_email_data
from src.helpers.prompting import build_classification_prompt, build_response_prompt
from src.email_processing.email_history import fetch_history, append_to_history
from src.models.rag_retriever import get_relevant_context
from src.utils.response_loader import get_random_response

logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self):
        self.valid_categories = {
            "complaint",
            "inquiry",
            "feedback",
            "support_request",
            "other",
        }
        self.last_confidence: int = 0

    async def classify_email(self, email: Dict) -> Optional[str]:
        # Await validate_email_data if it's async
        email_obj = await validate_email_data(email)
        if not email_obj:
            logger.error(f"Invalid email data: {email}")
            return None

        prompt = build_classification_prompt(email_obj.subject, email_obj.body)
        logger.info(f"[CLASSIFY] Prompt:\n{prompt[:300]}...")

        # Use configuration values (e.g., temperature)
        messages = [{"role": "user", "content": prompt}]
        response = await async_safe_chat_completion(messages, model=MODEL_NAME, temperature=TEMPERATURE)

        if not response:
            logger.error("No response from API.")
            return "other"  # Fallback if no response

        logger.info(f"[CLASSIFY] Response received: {response[:300]}...")

        # Parse response
        category, confidence = self._parse_classification_response(response)

        # Return fallback category if confidence is too low or category is invalid
        if category not in self.valid_categories or confidence < 3:
            logger.warning(f"Low confidence ({confidence}/5) or unknown category. Fallback to 'other'.")
            return "other"

        logger.info(f"Email classified as '{category}' with confidence {confidence}/5")
        return category

    def _parse_classification_response(self, response: str):
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
        return category, confidence

    async def generate_response(
        self, email: Dict, classification: str, history: Optional[List[Dict]] = None
    ) -> Optional[str]:
        # Await validate_email_data if it's async
        email_obj = await validate_email_data(email)
        if not email_obj:
            logger.error(f"Invalid email data: {email}")
            return None

        # Fetch history asynchronously if necessary
        history = await fetch_history(email_obj.from_)

        query = f"{email_obj.subject}\n{email_obj.body}"
        context = await get_relevant_context(query)

        prompt = (
            f"Use the context below to help draft your reply.\n\n"
            f"Context:\n{context}\n\n"
            f"{build_response_prompt(email_obj.subject, email_obj.body, classification, email_obj.from_, history)}"
        )

        logger.info(f"[RESPOND + RAG] Prompt:\n{prompt[:300]}...")

        messages = [{"role": "user", "content": prompt}]
        response = await async_safe_chat_completion(messages, model=MODEL_NAME, temperature=TEMPERATURE)

        if not response:
            logger.warning(f"LLM failed. Using fallback for category '{classification}'")
            return get_random_response(classification)

        logger.info(f"[RESPOND] Response received: {response[:300]}...")

        # Parse the final response
        final_response = self._parse_response_content(response)

        if not final_response:
            logger.warning(f"Failed to parse LLM output. Using fallback for category '{classification}'")
            return get_random_response(classification)

        # Append to history asynchronously if necessary
        await append_to_history(
            email_obj.from_,
            email_obj.subject,
            email_obj.body,
            classification,
            final_response,
        )

        return final_response

    def _parse_response_content(self, response: str):
        final_response = None
        for key in ["Drafted Response:", "Response:"]:
            if key in response:
                final_response = response.split(key)[1].strip()
                break
        return final_response
