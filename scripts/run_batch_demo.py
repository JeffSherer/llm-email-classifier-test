# scripts/run_batch_demo.py

import os
import json
import pandas as pd
import logging
import asyncio

from email_processing.email_processor import EmailProcessor
from email_processing.email_automation import EmailAutomationSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_emails_from_dir(dir_path):
    emails = []
    for file_name in os.listdir(dir_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(dir_path, file_name)
            try:
                with open(file_path, "r") as f:
                    email = json.load(f)
                    emails.append(email)
            except Exception as e:
                logger.warning(f"[SKIP] {file_name} - could not load: {e}")
    return emails

async def run_batch_demo(email_dir="data/inbox"):
    processor = EmailProcessor()
    automation_system = EmailAutomationSystem(processor)
    emails = load_emails_from_dir(email_dir)

    if not emails:
        print("[ERROR] No valid emails found.")
        return

    results = []
    for email in emails:
        try:
            logger.info(f"\nProcessing email {email['id']} from {email['from']}...")
            result = await automation_system.process_email(email)
        except Exception as e:
            logger.error(f"Failed to process email {email.get('id', 'unknown')}: {e}")
            result = {
                "email_id": email.get("id", "unknown"),
                "success": False,
                "classification": None,
                "confidence": None,
                "response_sent": "",
                "error": str(e)
            }
        results.append(result)

        # Save per-user log
        user_log_path = f"src/email_logs/{email['from'].replace('@', '_at_')}.jsonl"
        with open(user_log_path, "a") as f:
            f.write(json.dumps(result) + "\n")

    df = pd.DataFrame(results)
    print("\n=== ✅ BATCH PROCESSING COMPLETED ===")
    print(df[["email_id", "success", "classification", "confidence"]].to_string(index=False))

    print("\nGenerated responses (preview):\n")
    for row in df.itertuples():
        print(f"\U0001F4E8 Email {row.email_id} → {row.classification}")
        print(f"✉️  Response:\n{row.response_sent[:200]}...\n")

    return df

if __name__ == "__main__":
    asyncio.run(run_batch_demo())
