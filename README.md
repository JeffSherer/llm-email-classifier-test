# LLM Email Classifier and Automation System

This project implements an intelligent, automated pipeline for classifying customer emails and generating responses using OpenAI's GPT-3.5, with support for context-aware (RAG-based) replies and per-user memory. It is structured for modularity, extensibility, and real-world production readiness.

## Project Features

- **LLM-based Email Classification**
- **Chain-of-thought Response Generation**
- **Retrieval-Augmented Generation (RAG) for Support Context**
- **Per-User Email History Logging**
- **Batch Processing of Emails**
- **Confidence Thresholds and Error Recovery**
- **Mock Service Integrations for Action Simulation (e.g., ticketing)**

## Project Structure

```
llm-email-classifier-test/
├── data/
│   ├── inbox/                    
│   └── response_examples/        
├── logs/    
├── scripts/                    
├── src/
│   ├── __init__.py             
│   ├── config.py              
│   ├── email_processor.py       
│   ├── email_automation.py      
│   ├── mock_services.py        
│   ├── email_history.py         
│   ├── user_profile.py          
│   ├── prompting.py             
│   ├── rag_retriever.py        
│   ├── sample_emails.py         
│   ├── validation.py            
│   └── utils/                  
├── tests/                     
├── .env                       
├── pyproject.toml               
├── setup.py                    
└── README.md                    
```

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourname/llm-email-classifier-test.git
cd llm-email-classifier-test
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r pyproject.toml
```

### 3. Set OpenAI Key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_key_here
```

### 4. Enable Editable Mode (for clean imports)

```bash
pip install -e .
```

## Running the System

### Run Single Email

```bash
python python scripts/run_single_email.py data/inbox/email_001.json

```

### Run Batch Email Processing

This will process all `.json` emails in `data/inbox/`:

```bash
python -m scripts.run_batch_demo
```

## Inbox File Format

Each email should be a `.json` file in `data/inbox/`:

```json
{
  "id": "001",
  "from": "user@example.com",
  "subject": "Order issue",
  "body": "I received a damaged product. Please refund.",
  "timestamp": "2024-05-04T10:00:00Z"
}
```

## RAG Reference Files

Located in `data/response_examples/`. These `.txt` files store sample replies per category to improve context grounding for the LLM:

* `complaint.txt`
* `inquiry.txt`
* `feedback.txt`
* `support_request.txt`
* `other.txt`

## Developer Notes

* Per-user logs are stored in: `src/email_logs/{user}@example.com.jsonl`
* Modify prompts in: `src/prompting.py`
* Modify example-based RAG context: `src/rag_retriever.py`
* Classification logic: `src/email_processor.py`
* To add new categories, update:
  * `self.valid_categories` in `EmailProcessor`
  * `response_handlers` in `EmailAutomationSystem`
  * Add `.txt` context files in `data/response_examples/`

## Sample Run Output

After running `python -m scripts.run_batch_demo`, you'll see:

* Classification category
* Confidence score
* Response preview
* Logs showing RAG, reasoning, and mock service actions

## Testing and Logging

* Integration tests can be placed in `tests/`
* Cost tracking logs are saved to `logs/costs.log`
* Email processing logs show in console and `src/email_logs/`

## Notes

* RAG is context-aware but non-persistent across sessions unless user history is maintained
* The system is modular—each piece (classification, RAG, response) can be swapped or upgraded independently
* Designed for real-world extension (e.g., plug in IMAP, helpdesk ticketing APIs)