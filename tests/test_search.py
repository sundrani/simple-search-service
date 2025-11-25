from app.search import simple_substring_search


def test_simple_substring_search():
    data = [
        {"id": 1, "message": "Hello world"},
        {"id": 2, "message": "Another message"},
        {"id": 3, "message": "HELLO again"},
    ]

    results = simple_substring_search(data, "hello")
    assert len(results) == 2
    ids = {r["id"] for r in results}
    assert ids == {1, 3}
