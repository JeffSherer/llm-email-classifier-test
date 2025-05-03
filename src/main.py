from src.email_automation import EmailAutomationSystem
from src.email_processor import EmailProcessor
from src.sample_emails import sample_emails

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_demonstration():
    """Run a demonstration of the complete system."""
    processor = EmailProcessor()
    automation_system = EmailAutomationSystem(processor)

    results = []
    for email in sample_emails:
        logger.info(f"\nProcessing email {email['id']}...")
        result = automation_system.process_email(email)
        results.append(result)

    df = pd.DataFrame(results)
    print("\nProcessing Summary:")
    print(df[["email_id", "success", "classification", "response_sent"]])

    print("\n=== ✅ DEMO COMPLETED SUCCESSFULLY ===")
    print("Summary of processed emails:\n")
    print(
        df[["email_id", "success", "classification", "confidence"]].to_string(
            index=False
        )
    )
    print("\nGenerated responses (preview):\n")
    for idx, row in df.iterrows():
        print(f"\U0001F4E8 Email {row['email_id']} → {row['classification']}")
        print(f"✉️  Response:\n{row['response_sent'][:200]}...\n")

    return df

if __name__ == "__main__":
    run_demonstration()
