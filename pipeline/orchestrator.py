"""
Pipeline orchestrator: starts the research workflow task and streams SSE.

This is the bridge between the stateless web service and the durable
workflow service. It:
  1. Triggers the `research` orchestrator task via the Render SDK
  2. Awaits its completion (the SDK handles polling)
  3. Streams status updates as Server-Sent Events (SSE)

The orchestrator itself does no research work. All compute happens in
the workflow service on isolated instances with their own retry/timeout
config.
"""

import json
import os

from render_sdk import RenderAsync
from render_sdk.client.errors import TaskRunError

WORKFLOW_SLUG = os.environ.get("WORKFLOW_SLUG", "research-agent-workflow")

render = RenderAsync()


def _to_dict(obj):
    """Convert SDK objects to plain dicts for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_dict(i) for i in obj]
    if hasattr(obj, "__dict__") and not isinstance(obj, (str, int, float, bool)):
        return {k: _to_dict(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    return obj


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


async def run_pipeline(question: str):
    """Start the research orchestrator task and yield SSE events until it completes."""
    try:
        yield sse("status", {"message": "Starting research..."})

        started = await render.workflows.start_task(
            f"{WORKFLOW_SLUG}/research", {"question": question}
        )
        yield sse("status", {"message": "Researching...", "task_run_id": started.id})

        finished = await started

        report = {}
        if finished.results:
            raw = finished.results[0]
            report = _to_dict(raw) if not isinstance(raw, dict) else raw

        yield sse("done", {"report": report})

    except TaskRunError as e:
        yield sse("error", {"message": str(e)})

    except Exception as e:
        yield sse("error", {"message": str(e)})
