from render_sdk import Workflows, Retry

from agent import build_agent, SYSTEM_PROMPT
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

app = Workflows(
    default_retry=Retry(max_retries=2, wait_duration_ms=1000, backoff_scaling=1.5),
    default_timeout=120,
    default_plan="starter",
)


@app.task
async def agent_chat(message: str, history: list) -> str:
    agent = build_agent()
    if not agent:
        return "Error: ANTHROPIC_API_KEY is not set."

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=message))

    result = await agent.ainvoke({"messages": messages})
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage) and m.content]
    return ai_messages[-1].content if ai_messages else "I couldn't generate a response."


if __name__ == "__main__":
    app.start()
