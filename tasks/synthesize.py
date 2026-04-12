"""
Synthesize task: merges all analyses into a structured report.

Workflow config rationale:
  - plan: standard (1 CPU, 2 GB) — the heaviest Claude call; the prompt
    contains every analysis (findings + key points + sources) concatenated
    together. Token count scales with the number of search queries.
  - timeout: 90s — synthesis over 3-5 analyses with full context can take
    30-40s from Claude; 90s covers worst-case latency.
  - retry: 1 retry, 3s wait — the input is deterministic (all analyses are
    already computed), so a retry will produce the same result. One retry
    handles a transient Claude error without wasting compute on repeated
    failures.
"""

from render_sdk import Workflows, Retry

from .llm import ask, parse_json

app = Workflows()


@app.task(
    plan="standard",
    timeout_seconds=90,
    retry=Retry(max_retries=1, wait_duration_ms=3000, backoff_scaling=1),
)
def synthesize(question: str, analyses: list) -> dict:
    """Merge all analyses into a structured research report."""
    parts = []
    for a in analyses:
        section = f"**Findings:**\n{a.get('findings', '')}\n\n"
        points = a.get("key_points", [])
        if points:
            section += "**Key points:**\n" + "\n".join(f"- {p}" for p in points) + "\n\n"
        sources = a.get("sources", [])
        if sources:
            section += "**Sources:**\n" + "\n".join(
                f"- [{s.get('title', 'Source')}]({s.get('url', '')})" for s in sources
            )
        parts.append(section)

    context = "\n\n---\n\n".join(parts)
    raw = ask(
        system=(
            "You are a research synthesizer. Combine the analyses below into a structured report. "
            "Return ONLY a JSON object with:\n"
            '- "title": a concise report title\n'
            '- "summary": a 2-3 sentence executive summary\n'
            '- "sections": a list of objects with "heading" and "content" keys (use markdown in content)\n'
            '- "sources": a deduplicated list of objects with "title" and "url" keys\n'
            "No other text."
        ),
        user=f"Research question: {question}\n\nAnalyses:\n{context}",
    )
    return parse_json(raw, {
        "title": "Research Report",
        "summary": raw[:500],
        "sections": [],
        "sources": [],
    })
