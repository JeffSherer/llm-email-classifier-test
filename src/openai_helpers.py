from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import time
import logging
import os
import asyncio

logger = logging.getLogger(__name__)

COST_PER_1K_TOKENS = 0.0015
COST_LOG_PATH = "logs/costs.log"
os.makedirs(os.path.dirname(COST_LOG_PATH), exist_ok=True)

async def async_safe_chat_completion(messages, model="gpt-3.5-turbo-0125", temperature=0, max_retries=3):
    for attempt in range(max_retries):
        try:
            llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            )

            schema_messages = [HumanMessage(content=msg.get("content", "")) for msg in messages]

            start = time.time()
            response = await llm.ainvoke(schema_messages)
            duration = round(time.time() - start, 2)

            token_usage = llm.get_num_tokens_from_messages(schema_messages)
            cost = round((token_usage / 1000) * COST_PER_1K_TOKENS, 6)

            with open(COST_LOG_PATH, "a") as f:
                f.write(f"{token_usage} tokens | ${cost} estimated | {duration}s\n")

            return response.content
        except Exception as e:
            logger.warning(f"[Attempt {attempt + 1}] Error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                return None
