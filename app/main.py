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

def simple_substring_search(
    data: List[Dict[str, Any]],
    query: str,
    field: str = "message",
) -> List[Dict[str, Any]]:
    """Reusable search helper: case-insensitive substring search on a given field."""
    q = query.lower()
    results: List[Dict[str, Any]] = []

    for item in data:
        value = str(item.get(field, "")).lower()
        if q in value:
            results.append(item)

    return results

@app.on_event("startup")
async def load_messages():
    global messages_cache

    url = "https://november7-730026606190.europe-west1.run.app/messages"

    print(" Attempting to load remote messages...")

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            http2=False,
            headers={
                "accept": "application/json",
                "user-agent": "Mozilla/5.0"
            }
        ) as client:
            response = await client.get(url)

            # If still redirecting
            if response.is_redirect:
                redirect = response.headers.get("location")
                print(f"🔁 Redirecting to {redirect}")
                response = await client.get(redirect)

            response.raise_for_status()  # will go to except if not 200

            data = response.json()

            if isinstance(data, list):
                messages_cache = data
            elif isinstance(data, dict):
                for key in ("items", "messages", "results", "data"):
                    if key in data and isinstance(data[key], list):
                        messages_cache = data[key]
                        break

            print(f" Loaded {len(messages_cache)} messages from remote API.")
            return

    except Exception as e:
        print(" Remote data load failed:", e)
        print(" Using fallback local messages.")

    # FALLBACK DATA 
    messages_cache = [
        {"id": 1, "message": "Hello world"},
        {"id": 2, "message": "FastAPI running"},
        {"id": 3, "message": "Live fallback data"},
        {"id": 4, "message": "Render deployment OK"},
    ]

    print(" Fallback messages loaded.")


@app.get("/health")
async def health() -> Dict[str, Any]:
    """ health endpoint."""
    return {"status": "ok", "messages_loaded": len(messages_cache)}


@app.get("/search")
async def search(
    q: str = Query(..., description="Search query", min_length=1),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
) -> Dict[str, Any]:
    if not messages_cache:
        raise HTTPException(status_code=503, detail="Messages not loaded yet")

    matches = simple_substring_search(messages_cache, q)
    total = len(matches)

    start = (page - 1) * size
    end = start + size

    return {
        "query": q,
        "page": page,
        "size": size,
        "total": total,
        "results": matches[start:end],
    }