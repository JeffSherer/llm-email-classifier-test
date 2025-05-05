import os
import sys
import json
import asyncio
from typing import Optional
from email_processing.email_processor import EmailProcessor

def load_json(path: str) -> Optional[dict]:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read file {path}: {e}")
        return None

async def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <email.json>")
        sys.exit(1)

    email_path = sys.argv[1]
    email = load_json(email_path)
    if not email:
        sys.exit(1)

    processor = EmailProcessor()
    
    # Assuming classify_email is an async function
    category = await processor.classify_email(email)
    confidence = processor.last_confidence

    if not category:
        print("[FAIL] Classification failed.")
        sys.exit(1)

    print(f"[INFO] Classified as: {category} (confidence: {confidence}/5)")

    # Await the generate_response function
    response = await processor.generate_response(email, category)
    if response:
        print("\n=== Generated Response ===\n")
        print(response)
    else:
        print("[FAIL] Response generation failed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
