from typing import List, Dict, Any


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
