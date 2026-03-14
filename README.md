# 🔦 Mr. Clarke's Automated Briefing Generator

> *"Mr. Clarke, Hawkins' beloved science teacher, has mysteriously disappeared — leaving behind a collection of dense physics books, radio manuals, and research notes. The AV Club needs to brief the town sheriff on the strange signals appearing around Hawkins, but reading through hundreds of pages would take too long. So they built this."*

An **AI-powered presentation generator** that ingests your documents (PDF/TXT), retrieves the most relevant information using RAG (Retrieval-Augmented Generation), and automatically generates **beautiful, animated slide decks** — all with a Stranger Things theme.

![Theme: Stranger Things](https://img.shields.io/badge/Theme-Stranger_Things-e50914?style=for-the-badge)
![Backend: Django](https://img.shields.io/badge/Backend-Django-092E20?style=for-the-badge&logo=django)
![AI: Groq + LlamaIndex](https://img.shields.io/badge/AI-Groq_+_LlamaIndex-FF6B00?style=for-the-badge)
![DB: MongoDB Atlas](https://img.shields.io/badge/DB-MongoDB_Atlas-47A248?style=for-the-badge&logo=mongodb)

---

## ✨ What It Does

1. **Upload** your PDF or TXT documents
2. **Ask a question** or describe what your presentation should cover
3. The AI **reads your documents**, finds the most relevant sections, and **generates a complete animated slide deck**
4. **Navigate** through slides with animations that replay on every slide transition
5. **View fullscreen** for a presentation-ready experience

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  FRONTEND (React)                    │
│   CDN React 18 + Babel Standalone + Tailwind CSS     │
│   No Node.js needed! Served via Python HTTP server   │
└────────────────────┬────────────────────────────────┘
                     │ REST API calls
                     ▼
┌─────────────────────────────────────────────────────┐
│               BACKEND (Django + DRF)                 │
│                                                      │
│  ┌─────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │ Views   │→ │ RAG      │→ │ Groq LLM           │  │
│  │ (API)   │  │ Service  │  │ (Slide Generation)  │  │
│  └─────────┘  └────┬─────┘  └────────────────────┘  │
│                    │                                  │
│              ┌─────▼──────┐   ┌──────────────────┐   │
│              │ LlamaIndex │   │ HTML Exporter     │   │
│              │ (Retrieval)│   │ (Tailwind + Anim) │   │
│              └─────┬──────┘   └──────────────────┘   │
│                    │                                  │
│              ┌─────▼──────────────────┐               │
│              │  MongoDB Atlas          │               │
│              │  (Vector Search Store)  │               │
│              └────────────────────────┘               │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Hackfest/
├── .env                          # Environment variables (API keys)
├── README.md                     # You are here!
│
├── frontend-react/               # 🖥️ React Frontend (CDN-based, no Node.js)
│   ├── index.html                # HTML shell — loads React, Babel, Tailwind from CDN
│   ├── app.jsx                   # Main React app (components + API calls)
│   ├── style.css                 # Stranger Things theme + animation keyframes
│   └── particles.js              # Floating "Upside Down" spore particles effect
│
├── hackfest_project/             # 🐍 Django Backend
│   ├── manage.py                 # Django management script
│   ├── hackfest_project/         # Django project settings
│   │   ├── settings.py           # Config (DB, CORS, API keys, etc.)
│   │   └── urls.py               # Root URL routing
│   │
│   └── api/                      # 🔌 REST API app
│       ├── models.py             # Project & Document database models
│       ├── views.py              # API endpoints (upload, generate, render)
│       ├── urls.py               # API URL routing
│       ├── serializers.py        # DRF request validation
│       ├── prompts.py            # LLM system prompts (Stranger Things themed)
│       ├── llm_client.py         # Groq LLM client wrapper
│       ├── document_loaders.py   # PDF/TXT parsing utilities
│       ├── schemas.py            # Pydantic data schemas
│       │
│       ├── services/             # Business logic layer
│       │   ├── ingest_service.py # Document parsing → chunking → embedding → MongoDB
│       │   └── rag_service.py    # RAG pipeline: retrieve context → LLM → HTML slides
│       │
│       └── exporters/            # Output formatters
│           └── html_exporter.py  # Wraps slides in Tailwind + animations for fullscreen
│
├── frontend/                     # (Legacy) Original vanilla HTML/CSS/JS frontend
├── test_data/                    # Sample documents for testing
└── env/                          # Python virtual environment
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** (with pip)
- **MongoDB Atlas** account with a cluster ([free tier works!](https://www.mongodb.com/cloud/atlas))
- **Groq API key** ([get one free](https://console.groq.com/keys))

### 1. Clone & Set Up the Virtual Environment

```bash
git clone <your-repo-url>
cd Hackfest

# Create virtual environment
python -m venv env

# Activate it
# Windows:
.\env\Scripts\activate
# macOS/Linux:
source env/bin/activate
```

### 2. Install Dependencies

```bash
pip install django djangorestframework django-cors-headers
pip install python-dotenv pymongo
pip install llama-index llama-index-vector-stores-mongodb llama-index-llms-groq llama-index-embeddings-huggingface
pip install sentence-transformers PyMuPDF
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Set Up MongoDB Atlas Vector Search

1. Go to your MongoDB Atlas cluster
2. Create a database (e.g., `hackfest_db`)
3. Create a collection (e.g., `document_chunks`)
4. Go to **Atlas Search** → **Create Index** → choose **JSON Editor** and use:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}
```

### 5. Run Database Migrations

```bash
python hackfest_project/manage.py migrate
```

### 6. Start the Backend

```bash
python hackfest_project/manage.py runserver
```

The Django API will start at `http://127.0.0.1:8000/`.

### 7. Start the Frontend

Open a **new terminal**, activate the environment, and:

```bash
cd frontend-react
python -m http.server 8080
```

Open `http://localhost:8080` in your browser.

---

## 🎮 How to Use

1. **Open** `http://localhost:8080` in your browser
2. **Drag & drop** (or browse) your PDF/TXT files into the upload zone
3. **Type a query** describing what your presentation should cover, e.g.:
   > *"Create a presentation about electromagnetic wave interference patterns"*
4. **Click "GENERATE BRIEFING DECK"** and wait for the AI
5. **Navigate slides** with the ◀ PREV / NEXT ▶ buttons or **←/→ arrow keys**
6. **Click "VIEW FULLSCREEN"** for a presentation-ready view

To **update an existing presentation** with new information, just modify your query and click "UPDATE BRIEFING DECK" — the layout and animations are preserved while the content changes.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload/` | Upload PDF/TXT files. Returns a `project_id`. |
| `POST` | `/api/generate/` | Generate a new slide deck from uploaded docs + query. |
| `POST` | `/api/update/` | Update an existing presentation (preserves layout). |
| `GET`  | `/api/render/<project_id>/` | Get the fullscreen HTML slideshow. |
| `GET`  | `/api/project/<project_id>/` | Get project details + individual slides as an array. |

### Example: Generate a Presentation

```bash
# 1. Upload a document
curl -X POST http://127.0.0.1:8000/api/upload/ \
  -F "files=@my_document.pdf"

# Response: { "project_id": "abc-123-...", ... }

# 2. Generate slides
curl -X POST http://127.0.0.1:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize the key findings", "project_id": "abc-123-..."}'

# 3. View the presentation
# Open in browser: http://127.0.0.1:8000/api/render/abc-123-.../
```

---

## 🎨 The Stranger Things Theme

The entire UI is designed with a **Stranger Things / Upside Down** aesthetic:

- **Dark reddish gradients** (`from-[#0a0000] via-[#1a0505] to-[#2a0a0a]`)
- **Glassmorphism cards** with red tints and backdrop blur
- **Neon red accents** and glowing text effects
- **Share Tech Mono** font for that retro-terminal feel
- **Floating particle spores** drifting across the screen
- **Flickering header** animation (like Hawkins Lab lights)
- **7 animation types**: fade-in, fade-up, fade-down, fade-left, fade-right, zoom-in, slide-in
- **Staggered delays** so elements appear sequentially on each slide

---

## 🧠 How the AI Pipeline Works

```
User uploads documents
        │
        ▼
┌───────────────────────┐
│  1. INGEST            │  PyMuPDF parses PDFs → chunks text
│     Document Loader   │  Sentence-Transformers creates embeddings
│     + Embeddings      │  Stores vectors in MongoDB Atlas
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  2. RETRIEVE (RAG)    │  User query → vector similarity search
│     LlamaIndex        │  Returns top-10 most relevant chunks
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  3. GENERATE          │  System prompt + context + query
│     Groq LLM          │  → Raw Tailwind HTML slides with
│     (llama/mixtral)    │    CSS animations & Stranger Things theme
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  4. RENDER            │  HTML Exporter wraps slides with
│     HTML Exporter     │  Tailwind CDN + animation keyframes
│                       │  → Slideshow with keyboard navigation
└───────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 (CDN) | UI components |
| **Styling** | Tailwind CSS (CDN) | Slide design + responsive layout |
| **JSX Compile** | Babel Standalone | In-browser JSX → JS compilation |
| **Backend** | Django + DRF | REST API + file handling |
| **LLM** | Groq (via LlamaIndex) | Slide content generation |
| **Embeddings** | Sentence-Transformers | Document chunk embeddings |
| **Vector DB** | MongoDB Atlas | Vector search for RAG retrieval |
| **Doc Parsing** | PyMuPDF | PDF text extraction |

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'dotenv'` | Run `pip install python-dotenv` |
| CORS errors in browser console | Make sure `django-cors-headers` is installed and `CORS_ALLOW_ALL_ORIGINS = True` in `settings.py` |
| Blank presentation panel | Check Django server logs for LLM errors. Ensure `GROQ_API_KEY` is valid. |
| Slides show as one big block | The LLM may not have produced `<!-- SLIDE_BREAK -->` markers. Try regenerating. |
| Frontend won't load | Make sure you're running `python -m http.server` from the `frontend-react/` directory |

---

## 📜 License

Built for **Hackfest** 🏆

---

<p align="center">
  <i>"Mornings are for coffee and contemplation."</i> — Chief Hopper
</p>
