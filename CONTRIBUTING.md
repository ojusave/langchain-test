# Contributing

Thanks for helping improve this demo.

## Issues

Open an issue for bugs, unclear docs, or small feature ideas. Include what you expected, what happened, and relevant logs when it helps (redact secrets).

## Pull requests

1. Fork the repository and create a focused branch.
2. Match existing Python style and file layout (`main.py`, `pipeline/`, `tasks/`).
3. Install dependencies with `pip install -r requirements.txt` and confirm imports resolve. If you change dependencies, explain why in the PR.
4. Describe the change in the PR: what it does and why.

## Validating behavior

End-to-end runs need Render plus Anthropic and Exa keys. If you cannot run a full deploy, say so in the PR and explain what you verified (for example: import checks or a dry run).

## Security

Do not commit API keys, `.env` files, or internal Render URLs. Use environment variables only.
