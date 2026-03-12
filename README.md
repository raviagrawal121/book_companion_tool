# 💰 Money Coach Max — Demo Setup Guide

A RAG-powered AI financial coaching assistant built with Python + FastAPI + OpenAI.

---

## 🚀 Quick Start (Local)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# Start the server
uvicorn main:app --reload --port 8000
```

The backend will:
- Load the Rich Dad Poor Dad content
- Chunk and embed it (takes ~30 seconds on first run)
- Start the API at http://localhost:8000

### 2. Frontend

Open `frontend/widget.html` directly in your browser.

> The widget has **fallback demo responses** built in, so it works even without the backend running — perfect for showing the client the UI flow.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/session/new` | Create new session |
| POST | `/session/name` | Set user's name |
| GET | `/session/status` | Get session state |
| POST | `/chat` | Send message, get RAG response |
| POST | `/verify/code` | Validate access code |
| POST | `/verify/purchase` | Submit purchase verification |
| GET | `/admin/logs` | View anonymous question log |

---

## 🗂️ Project Structure

```
money-coach-max/
├── backend/
│   ├── main.py              ← FastAPI app + all routes
│   ├── rag/
│   │   └── engine.py        ← Chunking, embedding, retrieval
│   ├── services/
│   │   ├── session.py       ← Trial management + access codes
│   │   └── logger.py        ← Anonymous question logging
│   ├── data/
│   │   └── rdpd_content.txt ← Demo knowledge base
│   └── requirements.txt
└── frontend/
    └── widget.html          ← Complete embeddable chat UI
```

---

## 🔑 Access Codes (Demo)

```
STORM2026 | MAX2026 | JOEPLAN | SAFESEAS | SMARTMONEY
RICHLIFE  | MONEYMAX | FREEDOM26 | COACHMAX | WEALTHIQ
```

---

## 📦 Adding the Client's Book Content

1. Export book text as `.txt` file
2. Place in `backend/data/`
3. Add the path to `DOCUMENTS` list in `main.py`
4. Restart the server — it will re-embed automatically

---

## 🌐 Embedding in Wix

1. Deploy backend to Railway or Render
2. Update `API_BASE` in `widget.html` to your deployed URL
3. In Wix: Add → Embed → HTML iframe
4. Paste the full `widget.html` contents

---

## 📈 Upgrading to Production (v2)

- [ ] Replace in-memory store with Pinecone vector DB
- [ ] Add PostgreSQL for session + log persistence
- [ ] Add Redis for rate limiting
- [ ] Add streaming responses
- [ ] Add user accounts + auth
