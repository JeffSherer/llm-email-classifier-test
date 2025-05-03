import time
import logging
import openai

logger = logging.getLogger(__name__)

def safe_chat_completion(client, messages, model="gpt-3.5-turbo-0125", temperature=0):
    """Run OpenAI chat completion with basic retry logic."""
    for attempt in range(2):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
        except openai.error.RateLimitError:
            logger.warning("Rate limited. Retrying...")
            time.sleep(2)
        except openai.error.APIError as e:
            logger.error(f"API error: {e}")
            return None
        except openai.error.OpenAIError as e:
            logger.exception("OpenAI error during chat completion.")
            return None
