# Simple Search Engine on Top of /messages

This project implements a simple search engine API on top of the provided `/messages` data source:

- Data Source Swagger: https://november7-730026606190.europe-west1.run.app/docs#/default/get_messages_messages__get
- Data Endpoint: `GET https://november7-730026606190.europe-west1.run.app/messages`

The service exposes a `/search` endpoint that accepts a query string and returns a paginated list of matching records.

## Tech Stack

- Python 3.12
- FastAPI
- Uvicorn
- httpx
- pytest

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000/docs to explore the API

	•	Health: http://localhost:8000/health￼

