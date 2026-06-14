# CodeRecall AI Architecture

## Overview

CodeRecall AI is a memory-aware code review agent that uses Hindsight to remember past review outcomes and adapt future recommendations.

## System Flow

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

## Components

### reviewer.py

Responsible for identifying issues in source code.

Examples:

* Hardcoded passwords
* Debug print statements

### Hindsight Memory Bank

Stores historical review experiences.

Examples:

* Recommendations accepted
* Recommendations ignored
* Previous review outcomes

### memory_reviewer.py

Connects issue detection with memory retrieval.

Queries Hindsight using the current issue as context.

### recommendation_engine.py

Analyzes recalled memories and adapts recommendations based on historical behavior.

Example:

If password-related recommendations were repeatedly ignored, the engine recommends stronger enforcement rather than repeating the same advice.

## Memory-Driven Learning

Traditional code review tools:

Issue → Recommendation

CodeRecall AI:

Issue → Memory Recall → Historical Analysis → Adaptive Recommendation

This enables recommendations to evolve over time instead of remaining static.
