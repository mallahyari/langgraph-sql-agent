import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_openai_client() -> AsyncOpenAI:
    """Returns a configured AsyncOpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables.")
        _client = AsyncOpenAI(api_key=api_key)
    return _client
