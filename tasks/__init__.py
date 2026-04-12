"""
Tasks package: combines all workflow task apps into a single Workflows entry point.

Each task module (plan, search, analyze, synthesize, research) defines its own
Workflows app with per-task compute plans, timeouts, and retry strategies.
This file merges them into a single app that the `python -m tasks` entry point
starts.

No default_retry/default_timeout/default_plan is set here because every task
explicitly configures its own. This makes the config visible and intentional
rather than hidden behind a default.
"""

from render_sdk import Workflows

from .plan import app as plan_app
from .search import app as search_app
from .analyze import app as analyze_app
from .synthesize import app as synthesize_app
from .research import app as research_app

app = Workflows.from_workflows(
    research_app,
    plan_app,
    search_app,
    analyze_app,
    synthesize_app,
)

__all__ = ["app"]
