from typing import List, Dict, Any

import httpx
from fastapi import FastAPI, Query, HTTPException

DATA_SOURCE_URL = "http://november7-730026606190.europe-west1.run.app/messages/"

app = FastAPI(
    title="Simple Search Engine",
    description="Search API built on top of the /messages data source.",
    version="1.0.0",
)

# In-memory cache of messages
messages_cache: List[Dict[str, Any]] = []


# @app.on_event("startup")
# async def load_messages() -> None:
#     """Fetch all messages from the upstream data source on startup."""
#     global messages_cache
#     async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
#         response = await client.get(DATA_SOURCE_URL)
#         response.raise_for_status()
#         data = response.json()
#         if not isinstance(data, list):
#             raise RuntimeError("Expected a list of messages from data source.")
#         messages_cache = data
@app.on_event("startup")
async def load_messages() -> None:
    """
    Fetch all messages from the upstream data source on startup
    and keep them in memory for fast searches.
    Handles both list and dict-shaped JSON responses.
    """
    global messages_cache

    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
        response = await client.get(DATA_SOURCE_URL)
        response.raise_for_status()
        data = response.json()

    # Case 1: API returns a plain list
    if isinstance(data, list):
        messages_cache = data
        return

    # Case 2: API returns an object, e.g. {"items": [...]} or similar
    if isinstance(data, dict):
        # try common keys first
        for key in ("items", "results", "messages", "data"):
            if key in data and isinstance(data[key], list):
                messages_cache = data[key]
                return

        # If we still didn't find a list, as a fallback: first list value in the dict
        for value in data.values():
            if isinstance(value, list):
                messages_cache = value
                return

    # If we reach here, we couldn't find a list of messages
    raise RuntimeError(
        f"Could not find a list of messages in data source response. "
        f"Type: {type(data)}, keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}"
    )


def _search_messages(query: str) -> List[Dict[str, Any]]:
    """Simple case-insensitive substring search over the 'message' field."""
    q = query.lower()
    results: List[Dict[str, Any]] = []

    for m in messages_cache:
        text = str(m.get("message", "")).lower()
        if q in text:
            results.append(m)

    return results


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Simple health endpoint."""
    return {"status": "ok", "messages_loaded": len(messages_cache)}


@app.get("/search")
async def search(
    q: str = Query(..., description="Search query", min_length=1),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
) -> Dict[str, Any]:
    """Search endpoint: returns a paginated list of matching records."""
    if not messages_cache:
        raise HTTPException(status_code=503, detail="Messages not loaded yet")

    matches = _search_messages(q)
    total = len(matches)

    start = (page - 1) * size
    end = start + size

    paginated = matches[start:end]

    return {
        "query": q,
        "page": page,
        "size": size,
        "total": total,
        "results": paginated,
    }
