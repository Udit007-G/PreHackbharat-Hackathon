from hindsight_client import Hindsight
from config import HINDSIGHT_API_KEY

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY
)

client.retain(
    bank_id="code-review-memory",
    content="""
Issue: Debug Print Statement

Suggestion:
Remove debug print statements before production deployment.

Status:
Accepted
"""
)

client.close()

print("Debug memory stored.")