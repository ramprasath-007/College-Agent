# CampusAI -- Hackathon Submission Checklist

Agent Experience Hackathon: Strands Decider -- submission deadline 23 October 2026, 11:59 p.m. PT

## Completed automatically

- [x] Article body written: submission/article/body.md
- [x] Article fields (title, description, tags): submission/article/fields.md
- [x] Video narration script: submission/video/narration.md
- [x] Benchmark results: submission/bench/results.json and results.md
- [x] LICENSE file: Apache-2.0 (exists at root)
- [x] eval_cases.jsonl: 25 labelled cases across 6 domains

## Manual steps remaining

### 1. Deploy to AWS (required for submission)

Prerequisites:
- Set `DEPLOY_DECIDER_URL` in `.env` (the hosted API URL is already set as `DECIDER_URL`; copy it to `DEPLOY_DECIDER_URL`)
- Run `./kit aws-login` in the terminal to configure AWS credentials
- Ensure AgentCore CLI is installed: `./kit agentcore-cli`

Then run:
```
.\kit.cmd deploy
.\kit.cmd invoke "What is my current CGPA?"
```

Paste the deployed agent ARN here: ___

### 2. Record the demo video

```
.\kit.cmd demo-bg
.\kit.cmd video --target agentcore
```

Upload `submission/video/demo.mp4` to YouTube or Vimeo as **Public**.
Paste video URL here: ___

### 3. Publish the article on AWS Builder Center

1. Go to https://builder.aws.com and choose Create > Article
2. Paste title from `submission/article/fields.md`:
   CampusAI: Routing University Student Queries to Six Specialized Tools with Strands Decider 2B
3. Paste description from `submission/article/fields.md`
4. Add tags: `strands-decider-2b`, `tool-selection`, `amazon-bedrock`, `strands-agents`
5. Upload cover image (run `./kit article` to generate it, or create a 1200x675 PNG)
6. Paste `submission/article/body.md` section by section
7. Publish and paste URL here: ___

### 4. Publish the code repository

```
.\kit.cmd gh-login
.\kit.cmd publish fsd07-campusai-agent
```

Paste repo URL here: ___
Update the Footer section in `submission/article/body.md` with the repo URL.

## Links to fill in before submitting

- Article URL: ___
- Video URL: ___
- Repository URL: ___
- Deployed agent ARN: ___

## Required tags

- [x] #strands-decider-2b
- [x] #tool-selection

## Built with the AWS User Group Madurai Strands Decider hackathon kit.
