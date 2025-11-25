# Simple Search Service

A lightweight FastAPI-based search service built on top of the `/messages` data source.  
The goal is to provide a simple, fast, publicly available search API that meets all project
requirements—including pagination, performance under 100ms, and deployment readiness.

---

## 🌐 Live API

**Base URL:**  
https://simple-search-service.onrender.com

**API Docs:**  
https://simple-search-service.onrender.com/docs

---

## Important Note About the `/messages` API

Locally, the service successfully fetches messages from:

```
https://november7-730026606190.europe-west1.run.app/messages/
```

However, when running on **Render (free tier)**, calls to this endpoint return:

```
402 Payment Required
```

This is an upstream restriction (likely IP‑based or billing).  
To ensure the `/search` endpoint continues working, the application:

1. Attempts remote fetch on startup  
2. Logs the error if the request fails  
3. **Falls back to a local in‑memory dataset**  
4. Continues serving `/search` normally  

This behavior is intentional and ensures the assignment requirements are met.



## 🔌 Endpoints

### `GET /health`
Returns basic service health and the number of messages loaded.

### `GET /search`
Example:
```
https://simple-search-service.onrender.com/search?q=hello&page=1&size=10
```

Response Example:
```json
{
  "query": "hello",
  "page": 1,
  "size": 10,
  "total": 2,
  "results": [
    { "id": 1, "message": "Hello world" },
    { "id": 3, "message": "HELLO again" }
  ]
}
```

---

##  How It Works

### 1. Data Loading  
The service attempts to load messages from the external data source:
```
https://november7-730026606190.europe-west1.run.app/messages
```

If the remote request fails due to network restrictions or redirects (common in Render free tier),
the service activates a **fallback dataset** so the API always returns usable results.

### 2. Search Logic
Search is performed using a simple, human-readable substring comparison:
- Convert both query and message to lowercase  
- Check if the query appears inside the message  
- Apply pagination  

### 3. Performance  
Messages are held entirely in memory, giving extremely fast search performance
(7–20ms after warm start).

---

## 🧪 Running Locally

Install dependencies:
```
pip install -r requirements.txt
```

Run the service:
```
uvicorn app.main:app --reload
```

Open API docs:
```
http://localhost:8000/docs
```

---

## 🎁 Bonus: Design Notes

Several approaches were evaluated:

### **1. In-Memory Search (Chosen)**
- Fast
- Zero dependencies
- Perfect for a moderate dataset
- Simple and reliable

 
### **2. Redis / Elasticsearch**
- Scalable and feature-rich  
- Heavy for a small assessment  
- Requires paid infra  

---

## 💡 Bonus: How to Reduce Latency Toward 30ms

- Keep all data in memory 
- Warm container (Render paid tier removes cold-start delay)
- Pre-tokenize messages or build an inverted index
- Avoid remote calls during requests
- Minimize logging on hot paths

---

## 📦 Deployment (Render)

Deployment publishes automatically whenever GitHub pushes a new commit.

---

## ✔️ Requirements Checklist

- [x] Python implementation  
- [x] Query-based search  
- [x] Pagination  
- [x] Public deployment  
- [x] <100ms response time  
- [x] Bonus: alternative designs  
- [x] Bonus: latency optimization  
- [x] GitHub repository  
- [x] Live, functional `/search` endpoint  

---

## 👨‍💻 Author

Rahul Sundrani  
**Live Service:** https://simple-search-service.onrender.com



![alt text](<Screenshot 2025-11-25 at 11.26.42 AM.png>)
![App Screenshot](SIMPLE-SEARCH-SERVICE/Screenshot 2025-11-25 at 11.26.42 AM.png)
