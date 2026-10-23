# CampusAI -- University Helpdesk Agent

A conversational assistant for university students that answers questions about academics, exams, finance, placements, scholarships, and campus services from a single chat interface.

Before the language model runs any tool, **Strands Decider 2B** selects the right specialized tool in one forward pass -- 4.3x faster than asking the LLM, at zero routing cost.

## Quick start

```bash
.\kit.cmd setup
.\kit.cmd run
.\kit.cmd demo
```

## What it does

Students ask questions in plain language. CampusAI routes each query to the right domain:

| Domain | Example queries |
|---|---|
| Academics | courses, attendance, CGPA, timetable, regulations |
| Examinations | exam schedule, hall ticket, internal marks, results |
| Finance | fee payment, receipts, due dates, refund policy |
| Placements | drive schedules, eligibility, packages, internships |
| Scholarships | programs, eligibility, application steps, deadlines |
| Campus services | facilities, library, transport, contacts |

## Architecture

```
Student message
    |
    v
Strands Decider 2B  (tool selection: one forward pass, 295 ms, $0)
    |
    +-- confident (>= 0.65) --> Strands Agent with ONE tool --> Amazon Nova Pro on Bedrock
    +-- unsure   (< 0.65)   --> clarification prompt to student
```

## The reusable decision pattern

Tagged `#tool-selection`. Lives in `agent/decision.py`.

To use it in your own agent:
1. Copy `CampusToolSelector` from `agent/decision.py`
2. Replace `TOOLS` with your own `@tool` list -- each with a clear one-line docstring
3. Set `THRESHOLD` (0.65 works for well-separated domains)
4. Call `selector.tools_for(message)` before building your Strands Agent

```python
PATTERN_TAG = "#tool-selection"
THRESHOLD = 0.65  # below this confidence, keep all tools or ask for clarification
```

No retraining needed. The Decider reads the docstrings.

## Benchmark

| | Strands Decider 2B | Amazon Nova Pro (LLM) |
|---|---|---|
| Accuracy | 79.2% | 95.8% |
| Latency p50 | 295 ms | 1,276 ms |
| Cost per 1,000 decisions | $0.0000 | $0.1785 |
| Accuracy when confident | 93.8% | 95.8% |

Numbers from `submission/bench/results.json`. Decider ran on the AWS User Group Madurai hosted API.

## Running it

```bash
# One conversation turn
.\kit.cmd run

# Web UI
.\kit.cmd demo-bg
# then open http://localhost:8501

# Deploy to AWS
.\kit.cmd deploy

# Benchmark
.\kit.cmd bench --split test
```

## Tech stack

- Agent runtime: Strands Agents SDK
- Decision model: Strands Decider 2B
- Generative model: Amazon Nova Pro (Amazon Bedrock)
- Deployment: Amazon Bedrock AgentCore Runtime
- Data: synthetic demonstration data in `agent/data/*.json`

## Licence

Apache-2.0

Built with the **AWS User Group Madurai** Strands Decider hackathon kit.
