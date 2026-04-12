# LangChain Chat: Conversational Agent with Tools

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ojusave/langchain-test)

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

A direct API call can't decide on its own to search Wikipedia, read the result, and then formulate a grounded answer. LangChain's agent framework handles the reasoning loop: the LLM decides which tool to call, observes the result, and keeps looping until it has a final answer. This "ReAct" pattern would take significant boilerplate to build from scratch.

## Project Structure

```
├── main.py           # FastAPI app, routes, static serving
├── agent.py          # Agent config, system prompt, builder
├── tools.py          # Tool definitions (Wikipedia, calculator)
├── static/
│   └── index.html    # Chat UI
├── render.yaml       # Render Blueprint
├── requirements.txt  # Python dependencies
└── .env.example      # Environment variable reference
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | Your Anthropic API key |
| `ANTHROPIC_MODEL` | No | `claude-sonnet-4-20250514` | Model to use |
| `AGENT_TEMPERATURE` | No | `0.3` | LLM temperature |

## Deploying to Render

Click the **Deploy to Render** button above, or:

1. Fork/push this repo to GitHub
2. Go to https://dashboard.render.com/blueprint/new
3. Connect your repo
4. Set `ANTHROPIC_API_KEY` when prompted
5. Click **Apply**

## Local Development

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000 in your browser.

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
