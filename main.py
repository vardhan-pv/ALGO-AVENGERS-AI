"""
RepoSense AI — FastAPI Backend
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from github_service import extract_repo_info
from ai_service import analyze_changes
from readme_service import update_readme
import chat_service

app = FastAPI(
    title="RepoSense AI",
    description="Simulated GitHub repository analysis and documentation automation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# ── Request models ─────────────────────────────────────────────────────────

class RepoRequest(BaseModel):
    repo_url: str


class ChatRequest(BaseModel):
    question: str


# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/")
def serve_frontend():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "RepoSense AI backend is running. Open frontend/index.html in your browser."}


@app.get("/health")
def health():
    return {"status": "ok", "service": "RepoSense AI"}


@app.post("/analyze-repo")
def analyze_repo(req: RepoRequest):
    """
    Simulate analyzing a GitHub repository.
    Extracts repo name from URL, returns mock PR data and AI analysis.
    """
    if not req.repo_url or not req.repo_url.strip():
        raise HTTPException(status_code=400, detail="repo_url is required.")

    repo_info = extract_repo_info(req.repo_url)
    analysis = analyze_changes(repo_info)

    # Cache context for chat
    chat_service.set_context(analysis, repo_info)

    return {
        "repo_info": {
            "owner": repo_info["owner"],
            "repo_name": repo_info["repo_name"],
            "full_name": repo_info["full_name"],
            "url": repo_info["url"],
            "stars": repo_info["stars"],
            "forks": repo_info["forks"],
            "open_issues": repo_info["open_issues"],
            "tech_stack": repo_info["tech_stack"],
            "default_branch": repo_info["default_branch"],
            "last_commit": repo_info["last_commit"],
        },
        "analysis": analysis,
    }


@app.post("/update-readme")
def update_readme_endpoint(req: RepoRequest):
    """
    Simulate updating README.md with latest changes.
    Reads README.md, appends a '## 🔄 Latest Updates' section,
    and writes UPDATED_README.md.
    """
    if not req.repo_url or not req.repo_url.strip():
        raise HTTPException(status_code=400, detail="repo_url is required.")

    repo_info = extract_repo_info(req.repo_url)
    analysis = analyze_changes(repo_info)

    # Ensure chat context is updated
    chat_service.set_context(analysis, repo_info)

    result = update_readme(analysis, repo_info)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result


@app.post("/chat")
def chat(req: ChatRequest):
    """
    Answer a question about the analyzed repository.
    Uses keyword matching against cached analysis and UPDATED_README.md.
    """
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required.")

    answer = chat_service.answer_question(req.question)
    return {"answer": answer}
