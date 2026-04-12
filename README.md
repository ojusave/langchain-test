# LangChain Example: Conversational Agent with Tools

A FastAPI app demonstrating LangChain's agent framework. The agent can:

- **Search Wikipedia** for factual information
- **Calculate** math expressions
- **Maintain conversation context** across messages

Built with LangChain + LangGraph + Anthropic Claude, deployed on Render.

## Architecture

```
Browser  →  FastAPI  →  LangGraph ReAct Agent  →  Claude Sonnet
                              ↕
                     Tools (Wikipedia, Calculator)
```

**Why LangChain here (vs raw API calls)?**

A direct OpenAI API call can't decide on its own to search Wikipedia, read the result, and then formulate a grounded answer. LangChain's agent framework handles the reasoning loop: the LLM decides which tool to call, observes the result, and keeps looping until it has a final answer. This "ReAct" pattern would take significant boilerplate to build from scratch.

## Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic key
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Run the server
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000 in your browser.

## Deploying to Render

This repo includes a `render.yaml` Blueprint for one-click deployment:

1. Push this folder to a GitHub repository
2. Go to https://dashboard.render.com/blueprint/new
3. Connect your repo
4. Set the `ANTHROPIC_API_KEY` environment variable when prompted
5. Click **Apply** to deploy

The app binds to `0.0.0.0:$PORT` automatically (Render sets `$PORT`).

## API

### `POST /chat`

```json
{
  "message": "What is the population of Japan?",
  "history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi! How can I help?" }
  ]
}
```

Response:

```json
{
  "reply": "According to Wikipedia, Japan has a population of approximately 125 million people."
}
```

### `GET /health`

Returns `{ "status": "ok", "agent_loaded": true }`.
