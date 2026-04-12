"""
Analyze task: asks Claude to extract key findings from one set of search results.

Workflow config rationale:
  - plan: standard (1 CPU, 2 GB) — the prompt includes up to 10 KB of search
    result text per query; Claude needs more memory for larger contexts.
  - timeout: 60s — processing ~5 search results takes longer than planning.
  - retry: 2 retries, 2s base wait, 1.5x backoff — handles Claude rate limits.
    Each analyze task runs in parallel, so N simultaneous Claude calls are more
    likely to hit rate limits than a single plan call.
"""

from render_sdk import Workflows, Retry

from .llm import ask, parse_json

app = Workflows()


@app.task(
    plan="standard",
    timeout_seconds=60,
    retry=Retry(max_retries=2, wait_duration_ms=2000, backoff_scaling=1.5),
)
def analyze(query: str, results: list) -> dict:
    """Analyze search results for a single query and extract key findings."""
    context = "\n\n".join(
        f"### {r['title']}\nURL: {r['url']}\n{r['text'][:2000]}"
        for r in results
    )
    raw = ask(
        system=(
            "You are a research analyst. Analyze the search results below and extract key findings "
            "relevant to the query. Return ONLY a JSON object with:\n"
            '- "findings": a paragraph summarizing what you found\n'
            '- "key_points": a list of 2-4 concise bullet point strings\n'
            '- "sources": a list of objects with "title" and "url" keys\n'
            "No other text."
        ),
        user=f"Query: {query}\n\nSearch Results:\n{context}",
    )
    return parse_json(raw, {"findings": raw, "key_points": [], "sources": []})
