# LLM Email Classifier and Automation System

## Overview

This project demonstrates a system that uses a Large Language Model (LLM) to:
- **Classify** incoming emails into structured categories
- **Generate** chain-of-thought structured replies based on email content
- **Automate** responses or actions depending on classification

The system follows a modular design using OpenAI's `gpt-3.5-turbo` API, with clean error handling, structured prompting, and logging.

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/your-repo-here.git
cd llm-email-classifier-test
```

2. **Create and activate a virtual environment**

```bash
conda create -n cadre-ai python=3.10
conda activate cadre-ai
```

3. **Install dependencies**

```bash
pip install pandas openai python-dotenv
```

4. **Create a `.env` file in the root directory**

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

*Note: Make sure your API key has the correct permissions.*

---

## Project Structure

| File | Description |
|:---|:---|
| `email_classifier_template.py` | Main script containing email processor, automation system, and demonstration runner |
| `.env` | Contains your OpenAI API key (not tracked by version control) |
| `requirements.txt` | (Optional) File listing required Python packages |

---

## Main Components

- **EmailProcessor**
  - `classify_email(email)`: Classifies an email using chain-of-thought prompting
  - `generate_response(email, classification)`: Generates a professional, reasoned reply
  - `extract_email_parts(subject, body)`: Simple extractor for email information

- **EmailAutomationSystem**
  - `process_email(email)`: Complete processing pipeline (classify → generate → handle)
  - Category-specific handlers: complaint, inquiry, feedback, support_request, other

- **Mock Service Functions**
  - Simulate sending responses, creating tickets, and logging feedback

---

## How It Works

- Emails are **classified** into:
  - `complaint`
  - `inquiry`
  - `feedback`
  - `support_request`
  - `other`

- Responses are **generated** with explicit reasoning steps:
  - Issue summary
  - Tone detection
  - Urgency assessment
  - Final email draft

- **Automated actions** are triggered based on classification:
  - Sending a response
  - Creating a support or urgent ticket
  - Logging customer feedback

---

## To Run the Demonstration

```bash
python email_classifier_template.py
```

You will see:
- Logging output in your terminal
- A printed summary of email processing results

---

## Notes

- The system uses **Chain of Thought prompting** for better LLM decision-making.
- Designed for **easy production integration** with real-world services.
- Logging is added for visibility and easier troubleshooting.

---
