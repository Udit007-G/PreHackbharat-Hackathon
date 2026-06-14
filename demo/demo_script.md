# CodeRecall AI - Hackathon Demo Script

## Demo Duration

2-3 minutes

---

# Introduction

Hi, I'm Udit, and this is CodeRecall AI, a memory-aware code review agent powered by Hindsight.

Traditional code review tools repeatedly provide the same feedback every time they encounter an issue.

They don't remember whether developers accepted previous recommendations or ignored them.

CodeRecall AI solves this by using Hindsight memory to adapt future recommendations based on historical review outcomes.

---

# Demo 1 - First Review

Open sample_code.py

Show:

```python
password = "admin123"
```

Run:

```bash
python memory_reviewer.py
```

Show output:

Hardcoded password detected.

Explain:

The agent identifies the issue and provides a recommendation.

At this point, the system has no historical context.

---

# Simulating Review History

Open Hindsight dashboard.

Show stored memories.

Point out:

* Previous password recommendations were ignored.
* Debug print recommendations were accepted.

Explain:

These memories are stored in Hindsight and become available for future reviews.

---

# Demo 2 - Memory-Aware Review

Run:

```bash
python memory_reviewer.py
```

Show:

Hardcoded password detected

Past fixes were often ignored.

Recommend stronger enforcement.

Explain:

Instead of repeating the same recommendation, the agent adapts its feedback using historical memory.

---

# Demo 3 - Different Behavior for Different History

Show:

Debug print statement detected

Past fixes were mostly accepted.

Recommend applying the same solution.

Explain:

The recommendation changes because the memory history for this issue is different.

---

# Architecture

Show architecture.md

Explain:

Developer Code
→ Review Engine
→ Hindsight Memory
→ Memory Recall
→ Recommendation Engine
→ Adaptive Feedback

---

# Conclusion

CodeRecall AI demonstrates how persistent memory can transform static code reviews into adaptive engineering assistance.

By leveraging Hindsight, the system remembers previous review outcomes and evolves its recommendations over time.

Thank you.
