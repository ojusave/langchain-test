"""Tasks package: combines all workflow task apps into a single Workflows entry point."""

from render_sdk import Workflows, Retry

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
    default_retry=Retry(max_retries=2, wait_duration_ms=1000, backoff_scaling=1.5),
    default_timeout=120,
    default_plan="starter",
)

__all__ = ["app"]
