"""Synthesize task: merges all analyses into a structured report with title, sections, and sources."""

from render_sdk import Workflows

from .llm import ask, parse_json

app = Workflows()


@app.task
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
