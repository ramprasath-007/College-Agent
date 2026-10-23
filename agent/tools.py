"""CampusAI specialized agent tools — six domains, each reading its own synthetic JSON dataset.

Each tool has a clear one-line docstring: the Decider's tool-selection pattern reads it as the
option description when deciding which tool handles the student's request.

Data lives in agent/data/*.json (synthetic demonstration data; clearly marked in each file).
"""

from __future__ import annotations

import json
from pathlib import Path

from strands import tool

_DATA = Path(__file__).parent / "data"


def _load(name: str) -> dict:
    return json.loads((_DATA / f"{name}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. Academic Agent
# ---------------------------------------------------------------------------

@tool
def academic_agent(query: str) -> str:
    """Answers questions about courses, attendance, timetables and academic regulations."""
    data = _load("academic")
    summary = {
        "courses": [
            f"{c['code']} {c['name']} ({c['credits']} cr) — {c['faculty']} — {c['schedule']}"
            for c in data["courses"]
        ],
        "attendance_policy": data["attendance_policy"],
        "timetable_CS_SEM5": data["timetable"]["CS_SEM5"],
        "regulations": data["regulations"],
        "sample_students": [
            f"{s['name']} ({s['department']}, Yr{s['year']}): CGPA {s['cgpa']}, Attendance {s['attendance_pct']}%"
            for s in data["students"]
        ],
        "note": data["_note"],
    }
    return (
        f"CAMPUS ACADEMIC DATA (synthetic demonstration data):\n\n"
        f"Student query: {query}\n\n"
        f"Available information:\n{json.dumps(summary, indent=2)}"
    )


# ---------------------------------------------------------------------------
# 2. Examination Agent
# ---------------------------------------------------------------------------

@tool
def examination_agent(query: str) -> str:
    """Handles exam schedules, results, hall tickets and internal assessments."""
    data = _load("examinations")
    summary = {
        "upcoming_exams": data["upcoming_exams"],
        "hall_ticket_status": data["hall_tickets"],
        "results_last_semester": data["results"],
        "internal_assessments": data["internal_assessments"],
        "schedule_info": data["exam_schedule_info"],
        "note": data["_note"],
    }
    return (
        f"CAMPUS EXAMINATION DATA (synthetic demonstration data):\n\n"
        f"Student query: {query}\n\n"
        f"Available information:\n{json.dumps(summary, indent=2)}"
    )


# ---------------------------------------------------------------------------
# 3. Finance Agent
# ---------------------------------------------------------------------------

@tool
def finance_agent(query: str) -> str:
    """Resolves fee payment status, receipts, refunds and tuition fee queries."""
    data = _load("finance")
    summary = {
        "fee_structure": data["fee_structure"],
        "recent_transactions": data["payment_transactions"],
        "refund_policy": data["refund_policy"],
        "due_dates": data["due_dates"],
        "payment_modes": data["payment_modes"],
        "note": data["_note"],
    }
    return (
        f"CAMPUS FINANCE DATA (synthetic demonstration data):\n\n"
        f"Student query: {query}\n\n"
        f"Available information:\n{json.dumps(summary, indent=2)}"
    )


# ---------------------------------------------------------------------------
# 4. Placement Agent
# ---------------------------------------------------------------------------

@tool
def placement_agent(query: str) -> str:
    """Provides placement drive schedules, eligibility criteria and internship information."""
    data = _load("placements")
    summary = {
        "upcoming_drives": [d for d in data["placement_drives"] if d["status"] == "upcoming"],
        "completed_drives": [d for d in data["placement_drives"] if d["status"] == "completed"],
        "internships": data["internships"],
        "placement_stats_2025_26": data["placement_stats"],
        "eligibility_rules": data["eligibility_rules"],
        "note": data["_note"],
    }
    return (
        f"CAMPUS PLACEMENT DATA (synthetic demonstration data):\n\n"
        f"Student query: {query}\n\n"
        f"Available information:\n{json.dumps(summary, indent=2)}"
    )


# ---------------------------------------------------------------------------
# 5. Scholarship Agent
# ---------------------------------------------------------------------------

@tool
def scholarship_agent(query: str) -> str:
    """Explains scholarship programs, eligibility, application steps and deadlines."""
    data = _load("scholarships")
    summary = {
        "available_scholarships": data["scholarships"],
        "applications": data["applications"],
        "general_instructions": data["general_instructions"],
        "note": data["_note"],
    }
    return (
        f"CAMPUS SCHOLARSHIP DATA (synthetic demonstration data):\n\n"
        f"Student query: {query}\n\n"
        f"Available information:\n{json.dumps(summary, indent=2)}"
    )


# ---------------------------------------------------------------------------
# 6. General Support Agent
# ---------------------------------------------------------------------------

@tool
def general_support_agent(query: str) -> str:
    """Covers campus facilities, transport, library and general college services."""
    data = _load("campus")
    summary = {
        "departments": data["departments"],
        "library": data["library"],
        "transport": data["transport"],
        "facilities": data["facilities"],
        "important_contacts": data["important_contacts"],
        "academic_calendar_highlights": data["academic_calendar_highlights"],
        "note": data["_note"],
    }
    return (
        f"CAMPUS GENERAL INFORMATION (synthetic demonstration data):\n\n"
        f"Student query: {query}\n\n"
        f"Available information:\n{json.dumps(summary, indent=2)}"
    )


# ---------------------------------------------------------------------------
# Exported list: order matters — it becomes the Decider's option order
# ---------------------------------------------------------------------------

TOOLS = [
    academic_agent,
    examination_agent,
    finance_agent,
    placement_agent,
    scholarship_agent,
    general_support_agent,
]
