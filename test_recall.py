from hindsight_client import Hindsight
from config import HINDSIGHT_API_KEY

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY
)

results = client.recall(
    bank_id="code-review-memory",
    query="hardcoded password"
)

print(type(results))
print(results)