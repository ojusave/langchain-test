"""Plan task: asks Claude to generate 3-5 targeted search queries from the user's question."""

from render_sdk import Workflows

from .llm import ask, parse_json

app = Workflows()


@app.task
def plan_research(question: str) -> dict:
    """Generate 3-5 targeted search queries for the research question."""
    raw = ask(
        system=(
            "You are a research planner. Given a question, generate 3-5 targeted web search queries "
            "that would help answer it comprehensively. Return ONLY a JSON object with a 'queries' key "
            "containing a list of query strings. No other text."
        ),
        user=question,
    )
    return parse_json(raw, {"queries": [question]})
