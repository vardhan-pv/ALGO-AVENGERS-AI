"""
GitHub Service — Simulates extracting repo info and recent PR changes.
No real API calls are made; all data is mocked for demo purposes.
"""

import random
from urllib.parse import urlparse


MOCK_PR_POOL = [
    {
        "id": "PR-142",
        "title": "Add JWT authentication system",
        "author": "alice_dev",
        "merged_at": "2025-01-15T10:30:00Z",
        "files_changed": ["auth/jwt.py", "middleware/auth.py", "tests/test_auth.py"],
        "description": "Implemented JWT-based authentication with refresh token support. All API endpoints now require Bearer tokens.",
        "breaking": True,
        "breaking_note": "All API endpoints now require Authorization header.",
    },
    {
        "id": "PR-139",
        "title": "Refactor database connection pooling",
        "author": "bob_engineer",
        "merged_at": "2025-01-13T14:15:00Z",
        "files_changed": ["db/pool.py", "config/database.py"],
        "description": "Switched to async connection pooling using asyncpg. Improves throughput by ~40% under load.",
        "breaking": False,
        "breaking_note": None,
    },
    {
        "id": "PR-135",
        "title": "Add rate limiting middleware",
        "author": "charlie_ops",
        "merged_at": "2025-01-11T09:00:00Z",
        "files_changed": ["middleware/rate_limit.py", "config/settings.py", "README.md"],
        "description": "Rate limiting added: 100 requests/minute per IP by default. Configurable via RATE_LIMIT env variable.",
        "breaking": False,
        "breaking_note": None,
    },
    {
        "id": "PR-131",
        "title": "Migrate to v3 REST API endpoints",
        "author": "diana_backend",
        "merged_at": "2025-01-09T16:45:00Z",
        "files_changed": ["api/v3/routes.py", "api/v2/deprecated.py", "docs/migration.md"],
        "description": "All routes migrated to /api/v3/. v2 endpoints still work but emit deprecation warnings.",
        "breaking": True,
        "breaking_note": "Base path changed from /api/v2 to /api/v3.",
    },
    {
        "id": "PR-128",
        "title": "Add Docker Compose setup for local dev",
        "author": "eve_devops",
        "merged_at": "2025-01-07T11:20:00Z",
        "files_changed": ["docker-compose.yml", "Dockerfile", ".env.example"],
        "description": "Added full Docker Compose stack with PostgreSQL, Redis, and the app service for one-command local setup.",
        "breaking": False,
        "breaking_note": None,
    },
    {
        "id": "PR-124",
        "title": "Implement WebSocket support for real-time events",
        "author": "frank_fullstack",
        "merged_at": "2025-01-05T08:30:00Z",
        "files_changed": ["ws/handlers.py", "ws/events.py", "frontend/socket.js"],
        "description": "WebSocket endpoint at /ws/events now broadcasts live updates to connected clients.",
        "breaking": False,
        "breaking_note": None,
    },
]


MOCK_TECH_STACKS = {
    "web": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
    "ml": ["Python", "PyTorch", "FastAPI", "Celery", "MinIO"],
    "frontend": ["TypeScript", "React", "Vite", "Tailwind CSS", "Zustand"],
    "fullstack": ["Node.js", "Express", "MongoDB", "Vue.js", "AWS S3"],
    "mobile": ["Dart", "Flutter", "Firebase", "REST APIs"],
}


def extract_repo_info(repo_url: str) -> dict:
    """Parse a GitHub URL and return structured repo metadata."""
    try:
        parsed = urlparse(repo_url.strip())
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]

        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo_name = path_parts[1].replace(".git", "")
        elif len(path_parts) == 1:
            owner = "unknown"
            repo_name = path_parts[0].replace(".git", "")
        else:
            owner = "demo-org"
            repo_name = "demo-project"

    except Exception:
        owner = "demo-org"
        repo_name = "demo-project"

    # Deterministic "randomness" based on repo name length
    stack_key = list(MOCK_TECH_STACKS.keys())[len(repo_name) % len(MOCK_TECH_STACKS)]
    tech_stack = MOCK_TECH_STACKS[stack_key]

    # Pick 3–4 PRs deterministically
    num_prs = 3 + (len(repo_name) % 2)
    selected_prs = MOCK_PR_POOL[:num_prs]

    return {
        "owner": owner,
        "repo_name": repo_name,
        "full_name": f"{owner}/{repo_name}",
        "url": repo_url,
        "stars": 200 + (len(repo_name) * 47) % 800,
        "forks": 20 + (len(repo_name) * 13) % 120,
        "open_issues": 5 + (len(repo_name) * 3) % 30,
        "tech_stack": tech_stack,
        "recent_prs": selected_prs,
        "default_branch": "main",
        "last_commit": "2025-01-15T12:00:00Z",
    }
