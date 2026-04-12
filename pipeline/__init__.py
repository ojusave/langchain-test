"""
Pipeline package: exposes run_pipeline for the web service.

The web service (main.py) imports `run_pipeline` from this package.
The orchestrator starts the research workflow task via the Render SDK
and streams status updates back to the client as Server-Sent Events.
"""

from .orchestrator import run_pipeline

__all__ = ["run_pipeline"]
