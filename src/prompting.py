# src/prompting.py

from src.data import CATEGORY_DEFINITIONS, SAMPLE_RESPONSES


def build_classification_prompt(subject: str, body: str) -> str:
    return (
        "You are a highly trained AI assistant tasked with classifying emails into the correct category.\n\n"
        "Categories:\n"
        + "\n".join([f"- {k}: {v}" for k, v in CATEGORY_DEFINITIONS.items()])
        + "\n\n"
        f"Email:\nSubject: {subject}\nBody: {body}\n\n"
        "Respond in this format:\n"
        "Category: <category>\nConfidence: <1-5>"
    )


def build_response_prompt(subject: str, body: str, category: str, sender: str) -> str:
    guidance = SAMPLE_RESPONSES.get(category, "")
    tone_hint = (
        f"Note: This user ({sender}) may have prior interactions or a specific tone preference. "
        "Adjust tone accordingly while keeping the response clear and professional."
    )

    return (
        "You are a professional customer service assistant generating responses to user emails.\n\n"
        f"Category: {category}\nGuidance: {guidance}\n{tone_hint}\n\n"
        "Please follow these steps:\n"
        "1. Summarize the issue.\n"
        "2. Infer the tone (angry, happy, confused, etc).\n"
        "3. Assess urgency (low, medium, high).\n"
        "4. Write a clear and empathetic reply using the brand tone.\n\n"
        f"Email:\nSubject: {subject}\nBody: {body}\n\n"
        "Respond in this format:\n"
        "Reasoning:\n"
        "1. Summary: <summary>\n"
        "2. Tone: <tone>\n"
        "3. Urgency: <urgency>\n\n"
        "Drafted Response:\n"
        "<response>"
    )
