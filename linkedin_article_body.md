The problem with most code review automation is not that it misses every issue. The problem is that it forgets what happened the last ten times it found one.

I ran into this while building CodeRecall Reviewer, a memory-aware code review system that uses Hindsight to connect static findings with past review outcomes. The useful idea was smaller than I expected: find a concrete issue, recall similar past findings, then change the recommendation based on whether developers usually accepted or ignored the advice.

That sounds almost too simple, but the simplicity is the point. A linter can tell me that `print()` made it into a production path. A static analyzer can flag a secret-looking assignment. What those tools usually cannot tell me is whether this team repeatedly ignores that class of warning, whether the last three suggestions worked, or whether a stronger guardrail is now justified.

I did not need another detector first. I needed memory.

## What CodeRecall Does

CodeRecall Reviewer is built around a compact review loop:

1. Read a source file.
2. Detect review findings.
3. Query Hindsight for related historical review outcomes.
4. Generate a recommendation using both the current finding and recalled memory.
5. Store the current outcome so future reviews have more context.

The core project is split into a few small modules:

- `reviewer.py` owns issue detection.
- `memory_reviewer.py` orchestrates file review, memory recall, and output.
- `recommendation_engine.py` decides how prior outcomes change the recommendation.
- `hindsight_memory.py` stores review outcomes in Hindsight.
- `config.py` loads API keys and runtime configuration.

The interesting part is not the detector. It is the decision to treat review feedback as something with history.

## Architecture Diagram

[UPLOAD IMAGE: assets/coderecall-architecture.png]

Architecture: deterministic detection finds the issue; Hindsight supplies the history; the recommendation engine decides what to do with both.

The important boundary is that Hindsight does not replace detection. It gives the reviewer historical context after a concrete issue has already been found.

## The First Useful Loop

The review loop starts with detection. In the repository, that boundary is represented by a small `review_code` function:

```python
def review_code(code):

    findings = []

    if "password =" in code:
        findings.append(
            "Hardcoded password detected"
        )

    if "print(" in code:
        findings.append(
            "Debug print statement detected"
        )

    return findings
```

The production detector is stricter than this excerpt, but the interface stayed intentionally boring: source code goes in, review findings come out. That kept the memory work separate from the parsing work.

If the reviewer finds:

```python
password = "admin123"

print("hello")
```

the basic findings are obvious:

```text
Hardcoded password detected
Debug print statement detected
```

A conventional tool stops there. It emits generic advice:

```text
Use environment variables instead of hardcoded credentials.
Remove debug print statements before production deployment.
```

That advice is not wrong. It is just incomplete. If a team has ignored hardcoded-password comments five times in a row, repeating the same suggestion is not persistence. It is amnesia. Maybe the code path is test-only and needs better classification. Maybe the team needs a blocking rule. Maybe the recommendation should include a migration path, not just a warning.

That is where [Hindsight agent memory](https://github.com/vectorize-io/hindsight) became useful. I wanted the review system to recall previous review outcomes, not just previous source text.

## Memory as Review Context

The memory write path stores a review outcome in Hindsight:

```python
from hindsight_client import Hindsight
from config import HINDSIGHT_API_KEY

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY
)

client.retain(
    bank_id="code-review-memory",
    content="""
Issue: Hardcoded Password

Suggestion:
Use environment variables.

Status:
Ignored
"""
)
```

Each memory needs enough structure to answer a future question:

- What issue did we find?
- What did we recommend?
- What happened?

I do not want the next review to retrieve arbitrary notes. I want it to retrieve operationally relevant memory: previous review outcomes.

The read path is equally direct:

```python
memories = client.recall(
    bank_id="code-review-memory",
    query=finding
)
```

[UPLOAD IMAGE: assets/hindsight-retain-recall-terminal.png]

Retain/recall: CodeRecall stores review outcomes in Hindsight, then queries them when a similar finding appears again.

That line is doing a lot of architectural work. The current finding becomes the query. Hindsight returns related prior outcomes. The recommendation engine then interprets those memories.

The [Hindsight documentation](https://hindsight.vectorize.io/) describes the mechanics of retaining and recalling memory, but the important design choice was deciding what should become memory. I stored outcomes.

That avoided a common trap with memory systems: dumping logs into a vector store and hoping useful behavior falls out later. Review memory needs a schema, even if the schema starts as text.

## The Recommendation Engine Is Deliberately Boring

The recommendation engine started with a boring rule: count what happened before.

```python
def generate_recommendation(
    finding,
    memories
):

    accepted = 0
    ignored = 0

    finding_lower = finding.lower()

    for memory in memories:

        text = memory.text.lower()

        if "password" in finding_lower:

            if "password" not in text:
                continue

        elif "debug" in finding_lower:

            if (
                "debug" not in text
                and
                "print" not in text
            ):
                continue

        if "accepted" in text:
            accepted += 1

        if (
            "ignored" in text
            or
            "rejected" in text
        ):
            ignored += 1
```

This is not a clever algorithm. That is why I like it. The system filters recalled memories by issue family, counts whether prior recommendations were accepted or ignored, and changes the final recommendation based on that count:

```python
if accepted > ignored:

    return (
        f"{finding}\n\n"
        f"Past fixes were mostly accepted.\n"
        f"Recommend applying the same solution."
    )

elif ignored > accepted:

    return (
        f"{finding}\n\n"
        f"Past fixes were often ignored.\n"
        f"Recommend stronger enforcement."
    )

else:

    return (
        f"{finding}\n\n"
        f"No clear team preference found."
    )
```

There is a temptation to reach for a more sophisticated policy engine immediately. I resisted that. The useful baseline needed to answer one question reliably:

> Did this advice work the last few times we gave it?

That question is simple enough to debug and useful enough to change behavior. If hardcoded-password guidance is usually accepted, the reviewer can keep recommending the established fix. If it is usually ignored, the reviewer can escalate from "please consider" to "this should be enforced by a secret scanner or pre-merge check."

This made the system easier to trust. Experienced engineers are allergic to tools that sound certain for no reason. "No clear team preference found" is sometimes the most honest output.

## Orchestrating the Review

The main workflow ties detection, memory recall, and recommendation together:

```python
with open(
    file_path,
    "r"
) as f:
    code = f.read()

findings = review_code(code)

for finding in findings:

    memories = client.recall(
        bank_id="code-review-memory",
        query=finding
    )

    recommendation = (
        generate_recommendation(
            finding,
            memories.results
        )
    )

    print("\nFINAL RECOMMENDATION:")
    print(recommendation)
```

In production, this loop runs against changed files in a pull request and writes structured review output back to the developer workflow. The important shape is the same:

```text
finding -> recall related outcomes -> adapt recommendation
```

The system does not ask Hindsight to "review code." The detector identifies the present issue. Hindsight supplies the past. The recommendation engine decides how the past should affect the present response.

## A Concrete Example

Suppose the reviewer sees this:

```python
password = "admin123"
```

On a project with no relevant memory, the output can be conservative:

```text
Hardcoded password detected

No clear team preference found.
```

After Hindsight has retained prior review outcomes like:

```text
Issue: Hardcoded Password
Suggestion: Use environment variables.
Status: Ignored
```

the next review changes:

```text
Hardcoded password detected

Past fixes were often ignored.
Recommend stronger enforcement.
```

[UPLOAD IMAGE: assets/coderecall-review-output.png]

Output: the finding is the same, but the recommendation changes because Hindsight recalled ignored prior fixes.

That is a small change, but it is the difference between generic advice and contextual advice. For debug prints, the behavior can go the other way:

```text
Debug print statement detected

Past fixes were mostly accepted.
Recommend applying the same solution.
```

This is the part I cared about most: the reviewer can be stricter where gentle suggestions have failed and quieter where the existing advice already works.

## Why Hindsight Fit This Problem

I used Hindsight because this problem is not just search and not just storage. It is memory attached to an agent workflow.

The distinction matters. A database can store every review result. A search index can retrieve matching strings. But for a review agent, I needed a memory bank that could recall relevant prior experiences at the moment of decision.

The [Vectorize explanation of agent memory](https://vectorize.io/what-is-agent-memory) maps closely to this use case: the system improves future behavior by carrying forward useful context from previous interactions. In CodeRecall, that context is engineering feedback history.

The most useful memories were not long. They were small, factual records:

```text
Issue: Debug Print Statement
Suggestion: Remove debug print statements before production deployment.
Status: Accepted
```

Small memories are easier to inspect, easier to prune, and easier to explain when someone asks, "Why did the reviewer say this?"

## The Painful Parts

The first painful part was deciding what not to remember. It is easy to keep adding context: file path, author, reviewer, repository, timestamp, severity, diff hunk, final merged code, linked ticket, CI state. Some of that is useful. Too much of it makes the system harder to reason about.

I settled on issue, suggestion, and outcome as the minimum useful memory. Everything else can be layered on later.

The second painful part was avoiding fake intelligence. It would have been easy to generate a more elaborate paragraph for every finding, making the system feel more capable and less predictable.

I preferred a blunt recommendation:

```text
Past fixes were often ignored.
Recommend stronger enforcement.
```

That sentence is not flashy, but an engineer can act on it: add a blocking check, tighten a rule, or improve the migration path.

The third painful part was accepting that detection quality and memory quality are separate problems. Better static analysis matters, but better detection does not solve repeated ignored feedback.

That was the core lesson of the project.

## What I Learned

### Memory Should Store Outcomes, Not Noise

The most valuable review memories were not full conversations. They were compact records of what was found, what was suggested, and what happened next.

That made recall useful. It also made the recommendation layer testable.

### Start With a Boring Policy

Counting accepted versus ignored outcomes sounds primitive. It is also transparent. Before adding more advanced ranking or model-driven reasoning, I wanted one behavior I could explain in a sentence.

If ignored outcomes dominate, escalate. If accepted outcomes dominate, repeat the known fix. If neither dominates, say there is no clear signal.

That policy is not the end state, but it is a solid baseline.

### Generic Advice Has a Half-Life

"Use environment variables" is good advice the first time. After it has been ignored several times, the problem has changed. The issue is no longer only a hardcoded password. The issue is that the current intervention does not work.

Hindsight made that visible.

### Explain the Memory Behind the Recommendation

A memory-aware reviewer should be able to say why its advice changed. "Past fixes were often ignored" is not just flavor text. It is the reason for the recommendation.

That explanation is what keeps the system from feeling arbitrary.

## The Part I Still Like

Code review automation does not need to pretend every finding is new. It can remember what happened before, notice when advice worked, and stop repeating itself when advice failed.

Hindsight gave me a practical way to add that memory without turning the reviewer into an opaque blob. The detector finds the issue. Hindsight recalls the history. The recommendation engine makes a plain decision.

