"""Model config. Swap providers here, nowhere else."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

AGENT_MODEL = "gemini-2.5-flash"
JUDGE_MODEL = "gemini-2.5-flash-lite"   # separate free-tier quota bucket


def get_model(name: str = AGENT_MODEL):
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=name,
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        temperature=0,
    )