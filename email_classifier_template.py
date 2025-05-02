# Standard library
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time

# Third-party libraries
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import openai.error

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

        self.valid_categories = {"complaint", "inquiry", "feedback", "support_request", "other"}

    
    def classify_email(self, email: Dict) -> Optional[str]:

        """
        Classify an email into a predefined category using an OpenAI LLM.

        Args:
            email (Dict): A dictionary with keys like 'subject' and 'body'.

        Returns:
            Optional[str]: One of the valid categories or 'other' if classification fails.
        """
        try:
            for field in ["id", "subject", "body"]:
                if field not in email or not email[field]:
                    logger.error(f"Email is missing required field '{field}': {email}")
                    return None
                
            # Prepare prompt components for modular prompting
            subject = email.get("subject", "")
            body = email.get("body", "")
            prompt = (
                # Define assistant persona and frame task
                "You are a highly trained expert customer support assistant. "
                "Your job is to classify customer emails accurately using reasoning and clear formatting.\n\n"
                # Chain-of-thought for reasoning
                "1. Carefully analyze the email content step by step.\n"
                "2. Classify the email into one of the following categories based on its intent:\n"
                "   - complaint: A customer expressing dissatisfaction or demanding a resolution.\n"
                "   - inquiry: A question or request for clarification or product info.\n"
                "   - feedback: A general comment or praise with no requested action.\n"
                "   - support_request: A help request related to using a product or service.\n"
                "   - other: Anything that doesn't clearly match the above.\n"
                # Self-evaluated confidence measure
                "3. Estimate your confidence in the classification on a scale from 1 (very unsure) to 5 (very confident).\n\n"
                # Include email content
                f"Email:\nSubject: {subject}\nBody: {body}\n\n"
                # Expected output format
                "Respond in this format:\n"
                "Category: <one of the five categories>\n"
                "Confidence: <1-5>"
            )
            logger.info(f"Classifying email {email['id']}...")
            logger.debug(f"Classification prompt:\n{prompt}")

            # OpenAI API call wihh retry logic to classify email
            # Setting temperature=0 for consistent output (classification should be deterministic)
            for attempt in range(2):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo-0125",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0
                    )
                    break
                except openai.error.RateLimitError:
                    logger.warning("Rate limited. Retrying...")
                    time.sleep(2)
                except openai.error.APIError as e:
                    logger.error(f"API error: {e}")
                    return None
                except openai.error.OpenAIError as e:
                    logger.exception("OpenAI error during classification.")
                    return None


            # Extract raw response from LLM output
            raw_output = response.choices[0].message.content.strip()
            logger.debug(f"Raw classification response:\n{raw_output}")

            # Initializing category and confidence fields
            category = None
            confidence = 0 
            
            # Parse LLM output to extract classification and confidence score
            for line in raw_output.lower().splitlines():
                if line.startswith("category:"):
                    category = line.split("category:")[1].strip()
                elif line.startswith("confidence:"):
                    try:
                        confidence = int(line.split("confidence:")[1].strip())
                    except ValueError:
                        confidence = 0  # Default to low confidence
            self.last_confidence = confidence

            # Fallback to "other" if confidence is too low or category is invalid
            if category not in self.valid_categories or confidence < 3:
                logger.warning(f"Email {email['id']} classified with low confidence ({confidence}/5). Using fallback category 'other'.")
                return "other"

            # Log classification result 
            logger.info(f"Email {email['id']} classified as '{category}' with confidence {confidence}/5.")
            return category

        # Log runtime error
        except Exception as e:
            logger.error(f"Error classifying email {email['id']}: {str(e)}")
            return None

    def generate_response(self, email: Dict, classification: str) -> Optional[str]:
        """
        Generate a structured response using chain-of-thought reasoning.

        Args:
            email (Dict): The original email content.
            classification (str): The category the email was classified into.

        Returns:
            Optional[str]: A customer-friendly response message or None on failure.
        """
        try:
            # Confirm email fields exist
            for field in ["id", "subject", "body"]:
                if field not in email or not email[field]:
                    logger.error(f"Cannot generate response. Missing '{field}' in email: {email}")
                    return None
            
            # Prepare prompt components
            subject = email.get("subject", "")
            body = email.get("body", "")
            # Prepare prompt components
            subject = email.get("subject", "")
            body = email.get("body", "")
            prompt = (
                # Define assistant persona and frame task
                "You are an expert AI assistant trained in customer service. "
                "You will generate a structured response using reasoning steps and a clear, empathetic tone.\n"
                # Chain-of-thought structure
                "Follow these steps:\n"
                "1. Summarize the user's issue.\n"
                "2. Infer their tone (angry, happy, neutral, confused, unsure).\n"
                "3. Judge urgency (low, medium, high, unsure).\n"
                "4. Then write a short, professional, empathetic reply.\n\n"
                # Include email content and classification context
                f"Email:\nSubject: {subject}\nBody: {body}\n\n"
                f"Category: {classification}\n\n"
                # Expected output format
                "Respond using this format:\n"
                "Reasoning:\n"
                "1. Summary: <summary>\n"
                "2. Tone: <tone>\n"
                "3. Urgency: <urgency>\n\n"
                "Drafted Response:\n"
                "<response>"
            )
            logger.info(f"Generating response for email {email['id']} ({classification})...")

            # OpenAI API call with retry logic to generate structured response
            # temperature=0.5 allows for slight variation in tone while maintaining coherence
            for attempt in range(2):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo-0125",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.5
                    )
                    break
                except openai.error.RateLimitError:
                    logger.warning("Rate limited. Retrying...")
                    time.sleep(2)
                except openai.error.APIError as e:
                    logger.error(f"API error: {e}")
                    return None
                except openai.error.OpenAIError as e:
                    logger.exception("OpenAI error during response generation.")
                    return None
                

            
            # Extract full response text from LLM output
            full_response = response.choices[0].message.content.strip()
            logger.debug(f"Raw generated response:\n{full_response}")

            # Parse out the final drafted reply from model output
            if "Drafted Response:" in full_response:
                drafted = full_response.split("Drafted Response:")[1].strip()
                logger.info(f"Response generated for email {email['id']}.")
                return drafted
            else:
                logger.warning(f"Unexpected format for email {email['id']}. Full response: {full_response}")
                return None
        
        # Log runtime errors
        except Exception as e:
            logger.error(f"Error generating response for email {email['id']}: {str(e)}")
            return None




class EmailAutomationSystem:
    def __init__(self, processor: EmailProcessor):
        """Initialize the automation system with an EmailProcessor."""
        self.processor = processor
        # Route each classification to a corresponding handler
        self.response_handlers = {
            "complaint": self._handle_complaint,
            "inquiry": self._handle_inquiry,
            "feedback": self._handle_feedback,
            "support_request": self._handle_support_request,
            "other": self._handle_other
        }

    def process_email(self, email: Dict) -> Dict:
        # Initialize response structure
        result = {
            "email_id": email.get("id", "unknown"),
            "success": False,
            "classification": None,
            "confidence": None,
            "response_sent": None
        }

        try:
            # Input strucutre validation
            if not isinstance(email, dict) or "id" not in email:
                logger.error("Invalid email format passed to process_email. Skipping...")
                return result
            
            # Call classification method
            classification = self.processor.classify_email(email)
            if hasattr(self.processor, 'last_confidence'):
                result["confidence"] = self.processor.last_confidence

            if not classification:
                logger.error(f"Failed to classify email {email['id']}.")
                return result

            result["classification"] = classification
            # Call response generation method
            response = self.processor.generate_response(email, classification)
            if not response:
                logger.error(f"Failed to generate response for email {email['id']}.")
                return result
            # Call assigned category handler
            handler = self.response_handlers.get(classification, self._handle_other)
            handler(email)

            # Service response based on classification
            if classification == "complaint":
                send_complaint_response(email["id"], response)
            elif classification == "inquiry":
                send_standard_response(email["id"], response)
            elif classification == "feedback":
                send_standard_response(email["id"], response)
            elif classification == "support_request":
                send_standard_response(email["id"], response)
            elif classification == "other":
                send_standard_response(email["id"], response)
            else:
                logger.warning(f"Unknown classification '{classification}' for email {email['id']}. Sending standard response as fallback.")
                send_standard_response(email["id"], response)

            # Tracking the success of the system all working together
            result["success"] = True
            result["response_sent"] = response

        except Exception as e:
            logger.error(f"Error processing email {email['id']}: {str(e)}")

        logger.info(f"Successfully processed email {email['id']} as {classification}.")
        return result


    def _handle_complaint(self, email: Dict):
        """Handle complaint emails by creating an urgent ticket."""
        # Create a support ticket for the complaint
        create_urgent_ticket(email["id"], "complaint", email.get("body", ""))

    def _handle_inquiry(self, email: Dict):
        """Handle inquiry emails by logging inquiry."""
        # Log the inquiry for follow-up
        logger.info(f"Handling inquiry email {email['id']}.")

    def _handle_feedback(self, email: Dict):
        """Handle feedback emails by logging the feedback."""
        # Record the feedback
        feedback_text = email.get("body", "")
        log_customer_feedback(email["id"], feedback_text)

    def _handle_support_request(self, email: Dict):
        """Handle support request emails by creating a support ticket."""
        # Create a support ticket based on the request
        context = email.get("body", "")
        create_support_ticket(email["id"], context)


    def _handle_other(self, email: Dict):
        """Handle other types of emails by logging."""
        # Log uncategorized emails
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

    print("\n=== ✅ DEMO COMPLETED SUCCESSFULLY ===")
    print("Summary of processed emails:\n")
    print(df[["email_id", "success", "classification", "confidence"]].to_string(index=False))
    print("\nGenerated responses (preview):\n")
    for idx, row in df.iterrows():
        print(f"📨 Email {row['email_id']} → {row['classification']}")
        print(f"✉️  Response:\n{row['response_sent'][:200]}...\n")  # Truncate for readability

    return df


# Example usage:
if __name__ == "__main__":
    run_demonstration()
