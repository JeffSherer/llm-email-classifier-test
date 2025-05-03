import argparse
import logging
import os

from src.email_processor import EmailProcessor

# === Logging setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("email_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Override safe_chat_completion to log usage + cost ===
from src.openai_helpers import safe_chat_completion as original_safe_chat_completion

def wrapped_safe_chat_completion(client, messages, temperature=0):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature,
    )
    content = response.choices[0].message.content
    usage = response.usage
    total_tokens = usage.total_tokens
    print(f"🧾 Tokens used: {total_tokens}")
    print(f"💵 Estimated cost: ${(total_tokens / 1000) * 0.0015:.6f}")
    return content

# Monkey patch the function used inside EmailProcessor
import src.openai_helpers
src.openai_helpers.safe_chat_completion = wrapped_safe_chat_completion


# === Main execution ===
def main():
    parser = argparse.ArgumentParser(description="Run email classification and response.")
    parser.add_argument("--subject", type=str, required=True, help="Email subject")
    parser.add_argument("--body", type=str, required=True, help="Email body")
    parser.add_argument("--from_email", type=str, default="user@example.com", help="Sender email")
    args = parser.parse_args()

    sample_email = {
        "id": "cli-test",
        "subject": args.subject,
        "body": args.body,
        "from_": args.from_email
    }

    processor = EmailProcessor()

    print("\n=== 📧 Running classification ===")
    category = processor.classify_email(sample_email)

    if category:
        print(f"\n📝 Detected Category: {category}")
        print("\n=== ✍️ Running response generation ===")
        response = processor.generate_response(sample_email, category)

        print("\n📨 Final Response:\n")
        print(response)
    else:
        print("❌ Classification failed. Skipping response generation.")


if __name__ == "__main__":
    main()

