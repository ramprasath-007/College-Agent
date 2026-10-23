# CampusAI Demo Video Narration Script

Generated from agent/demo_script.yaml. Record using `./kit demo-bg` then `./kit video`.

## Turn 1: Academic query

Student: "What courses am I enrolled in and what is my current attendance?"
Decider routes to: academic_agent
Narration: The student asks about their enrolled courses and attendance. Strands Decider 2B reads the query and routes it to the academic tool with high confidence. The agent returns course details and attendance data from the academic domain without calling any other tool.

## Turn 2: Finance query

Student: "How much of my tuition fee is still due this semester?"
Decider routes to: finance_agent
Narration: A finance query. The Decider routes to the finance tool, which returns the fee structure, payment status and the upcoming due date. No academic or placement data is loaded.

## Turn 3: Placement query

Student: "Which companies are visiting campus for placements next month?"
Decider routes to: placement_agent
Narration: The student asks about upcoming placement drives. The Decider selects the placement tool. The agent lists the scheduled drives, the companies visiting, and the eligibility criteria.

## Turn 4: Scholarship query

Student: "Are there any scholarships I can apply for before the end of the month?"
Decider routes to: scholarship_agent
Narration: A scholarship deadline query. The Decider routes to the scholarship tool, which returns available programs, their eligibility conditions, and the application deadlines. The decision took one forward pass through Strands Decider 2B -- no generative model call was needed to pick the tool.

## How to record

1. Open a terminal in the workspace root
2. Run: `.\kit.cmd demo-bg` to start the demo UI at http://localhost:8501
3. Run: `.\kit.cmd video --target agentcore` (if deployed) or `.\kit.cmd video` (local)
4. The video will be saved to submission/video/demo.mp4
5. Upload to YouTube or Vimeo as Public and paste the URL in submission/SUBMISSION.md
