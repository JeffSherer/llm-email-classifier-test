import time
import logging
import openai

logger = logging.getLogger(__name__)

def safe_chat_completion(client, messages, model="gpt-3.5-turbo-0125", temperature=0, max_retries=3):
    """Run OpenAI chat completion with latency and token usage logging."""
    for attempt in range(max_retries):
        try:
            # Log the messages being sent
            logger.info(f"Sending messages: {messages}")

            start = time.time()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            duration = round(time.time() - start, 2)

            # Log the API response
            logger.info(f"Response: {response}")

            usage = getattr(response, "usage", None)
            token_info = f"{usage.total_tokens} tokens" if usage else "unknown tokens"

            logger.info(f"LLM completed in {duration}s using {token_info}")
            return response.choices[0].message.content
        except openai.RateLimitError as e:
            logger.warning(f"Rate limited. Attempt {attempt + 1}/{max_retries}. Retrying...")
            if attempt < max_retries - 1:
                time.sleep(2)  # Retry after 2 seconds
            else:
                logger.error("Max retries reached. Rate limit still in place.")
                raise
        except openai.AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return None
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return None
