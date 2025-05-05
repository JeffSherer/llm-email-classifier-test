# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Configuration settings
API_KEY = os.getenv("OPENAI_API_KEY", "your-default-api-key-here")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")  # Default model if not set
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))  # Default temperature if not set
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1500))  # Default token limit if not set
