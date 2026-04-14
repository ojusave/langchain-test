"""
Pipeline package: exposes run_pipeline for the web service.

The web service (main.py) imports `run_pipeline` from this package.
The orchestrator dispatches plan, research, and synthesize as individual
workflow tasks via the Render SDK, polls each one, and streams real-time
progress back to the client as Server-Sent Events.
"""

from .orchestrator import run_pipeline

__all__ = ["run_pipeline"]
