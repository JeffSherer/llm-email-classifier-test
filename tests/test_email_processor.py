import pytest  # type: ignore
import sys
import os

# Ensure the project root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_classifier_template import EmailProcessor


@pytest.fixture
def processor():
    return EmailProcessor()


def test_classify_complaint(processor):
    email = {
        "id": "test001",
        "subject": "This is terrible service",
        "body": "My package arrived broken and I want a refund now."
    }
    category = processor.classify_email(email)
    assert category in processor.valid_categories
    assert category == "complaint"


def test_classify_inquiry(processor):
    email = {
        "id": "test002",
        "subject": "Question about compatibility",
        "body": "Does your product work with Mac OS?"
    }
    category = processor.classify_email(email)
    assert category in processor.valid_categories
    assert category == "inquiry"


def test_generate_response_format(processor):
    email = {
        "id": "test003",
        "subject": "Help with setup",
        "body": "I tried to install it but it won’t start."
    }
    category = processor.classify_email(email)
    response = processor.generate_response(email, category)
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 10


def test_missing_subject_field(processor):
    email = {
        "id": "test004",
        "body": "This has no subject field."
    }
    category = processor.classify_email(email)
    assert category is None


def test_invalid_classification_response(monkeypatch, processor):
    # Patch OpenAI call to return invalid category
    def mock_create(*args, **kwargs):
        class MockResponse:
            class Choice:
                message = type("obj", (object,), {"content": "not_a_real_category"})
            choices = [Choice()]
        return MockResponse()

    monkeypatch.setattr(processor.client.chat.completions, "create", mock_create)

    email = {
        "id": "test005",
        "subject": "Random",
        "body": "Unclear message"
    }
    category = processor.classify_email(email)
    assert category == "other"


def test_api_failure(monkeypatch, processor):
    # Simulate API error
    def raise_error(*args, **kwargs):
        raise Exception("API call failed")

    monkeypatch.setattr(processor.client.chat.completions, "create", raise_error)

    email = {
        "id": "test006",
        "subject": "Error Test",
        "body": "Trigger an API failure"
    }
    category = processor.classify_email(email)
    assert category is None
