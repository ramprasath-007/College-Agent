"""REUSABLE DECISION PATTERN: campus query routing  (#tool-selection)

What it does
    Before the campus helpdesk agent runs any tool, Strands Decider 2B reads the student's
    message and selects which of the six specialized agents (tools) should handle it:
    academic, examination, finance, placement, scholarship or general support.
    When the decider is confident (>= 0.65) the agent is built with only that one tool,
    which means fewer tokens, a faster LLM turn and no cross-domain hallucination.
    When confidence is below 0.65 the agent receives all tools and the LLM decides,
    or the caller returns a clarifying question to the student.

Typed questions and options
    `tool` (choice): one option per specialized agent tool, plus `none`.
    - academic_agent: answers questions about courses, attendance, timetables and academic regulations
    - examination_agent: handles exam schedules, results, hall tickets and internal assessments
    - finance_agent: resolves fee payment status, receipts, refunds and tuition queries
    - placement_agent: provides placement drive schedules, eligibility criteria and internship information
    - scholarship_agent: explains scholarship programs, eligibility, application steps and deadlines
    - general_support_agent: covers campus facilities, transport, library and general college services
    - none: no specialized tool needed; the assistant can answer directly

    The option descriptions come from each tool's one-line docstring, so no retraining is needed
    when a tool is added or renamed.

Wiring
    `CampusToolSelector` wraps `decider_kit.patterns.tool_selection.ToolSelector`.
    It is called in HackathonAgent before the Strands Agent is constructed:

        selector = CampusToolSelector(decider, tools=TOOLS)
        narrowed = selector.tools_for(student_message)
        agent = Agent(model=..., tools=narrowed, ...)

    If confidence < THRESHOLD the agent gets all tools; the caller may also intercept
    selector.last_selection.confidence < THRESHOLD to return a clarification prompt.

How to reuse it
    Copy this file. Replace TOOLS with your own list of @tool functions, each with a clear
    one-line docstring describing what it handles. Adjust THRESHOLD if your domain has
    more or fewer clear-cut categories. The Decider reads the docstrings as option
    descriptions, so sharper docstrings yield sharper routing.
"""

from __future__ import annotations

from typing import Any

from decider_kit import Decider
from decider_kit.patterns.tool_selection import ToolSelector, Selection, questions_for

PATTERN_TAG = "#tool-selection"
THRESHOLD = 0.65  # below this confidence all tools are kept and the LLM decides

# QUESTIONS is used by the benchmark (./kit bench) to evaluate the decider's routing accuracy.
# It is populated at import time from the tools list — see bottom of this file.
QUESTIONS: dict[str, Any] = {}


class CampusToolSelector:
    """Wraps ToolSelector for the campus helpdesk: selects one of six specialized agent tools."""

    def __init__(self, decider: Decider, tools: list[Any]):
        self._selector = ToolSelector(decider, tools, threshold=THRESHOLD)
        self.last_selection: Selection | None = None
        # expose QUESTIONS for the benchmark
        global QUESTIONS
        QUESTIONS.update(questions_for(tools))

    def tools_for(self, request: str, history: str = "") -> list[Any]:
        """Return the narrowed tool list for this request (one tool if confident, all if not)."""
        self.last_selection = self._selector.select(request, history)
        if self.last_selection.narrowed:
            sel_name = self.last_selection.tool
            if sel_name == "none":
                return []
            tool = self._selector.by_name.get(sel_name)
            return [tool] if tool else list(self._selector.tools)
        return list(self._selector.tools)

    @property
    def log(self) -> list[dict[str, Any]]:
        return self._selector.log

    def is_unsure(self) -> bool:
        """True when the last selection confidence was below THRESHOLD."""
        return self.last_selection is not None and not self.last_selection.narrowed

# Initialize QUESTIONS at import time by reading tool docstrings
# This is needed for the benchmark (./kit bench) to know what questions to evaluate
def _init_questions():
    """Populate QUESTIONS from the tools at import time."""
    global QUESTIONS
    if not QUESTIONS:
        # Import tools here to avoid circular imports
        from agent.tools import TOOLS
        QUESTIONS.update(questions_for(TOOLS))


_init_questions()
