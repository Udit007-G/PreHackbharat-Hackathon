import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None


if load_dotenv:
    load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io",
)
HINDSIGHT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "code-review-memory")
LOCAL_MEMORY_PATH = os.getenv("LOCAL_MEMORY_PATH", "memory_seed.json")
