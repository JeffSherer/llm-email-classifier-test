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

## Prompt Design Decisions

The system uses **instructional prompting** to drive both classification and response generation. The prompts were optimized with several design goals in mind:

- **Expert Assistant Framing**  
  The model is instructed to act as a highly trained customer service representative, which guides tone and reasoning style.

- **Explicit Category Definitions**  
  Categories such as `inquiry`, `feedback`, and `support_request` are framed with real-world meanings to reduce overlap. Definitions are based on common customer service standards to improve model accuracy.

- **Reasoning Before Responding**  
  Chain-of-thought style instructions are included to encourage the model to explain its process before providing an output. This supports more stable and interpretable predictions.

- **Confidence Scoring**  
  The prompt asks the model to self-report confidence (1–5) which is then parsed and used as a fallback safeguard.

- **Format Reinforcement**  
  All outputs are constrained to a predictable structure (e.g., `Category:`, `Confidence:`, `Drafted Response:`), making parsing and downstream automation reliable and error-resistant.

- **Response Prompt Mirrors Real Support Flow**  
  The reply generation prompt mirrors a real agent's mental model: understand the issue → detect tone → assess urgency → write message. This structure makes generated replies more trustworthy and context-sensitive.

These prompt strategies collectively support accuracy, interpretability, and modular extensibility—key criteria for safe, real-world LLM deployment.

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

## Prompt Iteration and Design Reflection

### Prompt Iteration

This system evolved through multiple prompt iterations, starting simple and gradually incorporating more structure and safeguards.

**Initial Prompt (v1):**
- Basic task framing: “Classify this email into one of five categories.”
- No assistant persona or output formatting
- No reasoning steps or confidence scoring

**Problems Encountered:**
- Inconsistent output format made parsing unreliable
- Missing or incorrect category labels
- No way to detect ambiguous or low-confidence outputs

**Final Prompt Improvements:**
- **Persona Framing:** Assigned the role of a professional customer support assistant to guide tone and intent
- **Step-by-Step Reasoning:** Introduced a numbered thought process to improve consistency and accuracy
- **Category Definitions:** Added concise industry-aligned definitions for each classification label
- **Confidence Scoring:** Prompted the model to estimate its confidence on a 1–5 scale to handle uncertain cases programmatically
- **Structured Output Format:** Defined a fixed response structure (e.g., `Category: ...`, `Confidence: ...`) to support robust parsing

The generation prompt followed a similar progression, ultimately producing output that begins with structured reasoning steps (summary, tone, urgency) followed by a customer-ready reply.

---

### Design Decisions

Key choices made throughout development:

- **Model Selection:** Used `gpt-3.5-turbo-0125` with `temperature=0` for classification (for determinism) and `0.5` for response generation (for natural tone)
- **Fallback Logic:** Implemented confidence-based fallback to "other" category when confidence was low or outputs were malformed
- **Structured Prompting:** Both classification and generation prompts use explicit formatting to reduce variation and simplify parsing
- **Retry Mechanism:** Wrapped OpenAI API calls with a retry loop to handle rate limits and transient errors
- **Inline Logging:** Used Python logging to trace actions without interfering with normal execution

---

### Challenges Encountered

- **LLM Output Instability:** Early prompts yielded inconsistent and difficult-to-parse responses
- **Confidence Handling:** Needed to implement logic for low-confidence cases without adding unnecessary complexity
- **Prompt Token Budget:** Few-shot examples were tested but excluded due to prompt length concerns and sufficient performance without them
- **Single-Script Structure:** The provided boilerplate code was flat; refactoring into modules would have improved readability and testing

---

### Potential Improvements

- **Modularization:** Split logic into distinct modules (e.g., `config.py`, `data.py`, `prompting.py`, `handlers.py`, `demo.py`)
- **User-Tailored Prompts:** Adapt generation behavior based on prior user history, tone preference, or brand voice
- **Real Email Integration:** Connect to actual inboxes using IMAP/SMTP for live classification and response
- **Category-Specific Prompts:** Tailor prompts for each category (e.g., apologies for complaints, gratitude for feedback)
- **Extended Observability:** Add latency tracking, confidence trend logging, and response quality checks
- **Production Deployment:** Containerize the service, add schema validation, integrate with CI/CD and MLOps workflows

---

### Production Considerations

While designed for demonstration, the implementation accounts for real-world concerns:

- **Environment-based secrets management** for safe and flexible deployment
- **Error tolerance and graceful degradation** when faced with malformed inputs or LLM failures
- **Structured output for downstream integration** with ticketing systems, dashboards, or monitoring tools
- **Modular class design** for easy expansion to new categories or business logic

This setup could be extended into a production-ready customer support assistant with relatively minimal effort.


---

## Author

Jeffrey Sherer
