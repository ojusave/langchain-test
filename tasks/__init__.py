"""
Tasks package: combines all workflow task apps into a single Workflows entry point.

Four task modules register with the Workflows runtime:
  - classify: routes queries to research pipeline or direct answer (ChatAnthropic)
  - plan: breaks a question into subtopics (ChatAnthropic)
  - research_agent: runs a LangGraph ReAct agent per subtopic (Exa tools)
  - synthesize: merges findings into a report (ChatAnthropic)

The web service orchestrates these tasks step-by-step via the Render SDK,
streaming real-time progress to the frontend.

All Claude calls go through the shared ChatAnthropic model in tasks/llm.py.
Each module defines its own per-task compute plan, timeout, and retry strategy.
"""

from render_sdk import Workflows

from .classify import app as classify_app
from .plan import app as plan_app
from .research_agent import app as research_agent_app
from .synthesize import app as synthesize_app

app = Workflows.from_workflows(
    classify_app,
    plan_app,
    research_agent_app,
    synthesize_app,
)

__all__ = ["app"]
