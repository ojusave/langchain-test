"""
Classify task: determines whether a query needs web research or can be
answered directly by Claude.

Single-turn Claude call via the shared ChatAnthropic model (tasks/llm.py).
Returns a type ("research" or "direct") and, for direct queries, a reply.

Workflow config rationale:
  - plan: starter (0.5 CPU, 512 MB): lightweight LLM call, short prompt.
  - timeout: 30s: classification should take <5s; 30s covers cold starts.
  - retry: 1 retry, 2s wait: handles transient Claude errors.
"""

from render_sdk import Workflows, Retry

from .llm import ask, parse_json

app = Workflows()


@app.task(
    plan="starter",
    timeout_seconds=30,
    retry=Retry(max_retries=1, wait_duration_ms=2000, backoff_scaling=1),
)
def classify_query(question: str) -> dict:
    """Classify a query as needing research or answerable directly."""
    raw = ask(
        system=(
            "You are a query classifier. Determine if the user's message requires "
            "web research (searching for current information, facts, data, news, etc.) "
            "or can be answered directly (greetings, simple questions, math, definitions, "
            "opinions, coding help, etc.).\n\n"
            "Return ONLY a JSON object with:\n"
            '- "type": either "research" or "direct"\n'
            '- "reply": if type is "direct", a helpful response to the user. '
            'If type is "research", omit this field.\n'
            "No other text."
        ),
        user=question,
    )
    return parse_json(raw, {"type": "research"})
