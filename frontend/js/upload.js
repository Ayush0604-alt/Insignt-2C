/* ─────────────────────────────────────────────────────────────
   Insight2C — upload.js
   Handles: upload, chart generation, UI state, history
───────────────────────────────────────────────────────────── */

// ── State ──────────────────────────────────────────────────
const state = {
    filePath:   "",
    columns:    { numeric_columns: [], categorical_columns: [] },
    chartColor: "orange",
    history:    [],   // { imageUrl, label, time }
};

// ── DOM refs ───────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

const els = {
    fileInput:        $("fileInput"),
    fileName:         $("fileName"),
    fileInfo:         $("fileInfo"),
    dropZone:         $("dropZone"),
    uploadBtn:        $("uploadDatasetBtn"),
    uploadStatus:     $("uploadStatus"),
    configCard:       $("configCard"),
    cleanCard:        $("cleanCard"),
    chartType:        $("chartType"),
    chartColor:       $("chartColor"),
    binsContainer:    $("binsContainer"),
    binsInput:        $("binsInput"),
    binsValue:        $("binsValue"),
    xColumnContainer: $("xColumnContainer"),
    yColumnContainer: $("yColumnContainer"),
    yColumnLabel: $("yColumnLabel"),
    xColumn:          $("xColumn"),
    yColumn:          $("yColumn"),
    heatmapInfo:      $("heatmapInfo"),
    generateBtn:      $("generateChartBtn"),
    message:          $("message"),
    emptyState:       $("emptyChartState"),
    chartDisplay:     $("chartDisplay"),
    chartImage:       $("chartImage"),
    chartTitle:       $("chartTitle"),
    downloadChartBtn: $("downloadChartBtn"),
    downloadDataset:  $("downloadDatasetBtn"),
    statsRow:         $("statsRow"),
    statRows:         $("statRows"),
    statCols:         $("statCols"),
    statDups:         $("statDups"),
    statMissing:      $("statMissing"),
    statQuality:      $("statQuality"),
    analyticsRow:     $("analyticsRow"),
    cleaningReport:   $("cleaningReportContent"),
    insightsList:     $("insightsList"),
    recBanner:        $("recommendationsBanner"),
    recChips:         $("recChips"),
    historyCard:      $("historyCard"),
    historyGrid:      $("historyGrid"),
    clearHistoryBtn:  $("clearHistoryBtn"),
    headerStatus:     $("headerStatus"),
};

// ── Init ───────────────────────────────────────────────────
function init() {
    setupDragDrop();
    setupColorPicker();
    setupBinsSlider();

    els.fileInput.addEventListener("change", onFileSelected);
    els.uploadBtn.addEventListener("click", uploadDataset);
    els.generateBtn.addEventListener("click", generateChart);
    els.chartType.addEventListener("change", updateColumnDropdowns);
    els.clearHistoryBtn.addEventListener("click", clearHistory);
}

// ── Drag & Drop ────────────────────────────────────────────
function setupDragDrop() {
    const zone = els.dropZone;

    zone.addEventListener("dragover", (e) => {
        e.preventDefault();
        zone.classList.add("drag-over");
    });

    zone.addEventListener("dragleave", () => {
        zone.classList.remove("drag-over");
    });

    zone.addEventListener("drop", (e) => {
        e.preventDefault();
        zone.classList.remove("drag-over");
        const file = e.dataTransfer.files[0];
        if (file) {
            els.fileInput.files = e.dataTransfer.files;
            onFileSelected();
        }
    });

    zone.addEventListener("click", (e) => {
        if (e.target.classList.contains("btn-outline") || e.target === zone) return;
        els.fileInput.click();
    });
}

// ── File Selected ──────────────────────────────────────────
function onFileSelected() {
    const file = els.fileInput.files[0];
    if (!file) return;
    els.fileName.textContent = file.name;
    els.fileInfo.classList.remove("hidden");
}

// ── Color Picker ───────────────────────────────────────────
function setupColorPicker() {
    document.querySelectorAll(".color-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".color-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            state.chartColor = btn.dataset.color;
            els.chartColor.value = btn.dataset.color;
        });
    });
}

// ── Bins Slider ────────────────────────────────────────────
function setupBinsSlider() {
    els.binsInput.addEventListener("input", () => {
        els.binsValue.textContent = els.binsInput.value;
    });
}

// ── Status Helpers ─────────────────────────────────────────
function setStatus(el, message, type = "") {
    el.textContent = message;
    el.className = "status-msg" + (type ? ` ${type}` : "");
}

function setHeaderStatus(text, loading = false) {
    const dot = els.headerStatus.querySelector(".status-dot");
    els.headerStatus.querySelector("span:last-child").textContent = text;
    dot.className = "status-dot" + (loading ? " loading" : "");
}

function setButtonLoading(btn, loading) {
    const text    = btn.querySelector(".btn-text");
    const spinner = btn.querySelector(".btn-spinner");
    if (loading) {
        text.textContent = "Working…";
        spinner.classList.remove("hidden");
        btn.classList.add("loading");
    } else {
        spinner.classList.add("hidden");
        btn.classList.remove("loading");
    }
}

// ── Upload Dataset ─────────────────────────────────────────
async function uploadDataset() {
    const file = els.fileInput.files[0];

    if (!file) {
        setStatus(els.uploadStatus, "Please select a dataset file.", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setButtonLoading(els.uploadBtn, true);
    setStatus(els.uploadStatus, "Uploading…");
    setHeaderStatus("Uploading…", true);

    try {
        const res  = await fetch(`${window.location.origin}/api/upload-file`, {
            method: "POST",
            body:   formData,
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.message);

        state.filePath = data.filePath;
        state.columns  = data.columns;

        // Enable config + clean cards
        els.configCard.classList.add("enabled");
        els.cleanCard.classList.add("enabled");

        // Populate dropdowns
        updateColumnDropdowns();

        // Show recommendations if returned
        if (data.recommendations?.length) {
            showRecommendations(data.recommendations);
        }

        setStatus(els.uploadStatus, `Uploaded: ${file.name}`, "success");
        setHeaderStatus("Ready");

        // Update upload btn text
        els.uploadBtn.querySelector(".btn-text").textContent = "Re-upload";

    } catch (err) {
        console.error(err);
        setStatus(els.uploadStatus, `Error: ${err.message}`, "error");
        setHeaderStatus("Error");
    } finally {
        setButtonLoading(els.uploadBtn, false);
    }
}

// ── Column Dropdowns ───────────────────────────────────────
function updateColumnDropdowns() {
    const chartType = els.chartType.value;
    const { numeric_columns = [], categorical_columns = [] } = state.columns;

    els.xColumn.innerHTML = "";
    els.yColumn.innerHTML = "";

    // Reset visibility
    els.xColumnContainer.classList.remove("hidden");
    els.yColumnContainer.classList.remove("hidden");
    els.binsContainer.classList.remove("hidden");
    els.heatmapInfo.classList.add("hidden");
    els.yColumnLabel.textContent = "Y Column";

    const addOptions = (select, cols) => {
        cols.forEach((col) => {
            const opt = document.createElement("option");
            opt.value = col;
            opt.textContent = col;
            select.appendChild(opt);
        });
    };

    switch (chartType) {
        case "histogram":
            els.yColumnContainer.classList.add("hidden");
            addOptions(els.xColumn, numeric_columns);
            break;

        case "pie":
            els.yColumnContainer.classList.add("hidden");
            els.binsContainer.classList.add("hidden");
            addOptions(els.xColumn, categorical_columns);
            break;

        case "scatter":
            els.binsContainer.classList.add("hidden");
            addOptions(els.xColumn, numeric_columns);
            addOptions(els.yColumn, numeric_columns);
            // Default Y to second column if available
            if (els.yColumn.options.length > 1) {
                els.yColumn.selectedIndex = 1;
            }
            break;

        case "bar":
            els.binsContainer.classList.add("hidden");
            addOptions(
                els.xColumn,
                categorical_columns.filter(c => !c.toLowerCase().includes("id"))
            );
            addOptions(els.yColumn, numeric_columns);
            break;

        case "boxplot":
            els.binsContainer.classList.add("hidden");
            els.yColumnLabel.textContent = "Group By (optional)";
            addOptions(els.xColumn, numeric_columns);

            const noneOpt = document.createElement("option");
            noneOpt.value = "";
            noneOpt.textContent = "None";
            els.yColumn.appendChild(noneOpt);
            addOptions(
                els.yColumn,
                categorical_columns.filter(c => !c.toLowerCase().includes("id"))
            );
            break;

        case "heatmap":
            els.xColumnContainer.classList.add("hidden");
            els.yColumnContainer.classList.add("hidden");
            els.binsContainer.classList.add("hidden");
            els.heatmapInfo.classList.remove("hidden");
            break;
    }
}

// ── Recommendations ────────────────────────────────────────
function showRecommendations(recs) {
    els.recChips.innerHTML = "";
    recs.forEach(({ chart, reason }) => {
        const chip = document.createElement("button");
        chip.className = "rec-chip";
        chip.textContent = chartLabel(chart);
        chip.title = reason;
        chip.addEventListener("click", () => {
            els.chartType.value = chart;
            updateColumnDropdowns();
            // Scroll sidebar to chart config
            document.getElementById("configCard").scrollIntoView({ behavior: "smooth" });
        });
        els.recChips.appendChild(chip);
    });
    els.recBanner.classList.remove("hidden");
}

function chartLabel(type) {
    return { histogram: "Histogram", bar: "Bar Chart", pie: "Pie Chart", scatter: "Scatter Plot", heatmap: "Heatmap", boxplot: "Boxplot" }[type] || type;
}

// ── Validate chart selection ───────────────────────────────
function validateChartSelection(chartType, xColumn, yColumn) {
    const { numeric_columns = [] } = state.columns;

    if (chartType === "pie" && xColumn.toLowerCase().includes("id")) {
        return "Pie chart is not suitable for ID columns.";
    }
    if (chartType === "scatter" && xColumn === yColumn) {
        return "Scatter plot requires two different columns.";
    }
    if (chartType === "heatmap" && numeric_columns.length < 2) {
        return "Heatmap requires at least 2 numeric columns.";
    }
    return null;
}

// ── Generate Chart ─────────────────────────────────────────
async function generateChart() {
    if (!state.filePath) {
        setStatus(els.message, "Please upload a dataset first.", "error");
        return;
    }

    const chartType       = els.chartType.value;
    const xColumn         = els.xColumn.value;
    const yColumn         = els.yColumn.value;
    const removeDuplicates = $("removeDuplicates").checked;
    const dropMissing      = $("dropMissing").checked;
    const missingStrategy  = $("missingStrategy").value;
    const chartColor       = state.chartColor;
    const bins             = els.binsInput.value;

    const validationError = validateChartSelection(chartType, xColumn, yColumn);
    if (validationError) {
        setStatus(els.message, validationError, "error");
        return;
    }

    setButtonLoading(els.generateBtn, true);
    setStatus(els.message, "Generating chart…");
    setHeaderStatus("Generating…", true);

    try {
        const res  = await fetch(`${window.location.origin}/api/generate-chart`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({
                filePath: state.filePath,
                chartType,
                xColumn,
                yColumn,
                removeDuplicates,
                dropMissing,
                missingStrategy,
                chartColor,
                bins,
            }),
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.message);

        // ── Render chart ──────────────────────────────────
        const imageUrl = `${data.imageUrl}?t=${Date.now()}`;

        els.chartImage.src    = imageUrl;
        els.chartTitle.textContent = `${chartLabel(chartType)} — ${xColumn || "All Columns"}`;
        els.emptyState.classList.add("hidden");
        els.chartDisplay.classList.remove("hidden");
        els.downloadChartBtn.href   = data.imageUrl;
        els.downloadDataset.href    = data.cleanedFileUrl;

        // ── Stats ─────────────────────────────────────────
        const s = data.summary;
        const totalMissing = Object.values(s.missing_values || {}).reduce((a, b) => a + b, 0);
        els.statRows.textContent    = s.rows.toLocaleString();
        els.statCols.textContent    = s.columns.toLocaleString();
        els.statDups.textContent    = s.duplicate_rows.toLocaleString();
        els.statMissing.textContent = totalMissing.toLocaleString();

        const qualityScore = s.data_quality_score;
        els.statQuality.textContent = qualityScore != null ? `${qualityScore}` : "—";
        els.statQuality.classList.remove("quality-good", "quality-fair", "quality-poor");
        if (qualityScore != null) {
            const tier = qualityScore >= 80 ? "quality-good" : qualityScore >= 50 ? "quality-fair" : "quality-poor";
            els.statQuality.classList.add(tier);
        }

        els.statsRow.classList.remove("hidden");

        // ── Cleaning Report ───────────────────────────────
        const cr = data.cleaningReport || {};
        els.cleaningReport.innerHTML = `
            <div class="report-row"><span>Duplicate Rows</span><strong>${cr.duplicate_rows ?? "—"}</strong></div>
            <div class="report-row"><span>Empty Columns</span><strong>${(cr.empty_columns || []).length}</strong></div>
            <div class="report-row"><span>Numeric-String Cols</span><strong>${(cr.numeric_string_columns || []).length}</strong></div>
            ${Object.entries(cr.missing_values || {}).slice(0, 5).map(
                ([col, count]) => `<div class="report-row"><span>${col}</span><strong>${count} missing</strong></div>`
            ).join("")}
        `;

        // ── Insights ──────────────────────────────────────
        els.insightsList.innerHTML = (data.insights || [])
            .map((item, i) => `<li style="animation-delay:${i * 0.05}s">${item}</li>`)
            .join("");

        els.analyticsRow.classList.remove("hidden");

        // ── History ───────────────────────────────────────
        addToHistory(imageUrl, `${chartType} · ${xColumn || "auto"}`);

        setStatus(els.message, "Chart generated successfully", "success");
        setHeaderStatus("Done");

    } catch (err) {
        console.error(err);
        setStatus(els.message, `Error: ${err.message}`, "error");
        setHeaderStatus("Error");
    } finally {
        setButtonLoading(els.generateBtn, false);
        // Reset generate button label
        els.generateBtn.querySelector(".btn-text").textContent = "Generate Chart";
    }
}

// ── Chart History ──────────────────────────────────────────
function addToHistory(imageUrl, label) {
    state.history.unshift({ imageUrl, label, time: Date.now() });

    // Keep max 12
    if (state.history.length > 12) state.history.pop();

    renderHistory();
    els.historyCard.classList.remove("hidden");
}

function renderHistory() {
    els.historyGrid.innerHTML = state.history.map((item, i) => `
        <div class="history-item" onclick="loadHistoryItem(${i})" title="${item.label}">
            <img src="${item.imageUrl}" alt="${item.label}" loading="lazy">
            <div class="history-item-label">${item.label}</div>
        </div>
    `).join("");
}

function loadHistoryItem(index) {
    const item = state.history[index];
    if (!item) return;
    els.chartImage.src = item.imageUrl;
    els.chartTitle.textContent = item.label;
    els.emptyState.classList.add("hidden");
    els.chartDisplay.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

// Expose to inline handlers
window.loadHistoryItem = loadHistoryItem;

function clearHistory() {
    state.history = [];
    els.historyGrid.innerHTML = "";
    els.historyCard.classList.add("hidden");
}

// ── Boot ───────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", init);