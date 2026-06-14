# CodeRecall AI

## Memory-Aware Code Review Agent Powered by Hindsight

### Problem

Traditional code review tools repeatedly provide the same feedback every time they encounter an issue.

For example:

* Hardcoded passwords
* Debug print statements
* Security misconfigurations

Even if developers repeatedly ignore or accept certain recommendations, the review system has no memory of previous interactions.

As a result, reviews remain static and fail to adapt to team behavior over time.

---

## Solution

CodeRecall AI is a memory-aware code review agent built using Hindsight.

The agent:

1. Reviews source code and identifies issues.
2. Stores review history in Hindsight memory.
3. Recalls relevant past review outcomes.
4. Adapts future recommendations based on historical behavior.

Instead of providing identical feedback every time, the agent learns from previous reviews and produces context-aware recommendations.

---

## Example

### First Review

Issue:

Hardcoded password detected

Recommendation:

Use environment variables instead of hardcoded credentials.

Outcome:

Ignored

---

### Future Review

Issue:

Hardcoded password detected

Recommendation:

Past fixes were often ignored.

Recommend stronger enforcement.

The recommendation changes because the agent remembers what happened previously.

---

## Architecture

Developer Code
↓
Review Engine
↓
Issue Detection
↓
Hindsight Memory Bank
↓
Memory Recall
↓
Recommendation Engine
↓
Adaptive Feedback

---

## Features

* Memory-aware code reviews
* Long-term memory using Hindsight
* Adaptive recommendations
* Historical review analysis
* Context-aware feedback generation

---

## Tech Stack

* Python
* Hindsight Memory Platform
* GitHub

---

## Project Structure

config.py

* Configuration and API keys

reviewer.py

* Code issue detection

memory_reviewer.py

* Memory-powered review workflow

recommendation_engine.py

* Adaptive recommendation generation

hindsight_memory.py

* Memory storage utilities

test_recall.py

* Memory retrieval testing

sample_code.py

* Example code for demonstration

---

## Installation

Clone the repository:

git clone <repository-url>

Install dependencies:

pip install -r requirements.txt

Create a .env file and add:

HINDSIGHT_API_KEY=your_api_key

Run:

python memory_reviewer.py

---

## Why Hindsight?

Hindsight enables persistent memory for AI systems.

By integrating Hindsight, CodeRecall AI can remember previous review outcomes and adapt future recommendations accordingly.

This transforms static code reviews into evolving, memory-aware engineering assistance.

---

## Hackathon Submission

Built for the Hindsight Memory Challenge.

Demonstrates how long-term memory can improve developer tooling by making code review feedback adaptive rather than repetitive.
