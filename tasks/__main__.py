"""
Workflow service entry point: run with `python -m tasks`.

This starts the Render Workflows runtime, which registers all tasks
(plan, search, analyze, synthesize, research) and begins polling for
incoming task runs.
"""

from tasks import app

app.start()
