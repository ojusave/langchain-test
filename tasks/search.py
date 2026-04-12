"""
Search task: runs a single Exa web search and returns title, URL, and text.

Workflow config rationale:
  - plan: starter (0.5 CPU, 512 MB) — I/O-bound; the task is waiting on the
    Exa API, not doing local compute.
  - timeout: 30s — external API call should complete in <5s; 30s covers slow
    responses without blocking the pipeline indefinitely.
  - retry: 3 retries, 1s base wait, 2x backoff — network failures against
    third-party APIs are transient and common. 3 retries with exponential
    backoff (1s, 2s, 4s) means a brief Exa outage doesn't fail the whole
    research. Without this, a single DNS timeout kills one branch of results.
"""

import os

from exa_py import Exa
from render_sdk import Workflows, Retry

app = Workflows()


@app.task(
    plan="starter",
    timeout_seconds=30,
    retry=Retry(max_retries=3, wait_duration_ms=1000, backoff_scaling=2),
)
def search(query: str) -> dict:
    """Run a single Exa search and return results."""
    exa = Exa(api_key=os.environ["EXA_API_KEY"])
    response = exa.search_and_contents(query, num_results=5, text=True)
    results = []
    for r in response.results:
        results.append({
            "title": r.title or "Untitled",
            "url": r.url,
            "text": (r.text or "")[:3000],
        })
    return {"query": query, "results": results}
