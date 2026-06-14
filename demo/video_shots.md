# CodeRecall AI - Video Recording Shots

## Shot 1 - Repository Overview (10 seconds)

Screen:

GitHub Repository

Show:

* README
* architecture.md
* demo folder
* reviewer.py
* memory_reviewer.py
* recommendation_engine.py

Narration:

"This is CodeRecall AI, a memory-aware code review agent powered by Hindsight."

---

## Shot 2 - Problem Statement (10 seconds)

Open:

sample_code.py

Show:

```python
password = "admin123"

print("debug")
```

Narration:

"Traditional code review systems repeatedly provide the same recommendations and never learn from previous outcomes."

---

## Shot 3 - Hindsight Dashboard (15 seconds)

Open Hindsight dashboard.

Show:

* Memory Bank
* Stored memories
* Password-related memories
* Debug-related memories

Narration:

"CodeRecall AI stores review history in Hindsight and uses it as long-term memory."

---

## Shot 4 - Run Review Agent (25 seconds)

Terminal:

```bash
python memory_reviewer.py
```

Show:

CURRENT ISSUE

RELEVANT MEMORIES

FINAL RECOMMENDATION

Focus on:

```text
Hardcoded password detected

Past fixes were often ignored.

Recommend stronger enforcement.
```

Narration:

"The agent recalls historical review outcomes and adapts its recommendations."

---

## Shot 5 - Different Historical Outcome (20 seconds)

Continue showing terminal output.

Focus on:

```text
Debug print statement detected

Past fixes were mostly accepted.

Recommend applying the same solution.
```

Narration:

"The recommendation changes because the historical behavior for this issue is different."

---

## Shot 6 - Architecture (15 seconds)

Open:

architecture.md

Show architecture diagram.

Narration:

"Developer code is analyzed by the review engine. Relevant memories are recalled from Hindsight and used by the recommendation engine to generate adaptive feedback."

---

## Shot 7 - Closing (10 seconds)

Return to repository.

Narration:

"CodeRecall AI demonstrates how persistent memory can transform static code reviews into adaptive engineering assistance."

Display:

Thank You
Built with Hindsight
