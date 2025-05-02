# LLM Email Classifier and Automation System

## Overview

This project implements an automated email classification and response system powered by OpenAI’s `gpt-3.5-turbo-0125`. It:

- **Classifies** emails into predefined categories  
- **Generates** chain-of-thought based customer service replies  
- **Automates** responses or support actions based on classification  

The architecture is modular, fault-tolerant, and designed to reflect real-world LLM integration best practices.

---

## Setup Instructions

```bash
# Clone the repo
git clone https://github.com/JeffSherer/llm-email-classifier-test.git
cd llm-email-classifier-test

# Create and activate a virtual environment
conda create -n cadre-ai python=3.10
conda activate cadre-ai

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI key
echo "OPENAI_API_KEY=your_key_here" > .env
```

---

## Project Structure

| File/Folder              | Description                                                |
|--------------------------|------------------------------------------------------------|
| `email_classifier_template.py` | Main system logic (classification, response, automation)     |
| `tests/`                 | Test suite using `pytest` and `monkeypatch`                |
| `.env`                   | API key storage (excluded from version control)            |
| `requirements.txt`       | Python dependencies                                        |

---

## How It Works

Each email is passed through the following steps:

1. **Classification** using LLM and a structured prompt  
2. **Confidence score** (1–5) is parsed from the output  
3. If confidence is too low or category is invalid, fallback to `"other"`  
4. **Structured response** is generated using reasoning format  
5. **Routing** triggers a mock action (e.g., create ticket, send response)  
6. Results are stored and summarized with `pandas`  

---

## Key Features

These components implement the core requirements of the assignment:

- **Email Validation**  
  Ensures each email has required fields (`id`, `subject`, `body`) before processing.

- **LLM Classification via Prompting**  
  Uses OpenAI's `gpt-3.5-turbo-0125` with a structured prompt to classify emails into one of five categories.  
  This model was selected for its reliable latency and cost-performance balance, sufficient for the classification and reasoning tasks.

- **Confidence-Based Safeguard**  
  Parses model’s self-reported confidence (1–5). Falls back to `"other"` if score is low or output is malformed.

- **Chain-of-Thought Response Generation**  
  Generates helpful, empathetic replies by reasoning through issue summary, tone, and urgency before drafting the message.

- **Pipeline Automation**  
  Full flow: classification → response → routed action. Each component is modular and testable.

- **Logging and Summary Output**  
  Logs decisions and prints a summary DataFrame with email ID, classification, confidence, and success status.

- **Robust Error Handling**  
  Catches malformed input, OpenAI errors, and unexpected outputs without crashing the system.

---

## Run the Demo

```bash
python email_classifier_template.py
```

You’ll see terminal logs and a pandas summary table showing:
- Email ID
- Classification
- Confidence score
- Response text
- Success status

---

## Testing

Tests are written with `pytest` and include:

- Valid classification and response generation  
- Handling of missing fields  
- Handling malformed or invalid LLM responses  
- Low-confidence fallback  
- Full pipeline integration  

Run tests with:

```bash
pytest tests/test_email_processor.py -v
```

---

## Design Additions

These enhancements improve performance, reliability, and testability beyond the base assignment:

### Retry Logic for OpenAI API Calls  
Retries once on `RateLimitError`, `APIError`, or `OpenAIError` to avoid transient failure.

### Confidence Scoring and Fallback  
Extracts a 1–5 confidence rating from the LLM. Falls back to `"other"` on low confidence or invalid category to protect response quality.

### Structured Prompting  
Uses explicit, step-by-step prompting for both classification and generation. Improves model reliability and simplifies downstream parsing.

### Mocked LLM in Tests  
Mocks LLM responses using `monkeypatch` to test classification, generation, and failure scenarios without hitting the API.

### Integrated Logging  
Logs key flow events including classification results, retry attempts, errors, and response generation for full traceability.

### End-to-End Integration Tests  
Verifies full flow from email input to final action handling to ensure component coordination.

---

## Author

Jeffrey Sherer
