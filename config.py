import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"  
CONFIDENCE_THRESHOLD = 0.7
MAX_TOKENS = 1000  
TEMPERATURE = 0.1  