# Configuration and imports
import os
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Sample email dataset
sample_emails = [
    {
        "id": "001",
        "from": "angry.customer@example.com",
        "subject": "Broken product received",
        "body": "I received my order #12345 yesterday but it arrived completely damaged. This is unacceptable and I demand a refund immediately. This is the worst customer service I've experienced.",
        "timestamp": "2024-03-15T10:30:00Z"
    },
    {
        "id": "002",
        "from": "curious.shopper@example.com",
        "subject": "Question about product specifications",
        "body": "Hi, I'm interested in buying your premium package but I couldn't find information about whether it's compatible with Mac OS. Could you please clarify this? Thanks!",
        "timestamp": "2024-03-15T11:45:00Z"
    },
    {
        "id": "003",
        "from": "happy.user@example.com",
        "subject": "Amazing customer support",
        "body": "I just wanted to say thank you for the excellent support I received from Sarah on your team. She went above and beyond to help resolve my issue. Keep up the great work!",
        "timestamp": "2024-03-15T13:15:00Z"
    },
    {
        "id": "004",
        "from": "tech.user@example.com",
        "subject": "Need help with installation",
        "body": "I've been trying to install the software for the past hour but keep getting error code 5123. I've already tried restarting my computer and clearing the cache. Please help!",
        "timestamp": "2024-03-15T14:20:00Z"
    },
    {
        "id": "005",
        "from": "business.client@example.com",
        "subject": "Partnership opportunity",
        "body": "Our company is interested in exploring potential partnership opportunities with your organization. Would it be possible to schedule a call next week to discuss this further?",
        "timestamp": "2024-03-15T15:00:00Z"
    }
]


class EmailProcessor:
    def __init__(self):
        """Initialize the email processor with OpenAI API key."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Define valid categories
        self.valid_categories = {
            "complaint", "inquiry", "feedback",
            "support_request", "other"
        }

    def classify_email(self, email: Dict) -> Optional[str]:

        """
        Classify an email using LLM with detailed logging.
        """
        try:
            # Validate required fields
            required_fields = ["id", "subject", "body"]
            for field in required_fields:
                if field not in email or not email[field]:
                    logger.error(f"Email is missing required field '{field}': {email}")
                    return None
            subject = email.get("subject", "")
            body = email.get("body", "")
            email_text = f"Subject: {subject}\nBody: {body}".strip()

            prompt = (
                "You are an AI email classifier. Read the email and do the following:\n"
                "1. Think step-by-step about the issue.\n"
                "2. Classify the email into one of the following categories:\n"
                "   complaint, inquiry, feedback, support_request, other\n"
                "3. Estimate your confidence in the classification on a scale from 1 (very unsure) to 5 (very confident).\n\n"
                f"Email:\nSubject: {subject}\nBody: {body}\n\n"
                "Respond in this format:\n"
                "Category: <one of the five categories>\n"
                "Confidence: <1-5>"
            )

            logger.info(f"Classifying email {email['id']}...")
            logger.debug(f"Classification prompt:\n{prompt}")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            raw_output = response.choices[0].message.content.strip()
            logger.debug(f"Raw classification response:\n{raw_output}")

            # Parse category and confidence
            category = None
            confidence = 5  # Default to high confidence
            self.last_confidence = confidence

            for line in raw_output.lower().splitlines():
                if line.startswith("category:"):
                    category = line.split("category:")[1].strip()
                elif line.startswith("confidence:"):
                    try:
                        confidence = int(line.split("confidence:")[1].strip())
                    except ValueError:
                        confidence = 1  # Default to low confidence on parse failure

            # Fallback logic if confidence is too low or category is invalid
            if category not in self.valid_categories or confidence < 3:
                logger.warning(f"Email {email['id']} classified with low confidence ({confidence}/5). Using fallback category 'other'.")
                return "other"

            logger.info(f"Email {email['id']} classified as '{category}' with confidence {confidence}/5.")
            return category


        except Exception as e:
            logger.error(f"Error classifying email {email['id']}: {str(e)}")
            return None

    def generate_response(self, email: Dict, classification: str) -> Optional[str]:
        """
        Generate a structured response using chain-of-thought reasoning.
        """
        try:
            # Validate required fields
            required_fields = ["id", "subject", "body"]
            for field in required_fields:
                if field not in email or not email[field]:
                    logger.error(f"Cannot generate response. Missing '{field}' in email: {email}")
                    return None
            subject = email.get("subject", "")
            body = email.get("body", "")
            email_text = f"Subject: {subject}\nBody: {body}".strip()

            prompt = (
                "You are a helpful AI assistant drafting a customer service response.\n"
                "Follow these steps:\n"
                "1. Summarize the user's issue.\n"
                "2. Infer their tone (angry, happy, neutral, confused, unsure).\n"
                "3. Judge urgency (low, medium, high, unsure).\n"
                "4. Then write a short, professional, empathetic reply.\n\n"
                f"Email:\n{email_text}\n\n"
                f"Category: {classification}\n\n"
                "Respond using this format:\n"
                "Reasoning:\n"
                "1. Issue: <summary>\n"
                "2. Tone: <tone>\n"
                "3. Urgency: <urgency>\n\n"
                "Drafted Response:\n"
                "<response>"
            )

            logger.info(f"Generating response for email {email['id']} ({classification})...")
            logger.debug(f"Response prompt:\n{prompt}")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )

            full_response = response.choices[0].message.content.strip()
            logger.debug(f"Raw generated response:\n{full_response}")

            if "Drafted Response:" in full_response:
                drafted = full_response.split("Drafted Response:")[1].strip()
                logger.info(f"Response generated for email {email['id']}.")
                return drafted
            else:
                logger.warning(f"Unexpected format for email {email['id']}. Full response: {full_response}")
                return None

        except Exception as e:
            logger.error(f"Error generating response for email {email['id']}: {str(e)}")
            return None



    def extract_email_parts(self, subject: str, body: str) -> Dict[str, str]:
        """
        Very basic placeholder extractor to structure the email information.
        Can later be upgraded to an LLM call for smarter extraction.
        """
        summary = subject if subject else "No subject provided."
        
        # Simple rules to infer tone and urgency
        lower_body = body.lower()
        tone = "angry" if any(word in lower_body for word in ["angry", "unacceptable", "terrible", "upset", "worst"]) else "neutral"
        urgency = "urgent" if any(word in lower_body for word in ["urgent", "asap", "immediately", "right away"]) else "normal"
        
        # Basic guess about request
        if "refund" in lower_body:
            request = "refund request"
        elif "help" in lower_body or "error" in lower_body:
            request = "technical support"
        elif "question" in lower_body or "clarify" in lower_body:
            request = "product inquiry"
        elif "thank you" in lower_body or "great" in lower_body:
            request = "positive feedback"
        elif "partnership" in lower_body or "collaboration" in lower_body:
            request = "business opportunity"
        else:
            request = "general inquiry"
        
        return {
            "summary": summary,
            "tone": tone,
            "request": request,
            "urgency": urgency
        }



class EmailAutomationSystem:
    def __init__(self, processor: EmailProcessor):
        """Initialize the automation system with an EmailProcessor."""
        self.processor = processor
        self.response_handlers = {
            "complaint": self._handle_complaint,
            "inquiry": self._handle_inquiry,
            "feedback": self._handle_feedback,
            "support_request": self._handle_support_request,
            "other": self._handle_other
        }

    def process_email(self, email: Dict) -> Dict:
        """
        Process a single email through the complete pipeline:
        1. Classify the email.
        2. Generate a response.
        3. Send or log the response based on the classification.
        4. Return structured results.
        """
        return {
            "email_id": "unknown",
            "success": False,
            "classification": None,
            "confidence": None,
            "response_sent": None
        }


        try:
            # Validate input structure early
            if not isinstance(email, dict) or "id" not in email:
                logger.error("Invalid email format passed to process_email. Skipping...")
                return {
                    "email_id": "unknown",
                    "success": False,
                    "classification": None,
                    "response_sent": None
                }
            # Step 1: Classify
            classification = self.processor.classify_email(email)
            if hasattr(self.processor, 'last_confidence'):
                result["confidence"] = self.processor.last_confidence

            if not classification:
                logger.error(f"Failed to classify email {email['id']}.")
                return result
            result["classification"] = classification

            # Step 2: Generate Response
            response = self.processor.generate_response(email, classification)
            if not response:
                logger.error(f"Failed to generate response for email {email['id']}.")
                return result

            # Step 3: Handle Based on Classification
            handler = self.response_handlers.get(classification, self._handle_other)
            handler(email)

            # Log response sending
            if classification == "complaint":
                send_complaint_response(email["id"], response)
            else:
                send_standard_response(email["id"], response)

            # Mark success
            result["success"] = True
            result["response_sent"] = response

        except Exception as e:
            logger.error(f"Error processing email {email['id']}: {str(e)}")
        logger.info(f"Successfully processed email {email['id']} as {classification}.")

        return result

    def _handle_complaint(self, email: Dict):
        """Handle complaint emails by creating an urgent ticket."""
        create_urgent_ticket(email["id"], "complaint", email.get("body", ""))

    def _handle_inquiry(self, email: Dict):
        """Handle inquiry emails by logging inquiry."""
        logger.info(f"Handling inquiry email {email['id']}.")

    def _handle_feedback(self, email: Dict):
        """Handle feedback emails by logging the feedback."""
        feedback_text = email.get("body", "")
        log_customer_feedback(email["id"], feedback_text)

    def _handle_support_request(self, email: Dict):
        """Handle support request emails by creating a support ticket."""
        context = email.get("body", "")
        create_support_ticket(email["id"], context)

    def _handle_other(self, email: Dict):
        """Handle other types of emails by logging."""
        logger.info(f"Handling 'other' type email {email['id']}.")



# Mock service functions
def send_complaint_response(email_id: str, response: str):
    """Mock function to simulate sending a response to a complaint"""
    logger.info(f"Sending complaint response for email {email_id}")
    # In real implementation: integrate with email service


def send_standard_response(email_id: str, response: str):
    """Mock function to simulate sending a standard response"""
    logger.info(f"Sending standard response for email {email_id}")
    # In real implementation: integrate with email service


def create_urgent_ticket(email_id: str, category: str, context: str):
    """Mock function to simulate creating an urgent ticket"""
    logger.info(f"Creating urgent ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def create_support_ticket(email_id: str, context: str):
    """Mock function to simulate creating a support ticket"""
    logger.info(f"Creating support ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def log_customer_feedback(email_id: str, feedback: str):
    """Mock function to simulate logging customer feedback"""
    logger.info(f"Logging feedback for email {email_id}")
    # In real implementation: integrate with feedback system


def run_demonstration():
    """Run a demonstration of the complete system."""
    # Initialize the system
    processor = EmailProcessor()
    automation_system = EmailAutomationSystem(processor)

    # Process all sample emails
    results = []
    for email in sample_emails:
        logger.info(f"\nProcessing email {email['id']}...")
        result = automation_system.process_email(email)
        results.append(result)

    # Create a summary DataFrame
    df = pd.DataFrame(results)
    print("\nProcessing Summary:")
    print(df[["email_id", "success", "classification", "response_sent"]])

    return df


# Example usage:
if __name__ == "__main__":
    run_demonstration()
