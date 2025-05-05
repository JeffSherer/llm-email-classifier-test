import logging

logger = logging.getLogger(__name__)

def create_urgent_ticket(email_id: str, category: str, context: str):
    logger.info(f"Creating urgent ticket for email {email_id} | Category: {category} | Context: {context[:100]}...")

def create_support_ticket(email_id: str, context: str):
    logger.info(f"Creating support ticket for email {email_id} | Context: {context[:100]}...")

def log_customer_feedback(email_id: str, feedback: str):
    logger.info(f"Logging feedback for email {email_id} | Feedback: {feedback[:100]}...")

def send_complaint_response(email_id: str, response: str):
    logger.info(f"Sending complaint response for email {email_id} | Response: {response[:100]}...")

def send_standard_response(email_id: str, response: str):
    logger.info(f"Sending standard response for email {email_id} | Response: {response[:100]}...")
