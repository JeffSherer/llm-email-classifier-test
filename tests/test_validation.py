# tests/test_validation.py

from src.validation import validate_email_data

def test_valid_email_data():
    email = {
        "id": "test001",
        "subject": "Sample subject",
        "body": "Sample body",
        "from_": "user@example.com"
    }
    validated = validate_email_data(email)
    assert validated is not None
    assert validated.from_ == "user@example.com"

def test_missing_required_fields():
    email = {
        "id": "test002",
        "subject": "Missing body"
        # no body, no from_
    }
    validated = validate_email_data(email)
    assert validated is None

def test_invalid_email_format():
    email = {
        "id": "test003",
        "subject": "Invalid email",
        "body": "Body text",
        "from_": "not-an-email"
    }
    validated = validate_email_data(email)
    assert validated is None
