# LLM Email Classifier and Responder

This project classifies incoming emails into predefined categories and generates structured, empathetic responses using GPT-based LLMs via LangChain. It logs usage history, cost estimates, and supports containerized deployment.

## Features

- Email classification with confidence rating  
- Contextual response generation using LangChain  
- Email history logging per sender  
- Usage-based token cost tracking  
- CLI support for JSON input  
- Dockerized deployment  

## Project Structure

```
llm-email-classifier-test/
├── src/
│   ├── email_processor.py         # Core logic for classification and response  
│   ├── email_history.py           # History tracking for past emails  
│   ├── prompting.py               # Prompt builders  
│   ├── validation.py              # Input validation  
│   ├── openai_helpers.py          # LangChain + cost logging  
│   └── ...
├── logs/
│   └── costs.log                  # Auto-generated token usage log  
├── tests/                         # Test suite  
├── sample_email.json             # Example input  
├── run.py                        # CLI entry point  
├── requirements.txt              # Python dependencies  
├── Dockerfile                    # Docker build config  
├── .env.example                  # Sample environment file  
└── README.md  
```

## Setup

1. **Install dependencies**  
```bash
pip install -r requirements.txt
```

2. **Set your OpenAI API key**  
```bash
cp .env.example .env
# then edit .env with your OpenAI API key
```

3. **Run from command line**  
```bash
python run.py sample_email.json
```

4. **Run in Docker**  
```bash
docker build -t email-classifier-app .
docker run --rm -v $(pwd):/app --env-file .env email-classifier-app python run.py sample_email.json
```

## Input Format (`sample_email.json`)

```json
{
  "from_": "returning_user@example.com",
  "subject": "Pricing Options",
  "body": "Can you explain your monthly plans? I'm deciding between options."
}
```

## 🧪 Run Tests

```bash
pytest -v tests/
```