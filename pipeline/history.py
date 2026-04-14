"""
Optional threaded research history backed by Render PostgreSQL.

Data model: threads contain entries. Each entry is one question → report pair.
Follow-up queries within a thread share a thread_id.

All functions no-op gracefully when DATABASE_URL is not set.
To remove: delete this file and remove the related imports from main.py
and pipeline/orchestrator.py.
"""

import json
import os
import uuid

DATABASE_URL = os.environ.get("DATABASE_URL")

_pool = None

_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS threads (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT            NOT NULL,
    created_at  TIMESTAMPTZ     DEFAULT now(),
    updated_at  TIMESTAMPTZ     DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research_entries (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id   UUID            NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    question    TEXT            NOT NULL,
    report      JSONB           NOT NULL,
    run_id      TEXT,
    created_at  TIMESTAMPTZ     DEFAULT now()
);

DROP TABLE IF EXISTS research_history;
"""


async def init_db():
    """Create the connection pool and tables. No-op without DATABASE_URL."""
    global _pool
    if not DATABASE_URL:
        return

    import asyncpg
    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    async with _pool.acquire() as conn:
        await conn.execute(_CREATE_TABLES)


async def close_db():
    """Close the connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# ---------------------------------------------------------------------------
# Threads
# ---------------------------------------------------------------------------

async def create_thread(title: str) -> str | None:
    """Create a new thread. Returns the thread id."""
    if not _pool:
        return None

    thread_id = str(uuid.uuid4())
    await _pool.execute(
        "INSERT INTO threads (id, title) VALUES ($1, $2)",
        uuid.UUID(thread_id),
        title[:200],
    )
    return thread_id


async def list_threads(limit: int = 30) -> list[dict]:
    """Return recent threads (newest first, without entry bodies)."""
    if not _pool:
        return []

    rows = await _pool.fetch(
        "SELECT id, title, updated_at FROM threads ORDER BY updated_at DESC LIMIT $1",
        limit,
    )
    return [
        {"id": str(r["id"]), "title": r["title"], "updated_at": r["updated_at"].isoformat()}
        for r in rows
    ]


async def get_thread(thread_id: str) -> dict | None:
    """Return a thread with all its entries."""
    if not _pool:
        return None

    thread = await _pool.fetchrow(
        "SELECT id, title, created_at, updated_at FROM threads WHERE id = $1",
        uuid.UUID(thread_id),
    )
    if not thread:
        return None

    entries = await _pool.fetch(
        "SELECT id, question, report, run_id, created_at FROM research_entries "
        "WHERE thread_id = $1 ORDER BY created_at ASC",
        uuid.UUID(thread_id),
    )

    return {
        "id": str(thread["id"]),
        "title": thread["title"],
        "created_at": thread["created_at"].isoformat(),
        "updated_at": thread["updated_at"].isoformat(),
        "entries": [
            {
                "id": str(e["id"]),
                "question": e["question"],
                "report": json.loads(e["report"]) if isinstance(e["report"], str) else e["report"],
                "run_id": e["run_id"],
                "created_at": e["created_at"].isoformat(),
            }
            for e in entries
        ],
    }


async def delete_thread(thread_id: str) -> bool:
    """Delete a thread and all its entries. Returns True if deleted."""
    if not _pool:
        return False

    result = await _pool.execute(
        "DELETE FROM threads WHERE id = $1",
        uuid.UUID(thread_id),
    )
    return result == "DELETE 1"


# ---------------------------------------------------------------------------
# Entries
# ---------------------------------------------------------------------------

async def save_entry(
    thread_id: str, question: str, report: dict, run_id: str | None = None
) -> str | None:
    """Save a research entry to a thread. Returns the entry id."""
    if not _pool:
        return None

    entry_id = str(uuid.uuid4())
    await _pool.execute(
        "INSERT INTO research_entries (id, thread_id, question, report, run_id) "
        "VALUES ($1, $2, $3, $4::jsonb, $5)",
        uuid.UUID(entry_id),
        uuid.UUID(thread_id),
        question,
        json.dumps(report),
        run_id,
    )
    await _pool.execute(
        "UPDATE threads SET updated_at = now() WHERE id = $1",
        uuid.UUID(thread_id),
    )
    return entry_id


async def get_prior_context(thread_id: str) -> str | None:
    """Build a lightweight context string from the last entry in a thread.

    Returns the report title + section headings (~50 tokens) so follow-up
    queries know what was already covered without blowing up the prompt.
    """
    if not _pool:
        return None

    row = await _pool.fetchrow(
        "SELECT question, report FROM research_entries "
        "WHERE thread_id = $1 ORDER BY created_at DESC LIMIT 1",
        uuid.UUID(thread_id),
    )
    if not row:
        return None

    report = json.loads(row["report"]) if isinstance(row["report"], str) else row["report"]
    title = report.get("title", row["question"])
    headings = [s.get("heading", "") for s in report.get("sections", []) if s.get("heading")]

    if not headings:
        return f'Previous research: "{title}"'

    return f'Previous research: "{title}"\nCovered: {", ".join(headings)}'
