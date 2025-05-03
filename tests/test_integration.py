import pytest
from unittest.mock import patch
from src.email_processor import EmailProcessor

def mocked_safe_chat_completion(client, messages, temperature=0, model="gpt-3.5-turbo-0125"):
    prompt = messages[0]["content"]

    # Detect classification prompt
    if "Respond in this format:\nCategory:" in prompt:
        if "Inquiry about product" in prompt:
            return "Category: inquiry\nConfidence: 5"
        if "Feedback on product" in prompt:
            return "Category: feedback\nConfidence: 5"
        if "my recent order" in prompt:
            return "Category: support_request\nConfidence: 5"
        return "Category: other\nConfidence: 1"

    # Detect response generation prompt
    if "Please follow these steps:" in prompt and "Respond in this format:\nReasoning:" in prompt:
        return (
            "Reasoning:\n"
            "1. Summary: User asked a question or gave feedback\n"
            "2. Tone: Neutral\n"
            "3. Urgency: Medium\n\n"
            "Drafted Response:\n"
            "Thank you for your message. We appreciate your feedback and will get back to you shortly."
        )

    return None


@pytest.fixture(autouse=True)
def mock_openai_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "mocked-api-key")

def test_email_processing():
    email = {
        "id": "001",
        "subject": "Inquiry about product",
        "body": "I am interested in learning more about your product.",
        "from_": "user@example.com"
    }

    processor = EmailProcessor()

    with patch("src.email_processor.safe_chat_completion", side_effect=mocked_safe_chat_completion):
        classification = processor.classify_email(email)
        assert classification == "inquiry", f"Expected 'inquiry', got {classification}"

        response = processor.generate_response(email, classification)
        assert response
        assert "thank you" in response.lower()

def test_valid_email_processing():
    email = {
        "id": "002",
        "subject": "Feedback on product",
        "body": "Great product! Would love to see more features.",
        "from_": "feedback@example.com"
    }

    processor = EmailProcessor()

    with patch("src.email_processor.safe_chat_completion", side_effect=mocked_safe_chat_completion):
        classification = processor.classify_email(email)
        assert classification == "feedback", f"Expected 'feedback', got {classification}"

        response = processor.generate_response(email, classification)
        assert response
        assert "thank you" in response.lower()

def test_invalid_email_format():
    email = {
        "id": "003",
        "subject": "Invalid email",
        "body": "This email is invalid.",
        "from_": "invalid-email"
    }

    processor = EmailProcessor()

    with patch("src.email_processor.safe_chat_completion", side_effect=mocked_safe_chat_completion):
        classification = processor.classify_email(email)
        assert classification is None

        response = processor.generate_response(email, "complaint")
        assert response is None
