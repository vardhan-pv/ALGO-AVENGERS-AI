"""
AI Service — Simulates LLM-based analysis of repository changes.
Generates structured, human-readable summaries from mock PR data.
"""


def analyze_changes(repo_info: dict) -> dict:
    """
    Produce a structured AI analysis of recent pull requests.
    Returns summary, breaking changes, and plain-English explanation.
    """
    prs = repo_info.get("recent_prs", [])
    repo_name = repo_info.get("repo_name", "this project")
    tech_stack = repo_info.get("tech_stack", [])

    # Build summary sentence
    pr_titles = [pr["title"] for pr in prs]
    breaking_prs = [pr for pr in prs if pr.get("breaking")]
    non_breaking_prs = [pr for pr in prs if not pr.get("breaking")]

    summary_parts = []
    if pr_titles:
        summary_parts.append(
            f"Detected {len(prs)} merged pull request(s) in **{repo_name}**."
        )
    if breaking_prs:
        summary_parts.append(
            f"{len(breaking_prs)} of them introduce breaking changes that require migration."
        )
    if non_breaking_prs:
        summary_parts.append(
            f"{len(non_breaking_prs)} change(s) are backward-compatible improvements."
        )

    summary = " ".join(summary_parts) or f"No recent changes detected in {repo_name}."

    # Breaking changes list
    breaking_changes = []
    for pr in breaking_prs:
        breaking_changes.append({
            "pr": pr["id"],
            "title": pr["title"],
            "note": pr.get("breaking_note", "Review required before upgrading."),
            "author": pr["author"],
        })

    # Simple explanation paragraph
    stack_str = ", ".join(tech_stack) if tech_stack else "modern technologies"
    explanations = []
    for pr in prs:
        explanations.append(
            f"• **{pr['id']}** by @{pr['author']}: {pr['description']}"
        )

    simple_explanation = (
        f"This project is built with {stack_str}. "
        f"Here's what changed recently:\n\n"
        + "\n".join(explanations)
    )

    # Changelog entries
    changelog = []
    for pr in prs:
        changelog.append({
            "id": pr["id"],
            "title": pr["title"],
            "author": pr["author"],
            "merged_at": pr["merged_at"],
            "files_changed": pr["files_changed"],
            "breaking": pr["breaking"],
        })

    # Setup instructions (simulated)
    setup_steps = [
        f"Clone the repository: `git clone {repo_info.get('url', 'https://github.com/...')}`",
        "Install dependencies: `pip install -r requirements.txt`",
        "Copy environment file: `cp .env.example .env`",
        "Start the application: `uvicorn main:app --reload`",
    ]

    if any("docker" in pr["title"].lower() for pr in prs):
        setup_steps.insert(2, "Or use Docker: `docker-compose up --build`")

    return {
        "summary": summary,
        "breaking_changes": breaking_changes,
        "simple_explanation": simple_explanation,
        "changelog": changelog,
        "setup_instructions": setup_steps,
        "total_prs": len(prs),
        "has_breaking_changes": len(breaking_prs) > 0,
        "files_affected": sum(len(pr["files_changed"]) for pr in prs),
        "contributors": list({pr["author"] for pr in prs}),
    }
