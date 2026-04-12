"""Research orchestrator: chains plan, search (fan-out), analyze (fan-out), and synthesize as subtasks."""

import asyncio

from render_sdk import Workflows

from .plan import plan_research
from .search import search
from .analyze import analyze
from .synthesize import synthesize

app = Workflows()


@app.task
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
