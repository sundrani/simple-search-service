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
async def load_messages():
    global messages_cache
    
    url = "https://november7-730026606190.europe-west1.run.app/messages"

    # Force HTTP/1.1 (Render sometimes defaults to HTTP/2)
    limits = httpx.Limits(max_keepalive_connections=0, max_connections=1)

    async with httpx.AsyncClient(
        timeout=10.0,
        follow_redirects=False,
        http2=False,
        limits=limits,
        headers={
            "accept": "application/json",
            "user-agent": "Mozilla/5.0"
        }
    ) as client:
        response = await client.get(url)

        # If the API wants trailing slash:
        if response.status_code == 307:
            redirected = response.headers.get("location")
            response = await client.get(redirected)

        response.raise_for_status()

        data = response.json()

        # Handle list or dict response
        if isinstance(data, list):
            messages_cache = data
        elif isinstance(data, dict):
            for key in ("items", "messages", "results", "data"):
                if key in data and isinstance(data[key], list):
                    messages_cache = data[key]
                    break
        else:
            raise RuntimeError(f"Unexpected messages response type: {type(data)}")

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
