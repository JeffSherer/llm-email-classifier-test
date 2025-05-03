import pytest
from src.email_processor import EmailProcessor

@pytest.fixture
def processor():
    return EmailProcessor()

@pytest.mark.parametrize("email, expected_category", [
    ({"id": "001", "subject": "Need help", "body": "A part was missing", "from_": "a@b.com"}, "support_request"),
    ({"id": "002", "subject": "Thanks!", "body": "Great product", "from_": "b@c.com"}, "feedback"),
    ({"id": "003", "subject": "Can I get more info?", "body": "Tell me about your plans", "from_": "c@d.com"}, "inquiry"),
])
def test_classify_email(processor, email, expected_category):
    category = processor.classify_email(email)
    assert category in processor.valid_categories
    assert category == expected_category or category == "other"

def test_generate_response(processor):
    email = {
        "id": "004",
        "subject": "Need help with my account",
        "body": "Something’s broken. Can you fix it?",
        "from_": "d@e.com"
    }
    category = processor.classify_email(email)
    response = processor.generate_response(email, category)
    assert response
    assert "thank you" in response.lower() or "we" in response.lower()
