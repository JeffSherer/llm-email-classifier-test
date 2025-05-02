import pytest  # type: ignore
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_classifier_template import EmailProcessor, EmailAutomationSystem

# Init processor
@pytest.fixture
def processor():
    return EmailProcessor()

# Init automation with processor
@pytest.fixture
def automation(processor):
    return EmailAutomationSystem(processor)

# Complaint classification test
def test_classify_complaint(processor):
    email = {
        "id": "test001",
        "subject": "This is terrible service",
        "body": "My package arrived broken and I want a refund now."
    }
    category = processor.classify_email(email)
    assert category == "complaint"

# Inquiry classification test
def test_classify_inquiry(processor):
    email = {
        "id": "test002",
        "subject": "Question about compatibility",
        "body": "Does your product work with Mac OS?"
    }
    category = processor.classify_email(email)
    assert category == "inquiry"

# Response generation format test
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

# Missing subject field
def test_missing_subject_field(processor):
    email = {
        "id": "test004",
        "body": "This has no subject field."
    }
    category = processor.classify_email(email)
    assert category is None

# Invalid category returned by LLM
def test_invalid_classification_response(monkeypatch, processor):
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

# Simulate API failure
def test_api_failure(monkeypatch, processor):
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

# Low confidence fallback
def test_low_confidence_fallback(monkeypatch, processor):
    def mock_create(*args, **kwargs):
        class MockResponse:
            class Choice:
                message = type("obj", (object,), {"content": "Category: feedback\nConfidence: 2"})
            choices = [Choice()]
        return MockResponse()

    monkeypatch.setattr(processor.client.chat.completions, "create", mock_create)

    email = {
        "id": "test007",
        "subject": "Not sure",
        "body": "Maybe feedback but vague"
    }
    category = processor.classify_email(email)
    assert category == "other"

# Confidence capture in automation
def test_confidence_capture(monkeypatch, processor):
    def mock_create(*args, **kwargs):
        class MockResponse:
            class Choice:
                message = type("obj", (object,), {"content": "Category: inquiry\nConfidence: 4"})
            choices = [Choice()]
        return MockResponse()

    monkeypatch.setattr(processor.client.chat.completions, "create", mock_create)

    automation = EmailAutomationSystem(processor)
    email = {
        "id": "test008",
        "subject": "Info needed",
        "body": "Just wondering about features"
    }
    result = automation.process_email(email)
    assert result["confidence"] == 4
    assert result["classification"] == "inquiry"

# Full pipeline test
def test_end_to_end_automation_success(automation):
    email = {
        "id": "test009",
        "subject": "Thanks!",
        "body": "Great service from your team!"
    }
    result = automation.process_email(email)
    assert result["success"] is True
    assert result["classification"] in automation.processor.valid_categories
    assert isinstance(result["response_sent"], str)

# Malformed LLM output (missing category)
def test_malformed_llm_output(monkeypatch, processor):
    def mock_create(*args, **kwargs):
        class MockResponse:
            class Choice:
                message = type("obj", (object,), {"content": "Confidence: 5"})
            choices = [Choice()]
        return MockResponse()

    monkeypatch.setattr(processor.client.chat.completions, "create", mock_create)

    email = {
        "id": "test010",
        "subject": "Missing category",
        "body": "This will confuse the parser"
    }
    result = processor.classify_email(email)
    assert result == "other"
