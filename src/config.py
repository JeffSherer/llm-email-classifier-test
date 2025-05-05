# src/config.py
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the environment variables
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))  # Default to 0.7 if not set
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1500))  # Default to 1500 if not set
