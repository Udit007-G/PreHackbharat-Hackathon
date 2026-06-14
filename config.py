from dotenv import load_dotenv
import os

load_dotenv()

HINDSIGHT_API_KEY = os.getenv(
    "HINDSIGHT_API_KEY"
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)