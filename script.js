/**
 * RepoSense AI — Frontend Logic
 * Communicates with the FastAPI backend (http://localhost:8000)
 */

const API = "http://localhost:8000";

// ── State ────────────────────────────────────────────────────────────────
let currentRepoUrl = "";
let analysisReady = false;

// ── Helpers ──────────────────────────────────────────────────────────────

function setStatus(text, active = true) {
    document.getElementById("statusText").textContent = text;
    const dot = document.querySelector(".status-dot");
    dot.style.background = active ? "var(--accent)" : "var(--warn)";
    dot.style.boxShadow = active ? "0 0 8px var(--accent)" : "0 0 8px var(--warn)";
}

function showLoading(label = "Processing…") {
    document.getElementById("loadingLabel").textContent = label;
    document.getElementById("loadingOverlay").classList.remove("hidden");
}

function hideLoading() {
    document.getElementById("loadingOverlay").classList.add("hidden");
}

function show(id) {
    const el = document.getElementById(id);
    el.classList.remove("hidden");
    el.classList.add("fade-in");
}

function mdBold(text) {
    if (!text) return "No response generated.";

    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/\n/g, "<br>");
}

// ── Analyze Repo ─────────────────────────────────────────────────────────

async function analyzeRepo() {
    const url = document.getElementById("repoUrl").value.trim();
    if (!url) {
        alert("Please enter a GitHub repository URL.");
        return;
    }
    currentRepoUrl = url;

    const btn = document.getElementById("analyzeBtn");
    btn.classList.add("loading");
    btn.disabled = true;
    showLoading("Scanning repository…");
    setStatus("Analyzing…");

    try {
        const res = await fetch(`${API}/analyze-repo`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ repo_url: url }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Server error");
        }

        const data = await res.json();
        renderRepoCard(data.repo_info);
        renderAnalysis(data.analysis, data.repo_info);

        analysisReady = true;
        document.getElementById("updateBtn").disabled = false;
        setStatus("Analysis Complete");

        appendChatMessage(
            "assistant",
            `✅ Analyzed <strong>${data.repo_info.full_name}</strong>! Found <strong>${data.analysis.total_prs}</strong> recent PR(s) and <strong>${data.analysis.files_affected}</strong> changed files. Ask me anything about this project!`
        );

    } catch (err) {
        setStatus("Error", false);
        appendChatMessage("assistant", `⚠️ Could not analyze repository: <em>${err.message}</em>. Make sure the backend is running on port 8000.`);
    } finally {
        btn.classList.remove("loading");
        btn.disabled = false;
        hideLoading();
    }
}

// ── Render Repo Card ─────────────────────────────────────────────────────

function renderRepoCard(info) {
    document.getElementById("repoName").textContent = info.full_name;
    document.getElementById("statStars").textContent = `★ ${info.stars.toLocaleString()}`;
    document.getElementById("statForks").textContent = `⑂ ${info.forks.toLocaleString()}`;
    document.getElementById("statIssues").textContent = `⚠ ${info.open_issues}`;

    const stackRow = document.getElementById("stackRow");
    stackRow.innerHTML = info.tech_stack
        .map(t => `<span class="stack-tag">${t}</span>`)
        .join("");

    show("repoCard");
}

// ── Render Analysis ──────────────────────────────────────────────────────

function renderAnalysis(analysis, info) {
    // Summary
    document.getElementById("summaryText").innerHTML = mdBold(analysis.summary);

    // Metrics
    document.getElementById("metricsGrid").innerHTML = `
    <div class="metric">
      <div class="metric-val">${analysis.total_prs}</div>
      <div class="metric-label">Pull Requests</div>
    </div>
    <div class="metric">
      <div class="metric-val">${analysis.files_affected}</div>
      <div class="metric-label">Files Changed</div>
    </div>
    <div class="metric">
      <div class="metric-val">${analysis.contributors.length}</div>
      <div class="metric-label">Contributors</div>
    </div>
  `;

    // PR List
    const prList = document.getElementById("prList");
    prList.innerHTML = analysis.changelog.map(pr => `
    <div class="pr-item ${pr.breaking ? "breaking" : ""}">
      <div class="pr-id">${pr.id}</div>
      <div class="pr-body">
        <div class="pr-title">${pr.title}</div>
        <div class="pr-meta">@${pr.author} · ${formatDate(pr.merged_at)}</div>
      </div>
      ${pr.breaking ? '<div class="pr-break-tag">⚠ BREAKING</div>' : ""}
    </div>
  `).join("");

    // Breaking changes banner
    const banner = document.getElementById("breakingBanner");
    if (analysis.has_breaking_changes) {
        const items = analysis.breaking_changes
            .map(bc => `<div>• <strong>${bc.pr}</strong>: ${bc.note}</div>`)
            .join("");
        document.getElementById("breakingContent").innerHTML =
            `<strong>Breaking Changes Detected — Review Before Upgrading</strong>${items}`;
        banner.classList.remove("hidden");
    } else {
        banner.classList.add("hidden");
    }

    show("analysisCard");
}

// ── Update README ─────────────────────────────────────────────────────────

async function updateReadme() {
    if (!currentRepoUrl) return;

    const btn = document.getElementById("updateBtn");
    btn.disabled = true;
    showLoading("Updating README…");
    setStatus("Updating README…");

    try {
        const res = await fetch(`${API}/update-readme`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ repo_url: currentRepoUrl }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Server error");
        }

        const data = await res.json();
        renderReadmeCard(data);
        setStatus("README Updated");

        appendChatMessage(
            "assistant",
            `📄 <strong>UPDATED_README.md</strong> has been written! Added ${data.updated_lines - data.original_lines} new lines with the latest changelog, breaking change notices, and setup instructions.`
        );

    } catch (err) {
        setStatus("Error", false);
        appendChatMessage("assistant", `⚠️ Failed to update README: <em>${err.message}</em>`);
    } finally {
        btn.disabled = false;
        hideLoading();
    }
}

// ── Render README Card ────────────────────────────────────────────────────

function renderReadmeCard(data) {
    document.getElementById("readmeMeta").innerHTML = `
    <span>Output: <span>${data.output_file}</span></span>
    <span>Original lines: <span>${data.original_lines}</span></span>
    <span>Updated lines: <span>${data.updated_lines}</span></span>
  `;
    document.getElementById("readmePreview").textContent = data.preview;
    show("readmeCard");
}

// ── Chat ──────────────────────────────────────────────────────────────────

async function sendChat() {
    const input = document.getElementById("chatInput");
    const question = input.value.trim();
    if (!question) return;

    input.value = "";
    appendChatMessage("user", escapeHtml(question));

    // Thinking indicator
    const thinkingId = "thinking-" + Date.now();
    appendThinking(thinkingId);

    try {
        const res = await fetch(`${API}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Server error");
        }

        const data = await res.json();
        removeThinking(thinkingId);

        if (!data.answer) {
            appendChatMessage("assistant", "Sorry, I couldn't generate a response. Please try again.");
        } else {
            appendChatMessage("assistant", mdBold(data.answer));
        }

    } catch (err) {
        removeThinking(thinkingId);
        appendChatMessage("assistant", `⚠️ Chat error: <em>${err.message}</em>. Is the backend running?`);
    }
}

function quickAsk(text) {
    document.getElementById("chatInput").value = text;
    sendChat();
}

function appendChatMessage(role, html) {
    const container = document.getElementById("chatMessages");
    const initials = role === "assistant" ? "AI" : "YOU";

    const msg = document.createElement("div");
    msg.className = `chat-msg ${role} fade-in`;
    msg.innerHTML = `
    <div class="msg-avatar">${initials}</div>
    <div class="msg-bubble">${html}</div>
  `;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
}

function appendThinking(id) {
    const container = document.getElementById("chatMessages");
    const msg = document.createElement("div");
    msg.className = "chat-msg assistant thinking fade-in";
    msg.id = id;
    msg.innerHTML = `
    <div class="msg-avatar">AI</div>
    <div class="msg-bubble">
      <div class="dot"></div><div class="dot"></div><div class="dot"></div>
    </div>
  `;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
}

function removeThinking(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// ── Utils ─────────────────────────────────────────────────────────────────

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function formatDate(iso) {
    try {
        return new Date(iso).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    } catch {
        return iso;
    }
}

// ── Enter key for repo input ──────────────────────────────────────────────

document.getElementById("repoUrl").addEventListener("keydown", e => {
    if (e.key === "Enter") analyzeRepo();
});