import pytest
import pdb
from unittest.mock import patch
from src.email_processor import EmailProcessor
from src.openai_helpers import safe_chat_completion

# Optional: Set a breakpoint if you want to debug the test execution
# pdb.set_trace()

# Mock the safe_chat_completion function
def mocked_safe_chat_completion(client, messages, model="gpt-3.5-turbo-0125", temperature=0):
    print(f"Mock called with message content: {messages[0]['content']}")

    if "Inquiry about product" in messages[0]["content"]:
        return {
            "choices": [{"message": {"content": "Category: inquiry\nConfidence: 5"}}]
        }
    elif "Feedback on product" in messages[0]["content"]:
        return {
            "choices": [{"message": {"content": "Category: feedback\nConfidence: 5"}}]
        }
    return {
        "choices": [{"message": {"content": "Category: other\nConfidence: 1"}}]
    }

# Test fixture to mock the OpenAI API key environment variable
@pytest.fixture(autouse=True)
def mock_openai_api_key(monkeypatch):
    # Mock the API key to avoid actual API calls
    monkeypatch.setenv("OPENAI_API_KEY", "mocked-api-key")

# Test for email processing
def test_email_processing():
    email = {
        "id": "001",
        "subject": "Inquiry about product",
        "body": "I am interested in learning more about your product.",
        "from_": "user@example.com"
    }

    processor = EmailProcessor()

    # Mock the API call to avoid hitting the actual OpenAI API
    with patch.object(safe_chat_completion, "__call__", side_effect=mocked_safe_chat_completion):
        # Test classification
        classification = processor.classify_email(email)
        assert classification == "inquiry", f"Expected 'inquiry', but got {classification}"

        # Test response generation
        response = processor.generate_response(email, classification)
        assert response == "Thank you for your inquiry. We will get back to you shortly.", f"Unexpected response: {response}"

# Test for valid email processing (feedback example)
def test_valid_email_processing():
    email = {
        "id": "002",
        "subject": "Feedback on product",
        "body": "Great product! Would love to see more features.",
        "from_": "feedback@example.com"
    }

    processor = EmailProcessor()

    # Mock the API call to avoid hitting the actual OpenAI API
    with patch.object(safe_chat_completion, "__call__", side_effect=mocked_safe_chat_completion):
        # Test classification
        classification = processor.classify_email(email)
        assert classification == "feedback", f"Expected 'feedback', but got {classification}"

        # Test response generation
        response = processor.generate_response(email, classification)
        assert response == "Thank you for your feedback. We appreciate your suggestions.", f"Unexpected response: {response}"

# Test for invalid email format (no valid category)
def test_invalid_email_format():
    email = {
        "id": "003",
        "subject": "Invalid email",
        "body": "This email is invalid.",
        "from_": "invalid-email"
    }

    processor = EmailProcessor()

    # Mock the API call to avoid hitting the actual OpenAI API
    with patch.object(safe_chat_completion, "__call__", side_effect=mocked_safe_chat_completion):
        # Test that the email processor catches the invalid format
        classification = processor.classify_email(email)
        assert classification is None, f"Expected None due to invalid email format, but got {classification}"

        # Test response generation for invalid email
        response = processor.generate_response(email, "complaint")
        assert response is None, f"Expected None due to invalid email format, but got {response}"
