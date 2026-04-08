"""
Chat Service — Now powered by LLM (OpenAI GPT)
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Loads OPENAI_API_KEY from .env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory cache for last analysis
_last_analysis: dict = {}
_last_repo_info: dict = {}
_last_readme_content: str = ""


def set_context(analysis: dict, repo_info: dict):
    """Cache the latest analysis and README for LLM context."""
    global _last_analysis, _last_repo_info, _last_readme_content
    _last_analysis = analysis
    _last_repo_info = repo_info
    
    # Read the latest UPDATED_README.md
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "..", "UPDATED_README.md"), "r", encoding="utf-8") as f:
            _last_readme_content = f.read()
    except FileNotFoundError:
        _last_readme_content = ""


def answer_question(question: str) -> str:
    if not _last_analysis:
        return "Please click **Analyze Repo** first so I can understand the repository and answer your questions accurately."

    try:
        # Build rich context for the LLM
        context = f"""
You are RepoSense AI, an expert assistant for the GitHub repository: {_last_repo_info.get('full_name', 'this project')}.

Tech Stack: {', '.join(_last_repo_info.get('tech_stack', []))}

Recent Changes Summary:
{_last_analysis.get('simple_explanation', 'No changes detected.')}

Breaking Changes:
{len(_last_analysis.get('breaking_changes', []))} breaking changes detected.

Setup Instructions from analysis:
{chr(10).join(_last_analysis.get('setup_instructions', []))}

Latest README Content (most important):
{_last_readme_content[-8000:]}  # Last 8000 chars to stay within token limit
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",          # Fast & cheap. Use "gpt-4o" for better quality
            temperature=0.7,
            max_tokens=800,
            messages=[
                {"role": "system", "content": "You are a helpful, concise, and technically accurate assistant for this GitHub project. Always base your answers on the provided context. Use markdown formatting."},
                {"role": "user", "content": f"Context:\n{context}\n\nUser Question: {question}"}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"LLM Error: {e}")
        # Fallback to old keyword system if LLM fails
        return f"Sorry, I encountered an error while using the AI. Please try again. (Error: {str(e)[:100]})"