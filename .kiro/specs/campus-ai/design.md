# CampusAI Design

## Architecture

```
Student Message
    │
    ▼
FastAPI Backend (POST /chat)
    │
    ▼
HackathonAgent.chat()
    │
    ▼
ToolSelector (decider_kit.patterns.tool_selection)
    │  state: "User request: <message>"
    │  question: choice over 6 agent tools + "none"
    │
    ▼
Strands Decider 2B (ugmdu hosted API)
    │  returns: tool name + confidence
    │
    ├─ confidence >= 0.65 → narrow to selected tool → Strands Agent (ugmdu LLM)
    │                                                      │
    │                                                      ▼
    │                                              Tool function (reads agent/data/*.json)
    │                                                      │
    │                                                      ▼
    │                                              LLM formats final reply
    │
    └─ confidence < 0.65 → return clarification prompt (no agent call)
    │
    ▼
{reply, decisions, model_id, latency_ms}
    │
    ▼
React + Tailwind Frontend
```

## Decision Pattern: #tool-selection

State format sent to the decider:
```
User request: <student message>
```

Tool options (one per agent, plus "none"):
- academic_agent: answers questions about courses, attendance, timetables and academic regulations
- examination_agent: handles exam schedules, results, hall tickets and internal assessments
- finance_agent: resolves fee payment status, receipts, refunds and tuition queries
- placement_agent: provides placement drive schedules, eligibility criteria and internship information
- scholarship_agent: explains scholarship programs, eligibility, application steps and deadlines
- general_support_agent: covers campus facilities, transport, library and general college services
- none: no tool needed; answer directly

Threshold: 0.65 (from ToolSelector default; set explicitly in decision.py)

## Data Layer

Each tool reads a JSON file from agent/data/:
- academic.json: students, courses, attendance records, timetables
- examinations.json: schedules, results, hall tickets
- finance.json: fee structure, payment transactions
- placements.json: companies, drives, eligibility, results
- scholarships.json: programs, applications, deadlines
- campus.json: facilities, departments, transport, library

## Agent Layer

One Strands Agent per session. ToolSelector narrows to one tool before the agent is built,
so the LLM sees only the relevant tool and does not cross-pollinate domains.

## Frontend Components

- Sidebar: nav links (Chat, Analytics, About)
- ChatPanel: message input, message list, agent badge per reply
- DecisionPanel: shows tool selected, confidence bar, probabilities
- AnalyticsPanel: per-agent query counts, average confidence
- AuthPanel: demo login (student / admin roles, hardcoded for demo)
