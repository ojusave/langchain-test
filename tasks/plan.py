"""
Plan task: asks Claude to generate 3-5 targeted search queries.

Workflow config rationale:
  - plan: starter (0.5 CPU, 512 MB) — lightweight LLM call with a short prompt.
  - timeout: 45s — Claude should respond in <10s; 45s gives room for cold starts.
  - retry: 2 retries, 2s base wait, 1.5x backoff — handles Claude rate limits
    or transient API errors. Without retries, a single 429 from Anthropic
    would kill the entire research pipeline.
"""

from render_sdk import Workflows, Retry

from .llm import ask, parse_json

app = Workflows()


@app.task(
    plan="starter",
    timeout_seconds=45,
    retry=Retry(max_retries=2, wait_duration_ms=2000, backoff_scaling=1.5),
)
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
