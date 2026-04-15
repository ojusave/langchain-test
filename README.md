# Research Agent

Ask a research question. The workflow classifies it, plans subtopics, runs parallel LangGraph agents with Exa search, then returns a synthesized report with sources. Powered by [Render Workflows](https://render.com/workflows).

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ojusave/langchain-test)

## Table of contents

- [Highlights](#highlights)
- [Overview](#overview)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Deploy](#deploy)
- [Configuration](#configuration)
- [API](#api)
- [Project structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## Highlights

- **Workflow-backed research**: planning, search agents, and synthesis run as Render Workflow tasks, not inside the FastAPI process.
- **Streaming client**: the UI shows an activity feed while the pipeline runs; status arrives over SSE from `POST /research`.
- **Optional threaded history**: add Postgres (`DATABASE_URL`) for multi-turn threads and follow-ups.
- **Optional observability**: LangSmith keys enable traces and in-UI feedback when you wire `LANGCHAIN_API_KEY` on both services.

## Overview

This repo is a Python FastAPI front end plus a Python workflow service that hosts LangGraph + Anthropic + Exa. Simple or off-topic questions get a fast path without spinning up research. The pattern matches the Render guidance: thin web, fat tasks.

## Usage

After deploy, open the web service URL. Type a question in the UI: research queries trigger the workflow; casual prompts get a direct answer. If `DATABASE_URL` is set, conversations persist as threads you can reopen.

Example API call (replace the host and use a real question):

```bash
curl -N -X POST "https://YOUR_SERVICE.onrender.com/research" \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the main tradeoffs between X and Y?","thread_id":""}'
```

The response is an SSE stream (`status`, `classified`, `plan`, agent events, `done`).

## How it works

![Architecture](static/images/architecture.png)

![Pipeline flow](static/images/pipeline.png)

Non-research queries (greetings, coding help, simple questions) get a direct reply without triggering search. The UI streams live progress as an activity feed.

## Prerequisites

- A [Render account](https://render.com/register?utm_source=github&utm_medium=referral&utm_campaign=ojus_demos&utm_content=readme_link)
- API keys: [Render](https://render.com/docs/api#1-create-an-api-key), [Anthropic](https://console.anthropic.com/), [Exa](https://exa.ai/)
- Optional: [LangSmith](https://smith.langchain.com/) for tracing and feedback

## Deploy

Installation is Render: clone is only needed if you fork the repo. Use the button below or import [`render.yaml`](render.yaml).

### 1. Web service (via Blueprint)

Click **Deploy to Render** above. Set `RENDER_API_KEY` during setup.

### 2. Workflow service (manual)

1. [Render Dashboard](https://dashboard.render.com) > **New** > **Workflow**
2. Connect the same repo
3. Build: `pip install -r requirements.txt`
4. Start: `python -m tasks`
5. Name: `research-agent-workflow` (must match `WORKFLOW_SLUG`)
6. Env vars: `ANTHROPIC_API_KEY`, `EXA_API_KEY`, `PYTHON_VERSION`: `3.12.3`

### 3. History (optional)

Create a Render PostgreSQL database and set its Internal URL as `DATABASE_URL` on the web service. Tables are auto-created on startup. Enables threaded research history with follow-up queries.

### 4. LangSmith (optional)

Set `LANGCHAIN_API_KEY` on both services. Enables auto-tracing of Claude and LangGraph calls, plus user feedback (thumbs up/down in the UI).

## Configuration

| Variable | Where | Default | Description |
|---|---|---|---|
| `RENDER_API_KEY` | Web service | (required) | Triggers workflow tasks |
| `WORKFLOW_SLUG` | Web service | `research-agent-workflow` | Must match workflow service name |
| `DATABASE_URL` | Web service | (optional) | PostgreSQL for research history |
| `LANGCHAIN_API_KEY` | Both | (optional) | LangSmith tracing + feedback |
| `ANTHROPIC_API_KEY` | Workflow | (required) | Claude API key |
| `EXA_API_KEY` | Workflow | (required) | Exa semantic search |
| `ANTHROPIC_MODEL` | Workflow | `claude-sonnet-4-20250514` | Claude model |
| `AGENT_TEMPERATURE` | Workflow | `0.3` | LLM temperature |

## API

**`POST /research`**: starts the pipeline, returns an SSE stream. Body: `{ "question": "...", "thread_id": "..." }`. Events: `status`, `classified`, `plan`, `agent_start`, `agent_done`, `done`, `error`.

**`POST /feedback`**: submits thumbs up/down to LangSmith. Body: `{ "run_id": "...", "score": 1 }`.

**`GET /history`**: recent threads. **`GET /history/:id`**: thread detail. **`DELETE /history/:id`**: delete thread.

**`GET /health`**: `{ "status": "ok" }`.

## Project structure

```
main.py                  FastAPI web service
pipeline/
  orchestrator.py        Dispatch tasks, poll, stream SSE
  history.py             PostgreSQL threaded history (optional)
  tracking.py            LangSmith pipeline run lifecycle (optional)
  feedback.py            POST /feedback: user ratings (optional)
tasks/
  __init__.py            Combines task apps for the workflow service
  __main__.py            Workflow entry point (python -m tasks)
  llm.py                 Shared ChatAnthropic model
  tools.py               Exa tools for LangGraph
  agent.py               LangGraph ReAct agent
  research_agent.py      Workflow task wrapping the agent
  classify.py            classify_query task
  plan.py                plan_research task
  synthesize.py          synthesize task
static/index.html        UI: threaded Q&A, activity feed
render.yaml              Render Blueprint
```

## Troubleshooting

**Workflow tasks not starting**: check that `WORKFLOW_SLUG` matches the workflow service name (default: `research-agent-workflow`).

**LangSmith traces not appearing**: set `LANGCHAIN_API_KEY` on the workflow service too (not just the web service). The workflow is where Claude and LangGraph calls happen.

**Exa returning empty**: check `EXA_API_KEY`. Exa occasionally returns 503s under load: Render Workflows auto-retries with backoff.
