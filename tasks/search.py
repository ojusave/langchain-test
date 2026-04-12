"""Search task: runs a single Exa web search and returns title, URL, and text for each result."""

import os

from exa_py import Exa
from render_sdk import Workflows

app = Workflows()


@app.task
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
