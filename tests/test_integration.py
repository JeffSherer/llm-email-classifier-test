import pytest
from unittest.mock import patch
from src.email_processing.email_processor import EmailProcessor


# Mocked function for async call
async def mocked_safe_chat_completion(messages, temperature=0, model="gpt-3.5-turbo-0125"):
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

@pytest.mark.asyncio  # Mark the tests as async
async def test_email_processing():
    email = {
        "id": "001",
        "subject": "Inquiry about product",
        "body": "I am interested in learning more about your product.",
        "from_": "user@example.com"
    }

    processor = EmailProcessor()

    with patch("src.helpers.openai_helper.async_safe_chat_completion", side_effect=mocked_safe_chat_completion):
        classification = await processor.classify_email(email)  # Await the async method
        assert classification == "inquiry", f"Expected 'inquiry', got {classification}"

        response = await processor.generate_response(email, classification)  # Await the async method
        assert response
        assert "thank you" in response.lower()

@pytest.mark.asyncio  # Mark the tests as async
async def test_email_processing():
    email = {
        "id": "001",
        "subject": "Inquiry about product",
        "body": "I am interested in learning more about your product.",
        "from_": "user@example.com"
    }

    processor = EmailProcessor()

    # Correct the patch to use the correct module name (openai_helpers)
    with patch("src.helpers.openai_helpers.async_safe_chat_completion", side_effect=mocked_safe_chat_completion):
        classification = await processor.classify_email(email)  # Await the async method
        assert classification == "inquiry", f"Expected 'inquiry', got {classification}"

        response = await processor.generate_response(email, classification)  # Await the async method
        assert response
        assert "thank you" in response.lower()

@pytest.mark.asyncio  # Mark the tests as async
async def test_valid_email_processing():
    email = {
        "id": "002",
        "subject": "Feedback on product",
        "body": "Great product! Would love to see more features.",
        "from_": "feedback@example.com"
    }

    processor = EmailProcessor()

    # Correct the patch to use the correct module name (openai_helpers)
    with patch("src.helpers.openai_helpers.async_safe_chat_completion", side_effect=mocked_safe_chat_completion):
        classification = await processor.classify_email(email)  # Await the async method
        assert classification == "feedback", f"Expected 'feedback', got {classification}"

        response = await processor.generate_response(email, classification)  # Await the async method
        assert response
        assert "thank you" in response.lower()

@pytest.mark.asyncio  # Mark the tests as async
async def test_invalid_email_format():
    email = {
        "id": "003",
        "subject": "Invalid email",
        "body": "This email is invalid.",
        "from_": "invalid-email"
    }

    processor = EmailProcessor()

    # Correct the patch to use the correct module name (openai_helpers)
    with patch("src.helpers.openai_helpers.async_safe_chat_completion", side_effect=mocked_safe_chat_completion):
        classification = await processor.classify_email(email)  # Await the async method
        assert classification is None

        response = await processor.generate_response(email, "complaint")  # Await the async method
        assert response is None
