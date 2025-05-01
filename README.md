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
git clone https://github.com/JeffSherer/llm-email-classifier-test.git
cd llm-email-classifier-test
```

2. **Create and activate a virtual environment**

```bash
conda create -n cadre-ai python=3.10
conda activate cadre-ai
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
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
| `requirements.txt` | File listing required Python packages |
| `README.md` | This documentation |

---

## System Architecture

| Component | Purpose |
|:---|:---|
| `EmailProcessor` | Classifies emails and generates responses with Chain of Thought prompting |
| `EmailAutomationSystem` | Full pipeline for processing, handling, and logging email interactions |
| Mock functions | Simulate sending email responses, creating support tickets, logging feedback |

---

## Key Features

- **Email Classification** using structured prompts and step-by-step reasoning
- **Automated Response Generation** with structured logic
- **Mock Integrations** for ticket creation and feedback logging
- **Chain-of-Thought Prompting** improves LLM reliability
- **Extensive Logging** for all classification and generation steps
- **Graceful Error Handling** for all parts of the pipeline

---

## Categories Used
- `complaint`
- `inquiry`
- `feedback`
- `support_request`
- `other`

---

## How It Works

1. Emails are loaded from a sample list.
2. Each email is processed:
   - Classified with the LLM
   - Reasoned over to extract tone, urgency, and draft a reply
   - Mock services simulate sending responses or logging actions
3. A final summary is printed using a pandas DataFrame.

---

## To Run the Demonstration

```bash
python email_classifier_template.py
```

You will see:
- Logging output in your terminal
- A printed summary of email processing results

---

## Development Log and Fixes

### Prompt Engineering
- Iterated on classification prompt to include step-by-step thinking
- Switched to a more structured reasoning format for response generation
- All prompts now explicitly separate reasoning from the final output

### Environment Errors
- Initially encountered NumPy compatibility issues
- Fixed by recreating the environment with pinned versions
- Confirmed compatibility by running on clean machines

### Code Structure
- All logic kept in a single file for simplicity
- Separation of concerns respected (processing vs. automation)
- Logging and validation added to support debugging and testing

---

## Evaluation Criteria Coverage

| Criterion | Addressed |
|----------|-----------|
| Code Quality | ✅ Modular, documented, validated |
| LLM Integration | ✅ Clean API handling, prompt tuning |
| Prompt Engineering | ✅ Iterative refinement, reasoning chain |
| System Design | ✅ Logging, extensibility, fail-safe guards |

---

## Testing

You can run basic manual tests using the provided `sample_emails` list.
Automated tests (e.g., using `pytest`) can be added in a `tests/` directory.

Sample test case outline:

```python
# tests/test_classification.py
import pytest
from email_classifier_template import EmailProcessor

@pytest.fixture
def processor():
    return EmailProcessor()

def test_complaint_classification(processor):
    email = {
        "id": "test-001",
        "subject": "Product broken",
        "body": "I received a damaged item. This is unacceptable. I want a refund."
    }
    result = processor.classify_email(email)
    assert result == "complaint"
```

---

## Final Notes

- The system can be extended easily with real email APIs
- Logging provides visibility during execution and failure points
- Designed with production patterns but scoped for evaluation

---

## Author
Jeffrey Sherer

---

## License
MIT (add `LICENSE` file if needed)

---