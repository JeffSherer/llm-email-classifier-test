import logging
from typing import Dict
from src.mock_services import (
    create_urgent_ticket,
    create_support_ticket,
    log_customer_feedback,
    send_complaint_response,
    send_standard_response,
)
from src.email_processor import EmailProcessor

logger = logging.getLogger(__name__)

class EmailAutomationSystem:
    def __init__(self, processor: EmailProcessor):
        self.processor = processor
        self.response_handlers = {
            "complaint": self._handle_complaint,
            "inquiry": self._handle_inquiry,
            "feedback": self._handle_feedback,
            "support_request": self._handle_support_request,
            "other": self._handle_other,
        }

    async def process_email(self, email: Dict) -> Dict:
        result = {
            "email_id": email.get("id", "unknown"),
            "success": False,
            "classification": None,
            "confidence": None,
            "response_sent": None,
        }

        try:
            classification = await self.processor.classify_email(email)
            if not classification:
                return result

            result["classification"] = classification
            if hasattr(self.processor, "last_confidence"):
                result["confidence"] = self.processor.last_confidence

            response = await self.processor.generate_response(email, classification)
            if not response:
                return result

            handler = self.response_handlers.get(classification, self._handle_other)
            await handler(email, response)

            result["success"] = True
            result["response_sent"] = response
            logger.info(f"Processed email {email['id']} as '{classification}'")
        except Exception as e:
            logger.error(f"Error processing email {email.get('id', 'unknown')}: {e}")

        return result

    async def _handle_complaint(self, email: Dict, response: str):
        create_urgent_ticket(email["id"], "complaint", email.get("body", ""))
        send_complaint_response(email["id"], response)

    async def _handle_inquiry(self, email: Dict, response: str):
        send_standard_response(email["id"], response)

    async def _handle_feedback(self, email: Dict, response: str):
        log_customer_feedback(email["id"], email.get("body", ""))
        send_standard_response(email["id"], response)

    async def _handle_support_request(self, email: Dict, response: str):
        create_support_ticket(email["id"], email.get("body", ""))
        send_standard_response(email["id"], response)

    async def _handle_other(self, email: Dict, response: str):
        send_standard_response(email["id"], response)
