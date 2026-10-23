# CampusAI Requirements

## Overview

CampusAI is an intelligent multi-agent campus helpdesk that routes student queries to six
specialized agents using Strands Decider 2B (#tool-selection). Students get accurate,
context-aware answers about academics, exams, fees, placements, scholarships and campus
services through a single chat interface.

## Functional Requirements

### FR-1: Decider-based routing
- The system MUST use Strands Decider 2B to select which specialized agent handles each query.
- Routing MUST be based on the decider's confidence scores, not keyword matching.
- If confidence < 0.65, the system MUST ask the student to clarify their topic.

### FR-2: Six specialized agents
Each agent handles its domain using its own tool and synthetic data:
1. Academic Agent: courses, attendance, timetables, regulations
2. Examination Agent: schedules, results, hall tickets, internal exams
3. Finance Agent: fee structures, payment status, receipts, refunds
4. Placement Agent: drives, eligibility, interviews, internships
5. Scholarship Agent: eligibility, applications, deadlines, status
6. General Support Agent: facilities, transport, library, departments

### FR-3: Synthetic data
- All six domains MUST have structured JSON datasets in agent/data/.
- Data MUST be clearly marked as synthetic/demonstration data.
- Architecture MUST allow real data integration without structural changes.

### FR-4: Low-confidence handling
- Below 0.65 confidence: ask a clarifying question listing all six topics.
- Never randomly select an agent when unsure.

### FR-5: Chat interface
- Students MUST be able to send messages and receive replies.
- Each reply MUST show which agent responded and the routing confidence.
- Chat history MUST persist within a session.

### FR-6: Decision visualization
- The interface MUST display the Decider's routing decision in real time.
- Confidence scores and selected agent MUST be visible.

### FR-7: Backend API
- FastAPI backend exposing POST /chat and GET /health.
- CORS enabled for local frontend development.

### FR-8: Frontend
- React + Tailwind CSS, professional university SaaS design.
- Sidebar navigation, chat panel, decision panel, analytics view.

## Non-Functional Requirements
- NFR-1: Every query passes through the real Decider routing workflow.
- NFR-2: No hardcoded agent selection that bypasses the Decider.
- NFR-3: Deployed agent uses Amazon Bedrock (AgentCore Runtime).
