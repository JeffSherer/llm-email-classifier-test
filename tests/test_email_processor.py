import pytest
from src.email_processor import EmailProcessor
from unittest.mock import patch

# Define the mocked version of async_safe_chat_completion
async def mocked_safe_chat_completion(messages, temperature=0, model="gpt-3.5-turbo-0125"):
    prompt = messages[0]["content"]

    # Simulate classification behavior
    if "Respond in this format:\nCategory:" in prompt:
        if "Need help" in prompt:
            return "Category: support_request\nConfidence: 5"
        elif "Thanks!" in prompt:
            return "Category: feedback\nConfidence: 5"
        else:
            return "Category: inquiry\nConfidence: 5"

    # Simulate response generation behavior
    if "Please follow these steps:" in prompt:
        return (
            "Reasoning:\n"
            "1. Summary: User asked a question\n"
            "2. Tone: Neutral\n"
            "3. Urgency: Medium\n\n"
            "Drafted Response:\n"
            "Thank you for your message. We will get back to you soon."
        )

    return None

@pytest.fixture
def processor():
    return EmailProcessor()

@pytest.mark.parametrize("email, expected_category", [
    ({"id": "001", "subject": "Need help", "body": "A part was missing", "from_": "a@b.com"}, "support_request"),
    ({"id": "002", "subject": "Thanks!", "body": "Great product", "from_": "b@c.com"}, "feedback"),
    ({"id": "003", "subject": "Can I get more info?", "body": "Tell me about your plans", "from_": "c@d.com"}, "inquiry"),
])
@pytest.mark.asyncio  # Mark the test as async
async def test_classify_email(processor, email, expected_category):
    category = await processor.classify_email(email)  # Await the async method
    assert category in processor.valid_categories
    assert category == expected_category or category == "other"

@pytest.mark.asyncio  # Mark the test as async
async def test_generate_response(processor):
    email = {
        "id": "004",
        "subject": "Need help with my account",
        "body": "Something’s broken. Can you fix it?",
        "from_": "d@e.com"
    }

    # Patch the async_safe_chat_completion function in the correct location
    with patch("src.openai_helpers.async_safe_chat_completion", side_effect=mocked_safe_chat_completion): 
        category = await processor.classify_email(email)  # Await the async method
        response = await processor.generate_response(email, category)  # Await the async method
        assert response
        assert "thank you" in response.lower() or "we" in response.lower()
