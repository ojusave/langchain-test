"""Pipeline orchestrator: starts the research task and streams status via SSE."""

import json
import os

from render_sdk import RenderAsync

WORKFLOW_SLUG = os.environ.get("WORKFLOW_SLUG", "research-agent-workflow")

render = RenderAsync()


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def run_pipeline(question: str):
    """Start the research orchestrator task and yield SSE events until it completes."""
    try:
        yield sse("status", {"message": "Starting research..."})

        started = await render.workflows.start_task(
            f"{WORKFLOW_SLUG}/research", {"question": question}
        )
        yield sse("status", {"message": "Researching...", "task_run_id": started.id})

        finished = await started

        if finished.status.value == "completed":
            report = finished.results[0] if finished.results else {}
            yield sse("done", {"report": report})
        else:
            error = getattr(finished, "error", None) or "Research failed after retries."
            yield sse("error", {"message": str(error)})

    except Exception as e:
        yield sse("error", {"message": str(e)})
