# RepoSense AI

A smart documentation assistant that monitors your GitHub repository and keeps your README always up to date.

## Features

- Automatic change detection from pull requests
- AI-powered README generation
- Interactive chat interface for project Q&A
- Breaking change alerts

## Setup

1. Clone the repository
2. Install dependencies: `pip install fastapi uvicorn`
3. Run: `uvicorn main:app --reload`

## How to Run

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Then open `frontend/index.html` in your browser.

## Tech Stack

- Python + FastAPI (backend)
- Vanilla JS + HTML/CSS (frontend)
- File-based storage (no database)

## API Endpoints

- `POST /analyze-repo` - Analyze a GitHub repository
- `POST /update-readme` - Update the README with latest changes
- `POST /chat` - Chat about your project
