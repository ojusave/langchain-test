# LangChain Chat: Conversational Agent with Tools

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ojusave/langchain-test)

A FastAPI app demonstrating LangChain's agent framework. The agent can:

- **Search Wikipedia** for factual information
- **Calculate** math expressions
- **Maintain conversation context** across messages

Built with LangChain + LangGraph + Anthropic Claude, running on [Render](https://render.com/).

## Deploy

Click the **Deploy to Render** button above. You'll be prompted to set your `ANTHROPIC_API_KEY`, then click **Apply**. That's it.

Don't have a Render account? [Sign up here](https://render.com/register).

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | Your Anthropic API key |
| `ANTHROPIC_MODEL` | No | `claude-sonnet-4-20250514` | Model to use |
| `AGENT_TEMPERATURE` | No | `0.3` | LLM temperature |

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
