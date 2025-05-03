import logging

logger = logging.getLogger(__name__)

def create_urgent_ticket(email_id: str, category: str, context: str):
    logger.info(f"Creating urgent ticket for email {email_id}")

def create_support_ticket(email_id: str, context: str):
    logger.info(f"Creating support ticket for email {email_id}")

def log_customer_feedback(email_id: str, feedback: str):
    logger.info(f"Logging feedback for email {email_id}")

