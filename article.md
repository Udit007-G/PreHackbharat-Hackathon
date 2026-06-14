# How Hindsight Helped My Reviewer Remember Ignored Fixes

The problem with most code review automation is not that it misses every issue. The problem is that it forgets what happened the last ten times it found one.

I ran into this while building CodeRecall Reviewer, a memory-aware code review system that uses Hindsight to connect static findings with past review outcomes. The first version of the idea was deliberately small: find hardcoded passwords and debug prints, recall similar past findings, then change the recommendation based on whether developers usually accepted or ignored the advice.

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

The architecture was designed so stronger detection rules and automatic outcome tracking can be added without changing the memory layer. But the shape of the architecture stayed close to the original version because the separation was useful: detection should not know how memory is stored, and recommendation logic should not know how source files are read.

The interesting part is not the detector. It is the decision to treat review feedback as something with history.

## Architecture Diagram

```text
Developer Code
      │
      ▼
Review Engine (reviewer.py)
      │
      ▼
Issue Detection
      │
      ▼
Memory Retrieval (Hindsight)
      │
      ▼
Recommendation Engine
      │
      ▼
Adaptive Feedback
```

## The First Useful Loop

The first version of the detector was intentionally plain:

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

That is not a production analyzer, and I would not pretend otherwise. The production version uses stronger parsing and rules. But this tiny function exposed the real design problem nicely.

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

That advice is not wrong. It is just incomplete.

If a team has ignored hardcoded-password comments five times in a row, repeating the same suggestion is not persistence. It is amnesia. Maybe the code path is test-only and needs better classification. Maybe the team needs a blocking rule. Maybe the recommendation should include a migration path, not just a warning. The next message should reflect what happened before.

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

The specific content format matters less than the contract. Each memory needs enough structure to answer a future question:

- What issue did we find?
- What did we recommend?
- What happened?

I do not want the next review to retrieve arbitrary notes. I want it to retrieve operationally relevant memory. For this project, that means previous review outcomes: accepted, ignored, rejected, deferred, or fixed by another mechanism.

The read path is equally direct:

```python
memories = client.recall(
    bank_id="code-review-memory",
    query=finding
)
```

That line is doing a lot of architectural work. The current finding becomes the query. Hindsight returns related prior outcomes. The recommendation engine then interprets those memories.

The [Hindsight documentation](https://hindsight.vectorize.io/) describes the mechanics of retaining and recalling memory, but the important implementation choice was deciding what should become memory in the first place. I did not store everything. I stored outcomes.

That avoided a common trap with memory systems: dumping logs into a vector store and hoping useful behavior falls out later. Review memory needs a schema, even if the schema starts as text. Without issue type, suggestion, and outcome, recall becomes trivia instead of context.

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

This is not a clever algorithm. That is why I like it.

The system first filters recalled memories by issue family. Then it counts whether prior recommendations were accepted or ignored. The final recommendation changes based on that count:

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

There is a temptation to reach for a more sophisticated policy engine immediately. I resisted that. The first useful version of memory-aware review did not need probabilistic scoring, a prompt chain, or a complex rules DSL. It needed to answer one question reliably:

> Did this advice work the last few times we gave it?

That question is simple enough to debug. It is also useful enough to change behavior.

If hardcoded-password guidance is usually accepted, the reviewer can keep recommending the established fix. If it is usually ignored, the reviewer can escalate from “please consider” to “this should be enforced by a secret scanner or pre-merge check.” If there is no clear signal, the reviewer can say so instead of inventing confidence.

This made the system easier to trust. Experienced engineers are allergic to tools that sound certain for no reason. “No clear team preference found” is sometimes the most honest output.

## Orchestrating the Review

The main workflow ties detection, memory recall, and recommendation together:

```python
with open(
    "sample_code.py",
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

The system does not ask Hindsight to “review code.” Detection and memory have different jobs. The detector identifies the present issue. Hindsight supplies the past. The recommendation engine decides how the past should affect the present response.

That boundary turned out to matter. When memory systems are allowed to do everything, they become hard to test. By keeping the detector deterministic and the memory layer focused on recall, I could test each piece separately.

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

That is a small change, but it is the difference between generic advice and contextual advice.

For debug prints, the behavior can go the other way. If the team has historically accepted debug-print cleanup, the reviewer does not need to escalate:

```text
Debug print statement detected

Past fixes were mostly accepted.
Recommend applying the same solution.
```

This is the part I cared about most: the reviewer can be stricter in places where gentle suggestions have failed and quieter where the existing advice already works.

That is a better default than treating every finding as if it appeared in a vacuum.

## Why Hindsight Fit This Problem

I used Hindsight because this problem is not just search and not just storage. It is memory attached to an agent workflow.

The distinction matters. A database can store every review result. A search index can retrieve matching strings. But for a review agent, I needed a memory bank that could retain outcomes and recall relevant prior experiences at the moment of decision.

The [Vectorize explanation of agent memory](https://vectorize.io/what-is-agent-memory) maps closely to this use case: the system improves its future behavior by carrying forward useful context from previous interactions. In CodeRecall, that context is not personality or chat history. It is engineering feedback history.

The most useful memories were not long. They were small, factual records:

```text
Issue: Debug Print Statement
Suggestion: Remove debug print statements before production deployment.
Status: Accepted
```

Small memories are easier to inspect. They are easier to prune. They also make recommendation behavior easier to explain when someone asks, “Why did the reviewer say this?”

That last question is not theoretical. If a tool comments on my pull request, I want to know whether it is enforcing a rule, repeating generic advice, or responding to actual project history. Memory-aware systems need explainable memory, not just memory.

## The Painful Parts

The first painful part was deciding what not to remember.

It is easy to keep adding context: file path, author, reviewer, repository, timestamp, severity, diff hunk, final merged code, linked ticket, CI state. Some of that is useful. Too much of it makes the first version impossible to reason about.

I settled on issue, suggestion, and outcome as the minimum useful memory. Everything else can be layered on later.

The second painful part was avoiding fake intelligence. It would have been easy to generate a more elaborate paragraph for every finding. That would have made the system feel more capable while making it less predictable.

I preferred a blunt recommendation:

```text
Past fixes were often ignored.
Recommend stronger enforcement.
```

That sentence is not flashy, but an engineer can act on it. Add a blocking check. Tighten a rule. Improve the migration path. Stop wasting review comments on advice nobody follows.

The third painful part was accepting that detection quality and memory quality are separate problems. Better static analysis matters, but better detection does not solve repeated ignored feedback. If the workflow forgets outcomes, it will continue to repeat itself with more accurate wording.

That was the core lesson of the project.

## What I Learned

### Memory Should Store Outcomes, Not Noise

The most valuable review memories were not full conversations. They were compact records of what was found, what was suggested, and what happened next.

That made recall useful. It also made the recommendation layer testable.

### Start With a Boring Policy

Counting accepted versus ignored outcomes sounds primitive. It is also transparent. Before adding more advanced ranking or model-driven reasoning, I wanted one behavior I could explain in a sentence.

If ignored outcomes dominate, escalate. If accepted outcomes dominate, repeat the known fix. If neither dominates, say there is no clear signal.

That policy is not the end state, but it is a solid baseline.

### Keep Detection Separate From Memory

The detector should identify present facts. The memory layer should retrieve past context. The recommendation engine should decide what to do with both.

Blurring those boundaries makes the system harder to test and harder to trust.

### Generic Advice Has a Half-Life

“Use environment variables” is good advice the first time. After it has been ignored several times, the problem has changed. The issue is no longer only a hardcoded password. The issue is that the current intervention does not work.

Hindsight made that visible.

### Explain the Memory Behind the Recommendation

A memory-aware reviewer should be able to say why its advice changed. “Past fixes were often ignored” is not just flavor text. It is the reason for the recommendation.

That explanation is what keeps the system from feeling arbitrary.

## The Part I Still Like

The part I still like about this project is that the main idea is small enough to survive contact with real code.

Code review automation does not need to pretend every finding is new. It can remember what happened before. It can notice when advice worked. It can notice when advice failed. It can stop repeating itself.

Hindsight gave me a practical way to add that memory without turning the reviewer into an opaque blob. The detector finds the issue. Hindsight recalls the history. The recommendation engine makes a plain decision.

That is the kind of agent behavior I want more of: less theatrical, more accountable, and grounded in the actual history of the work.

## Resources

- Hindsight GitHub: https://github.com/vectorize-io/hindsight
- Hindsight Documentation: https://hindsight.vectorize.io/
- Vectorize Agent Memory: https://vectorize.io/what-is-agent-memory