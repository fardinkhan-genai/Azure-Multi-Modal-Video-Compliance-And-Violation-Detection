const videoUrl = document.getElementById("videoUrl");
const auditButton = document.getElementById("auditButton");
const message = document.getElementById("message");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");

// Send the video URL to the existing backend API.
async function startAudit() {
    const url = videoUrl.value.trim();

    if (!url) {
        showError("Please enter a YouTube URL.");
        return;
    }

    setLoading(true);

    try {
        const response = await fetch("/audit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ video_url: url })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Audit failed.");
        }

        showResult(data);
        message.textContent = "Audit completed.";
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    auditButton.disabled = isLoading;
    result.classList.add("hidden");
    errorBox.classList.add("hidden");

    if (isLoading) {
        message.textContent = "Processing video... Azure Video Indexer may take some time.";
    }
}

function showResult(data) {
    const status = document.getElementById("status");
    const report = document.getElementById("report");
    const issues = document.getElementById("issues");

    const statusText = data.status || "UNKNOWN";
    const statusClass = statusText.toUpperCase() === "PASS"
        ? "pass"
        : statusText.toUpperCase() === "FAIL"
            ? "fail"
            : "unknown";

    status.innerHTML = `<span class="status ${statusClass}">${escapeHtml(statusText)}</span>`;
    report.textContent = data.final_report || "No report generated.";

    if (!data.compliance_results || data.compliance_results.length === 0) {
        issues.innerHTML = "<p>No violations found.</p>";
    } else {
        issues.innerHTML = data.compliance_results.map((issue) => `
            <div class="issue">
                <div>
                    <strong>${escapeHtml(issue.severity)}</strong>
                    ${escapeHtml(issue.category)}
                </div>
                <p>${escapeHtml(issue.description)}</p>
            </div>
        `).join("");
    }

    result.classList.remove("hidden");
}

function showError(messageText) {
    errorBox.textContent = messageText;
    errorBox.classList.remove("hidden");
    message.textContent = "";
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

auditButton.addEventListener("click", startAudit);

videoUrl.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        startAudit();
    }
});
