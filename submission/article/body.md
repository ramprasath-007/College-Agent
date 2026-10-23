# CampusAI: Routing University Student Queries to Six Specialized Tools with Strands Decider 2B

University life means navigating six separate portals: one for grades, one for fees, one for exam schedules, one for placements, one for scholarships, and a general student services site. A student trying to check attendance, pay a fee, and find a placement drive deadline in one sitting opens three browser tabs and remembers three different login credentials. CampusAI replaces that with a single chat interface. The headline result: before the language model runs any tool, Strands Decider 2B selects the right specialized tool in one forward pass at 295 ms median latency -- 4.3x faster than asking the LLM to make the same routing decision, at zero additional cost.

## The project

CampusAI is for university students who need quick, factual answers about their own academic situation. It covers six domains from a single chat interface.

- Academics: enrolled courses, attendance percentage, CGPA, timetable, regulations
- Examinations: upcoming exam schedules, hall ticket status, internal marks, results
- Finance: fee payment status, receipts, due dates, refund policy
- Placements: drive schedules, eligibility criteria, package information, internships
- Scholarships: available programs, eligibility, application steps, deadlines
- Campus services: facilities, library hours, transport routes, department contacts

A short real interaction shows how it works. A student types: "Are there any scholarships I can apply for before the end of the month?" CampusAI routes the query to the scholarship tool (the Decider selected it with 0.87 confidence in one forward pass), and the agent returns a list of available programs, their eligibility conditions, and the application deadlines. No academic or placement data is loaded. The student gets a direct answer in one turn.

When a query is ambiguous -- for example, "I need help with my college" -- the Decider's confidence falls below 0.65 and CampusAI returns a structured clarification prompt asking which of the six domains the student needs. This means the LLM never runs a tool-selection call at all on unclear input; the Decider catches it first.

## How I built it

The architecture has four layers. At the top, a Strands Agents SDK `Agent` handles the generative turn using Amazon Nova Pro on Amazon Bedrock. Below that, six `@tool` functions each load their own synthetic JSON dataset (one per domain). Before the agent is constructed on each turn, Strands Decider 2B runs a single `choice` question over the student's message to select which tool to include. Below that, the synthetic data layer holds demonstration records for all six domains in `agent/data/*.json`.

I built it with Kiro, using spec-driven development: `.kiro/specs/` holds the requirements and design documents that drove the code. The Strands Agents SDK, the decider client, and the five reusable patterns in `decider_kit/patterns/` are from the AWS User Group Madurai Strands Decider hackathon kit.

## The decision handed to Strands Decider 2B

Tool selection is a natural fit for a decision model: it is a language classification task (what did this student mean?) rather than a numeric check (is this value over a threshold?). The LLM could do it -- it just costs a full generative turn to do so. The Decider does it in one forward pass.

The question is a `choice` over seven options, one per tool plus `none`. The option descriptions come directly from each tool's one-line docstring. Here is the relevant section of `agent/decision.py`:

```python
PATTERN_TAG = "#tool-selection"
THRESHOLD = 0.65  # below this confidence, keep all tools and let the LLM decide

# questions_for(TOOLS) reads each tool's one-line docstring as the option description:
# academic_agent        -> "answers questions about courses, attendance, timetables and academic regulations"
# examination_agent     -> "handles exam schedules, results, hall tickets and internal assessments"
# finance_agent         -> "resolves fee payment status, receipts, refunds and tuition fee queries"
# placement_agent       -> "provides placement drive schedules, eligibility criteria and internship information"
# scholarship_agent     -> "explains scholarship programs, eligibility, application steps and deadlines"
# general_support_agent -> "covers campus facilities, transport, library and general college services"
# none                  -> "no tool needed; the assistant can answer directly"
```

The wiring is in `CampusToolSelector`. Before each agent turn it calls `selector.select(message, history)`. If confidence is at or above 0.65, the Strands Agent is built with exactly one tool. If confidence is below 0.65, the agent receives all six tools and the LLM decides, or the caller returns a clarification prompt to the student.

```python
narrowed_tools = self.selector.tools_for(message, history)
if self.selector.is_unsure():
    return {"reply": CLARIFICATION_RESPONSE, "routed_to": "clarification", ...}
strands_agent = Agent(model=agent_model(self.model_id), system_prompt=SYSTEM_PROMPT, tools=narrowed_tools)
```

No retraining is needed when a new tool is added. The Decider reads the docstring. Sharper docstrings yield sharper routing.

## Measured

I ran `./kit bench --split test` against the held-out test split of `agent/eval_cases.jsonl`. The decider ran on the AWS User Group Madurai hosted API (https://da25tnxy06gjk.cloudfront.net), model StrandsAgents/strands-decider-2B-qwen3.5-v1-2610. The LLM baseline used Amazon Nova Pro on Amazon Bedrock.

| | Strands Decider 2B | Amazon Nova Pro (LLM) |
|---|---|---|
| Accuracy | 79.2% | 95.8% |
| Latency p50 per decision | 295 ms | 1,276 ms |
| Latency p95 | 468 ms | 1,426 ms |
| Cost per 1,000 decisions | $0.0000 | $0.1785 |
| Answered alone (>= 0.70 conf) | 67% | 100% |
| Accuracy when confident | 93.8% | 95.8% |

At the median the Decider was 4.3x faster than the LLM. The raw accuracy (79.2% vs 95.8%) tells an honest story: the Decider trades 16 percentage points of accuracy for 4.3x speed and $0 routing cost. The more useful number is accuracy when confident: 93.8%, nearly matching the LLM, on the 67% of queries where the Decider is sure enough to answer alone. On the remaining 33% it falls back to all-tools mode, where the LLM picks the tool as it normally would. Those queries cost no more than a standard agent call.

The threshold of 0.65 was tuned on the tune split. Raising it to 0.70 would improve confident-mode accuracy further at the cost of sending more queries to fallback.

## The reusable decision pattern

The pattern lives in `agent/decision.py` and is tagged `#tool-selection`. To use it in your own agent:

1. Copy `CampusToolSelector` from `agent/decision.py`.
2. Replace `TOOLS` with your own list of `@tool` functions. Each tool needs a clear one-line docstring describing what it handles -- that docstring becomes the option description the Decider reads.
3. Set `THRESHOLD` (0.65 works well for six well-separated domains; lower it if your categories overlap more).
4. Call `selector.tools_for(message)` before constructing your Strands Agent. Done.

No model fine-tuning, no retraining, no prompt engineering for the routing step. The Decider reads the docstrings and classifies intent in one forward pass.

## What I learned

The biggest surprise was how well the Decider handles domain boundaries from docstrings alone. "I need a fee receipt for my scholarship application" correctly routes to `finance_agent` (not `scholarship_agent`) because the docstring for finance mentions "receipts" explicitly. The description quality matters more than I expected.

The main weakness is multi-domain queries: "What courses do I need for the placement drive?" could go to either academic or placement. The current design sends those to all-tools fallback, which is correct behavior but loses the speed and cost benefit. A multi-label version of the question -- asking for a ranked list rather than one winner -- would handle these better.

Next steps for CampusAI: real student portal integration via APIs (replacing the synthetic data), AgentCore Memory for session context so returning students are greeted by name, and a Gateway target for a campus notification service so the agent can send reminders about upcoming deadlines.

## Footer

Repository: TODO (run `./kit publish fsd07-campusai-agent` to create the public repo and paste the URL here)
Strands Decider: https://github.com/strands-agents/strands-decider
Tags: #strands-decider-2b #tool-selection

Built with the AWS User Group Madurai Strands Decider hackathon kit.
