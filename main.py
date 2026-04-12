import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from render_sdk import RenderAsync

WORKFLOW_SLUG = os.environ.get("WORKFLOW_SLUG", "langchain-chat-workflow")

app = FastAPI(title="LangChain Example")
render = RenderAsync()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        run = await render.workflows.run_task(
            f"{WORKFLOW_SLUG}/agent_chat",
            {"message": req.message, "history": req.history},
        )
        reply = run.results[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(reply=reply)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")
