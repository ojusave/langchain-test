"""
Shared Claude helpers: LLM instantiation, prompt execution, and JSON parsing.

Used by plan, analyze, and synthesize tasks. The LLM is configured via
environment variables (ANTHROPIC_MODEL, AGENT_TEMPERATURE) so the same
code works across environments without code changes.

The parse_json helper is deliberately lenient: Claude sometimes wraps JSON
in markdown code fences or adds preamble text. The fallback extraction
finds the first {...} block, which is good enough for structured output
without forcing function-calling mode.
"""

import json
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
TEMPERATURE = float(os.environ.get("AGENT_TEMPERATURE", "0.3"))


def get_llm():
    return ChatAnthropic(model=MODEL, temperature=TEMPERATURE)


def ask(system: str, user: str) -> str:
    response = get_llm().invoke([
        SystemMessage(content=system),
        HumanMessage(content=user),
    ])
    content = response.content
    return content if isinstance(content, str) else str(content)


def parse_json(raw: str, fallback: dict) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end])
            except json.JSONDecodeError:
                pass
        return fallback
