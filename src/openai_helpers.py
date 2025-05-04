import time
import logging
import openai
import os

logger = logging.getLogger(__name__)

COST_PER_1K_TOKENS = 0.0015  # Adjust based on current pricing
COST_LOG_PATH = "logs/costs.log"
os.makedirs(os.path.dirname(COST_LOG_PATH), exist_ok=True)

def safe_chat_completion(client, messages, model="gpt-3.5-turbo-0125", temperature=0, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            usage = getattr(response, "usage", None)
            if usage:
                tokens = usage.total_tokens
                cost = round((tokens / 1000) * COST_PER_1K_TOKENS, 6)
                with open(COST_LOG_PATH, "a") as f:
                    f.write(f"{tokens} tokens | ${cost} estimated\n")
            return response.choices[0].message.content
        except openai.RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise
        except openai.AuthenticationError:
            return None
        except openai.OpenAIError:
            return None
        except Exception:
            return None
