# src/demo_email_run.py

from src.email_processor import EmailProcessor

email = {
    "id": "demo001",
    "subject": "Question about pricing plans",
    "body": "Hi, can you explain the different pricing options you offer?",
    "from_": "returning_user@example.com",
}

processor = EmailProcessor()
classification = processor.classify_email(email)
response = processor.generate_response(email, classification)

print("\n=== Final Response ===")
print(response)
