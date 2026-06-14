from reviewer import review_code

from hindsight_client import Hindsight

from config import HINDSIGHT_API_KEY

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY
)

with open(
    "sample_code.py",
    "r"
) as f:
    code = f.read()

findings = review_code(code)

for finding in findings:

    print("\n" + "=" * 50)

    print("CURRENT ISSUE:")
    print(finding)

    memories = client.recall(
        bank_id="code-review-memory",
        query=finding
    )

    print("\nRELEVANT MEMORIES:")

    for memory in memories.results:

        print("-")
        print(memory.text)

try:
    client.close()
except:
    pass