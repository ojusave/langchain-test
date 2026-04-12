"""Analyze task: asks Claude to extract key findings, bullet points, and sources from search results."""

from render_sdk import Workflows

from .llm import ask, parse_json

app = Workflows()


@app.task
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
