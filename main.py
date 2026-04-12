import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

import httpx


# --- Tools the agent can use ---

@tool
async def search_wikipedia(query: str) -> str:
    """Search Wikipedia for a topic and return a summary. Use this when you need factual information about a person, place, event, or concept."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_"),
            headers={"User-Agent": "langchain-example/1.0"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("extract", "No summary available.")
        return f"Could not find a Wikipedia article for '{query}'."


@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression. Use this for any arithmetic or math calculation."""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "Error: only numeric expressions with +, -, *, /, (, ) are allowed."
    try:
        result = eval(expression)  # noqa: S307 – input is sanitized above
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


# --- App setup ---

SYSTEM_PROMPT = """You are a helpful assistant. You have access to tools:
- search_wikipedia: look up factual information
- calculate: do math

Use tools when they'd help answer the user's question. Be concise and friendly."""


def build_agent():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.3)
    return create_react_agent(llm, tools=[search_wikipedia, calculate])


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = build_agent()
    yield


app = FastAPI(title="LangChain Example", lifespan=lifespan)

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
    if not app.state.agent:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY is not set.")

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in req.history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=req.message))

    result = await app.state.agent.ainvoke({"messages": messages})
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage) and m.content]
    reply = ai_messages[-1].content if ai_messages else "I couldn't generate a response."

    return ChatResponse(reply=reply)


@app.get("/health")
async def health():
    return {"status": "ok", "agent_loaded": app.state.agent is not None}


# Serve the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")
