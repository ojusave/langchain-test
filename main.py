"""
FastAPI web service: the HTTP layer for the research agent.

This file is intentionally thin. It handles:
  - CORS middleware (so the browser UI can call the API)
  - The /research POST endpoint (delegates to the pipeline orchestrator)
  - The /feedback POST endpoint (LangSmith user ratings)
  - The /history endpoints (optional PostgreSQL threaded history)
  - The /health GET endpoint (for Render health checks)
  - Static file serving (the browser UI)

The pipeline orchestrator (pipeline/orchestrator.py) dispatches individual
workflow tasks via the Render SDK, polls each one, and streams real-time
progress to the frontend as SSE. Research execution happens on the
workflow service.
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pipeline import run_pipeline
from pipeline.feedback import router as feedback_router
from pipeline.history import (
    init_db, close_db,
    create_thread, list_threads, get_thread, delete_thread,
    get_prior_context,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Research Agent", lifespan=lifespan)
app.include_router(feedback_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    question: str
    thread_id: Optional[str] = None


@app.post("/research")
async def research(req: ResearchRequest):
    prior_context = None
    thread_id = req.thread_id

    if not thread_id:
        thread_id = await create_thread(req.question)
    else:
        prior_context = await get_prior_context(thread_id)

    return StreamingResponse(
        run_pipeline(req.question, thread_id=thread_id, prior_context=prior_context),
        media_type="text/event-stream",
    )


@app.get("/history")
async def history():
    return await list_threads()


@app.get("/history/{thread_id}")
async def history_entry(thread_id: str):
    thread = await get_thread(thread_id)
    if not thread:
        return JSONResponse({"error": "not found"}, status_code=404)
    return thread


@app.delete("/history/{thread_id}")
async def history_delete(thread_id: str):
    deleted = await delete_thread(thread_id)
    if not deleted:
        return JSONResponse({"error": "not found"}, status_code=404)
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")
