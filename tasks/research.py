"""
Research orchestrator: chains plan, search (fan-out), analyze (fan-out),
and synthesize as subtasks.

This is the top-level task the web service triggers. It doesn't do any work
itself: it chains four subtasks and coordinates them. Every subtask call
(plan_research, search, analyze, synthesize) triggers a separate Workflow
task run on its own compute instance.

Workflow config rationale:
  - plan: starter (0.5 CPU, 512 MB) — the orchestrator only awaits subtasks;
    it does no local compute.
  - timeout: 300s — the full pipeline can take 1-2 minutes (plan + N searches
    + N analyses + synthesis). 300s gives headroom for retries and cold starts
    of subtask instances.
  - retry: 1 retry, 5s wait — if the orchestrator itself fails (not a subtask),
    one retry is enough. Subtask failures are handled by their own retry config.
"""

import asyncio

from render_sdk import Workflows, Retry

from .plan import plan_research
from .search import search
from .analyze import analyze
from .synthesize import synthesize

app = Workflows()


@app.task(
    plan="starter",
    timeout_seconds=300,
    retry=Retry(max_retries=1, wait_duration_ms=5000, backoff_scaling=1),
)
async def research(question: str) -> dict:
    """Full research pipeline via task chaining. Each step runs on its own compute."""
    plan = await plan_research(question)
    queries = plan.get("queries", [question])

    search_results = await asyncio.gather(
        *[search(q) for q in queries]
    )

    analyses = await asyncio.gather(
        *[analyze(sd["query"], sd["results"]) for sd in search_results]
    )

    return await synthesize(question, list(analyses))
