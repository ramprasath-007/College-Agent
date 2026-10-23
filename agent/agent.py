"""CampusAI: an intelligent multi-agent campus helpdesk powered by Strands Agents and Decider.

Strands Decider 2B reads each student message and selects the right specialized agent tool
(#tool-selection). The Strands Agent then runs with only that tool, generating an accurate,
context-aware reply from the campus's synthetic data.

    from agent.agent import HackathonAgent
    out = HackathonAgent().chat("I paid my semester fees but the payment is still showing pending.")
    out["reply"], out["decisions"]
"""

from __future__ import annotations

import time
from typing import Any

from strands import Agent

from decider_kit import Decider
from decider_kit.llm import agent_model, default_model_id, strip_thinking

from .decision import CampusToolSelector
from .tools import TOOLS

NAME = "CampusAI — Intelligent Multi-Agent Campus Helpdesk"

SYSTEM_PROMPT = """You are CampusAI, an intelligent campus helpdesk assistant for college students.
You have access to a specialized tool that retrieves information from the campus knowledge base.

Your role:
- Answer the student's question accurately using the information returned by the tool.
- Be friendly, concise and clear. Use bullet points for lists.
- Always note that the data shown is synthetic demonstration data, not official records.
- If the information does not cover the student's specific case, tell them to contact the
  relevant department directly and provide the contact details from the data.
- Never invent information not present in the tool's response.

Respond in plain, student-friendly English."""

CLARIFICATION_RESPONSE = (
    "I'd be happy to help! Could you tell me which area your question is about?\n\n"
    "- **Academics** — courses, attendance, timetables, regulations\n"
    "- **Examinations** — schedules, results, hall tickets, internal marks\n"
    "- **Finance** — fee payment, receipts, refunds\n"
    "- **Placements** — drives, eligibility, internships\n"
    "- **Scholarships** — programs, applications, deadlines\n"
    "- **Campus Services** — facilities, transport, library, departments\n\n"
    "Just let me know which area and I'll get you the right information right away!"
)


class HackathonAgent:
    """One Strands Agent per session with Decider-based tool selection wired in."""

    def __init__(
        self,
        decider: Decider | None = None,
        model_id: str | None = None,
        eager: bool | None = None,
    ):
        import os

        self.decider = decider or Decider()
        self.model_id = model_id or default_model_id()
        self.eager = eager if eager is not None else os.environ.get("DEMO_EAGER") == "1"
        self.selector = CampusToolSelector(self.decider, TOOLS)
        # One Strands Agent per session_id, re-created with the right tool per turn
        self._session_history: dict[str, list[str]] = {}

    def _history_text(self, session_id: str) -> str:
        turns = self._session_history.get(session_id, [])
        if not turns:
            return ""
        return "\n".join(turns[-6:])  # last 3 exchanges

    def chat(
        self,
        message: str,
        session_id: str = "default",
        images: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Route the student's message through Strands Decider and answer with the right agent.

        Returns:
            reply        str  — the agent's response
            decisions    list — one dict per decider call with tool, confidence, probabilities
            model_id     str  — LLM used
            latency_ms   int  — wall-clock time for the whole chat() call
            agent        str  — agent name
            routed_to    str  — the tool selected (or "clarification" if unsure)
            confidence   float
        """
        t0 = time.perf_counter()
        history = self._history_text(session_id)

        # --- Decider: select the right tool ---
        narrowed_tools = self.selector.tools_for(message, history)
        sel = self.selector.last_selection

        # Record in history
        hist = self._session_history.setdefault(session_id, [])
        hist.append(f"student: {message}")

        # --- Low confidence: ask for clarification, skip the LLM ---
        if self.selector.is_unsure():
            reply = CLARIFICATION_RESPONSE
            hist.append(f"campusai: {reply}")
            latency_ms = round((time.perf_counter() - t0) * 1000)
            return {
                "reply": reply,
                "decisions": list(self.selector.log[-1:]),
                "model_id": self.model_id,
                "latency_ms": latency_ms,
                "agent": NAME,
                "routed_to": "clarification",
                "confidence": round(sel.confidence if sel else 0.0, 3),
                "eager": self.eager,
            }

        # --- High confidence: build agent with the narrowed tool and answer ---
        strands_agent = Agent(
            model=agent_model(self.model_id),
            system_prompt=SYSTEM_PROMPT,
            tools=narrowed_tools,
            callback_handler=None,
        )
        result = strands_agent(message)
        reply = strip_thinking(str(result))
        hist.append(f"campusai: {reply}")

        latency_ms = round((time.perf_counter() - t0) * 1000)
        return {
            "reply": reply,
            "decisions": list(self.selector.log[-1:]),
            "model_id": self.model_id,
            "latency_ms": latency_ms,
            "agent": NAME,
            "routed_to": sel.tool if sel else "unknown",
            "confidence": round(sel.confidence if sel else 0.0, 3),
            "eager": self.eager,
        }


if __name__ == "__main__":
    import json
    import sys

    agent = HackathonAgent()
    test_messages = sys.argv[1:] or [
        "What is the minimum attendance required to sit for exams?",
        "I paid my semester fees but the payment is still showing as pending.",
        "When is the TechCorp placement drive and what is the package?",
        "I need help with my college.",  # should trigger clarification
    ]
    for msg in test_messages:
        print(f"\n>>> {msg}")
        out = agent.chat(msg)
        print(f"[{out['routed_to']} | conf {out['confidence']} | {out['latency_ms']}ms]")
        print(out["reply"])
