from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import time
import logging
import os
import asyncio
from src.config import API_KEY, MODEL_NAME, TEMPERATURE  # Import configuration

logger = logging.getLogger(__name__)

COST_PER_1K_TOKENS = 0.0015
COST_LOG_PATH = "logs/costs.log"
os.makedirs(os.path.dirname(COST_LOG_PATH), exist_ok=True)

async def async_safe_chat_completion(messages, model=None, temperature=None, max_retries=3):
    model = model or MODEL_NAME  # Use the model from config.py, default to MODEL_NAME
    temperature = temperature if temperature is not None else TEMPERATURE  # Use the temperature from config.py, default to TEMPERATURE

    for attempt in range(max_retries):
        try:
            llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                openai_api_key=API_KEY,  # Use API_KEY from config.py
            )

            schema_messages = [HumanMessage(content=msg.get("content", "")) for msg in messages]

            start = time.time()
            response = await llm.ainvoke(schema_messages)
            duration = round(time.time() - start, 2)

            # Ensure this function exists in your version, or calculate manually
            token_usage = llm.get_num_tokens_from_messages(schema_messages)
            cost = round((token_usage / 1000) * COST_PER_1K_TOKENS, 6)

            # Log the cost and token usage
            with open(COST_LOG_PATH, "a") as f:
                f.write(f"{token_usage} tokens | ${cost} estimated | {duration}s\n")

            return response.content
        except OpenAIError as e:
            logger.warning(f"[Attempt {attempt + 1}] OpenAI API Error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                return None
        except Exception as e:
            logger.error(f"[Attempt {attempt + 1}] General Error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                return None
