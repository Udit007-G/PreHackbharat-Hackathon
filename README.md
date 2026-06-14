# CodeRecall AI

## Memory-Aware Code Review Agent Powered by Hindsight

CodeRecall AI is a small Python code review agent that remembers previous review outcomes and adapts its recommendations. Instead of repeating the same advice every time, it recalls whether similar findings were accepted or ignored before making a recommendation.

## Problem

Traditional code review tools repeatedly provide the same feedback for recurring issues:

* Hardcoded passwords
* Debug print statements
* Security-sensitive configuration mistakes

That feedback is static. It does not account for team behavior or previous review outcomes.

## Solution

CodeRecall AI:

1. Reviews Python source code for simple risk patterns.
2. Recalls related historical review outcomes from memory.
3. Adapts recommendations based on whether similar fixes were accepted or ignored.
4. Runs offline with local sample memory or connects to Hindsight for persistent memory.

## Example

First review:

```text
Issue: Hardcoded password detected
Recommendation: Use environment variables instead of hardcoded credentials.
Outcome: Ignored
```

Future review:

```text
Issue: Hardcoded password detected
Recommendation: Past fixes were often ignored. Recommend stronger enforcement.
```

## Architecture

```text
Developer Code
      |
      v
Review Engine
      |
      v
Memory Recall
      |
      v
Recommendation Engine
      |
      v
Adaptive Feedback
```

## Project Structure

```text
.
|-- config.py                 # Environment and Hindsight settings
|-- hindsight_memory.py       # Local and Hindsight memory clients
|-- memory_reviewer.py        # CLI review workflow
|-- recommendation_engine.py  # Adaptive recommendation logic
|-- reviewer.py               # Static code issue detection
|-- sample_code.py            # Demo input
|-- memory_seed.json          # Local sample memory for offline runs
|-- requirements.txt          # Python dependencies
`-- tests/                    # Regression tests
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the local demo:

```bash
python memory_reviewer.py
```

Connect to Hindsight:

1. Copy `.env.example` to `.env`.
2. Add your `HINDSIGHT_API_KEY`.
3. Run:

```bash
python memory_reviewer.py --use-hindsight
```

Run tests:

```bash
python -m unittest discover
```

## Why Hindsight?

Hindsight gives the reviewer persistent memory. CodeRecall AI uses that memory to make review feedback context-aware, so recommendations can evolve based on what happened in previous reviews.

## Hackathon Submission

Built for the Hindsight Memory Challenge to demonstrate how long-term memory can make developer tooling more adaptive.
