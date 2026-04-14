"""
Workflow service entry point: run with `python -m tasks`.

This starts the Render Workflows runtime, which registers all tasks
(plan_research, research_subtopic, synthesize) and begins polling for
incoming task runs.
"""

from tasks import app

app.start()
