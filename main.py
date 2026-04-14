"""
FastAPI web service: the HTTP layer for the research agent.

This file is intentionally thin. It handles:
  - CORS middleware (so the browser UI can call the API)
  - The /research POST endpoint (delegates to the pipeline orchestrator)
  - The /feedback POST endpoint (LangSmith user ratings)
  - The /health GET endpoint (for Render health checks)
  - Static file serving (the browser UI)

The pipeline orchestrator (pipeline/orchestrator.py) dispatches individual
workflow tasks via the Render SDK, polls each one, and streams real-time
progress to the frontend as SSE. Research execution happens on the
workflow service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pipeline import run_pipeline
from pipeline.feedback import router as feedback_router

app = FastAPI(title="Research Agent")
app.include_router(feedback_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    question: str


@app.post("/research")
async def research(req: ResearchRequest):
    return StreamingResponse(run_pipeline(req.question), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")
